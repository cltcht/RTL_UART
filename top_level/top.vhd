library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
--use ../uart_rx/uart_rx.vhd;



entity top is
    generic (
        DATA_BITS : integer := 12;
        CLK_UART_RX_FREQ : integer := 50_000_000;
        CLK_UART_TX_FREQ : integer := 115200 --BAUD_RATE
    );
    port (
        clk_uart_tx_i    : in  std_logic;                                  -- clock                                                     
        clk_uart_rx_i    : in  std_logic;                                  -- clock                             
        rst_i            : in  std_logic;                                  -- reset signal                                 
        uart_rx_i        : in  std_logic;                                  -- uart rx frame                                                                  
        data_o           : out std_logic_vector((DATA_BITS-1) downto 0);   -- data decoded by uart rx component                                 
        random_data_i    : in  std_logic_vector((DATA_BITS-1) downto 0);   -- data to be encoded by uart tx component                                                 
        tx_order_i       : in  std_logic;                                  -- tx order                                  
        uart_tx_o        : out std_logic;                                  -- uart tx frame                                 
        flag_rx_o        : out std_logic;                                  -- flag : uart rx component received frame                                 
        tx_busy_o        : out std_logic                                   -- flag : uart tx component is busy sending frame                                 

        
    );
end entity top;

architecture rtl_top of top is

--- Signals ---
signal clk_uart_tx_s     : std_logic;                                  -- (signal) clock  
signal clk_uart_rx_s     : std_logic;                                  -- (signal) clock                                         
signal rst_s             : std_logic;                                  -- (signal) reset signal                               
signal uart_rx_frame_s   : std_logic;                                  -- (signal) uart rx frame                               
signal data_s            : std_logic_vector((DATA_BITS-1) downto 0);   -- (signal) data decoded by uart rx component            
signal flag_rx_s         : std_logic;                                  -- (signal) flag : uart rx component received frame               
signal random_data_s     : std_logic_vector((DATA_BITS-1) downto 0);   -- (signal) data to be encoded by uart tx component                                             
signal tx_order_s        : std_logic;                                  -- (signal) tx order                                       
signal tx_busy_s         : std_logic;                                  -- (signal) flag : uart tx component is busy sending frame                   
signal uart_tx_frame_s   : std_logic       ;                           -- (signal) uart tx frame              


--- UART Rx ---
    component uart_rx is
    generic (
        DATA_BITS    : integer;
        CLK_FREQ     : integer;  
        BAUD_RATE    : integer
    );
    port (
        clk_i        : in  std_logic;
        rst_i        : in  std_logic;
        rx_i         : in  std_logic;
        data_o       : out std_logic_vector((DATA_BITS-1) downto 0);
        flag_rx_o    : out std_logic
    );
    end component;

--- UART Tx ---
    component uart_tx is
    generic (
        DATA_BITS    : integer;
        CLK_FREQ     : integer   
    );
    port (
        clk_i      : in  std_logic;
        rst_i      : in  std_logic;
        data_i     : in std_logic_vector((DATA_BITS-1) downto 0);
        tx_o       : out  std_logic;
        tx_order_i : in std_logic;
        tx_busy_o  : out std_logic
    );
    end component;



begin

--- Signals mapping ---
clk_uart_tx_s    <= clk_uart_tx_i   ;
clk_uart_rx_s    <= clk_uart_rx_i   ;
rst_s            <= rst_i           ;
uart_rx_frame_s  <= uart_rx_i       ;
data_o           <= data_s          ;
flag_rx_o        <= flag_rx_s       ;
random_data_s    <= random_data_i   ;
tx_order_s       <= tx_order_i      ;
tx_busy_o        <= tx_busy_s       ;
uart_tx_o        <= uart_tx_frame_s ;


--- Components instantiation ---

i_uart_rx : uart_rx
  generic map (
      DATA_BITS    => DATA_BITS,
      CLK_FREQ     => CLK_UART_RX_FREQ,
      BAUD_RATE    => CLK_UART_TX_FREQ
  )
    port map(
        clk_i => clk_uart_rx_s,      
        rst_i => rst_s,  
        rx_i => uart_rx_frame_s,   
        data_o => data_s, 
        flag_rx_o => flag_rx_s 
    );

i_uart_tx : uart_tx
    generic map (
        DATA_BITS    => DATA_BITS,
        CLK_FREQ     => CLK_UART_TX_FREQ
    )
    port map (
        clk_i     =>  clk_uart_tx_s,
        rst_i     =>  rst_s,
        data_i     => random_data_s,
        tx_o       => uart_tx_frame_s,
        tx_order_i => tx_order_s,
        tx_busy_o  => tx_busy_s 
    );



end architecture rtl_top;