import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
import numpy as np



def build_frame_UART(DATA_hex, START: bool, STOP: bool):

    #Conversion binaire + zero padding 
    DATA_bin = bin(DATA_hex)[2:].zfill(8)


    ## Reverse data for LSB first
    DATA_lsb_first = [int(DATA_bin[len(DATA_bin)-1-i]) for i in range (len(DATA_bin)+1)]

    TRAME_UART = [START] + DATA_lsb_first + [STOP]
    return TRAME_UART

@cocotb.test()
async def test_uart(dut):
    # Clock TX, RX, ratio f_Tx/F_Rx = 1/434
    #Ici on ramène la période à 1ns -> Clock Tx = 434 ns
    clk_rx = Clock(dut.clk_i, 1, unit="ns") 
    
    cocotb.start_soon(clk_rx.start())


    # Reset
    dut.rst_i.value = 1
    dut.rx_i.value = 0
    await RisingEdge(dut.clk_i)
    dut.rst_i.value = 0

    START = 0
    STOP = 1
    DATA_hex = 0xA2
    TRAME_UART = build_frame_UART(DATA_hex, START, STOP)
    print(f" DATA_hex : {hex(DATA_hex)}")
    print(f" TRAME UART : {TRAME_UART}")

    State_dict = {"0":"IDLE", "1":"START", "2":"DATA", "3":"STOP"}

    CLK_PER_BIT = int(50E6 / 115200) #434 coups d'horloge Rx pour un bit envoyé par Tx

    for i, bit in enumerate(TRAME_UART):
        ## Bit à envoyer
        if i == 0 :
            print(f"\nBit {i}"+" "*(10>i)+ " à envoyer = START", end=" ")
        elif i == len(TRAME_UART)-1 :
            print(f"\nBit {i}"+" "*(10>i)+ " à envoyer = STOP", end=" ")
        else :
            print(f"\nBit {i}"+" "*(10>i)+ f" à envoyer = {bit}", end=" ")

        print(f" State = {State_dict[str(int(dut.state.value))]}")

        ## Envoi d'un bit
        dut.rx_i.value = bit 
        
        ## Tempo pour l'envoi d'un bit tous les CLK_PER_BIT
        for _ in range (int(CLK_PER_BIT/2)) :
            await RisingEdge(dut.clk_i)

        ## Analyse de l'état après CLK_PER_BIT/2 pour le start
        if i == 0 :
            print(f"Bit {i}"+" "*(10>i)+ " reçu = START", end=" ")

        ## Analyse de l'état après CLK_PER_BIT
        for _ in range (int(CLK_PER_BIT/2)) :
            await RisingEdge(dut.clk_i)

        if i == len(TRAME_UART)-1 :
            print(f"Bit {i}"+" "*(10>i)+ " reçu = STOP", end=" ")
        else :
            print(f"Bit {i}"+" "*(10>i)+ f" reçu = {bit}", end=" ")

        print(f" State = {State_dict[str(int(dut.state.value))]}")


    for _ in range (CLK_PER_BIT) :
        await RisingEdge(dut.clk_i)
    print(f"\nFlag UART : ", dut.flag_rx_o.value)
    print(f"Vecteur UART : ", dut.data_o.value)


def hex_to_bin(hex_number):
    nb_octets = np.log(hex_number)//np.log(8)
    print(max(nb_octets, max(np.round(np.log(hex_number)/np.log(8)), 1.0)))

if __name__ == "__main__":

    hex_number = 0x00
    hex_to_bin(hex_number)