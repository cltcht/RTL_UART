# C. Chollet
# wave.tcl
# inspired from https://gist.github.com/carlosedp/97188d9b0749c9faf99f8a79df5a3db6 repo


gtkwave::/Edit/Insert_Comment "Simulation UART"
gtkwave::/Edit/Insert_Comment "Tx component"
gtkwave::/Edit/Insert_Blank

set top [list clk_i rst_i ]
gtkwave::/Edit/Insert_Comment "Clock & Reset"
gtkwave::addSignalsFromList $top
gtkwave::highlightSignalsFromList $top
gtkwave::/Edit/Color_Format/Red
gtkwave::/Edit/UnHighlight_All
gtkwave::/Edit/Insert_Blank


set input_signals [list data_i tx_order_i ]
gtkwave::/Edit/Insert_Comment "Input Signals"
gtkwave::addSignalsFromList $input_signals
gtkwave::highlightSignalsFromList $input_signals
gtkwave::/Edit/Color_Format/Green
gtkwave::/Edit/UnHighlight_All
gtkwave::/Edit/Insert_Blank

set output_signals [list tx_o tx_busy_o ]
gtkwave::/Edit/Insert_Comment "Output Signals"
gtkwave::addSignalsFromList $output_signals
gtkwave::highlightSignalsFromList $output_signals
gtkwave::/Edit/Color_Format/Green
gtkwave::/Edit/UnHighlight_All
gtkwave::/Edit/Insert_Blank

set internal_signals [list clk_count bit_count frame_sent b_saved b]
gtkwave::/Edit/Insert_Comment "Internal Signals"
gtkwave::addSignalsFromList $internal_signals
gtkwave::highlightSignalsFromList $internal_signals
gtkwave::/Edit/Color_Format/Orange
gtkwave::/Edit/UnHighlight_All
gtkwave::/Edit/Insert_Blank



# 1st plot : late reset
gtkwave::setZoomRangeTimes 0 200000000
gtkwave::/File/Grab_To_File uart_tx/sim_build/uart_tx_wave_sanity_late_reset.png

# 2nd plot : tx while busy
gtkwave::setZoomRangeTimes 3775800000 4000000000
gtkwave::/File/Grab_To_File uart_tx/sim_build/uart_tx_wave_sanity_tx_busy.png


gtkwave::/File/Quit


