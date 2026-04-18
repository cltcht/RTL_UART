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
async def tx_order_signal(tx_order, clk, up_time:float):
    """Step function for tx_order

    Args:
        dut (cocotb dut): Cocotb device under test
        delay (int): Delay to wait before signal beign set down
    """
    await RisingEdge(clk)
    await ReadWrite()
    tx_order.value = 1

    cocotb.start_soon(clock_management.reset_delay(tx_order, up_time))

async def looping(clk, signal1, signal2, delay):
    """Emulates external signal propagation.
       Assigns signal2 value to signal1 every delay ns

    Args:
        signal1 (cocotb dut.signal): signal
        signal2 (cocotb dut.signal): signal
        delay (int): delay in [ns]
    """
    buffer = [] # Values + timestamps that are delayed for looping
    
    while(1):
        await RisingEdge(clk)
        await ReadWrite()
        value_to_delay = signal2.value
        buffer.append({"value": value_to_delay, "time": delay}) 

        new_buffer = buffer #save
        for i,dictio in enumerate(buffer):  #scan all values
            if dictio["time"] == 0 : #if one's time is 0 assign it ...
                signal1.value = dictio["value"]
                new_buffer = buffer[1:] #... and make a new buffer that's updated at the end of the loop
            else :
                buffer[i]["time"] -= 1
        buffer = new_buffer

        
async def test_uart_rx_output(dut, expected_value, verbose):
    error_logger = sim_logger("test_uart_rx_output")
 
    await RisingEdge(dut.flag_rx_o)
    try :
        assert dut.data_o.value == expected_value
        if verbose : error_logger.print_info(f"Uart Rx data is as expected : {hex(expected_value)}")
    except :
        if verbose : error_logger.print_critical_error(f"Uart Rx data isn't as expected")
        raise ValueError
    

#########
# TESTS #
#########

log = sim_logger("top_level")

@cocotb.test()
async def uart_top_looping_two_frames_trivial_data(dut):
    """ Sets 0x000 and 0xFFF as input of Tx component.  
Validates the coherence of the Rx component data output.

    Args:
        dut (cocotb dut): Device under test
    """

    #Clock signal
    PERIOD_RX = 1 #ns
    PERIOD_TX = 434*PERIOD_RX #ns
    clk_uart_tx = Clock(dut.clk_uart_tx_i, PERIOD_TX, unit="ns")
    clk_uart_rx = Clock(dut.clk_uart_rx_i, PERIOD_RX, unit="ns")
    clk_mgnt = clock_management(dut.clk_uart_tx_i, PERIOD_TX)
    
    cocotb.start_soon(clk_uart_tx.start())
    cocotb.start_soon(clk_uart_rx.start())
    cocotb.start_soon(clk_mgnt.clock_start_count())

    #Prepare external looping
    cocotb.start_soon(looping(dut.clk_uart_tx_i, dut.uart_rx_i, dut.uart_tx_o, 1))

    #Define Data
    START = 0
    STOP = 1
    len_data = 12
    DATA = np.random.randint(low=0, high=2**(len_data))


    # Reset
    await RisingEdge(dut.clk_uart_tx_i)
    await ReadWrite(dut.clk_uart_tx_i)
    dut.rst_i.value = 1
    dut.tx_order_i.value = 0
    dut.random_data_i.value = 0
    await RisingEdge(dut.clk_uart_tx_i)
    await RisingEdge(dut.clk_uart_tx_i)
    dut.rst_i.value = 0

    DATA_list = [0xFFF, 0x000]
    for k in range(len(DATA_list)):
        #Starts test
        cocotb.start_soon(test_uart_rx_output(dut, DATA_list[k], verbose=False))
        await RisingEdge(dut.clk_uart_tx_i)
        await ReadWrite()
        dut.random_data_i.value = DATA_list[k]

        #Send tx_order
        cocotb.start_soon(tx_order_signal(dut.tx_order_i, dut.clk_uart_tx_i, up_time=round(PERIOD_TX)))

        await clk_mgnt.wait_until(20*PERIOD_TX)


@cocotb.test()
async def uart_top_looping_ten_frames_random_data(dut):
    """Sets ten frames with random data as input of Tx component.  
    Validates the coherence of the Rx component data output.

    Args:
        dut (cocotb dut): Device under test
    """

    #Clock signal
    PERIOD_RX = 1 #ns
    PERIOD_TX = 434*PERIOD_RX #ns
    clk_uart_tx = Clock(dut.clk_uart_tx_i, PERIOD_TX, unit="ns")
    clk_uart_rx = Clock(dut.clk_uart_rx_i, PERIOD_RX, unit="ns")
    clk_mgnt = clock_management(dut.clk_uart_tx_i, PERIOD_TX)
    
    cocotb.start_soon(clk_uart_tx.start())
    cocotb.start_soon(clk_uart_rx.start())
    cocotb.start_soon(clk_mgnt.clock_start_count())

    #Prepare external looping
    cocotb.start_soon(looping(dut.clk_uart_tx_i, dut.uart_rx_i, dut.uart_tx_o, 1))

    #Define Data
    START = 0
    STOP = 1
    len_data = 12
    DATA_list = [np.random.randint(low=0, high=2**(len_data)) for k in range (10)]

    # Reset
    await RisingEdge(dut.clk_uart_tx_i)
    await ReadWrite(dut.clk_uart_tx_i)
    dut.rst_i.value = 1
    dut.tx_order_i.value = 0
    dut.random_data_i.value = 0
    await RisingEdge(dut.clk_uart_tx_i)
    await RisingEdge(dut.clk_uart_tx_i)
    dut.rst_i.value = 0
        
    #Starts test
    for k in range (len(DATA_list)):
        cocotb.start_soon(test_uart_rx_output(dut, DATA_list[k], verbose=False))

        await RisingEdge(dut.clk_uart_tx_i)
        await ReadWrite()
        dut.random_data_i.value = DATA_list[k]

        #Send tx_order
        cocotb.start_soon(tx_order_signal(dut.tx_order_i, dut.clk_uart_tx_i, up_time=round(PERIOD_TX)))

        await clk_mgnt.wait_until(20*PERIOD_TX)






    





