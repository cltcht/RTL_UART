# wave.tcl
gtkwave::addSignalsFromList [list clk_i]
gtkwave::addSignalsFromList [list rst_i]
gtkwave::/Edit/Color_Format/Indigo
gtkwave::addSignalsFromList [list data_i]
gtkwave::addSignalsFromList [list tx_o]
gtkwave::addSignalsFromList [list tx_order_i]
gtkwave::addSignalsFromList [list tx_busy_o]
gtkwave::addSignalsFromList [list frame_sent]
gtkwave::addSignalsFromList [list b_saved]
gtkwave::addSignalsFromList [list clk_count]
gtkwave::addSignalsFromList [list bit_count]


gtkwave::/Time/Zoom/Zoom_Full