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
async def send_frame_test(dut, DATA_hex, CLK_PER_BIT, len_data, verbose = False):
    """Send uart frame to DUT

    Args:
        dut (cocotb dut): Cocotb device under test
        DATA_hex (int): Hexadecimal data to be sent
        CLK_PER_BIT (int): Number of clk hit per sent bit  = Clk frequency//baud rate
        len_data (int): Number of hexadecimal figures in DATA_hex
        verbose (bool, optional): Print info in log. Defaults to False.
    """
    ## Goal : Make sure with user that it's a wanted property
    try :
        assert dut.DATA_BITS.value == len_data
    except :
        critical_error_logger = sim_logger("send_frame_test")
        critical_error_logger.print_critical_error(f"Length of data len_data = {len_data} bits, is different from RTL design data length : dut.DATA_BITS = {int(dut.DATA_BITS.value)} ")
        raise ValueError
    
    START = 0
    STOP = 1
    TRAME_UART = build_frame_UART(DATA_hex, START, STOP, len_data)
    TRAME_UART_check = []

    if verbose :
        logger.print_info(f" DATA_hex : {hex(DATA_hex)}")
        logger.print_info(f" TRAME UART : {TRAME_UART}")
    


    # First Time step
    await RisingEdge(dut.clk_i)
    await ReadWrite(dut.clk_i)  # First Evaluation cycle
    dut.data_i.value = DATA_hex
    await NextTimeStep(dut.clk_i)
    await ReadWrite(dut.clk_i)  # Second Evaluation cycle
    dut.tx_order_i.value = 1
     
    if verbose :
        await ReadOnly()
        logger.print_info(f" dut.tx_order_i.value : {dut.tx_order_i.value}\n")


    
    for i, bit in enumerate(TRAME_UART):
        
        # Delay waiting CLK_PER_BIT
        for _ in range (CLK_PER_BIT) :
            await RisingEdge(dut.clk_i)
            
        # Time step for each bit
        await ReadWrite(dut.clk_i)
        dut.data_i.value = bit 

        if verbose :
            if i == len(TRAME_UART)-1 :
                logger.print_info(f"Bit {i}"+" "*(10>i)+ " input = STOP", 
                )
            elif i == 0 :
                logger.print_info(f"Bit {i}"+" "*(10>i)+ " input = START", end="\n")
            else :
                logger.print_info(f"Bit {i}"+" "*(10>i)+ f" input = {bit}", end="\n")
            
            logger.print_info(f" Busy flag = {str(dut.tx_busy_o.value)}")
        assert bin(dut.tx_busy_o.value) == bin(1), (f"Test failed with dut.tx_busy_o.value != 1 and DATA_hex = {DATA_hex}")
    
        await NextTimeStep(dut.clk_i)
        await ReadOnly()
        assert bin(dut.tx_o.value) == bin(TRAME_UART[i]), (f"Test failed with dut.tx_o.value != TRAME_UART[i] and i = {i}")
        

    # Time step to check busy signal
    for _ in range (CLK_PER_BIT) :
        await RisingEdge(dut.clk_i)
        if verbose : 
            await ReadOnly(dut.clk_i) 
            logger.print_info(f" Busy flag = {str(dut.tx_busy_o.value)}")

    assert bin(dut.tx_busy_o.value) == bin(0), (f"Test failed with dut.tx_busy_o.value != 0 and DATA_hex = {DATA_hex}")

    # Time step to set down tx order
    await RisingEdge(dut.clk_i)
    await ReadWrite(dut.clk_i) 
    dut.tx_order_i.value = 0
            

##############
# TESTS CCTB #
##############

logger = sim_logger("uart TX")

#Generics for RTL design
DATA_BITS = int(os.environ.get("DATA_BITS", 8))
CLK_FREQ  = int(os.environ.get("CLK_FREQ",  115200))
BAUD_RATE = int(os.environ.get("BAUD_RATE", 115200))
CLK_PER_BIT = CLK_FREQ // BAUD_RATE


@cocotb.test()
async def unitary_test_uart_tx(dut):
    # Clock TX
    clk_tx = Clock(dut.clk_i, 1, unit="ns") 
    
    cocotb.start_soon(clk_tx.start())

    CLK_PER_BIT = int(115200/115200) 

    # Reset
    await RisingEdge(dut.clk_i)
    await ReadWrite(dut.clk_i)
    dut.rst_i.value = 1
    dut.data_i.value = 0

    await RisingEdge(dut.clk_i)
    await ReadWrite(dut.clk_i)
    dut.rst_i.value = 0

    await send_frame_test(dut, 0xFA, CLK_PER_BIT, len_data = 8, verbose = True)







