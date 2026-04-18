# C. Chollet
# wave.tcl
# inspired from https://gist.github.com/carlosedp/97188d9b0749c9faf99f8a79df5a3db6 repo


gtkwave::/Edit/Insert_Comment "Simulation UART"
gtkwave::/Edit/Insert_Comment "Rx component"
gtkwave::/Edit/Insert_Blank

set top [list clk_i rst_i ]
gtkwave::/Edit/Insert_Comment "Clock & Reset"
gtkwave::addSignalsFromList $top
gtkwave::highlightSignalsFromList $top
gtkwave::/Edit/Color_Format/Red
gtkwave::/Edit/UnHighlight_All
gtkwave::/Edit/Insert_Blank


set input_signals [list rx_i ]
gtkwave::/Edit/Insert_Comment "Input Signals"
gtkwave::addSignalsFromList $input_signals
gtkwave::highlightSignalsFromList $input_signals
gtkwave::/Edit/Color_Format/Green
gtkwave::/Edit/UnHighlight_All
gtkwave::/Edit/Insert_Blank

set output_signals [list data_o flag_rx_o ]
gtkwave::/Edit/Insert_Comment "Output Signals"
gtkwave::addSignalsFromList $output_signals
gtkwave::highlightSignalsFromList $output_signals
gtkwave::/Edit/Color_Format/Green
gtkwave::/Edit/UnHighlight_All
gtkwave::/Edit/Insert_Blank

set internal_signals [list state data_bit_count]
gtkwave::/Edit/Insert_Comment "Internal Signals"
gtkwave::addSignalsFromList $internal_signals
gtkwave::highlightSignalsFromList $internal_signals
gtkwave::/Edit/Color_Format/Orange
gtkwave::/Edit/UnHighlight_All
gtkwave::/Edit/Insert_Blank

### 1st plot : trivial data ###
gtkwave::setZoomRangeTimes 0 15199500

gtkwave::/File/Grab_To_File uart_rx/sim_build/uart_rx_trivial_data_wave.png

### 2nd plot : random frames ####

gtkwave::setZoomRangeTimes 15199500 38000000
gtkwave::/File/Grab_To_File uart_rx/sim_build/uart_rx_random_data_wave.png


gtkwave::/File/Quit

