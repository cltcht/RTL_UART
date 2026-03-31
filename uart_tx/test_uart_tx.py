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

async def reset_delay(signal, delay):
    await Timer(delay, unit="ns")
    await ReadWrite()
    signal.value = 0

async def tx_order_signal(dut, up_time:float):
    """Step function for tx_order

    Args:
        dut (cocotb dut): Cocotb device under test
        delay (int): Delay to ait before signal beign set down
    """
    await RisingEdge(dut.clk_i)
    await ReadWrite()
    dut.tx_order_i.value = 1

    cocotb.start_soon(reset_delay(dut.tx_order_i, up_time))

async def send_frame_test(dut, DATA_hex, CLK_PER_BIT, len_data, verbose = False):
    """Send uart frame to DUT

    Args:
        dut (cocotb dut): Cocotb device under test
        DATA_hex (int): Hexadecimal data to be sent
        CLK_PER_BIT (int): Number of clk hit per sent bit  = Clk frequency//baud rate
        len_data (int): Number of hexadecimal figures in DATA_hex
        verbose (bool, optional): Print info in log. Defaults to False.
    """

    # Test : Data lenght is matching RTL settings
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
        logger.print_info(f"\n Start of 'send_frame_test'")
        logger.print_info(f"input data DATA_hex is {hex(DATA_hex)}", ",")
        logger.print_info(f"expected frame is {TRAME_UART}")
    

    # First Time step
    await RisingEdge(dut.clk_i)
    await ReadWrite(dut.clk_i)  # First Evaluation cycle
    dut.data_i.value = DATA_hex
    if verbose :
        logger.print_info(f"set dut.data_i.value <= {hex(DATA_hex)}\n")

    # for second Evaluation cycle : order Tx
    await tx_order_signal(dut, up_time=20)
    if verbose :
        logger.print_info(f"set dut.tx_order_i.value <= {True}\n")
    
    for i, bit in enumerate(TRAME_UART):
        
        # Delay waiting CLK_PER_BIT -> bit is being sent
        for _ in range (CLK_PER_BIT) :
            await RisingEdge(dut.clk_i)

        # Time step for each bit
        await ReadOnly()

        # Test : bit sent at i-th cycle is equal to frame[1]
        if i > 0 :
            assert bin(dut.tx_o.value) == bin(TRAME_UART[i]), (f"Test failed with dut.tx_o.value == TRAME_UART[i] and i = {i}")
            assert bin(dut.tx_o.value) == START if i == 0 else True
            if verbose :
                logger.print_info(f"Bit {i-1}"+" "*(10>i-1)+ f" sent by Tx = {dut.tx_o.value}", end="\n")

        if verbose :
            if i == len(TRAME_UART)-1 :
                logger.print_info(f"Bit {i}"+" "*(10>i)+ f" set as Tx input = {bit}(STOP)  ; Busy flag = {str(dut.tx_busy_o.value)}", end=", ")
            elif i == 0 :
                logger.print_info(f"Bit {i}"+" "*(10>i)+ f" set as Tx input = {bit}(START) ; Busy flag = {str(dut.tx_busy_o.value)}", end=", ")
            else :
                logger.print_info(f"Bit {i}"+" "*(10>i)+ f" set as Tx input = {bit}        ; Busy flag = {str(dut.tx_busy_o.value)}", end=", ")

        # Test : busy flag is up
        assert bin(dut.tx_busy_o.value) == bin(1), (f"Test failed with dut.tx_busy_o.value == 1")

    # Time step to check busy signal and last bit values
    for _ in range (CLK_PER_BIT) :
        await RisingEdge(dut.clk_i)

    await ReadOnly() 
    # Test : last bit is STOP
    assert bin(dut.tx_o.value) == bin(STOP)
    # Test : busy flag is still up
    assert bin(dut.tx_busy_o.value) == bin(1), (f"Test failed with dut.tx_busy_o.value == 1")
    if verbose :
        logger.print_info(f"Bit {i-1}"+" "*(10>i-1)+ f" sent by Tx = {dut.tx_o.value}", end="\n")
        logger.print_info(f"Busy flag = {str(dut.tx_busy_o.value)}")

    # Time step to set down tx order
    await RisingEdge(dut.clk_i)
    await ReadWrite(dut.clk_i) 
    dut.tx_order_i.value = 0
    if verbose :
        logger.print_info(f"set dut.tx_order_i.value <= {False}\n")
    await RisingEdge(dut.clk_i)
    await ReadOnly()
    # Test : busy flag is down after tx_order reset
    assert bin(dut.tx_busy_o.value) == bin(0), (f"Test failed with dut.tx_busy_o.value == 0")
             

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
    dut.data_i.value = 0x00
    dut.tx_order_i.value = 0
    logger.print_info(f"Reset set up\n")

    await RisingEdge(dut.clk_i)
    await ReadWrite(dut.clk_i)
    dut.rst_i.value = 0
    logger.print_info(f"Reset set down\n")

    await send_frame_test(dut, 0x00, CLK_PER_BIT, len_data = 8, verbose = True)

    await Timer(40, unit="ns")







