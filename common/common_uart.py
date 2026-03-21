import cocotb
from cocotb.clock import Clock, Timer
from cocotb.triggers import RisingEdge
import numpy as np
from asyncio import CancelledError
import logging


def build_frame_UART(DATA_hex:float, START: bool, STOP: bool, len_data:int)->list:
    """Build a UART binary frame from given hexadecimal data

    Args:
        DATA_hex (float): Hexadecimal to be translated
        START (bool): Usually 0
        STOP (bool): Usually 1
        len_data (int): Number of hexadecimal figures in DATA_hex

    Returns:
        (list of bool): Binary uart frame START DATA[0:N] STOP
    """

    #Conversion binaire + zero padding 
    DATA_bin = bin(DATA_hex)[2:].zfill(len_data)

    ## Reverse data for LSB first
    DATA_lsb_first = [int(DATA_bin[len(DATA_bin)-1-i]) for i in range (len(DATA_bin))]

    TRAME_UART = [START] + DATA_lsb_first + [STOP]
    return TRAME_UART