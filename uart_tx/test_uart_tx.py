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



#############
# FUNCTIONS #
#############
async def send_frame(dut, DATA_hex, CLK_PER_BIT, len_data, verbose = False):
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
        critical_error_logger = sim_logger("send_frame")
        critical_error_logger.print_critical_error(f"Length of data len_data = {len_data} bits, is different from RTL design data length : dut.DATA_BITS = {int(dut.DATA_BITS.value)} ")
        raise ValueError
    
    START = 0
    STOP = 1
    TRAME_UART = build_frame_UART(DATA_hex, START, STOP, len_data)
    if verbose :
        logger.print_info(f" DATA_hex : {hex(DATA_hex)}")
        logger.print_info(f" TRAME UART : {TRAME_UART}") 

    # First Time step
    await RisingEdge(dut.clk_i)
    await ReadWrite(dut.clk_i)  # First Evaluation cycle
    dut.tx_order_i.value = 1
     
    if verbose :
        await ReadWrite(dut.clk_i)
        logger.print_info(f" dut.tx_order_i.value : {dut.tx_order_i.value}\n")


    for i, bit in enumerate(TRAME_UART):
        
        ## Tempo pour l'envoi d'un bit tous les CLK_PER_BIT
        for _ in range (CLK_PER_BIT) :
            await RisingEdge(dut.clk_i)
            
        await ReadWrite(dut.clk_i)  
        dut.tx_o.value = bit 

        if verbose :
            if i == len(TRAME_UART)-1 :
                logger.print_info(f"Bit {i}"+" "*(10>i)+ " envoyé = STOP", 
                )
            elif i == 0 :
                logger.print_info(f"Bit {i}"+" "*(10>i)+ " envoyé = START", end="\n")
            else :
                logger.print_info(f"Bit {i}"+" "*(10>i)+ f" envoyé = {bit}", end="\n")
            
            logger.print_info(f" Busy flag = {str(dut.tx_busy_o.value)}")
        assert bin(dut.tx_busy_o.value) == bin(1), (f"Test failed with dut.tx_busy_o.value != 0 and DATA_hex = {DATA_hex}")

    
    await RisingEdge(dut.clk_i)
    await ReadWrite(dut.clk_i) 
    dut.tx_order_i.value = 0
            
    
    for _ in range (CLK_PER_BIT) :
        await RisingEdge(dut.clk_i)
        if verbose : 
            await ReadWrite(dut.clk_i) 
            logger.print_info(f" Busy flag = {str(dut.tx_busy_o.value)}")

    assert bin(dut.tx_busy_o.value) == bin(0), (f"Test failed with dut.tx_busy_o.value != 0 and DATA_hex = {DATA_hex}")



##############
# TESTS CCTB #
##############

logger = sim_logger("uart TX")


@cocotb.test()
async def test_uart(dut):
    # Clock TX
    clk_tx = Clock(dut.clk_i, 1, unit="ns") 
    
    cocotb.start_soon(clk_tx.start())

    CLK_PER_BIT = int(115200/115200) 

    # Reset
    await RisingEdge(dut.clk_i)
    await ReadWrite(dut.clk_i)
    dut.rst_i.value = 1
    dut.tx_o.value = 0

    await RisingEdge(dut.clk_i)
    await ReadWrite(dut.clk_i)
    dut.rst_i.value = 0

    # await send_frame(dut, 0xFF, CLK_PER_BIT, len_data = 8, verbose = False)
    await send_frame(dut, 0xFFA, CLK_PER_BIT, len_data = 12, verbose = True)






