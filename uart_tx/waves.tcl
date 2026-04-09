# C. Chollet
# wave.tcl
# inspired from https://gist.github.com/carlosedp/97188d9b0749c9faf99f8a79df5a3db6 repo


gtkwave::/Edit/Insert_Comment "Simulation UART"
gtkwave::/Edit/Insert_Comment "1st frame plot"
gtkwave::/Edit/Insert_Blank

set top [list clk_i rst_i ]
gtkwave::/Edit/Insert_Comment "Clock & Reset"
gtkwave::addSignalsFromList $top
gtkwave::highlightSignalsFromList $top
gtkwave::/Edit/Color_Format/Orange
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

set internal_signals [list clk_count bit_count frame_sent b_saved ]
gtkwave::/Edit/Insert_Comment "Internal Signals"
gtkwave::addSignalsFromList $internal_signals
gtkwave::highlightSignalsFromList $internal_signals
gtkwave::/Edit/Color_Format/Indigo
gtkwave::/Edit/UnHighlight_All
gtkwave::/Edit/Insert_Blank

#1st Frame
gtkwave::highlightSignalsFromList [list uart_tx.tx_busy_o]
gtkwave::/Markers/Find_Next_Edge
set time_value_start [ gtkwave::findNextEdge ]
puts "time_value_start: $time_value_start"
gtkwave::setNamedMarker A $time_value_start "Tx Starts"

gtkwave::/Markers/Find_Next_Edge
gtkwave::/Markers/Find_Previous_Edge
set time_value_1st_tx_end [ gtkwave::findNextEdge ]
puts "time_value_1st_tx_end: $time_value_1st_tx_end"
gtkwave::setNamedMarker B $time_value_1st_tx_end "Tx Ends"
gtkwave::/Edit/UnHighlight_All

gtkwave::highlightSignalsFromList [list uart_tx.tx_order_i]
gtkwave::/Markers/Find_Next_Edge
gtkwave::/Markers/Find_Previous_Edge
set time_value_2nd_tx_start [ gtkwave::findNextEdge ]
puts "time_value_2nd_tx_start: $time_value_2nd_tx_start"
gtkwave::/Edit/UnHighlight_All


gtkwave::setZoomRangeTimes 0 $time_value_2nd_tx_start



# Sauvegarder en PNG
gtkwave::/File/Grab_To_File uart_tx/sim_build/uart_tx_wave.png
#gtkwave::/File/Quit


