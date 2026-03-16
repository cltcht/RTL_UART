import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
import numpy as np



def build_frame_UART(DATA_hex, START: bool, STOP: bool, len_data):

    #Conversion binaire + zero padding 
    DATA_bin = bin(DATA_hex)[2:].zfill(len_data)

    ## Reverse data for LSB first
    DATA_lsb_first = [int(DATA_bin[len(DATA_bin)-1-i]) for i in range (len(DATA_bin))]

    TRAME_UART = [START] + DATA_lsb_first + [STOP]
    return TRAME_UART


async def send_frame(dut, DATA_hex, CLK_PER_BIT, verbose = False):

    START = 0
    STOP = 1
    TRAME_UART = build_frame_UART(DATA_hex, START, STOP, len_data = 8)
    if verbose :
        print(f" DATA_hex : {hex(DATA_hex)}")
        print(f" TRAME UART : {TRAME_UART}") 

    dut.tx_order_i.value = 1
    for i, bit in enumerate(TRAME_UART):

        ## Envoi d'un bit
        dut.tx_o.value = bit 
        
        ## Tempo pour l'envoi d'un bit tous les CLK_PER_BIT
        for _ in range (CLK_PER_BIT) :
            await RisingEdge(dut.clk_i)

        if verbose :
            if i == len(TRAME_UART)-1 :
                print(f"Bit {i}"+" "*(10>i)+ " envoyé = STOP", end="\n")
            elif i == 0 :
                print(f"Bit {i}"+" "*(10>i)+ " envoyé = START", end="\n")
            else :
                print(f"Bit {i}"+" "*(10>i)+ f" envoyé = {bit}", end="\n")
    
    dut.tx_order_i.value = 0

            
    
    for _ in range (CLK_PER_BIT) :
        await RisingEdge(dut.clk_i)
        if verbose : 
            print(f" Flag = {str(dut.flag_tx_o.value)}")

    assert bin(dut.flag_tx_o.value) == bin(1), (f"Test failed with dut.flag_tx_o.value != 1 and DATA_hex = {DATA_hex}")





@cocotb.test()
async def test_uart(dut):
    # Clock TX
    clk_tx = Clock(dut.clk_i, 1, unit="ns") 
    
    cocotb.start_soon(clk_tx.start())

    CLK_PER_BIT = int(115200/115200) 

    # Reset
    dut.rst_i.value = 1
    dut.tx_o.value = 0
    await RisingEdge(dut.clk_i)
    dut.rst_i.value = 0

    await send_frame(dut, 0xFF, CLK_PER_BIT, verbose = True)
    await send_frame(dut, 0xF0, CLK_PER_BIT, verbose = True)



