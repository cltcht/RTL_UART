SIM          = ghdl
TOPLEVEL_LANG = vhdl
VHDL_SOURCES  = $(PWD)/uart_rx.vhd
TOPLEVEL      = uart_rx
COCOTB_TEST_MODULES        = test_uart_rx

export PYTHONPATH := $(PWD)/../common:$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim