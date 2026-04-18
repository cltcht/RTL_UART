# C. Chollet
# wave.tcl
# inspired from https://gist.github.com/carlosedp/97188d9b0749c9faf99f8a79df5a3db6 repo


gtkwave::/Edit/Insert_Comment "Simulation UART"
gtkwave::/Edit/Insert_Comment "Top level"
gtkwave::/Edit/Insert_Blank

set top [list clk_i rst_i ]
gtkwave::/Edit/Insert_Comment "Clock & Reset"
gtkwave::addSignalsFromList $top
gtkwave::highlightSignalsFromList $top
gtkwave::/Edit/Color_Format/Red
gtkwave::/Edit/UnHighlight_All
gtkwave::/Edit/Insert_Blank


set input_signals [list random_data_i tx_order_i tx_busy_o uart_tx_o]
gtkwave::/Edit/Insert_Comment "Uart Tx Signals"
gtkwave::addSignalsFromList $input_signals
gtkwave::highlightSignalsFromList $input_signals
gtkwave::/Edit/Color_Format/Green
gtkwave::/Edit/UnHighlight_All
gtkwave::/Edit/Insert_Blank

set output_signals [list data_o uart_rx_i flag_rx_o]
gtkwave::/Edit/Insert_Comment "Uart Rx Signals"
gtkwave::addSignalsFromList $output_signals
gtkwave::highlightSignalsFromList $output_signals
gtkwave::/Edit/Color_Format/Green
gtkwave::/Edit/UnHighlight_All
gtkwave::/Edit/Insert_Blank

set internal_signals [list i_uart_tx.bit_count i_uart_tx.frame_sent i_uart_tx.b_saved ]
gtkwave::/Edit/Insert_Comment "Uart Tx Internal Signals"
gtkwave::addSignalsFromList $internal_signals
gtkwave::highlightSignalsFromList $internal_signals
gtkwave::/Edit/Color_Format/Orange
gtkwave::/Edit/UnHighlight_All
gtkwave::/Edit/Insert_Blank


set internal_signals [list i_uart_rx.data_bit_count i_uart_rx.state]
gtkwave::/Edit/Insert_Comment "Uart Rx Internal Signals"
gtkwave::addSignalsFromList $internal_signals
gtkwave::highlightSignalsFromList $internal_signals
gtkwave::/Edit/Color_Format/Orange
gtkwave::/Edit/UnHighlight_All
gtkwave::/Edit/Insert_Blank

#1st plot
gtkwave::setZoomRangeTimes 0 20000000
gtkwave::/File/Grab_To_File top_level/sim_build/uart_trivial_data_wave.png

#2nd plot
gtkwave::setZoomRangeTimes 20000000 40000000
gtkwave::/File/Grab_To_File top_level/sim_build/uart_random_data_wave.png

gtkwave::/File/Quit
