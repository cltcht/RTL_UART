SIM          = ghdl
TOPLEVEL_LANG = vhdl
VHDL_SOURCES  = $(PWD)/uart_tx.vhd 
TOPLEVEL      = uart_tx
SIM_ARGS = --vcd=simulation_$(COCOTB_TEST_MODULES).vcd


# Keep it to use home-made libraries
export PYTHONPATH := $(shell pwd)/../:$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim