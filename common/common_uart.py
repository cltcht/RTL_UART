import cocotb
from cocotb.clock import Clock, Timer
from cocotb.triggers import RisingEdge
import numpy as np
from asyncio import CancelledError
from common.clock_and_logger import *
from common.common_uart import *


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

    # Binary + zero padding 
    # bin(DATA_hex) = "Obxxxxxx" => bin(DATA_hex)[2:] = "xxxxxx"
    # if len_data > len(bin(DATA_hex[2:])) => padding
    # else does nothing special : len(bin(DATA_hex[2:])) > len_data
    # But we have a frame whose size is superior to target size
    DATA_bin = bin(DATA_hex)[2:].zfill(len_data)

    ## Goal : Make sure with user that it's a wanted property
    try :
        assert len_data == len(DATA_bin)
    except :
        critical_error_logger = sim_logger("build_frame_UART")
        critical_error_logger.print_critical_error(f"Lenght of data len_data = {len_data} bits, is different from computed data size of DATA_hex = {hex(DATA_hex)} length = {len(DATA_bin)} bits")
        raise ValueError

    ## Reverse data for LSB first
    DATA_lsb_first = [int(DATA_bin[len(DATA_bin)-1-i]) for i in range (len(DATA_bin))]

    TRAME_UART = [START] + DATA_lsb_first + [STOP]
    return TRAME_UART