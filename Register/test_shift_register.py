import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

@cocotb.test()
async def test_shift(dut):
    
    cocotb.start_soon(dut.clk_i.start())

    # Reset
    dut.rst_i.value = 1
    dut.d_i.value = 0
    await RisingEdge(dut.clk_i)
    dut.rst_i.value = 0

    # Envoyer un '1' pendant 1 cycle
    dut.d_i.value = 0
    await RisingEdge(dut.clk_i)
    dut.d_i.value = 2**8-1
    await RisingEdge(dut.clk_i)
    dut.d_i.value = 0

    for i in range(3):
        await RisingEdge(dut.clk_i)
        print(f"Cycle {i+1} : q_o = {dut.q_o.value}")