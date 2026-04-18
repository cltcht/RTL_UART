SIM          = ghdl
TOPLEVEL_LANG = vhdl
VHDL_SOURCES  = $(PWD)/top.vhd $(PWD)/../uart_tx/uart_tx.vhd $(PWD)/../uart_rx/uart_rx.vhd
TOPLEVEL      = top
COCOTB_TEST_MODULES        = "test_top"
SIM_ARGS = --vcd=simulation.vcd


# Keep it to use home-made libraries
export PYTHONPATH := $(shell pwd)/../:$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim