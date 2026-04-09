SIM          = ghdl
TOPLEVEL_LANG = vhdl
VHDL_SOURCES  = $(PWD)/uart_tx.vhd 
TOPLEVEL      = uart_tx
COCOTB_TEST_MODULES        = test_uart_tx
SIM_ARGS = --vcd=simulation.vcd


# Keep it to use home-made libraries
export PYTHONPATH := $(shell pwd)/../:$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim