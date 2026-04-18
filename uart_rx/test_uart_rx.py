#C. Cho.
#############
# LIBRARIES #
#############
import cocotb
from cocotb.clock import Clock, Timer
from cocotb.triggers import *
import numpy as np
from asyncio import CancelledError
import sys
sys.path.append("../common")
from common.clock_and_logger import *
from common.common_uart import *
import os

#############
# FUNCTIONS #
#############


async def receive_frame(dut, DATA_hex, CLK_PER_BIT, verbose = False):

    START = 0
    STOP = 1

    FRAME_UART = build_frame_UART(DATA_hex, START, STOP, len_data = 12)
    if verbose : 
        print(f" DATA_hex : {hex(DATA_hex)}")
        print(f" TRAME UART : {FRAME_UART}")

    State_dict = {"0":"IDLE", "1":"START", "2":"DATA", "3":"STOP"}

    for i, bit in enumerate(FRAME_UART):
        if verbose :
        ## Bit à envoyer
            if i == 0 :
                print(f"\nBit {i}"+" "*(10>i)+ " à envoyer = START", end=" ")
            elif i == len(FRAME_UART)-1 :
                print(f"\nBit {i}"+" "*(10>i)+ " à envoyer = STOP", end=" ")
            else :
                print(f"\nBit {i}"+" "*(10>i)+ f" à envoyer = {bit}", end=" ")

            print(f" State = {State_dict[str(int(dut.state.value))]}")

        ## Sending a bit -> supposing await RisingEdge is called out of function
        await ReadWrite()
        dut.rx_i.value = bit 
        
        ## Tempo for sending a bit every CLK_PER_BIT
        for _ in range (int(CLK_PER_BIT/2)) :
            await RisingEdge(dut.clk_i)

        ## Analysis of state after CLK_PER_BIT/2 for start
        if verbose :
            if i == 0 :
                print(f"Bit {i}"+" "*(10>i)+ " reçu = START", end=" ")

        ## Analysis of state after CLK_PER_BIT for sending a bit
        for _ in range (int(CLK_PER_BIT/2)) :
            await RisingEdge(dut.clk_i)

        if verbose :
            if i == len(FRAME_UART)-1 :
                print(f"Bit {i}"+" "*(10>i)+ " reçu = STOP", end=" ")
            else :
                print(f"Bit {i}"+" "*(10>i)+ f" reçu = {bit}", end=" ")

            await ReadWrite()
            print(f" State = {State_dict[str(int(dut.state.value))]}")


    for _ in range (CLK_PER_BIT) :
        await RisingEdge(dut.clk_i)

    await ReadWrite()
    assert bin(dut.data_o.value) == bin(DATA_hex), (f"Test failed with dut.data_o.value = {bin(dut.data_o.value)} and DATA_hex = {bin(DATA_hex)}")
    assert dut.flag_rx_o.value == 1, (f"Test failed with dut.flag_rx_o.value = {bin(dut.flag_rx_o.value)} != True ")

PERIOD = 434 #ns
@cocotb.test()
async def get_two_frames_trivial_data(dut):
    """Rx component receives frames as input with 0x000 and 0xFFF as data.  
Validates the coherence of the data output.

    Args:
        dut (cocotb dut): Device under test
    """

    clk_rx = Clock(dut.clk_i, 1, unit="ns") 
    
    cocotb.start_soon(clk_rx.start())

    # Reset
    dut.rst_i.value = 1
    dut.rx_i.value = 1
    await Timer(PERIOD, "ns")
    await ReadWrite()
    dut.rst_i.value = 0

    await Timer(10, "ns")

    DATA_hex = 0xFFF

    CLK_PER_BIT = int(50E6 / 115200) #434 coups d'horloge Rx pour un bit envoyé par Tx

    await receive_frame(dut, DATA_hex, CLK_PER_BIT, verbose = False)

    await Timer(2*PERIOD, "ns")
    DATA_hex = 0x000

    CLK_PER_BIT = int(50E6 / 115200) #434 coups d'horloge Rx pour un bit envoyé par Tx

    await receive_frame(dut, DATA_hex, CLK_PER_BIT, verbose = False)

    await Timer(2*PERIOD, "ns")

@cocotb.test()
async def get_hundred_frames_random_data(dut):
    """Rx component receives hundred frames as input with random data.  
Validates the coherence of the data output.

    Args:
        dut (cocotb dut): Device under test
    """

    clk_rx = Clock(dut.clk_i, 1, unit="ns") 
    
    cocotb.start_soon(clk_rx.start())

    # Reset
    dut.rst_i.value = 1
    dut.rx_i.value = 1
    await Timer(PERIOD, "ns")
    await ReadWrite()
    dut.rst_i.value = 0

    await Timer(10, "ns")

    len_data = 12
    DATA_frames = [np.random.randint(low=0, high=2**(len_data)) for n in range(100)]

    CLK_PER_BIT = int(50E6 / 115200) #434 coups d'horloge Rx pour un bit envoyé par Tx

    for DATA in DATA_frames:
        await receive_frame(dut, DATA, CLK_PER_BIT, verbose = False)

        await Timer(2*PERIOD, "ns")


        




