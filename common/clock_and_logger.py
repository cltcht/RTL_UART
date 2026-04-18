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
import logging



class sim_logger:
    def __init__(self, logger_name:str):
        self.logger = logging.getLogger(logger_name)
        self.set_level()

    def set_level(self, level=logging.DEBUG):
        """Set logger level

        Args:
            level (logging level, optional): NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
        """
        self.logger.setLevel(level)
    
    def print_info(self, msg:str, end:str="\n"):
        """Prints DEBUG level message

        Args:
            msg (str): Message to print
            end (str): End of String character
        """
        self.set_level(logging.DEBUG)
        self.logger.info(msg+end)

    def print_critical_error(self, msg:str, end:str="\n"):
        """Prints CRITICAL level message

        Args:
            msg (str): Message to print
            end (str): End of String character
        """
        self.set_level(logging.CRITICAL)
        self.logger.critical(msg+end)



class clock_management :
    def __init__(self, clk:cocotb.handle.LogicObject, clk_period:float):
        """

        Args:
            clk (cocotb.handle.LogicObject): cocotb clock signal
            clk_period (float): clock period **[in ns]**
        """
        self.clk = clk
        self.time = 0 #temps en ns
        self.clk_period = clk_period*1.0


    async def clock_start_count(self):
        """Assynchronous function \n
           ABSOLUTELY NEED TO BE STARTED WITH cocotb.start_soon()
           ON THE SAME TIME AS clk
        """
        while True:
            await RisingEdge(self.clk)
            self.time += self.clk_period
    

    def get_time(self):
        return self.time
    
    async def wait_until(self, time:float):
        """Awaits until clock's reaches "time" until resuming

        Args:
            time (float): Clock time to be reached **[in ns]**
        """
        try :
            assert time%self.clk_period == 0
        except :
            critical_error_logger = sim_logger("wait_until")
            critical_error_logger.print_critical_error("clk_period isn't a multiple of time : unknown/unstable state")
            raise ValueError
        cycles = int(time/self.clk_period)
        for _ in range(int(cycles)):
            await RisingEdge(self.clk)
    
    async def reset_delay(signal, delay):
        await Timer(delay, unit="ns")
        await ReadWrite()
        signal.value = 0


