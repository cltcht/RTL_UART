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
    await Timer(delay, unit="ms")
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


             
async def test_sanity_check(dut, len_data:int, START:bool, STOP: bool, verbose:bool):
    """Test : Data lenght is matching RTL settings
       Test : Start value is correct
       Test : Stop value is correct

    Args:
        dut (cocotb dut): Cocotb device under test
        len_data (int): Number of hexadecimal figures in DATA_hex
        ***TO BE WRITTER / START STOP / ***
        verbose (bool): Print info in log
    """

    if verbose :
        error_logger = sim_logger("test_sanity_check")

    try :
        assert dut.DATA_BITS.value == len_data
        if verbose : error_logger.print_info("Test : DATA_BITS is valid")
    except :
        if verbose : error_logger.print_critical_error(f"Length of data len_data in cocotb test = {len_data} bits, differs from RTL data length : dut.DATA_BITS = {int(dut.DATA_BITS.value)} ")
        raise ValueError
    
    #0-th cycle : Tx starts
    await RisingEdge(dut.tx_busy_o)
    #1-th cycle : Sending START bit
    await Timer(round(PERIOD), unit = "ms") 
    await ReadOnly()
    try :
        assert dut.tx_o.value == START
        if verbose : error_logger.print_info("Test : START value is valid")
    except :
        if verbose : error_logger.print_critical_error(f"1st bit of UART frame differs from cocotb specified START value")
        raise ValueError
  

    #Await len_data+1 cycles -> DATA+STOP
    for k in range (len_data+1):
        await RisingEdge(dut.clk_i)
    await ReadOnly()
    #10th cycle : Sending STOP bit
    try :
        assert dut.tx_o.value == STOP
        if verbose : error_logger.print_info("Test : STOP value is valid")
    except :
        if verbose :
            error_logger.print_critical_error(f"Last bit of UART frame differs from cocotb specified STOP value")
        raise ValueError

async def test_data_validity(dut, len_data:int, UART_FRAME:list, verbose:bool):
    """Test : Data integrity

    Args:
        dut (cocotb dut): Cocotb device under test
        len_data (int): Number of hexadecimal figures in DATA_hex
        UART_FRAME(list): Uart frame to be sent
        verbose (bool, optional): Print info in log
    """

    if verbose :
        error_logger = sim_logger("test_data_validity")

    #0-th cycle : Tx starts
    await RisingEdge(dut.tx_busy_o)
    if verbose : error_logger.print_info(f"Theoratical Frame is {UART_FRAME}")

    #1-th cycle : Sending START bit
    await Timer(round(PERIOD), unit = "ms") 
    #For len_data cycles : check bit validity 
    for k in range (len_data):
        await RisingEdge(dut.clk_i)
        await ReadOnly()
        try :
            assert dut.tx_o.value == UART_FRAME[k]
            if verbose : error_logger.print_info(f"Test : data bit {k+1} is valid : {dut.tx_o.value}")
        except :
            if verbose : error_logger.print_critical_error(f"Last bit of UART frame differs from cocotb specified STOP value")
            raise ValueError


##############
# TESTS CCTB #
##############

logger = sim_logger("uart TX")

#Generics for RTL design
CLK_FREQ = 115200
BAUD_RATE = CLK_FREQ
CLK_PER_BIT = CLK_FREQ // BAUD_RATE
PERIOD = 8.6 #ms



@cocotb.test()
async def two_frames_random_data(dut):
    #UART FRAME head, tail and data
    START = 0
    STOP = 1
    len_data = 8
    DATA_1st_frame = np.random.randint(low=0, high=2**(len_data))
    DATA_2nd_frame = np.random.randint(low=0, high=2**(len_data))
    

    # Clock TX
    clk_tx = Clock(dut.clk_i, PERIOD, unit="ms") 
    
    cocotb.start_soon(clk_tx.start())

    # Reset
    await RisingEdge(dut.clk_i)
    await ReadWrite(dut.clk_i)
    dut.rst_i.value = 1
    dut.data_i.value = 0x0
    dut.tx_order_i.value = 0
    logger.print_info(f"Reset set up\n")

    logger.print_info(f"dut.DATA_BITS.value = {int(dut.DATA_BITS.value)}")
    logger.print_info(f"PERIOD = {PERIOD} ms")

   
    #1st frame
    await RisingEdge(dut.clk_i)
    await ReadWrite(dut.clk_i)
    dut.rst_i.value = 0
    logger.print_info(f"Reset set down\n")
    dut.data_i.value = DATA_1st_frame

    cocotb.start_soon(test_sanity_check(dut, len_data, START, STOP, True))
    cocotb.start_soon(test_data_validity(dut, len_data, build_frame_UART(DATA_1st_frame, START, STOP, len_data), True))

    cocotb.start_soon(tx_order_signal(dut, up_time=round(PERIOD)))

    # await RisingEdge(dut.clk_i)
    # await Timer(2, "ns") #Waiting for tx order to be received by system
    # await ReadWrite(dut.clk_i)

    #2nd frame
    await Timer(round(20*PERIOD), unit="ms")
    await RisingEdge(dut.clk_i)
    await Timer(round(2*PERIOD), "ms") #Waiting for tx order to be received by system
    await ReadWrite(dut.clk_i)
    dut.data_i.value = DATA_2nd_frame

    cocotb.start_soon(test_data_validity(dut, len_data, build_frame_UART(DATA_2nd_frame, START, STOP, len_data), True))

    cocotb.start_soon(tx_order_signal(dut, up_time=round(PERIOD)))

    await Timer(round(20*PERIOD), unit="ms")



#@cocotb.test()
async def hundred_frames_random_data(dut):
    #UART FRAME head, tail and data
    START = 0
    STOP = 1
    len_data = 8
    DATA_frames = [np.random.randint(low=0, high=2**(len_data)) for n in range(100)]
    
    # Clock TX
    clk_tx = Clock(dut.clk_i, PERIOD, unit="ms") 
    
    cocotb.start_soon(clk_tx.start())

    # Reset
    await RisingEdge(dut.clk_i)
    await ReadWrite(dut.clk_i)
    dut.rst_i.value = 1
    dut.data_i.value = 0x0
    dut.tx_order_i.value = 0
    logger.print_info(f"Reset set up\n")

    logger.print_info(f"dut.DATA_BITS.value = {int(dut.DATA_BITS.value)}")

    for n in range(100):
        #1st frame
        await RisingEdge(dut.clk_i)
        await ReadWrite(dut.clk_i)
        dut.rst_i.value = 0
        logger.print_info(f"Reset set down\n")
        dut.data_i.value = DATA_frames[n]

        cocotb.start_soon(test_sanity_check(dut, len_data, START, STOP, False))
        cocotb.start_soon(test_data_validity(dut, len_data, build_frame_UART(DATA_frames[n], START, STOP, len_data), False))

        cocotb.start_soon(tx_order_signal(dut, up_time=round(PERIOD)))


        #2nd frame
        await Timer(round(20*PERIOD), unit="ms")
        await RisingEdge(dut.clk_i)
        await Timer(round(2*PERIOD), "ms") #Waiting for tx order to be received by system
        await ReadWrite(dut.clk_i)



