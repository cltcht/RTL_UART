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

async def reset_delay(signal, delay:int):
    """Sets down signal after waiting for "delay" ns.

    Args:
        signal (cocotb dut signal): dut.signal
        delay (int): Delay to await for before setting down [ns]
    """
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

async def random_tx_order_signal(dut, interval, verbose):
    """Random step function for tx_order random during interval [ns]

    Args:
        dut (cocotb dut): Cocotb device under test
        delay (int): Delay to ait before signal beign set down
    """
    log = sim_logger("random_tx_order_signal")
    start_time = np.random.randint(low=0, high=interval)
    down_time = np.random.randint(low=start_time, high=interval)
    if verbose :
        log.print_info(f"Tx_order up time : {down_time-start_time}")
    await Timer(start_time, "ns")
    await ReadWrite()
    dut.tx_order_i.value = 1

    cocotb.start_soon(reset_delay(dut.tx_order_i, down_time-start_time))

async def test_tx_while_reset(dut, verbose):
    error_logger = sim_logger("test_tx_while_reset")
    while (True) :
        await RisingEdge(dut.clk_i)
        await ReadOnly()
        if dut.rst_i.value == 1 and dut.tx_busy_o.value == 1 :
            if verbose : error_logger.print_critical_error("Tx started while reset signal is up")
            await Timer(round(10*PERIOD), "ns")
            raise ValueError

async def test_tx_order_while_busy(dut, FRAME, verbose):
    error_logger = sim_logger("test_tx_while_reset")
    if verbose : error_logger.print_info(f"Expected frame : {FRAME}")
    while (True) :
        await RisingEdge(dut.clk_i)
        await ReadOnly()
        if dut.tx_order_i == 1 and dut.tx_busy_o.value == 1 and dut.frame_sent.value == 0:
            if verbose : error_logger.print_info("Tx order while UART is busy")
        #Checks that bit values are not modified
            try :
                assert dut.tx_o.value == FRAME[dut.bit_count.value]
                if verbose : error_logger.print_info(f"Test : data bit {dut.bit_count.value} is valid : {dut.tx_o.value}")
            except :
                if verbose : error_logger.print_critical_error(f"Tx order perturbed UART")
                raise ValueError

        #Checks that bit count isnt modified



##############
# TESTS CCTB #
##############

logger = sim_logger("uart TX")

#Generics for RTL design
CLK_FREQ = 115200
PERIOD = int(1E9/CLK_FREQ) #ns
logger.print_info(f"PERIOD = {PERIOD}")

@cocotb.test()
async def late_reset(dut):
    """Sends tx order signal before reset. Tx shouldn't happen while reset is up.

    Args:
        dut (cocotb dut): Device under test
    """
    #UART FRAME head, tail and data
    START = 0
    STOP = 1
    len_data = 12
    N_Frames = 10
    DATA_frames = [np.random.randint(low=0, high=2**(len_data)) for n in range(N_Frames)]
    verbose = True

    if verbose : logger.print_info(f"PERIOD = {PERIOD} ns")
    
    # Clock TX
    clk_tx = Clock(dut.clk_i, PERIOD, unit="ns") 
    
    cocotb.start_soon(clk_tx.start())
   
    for n in range(N_Frames):
        # New cycle
        await RisingEdge(dut.clk_i)
        await ReadWrite(dut.clk_i)
        dut.rst_i.value = 1
        dut.data_i.value = 0x0
        dut.tx_order_i.value = 0
            

        #Sets Down reset signal randomly after smthg between 10 or 20 clk cycles
        cocotb.start_soon(reset_delay(dut.rst_i, np.random.randint(low=round(10*PERIOD), 
                                                                   high=round(20*PERIOD))))

        #Starts Tx randomly between 0 and 10 clk cycles
        await Timer(np.random.randint(low=0, high=round(5*PERIOD)), "ns") 
        await RisingEdge(dut.clk_i)
        await ReadWrite()
        dut.data_i.value = DATA_frames[n]

        cocotb.start_soon(test_tx_while_reset(dut, verbose))
        cocotb.start_soon(tx_order_signal(dut, up_time=round(PERIOD)))

        #Await 40 period before next frame
        await Timer(round(40*PERIOD), unit="ns")
        await RisingEdge(dut.clk_i)
        await ReadWrite()
        dut.rst_i.value = 0

@cocotb.test()
async def tx_busy(dut):
    """Sends tx order signal while uart is busy. Tx shouldn't happen while device is busy.

    Args:
        dut (cocotb dut): Device under test
    """
    #UART FRAME head, tail and data
    START = 0
    STOP = 1
    len_data = 12
    N_Frames = 4
    DATA_frames = [np.random.randint(low=0, high=2**(len_data)) for n in range(N_Frames)]
    verbose = False
    
    # Clock TX
    clk_tx = Clock(dut.clk_i, PERIOD, unit="ns") 
    cocotb.start_soon(clk_tx.start())

    # Reset
    await RisingEdge(dut.clk_i)
    await ReadWrite(dut.clk_i)
    dut.rst_i.value = 1
    dut.data_i.value = 0x0
    dut.tx_order_i.value = 0
    await RisingEdge(dut.clk_i)
    await ReadWrite()
    dut.rst_i.value = 0
    if verbose : logger.print_info(f"Reset set down\n")
    await RisingEdge(dut.clk_i)
    await ReadWrite()
    dut.data_i.value = DATA_frames[0]

    cocotb.start_soon(test_tx_order_while_busy(dut, build_frame_UART(DATA_frames[0], START, STOP, len_data), verbose))

    #Sending regular tx order
    await RisingEdge(dut.clk_i)
    await ReadWrite()
    cocotb.start_soon(tx_order_signal(dut, up_time=round(PERIOD)))

    #Sending perturbative order signal while sending data
    for k in range (3):
        await Timer(2*round(PERIOD), "ns")
        await ReadWrite()
        dut.data_i.value = DATA_frames[k+1]
        cocotb.start_soon(random_tx_order_signal(dut, round(PERIOD), verbose))

    #Await 40 period before next frame
    await Timer(round(40*PERIOD), unit="ns")
    await RisingEdge(dut.clk_i)
    await ReadWrite()
    dut.rst_i.value = 0
