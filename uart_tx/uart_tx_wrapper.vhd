library ieee;
  use ieee.std_logic_1164.all;
  use ieee.numeric_std.all;

entity uart_tx_wrapper is
        generic (
        DATA_BITS    : integer := 8;
        CLK_FREQ     : integer := 115200;  -- frequency of FPGA
        BAUD_RATE    : integer := 115200 
        );
    port (
        clk_i      : in  std_logic;
        rst_i      : in  std_logic;
        data_i     : in std_logic_vector((DATA_BITS-1) downto 0);
        tx_o       : out  std_logic;
        tx_order_i : in std_logic;
        tx_busy_o  : out std_logic
    );
end uart_tx_wrapper;

architecture struct of uart_tx_wrapper is
    component uart_tx
        generic (
        DATA_BITS    : integer := 8;
        CLK_FREQ     : integer := 115200;  -- frequency of FPGA
        BAUD_RATE    : integer := 115200 
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
    uut: uart_tx
        generic map (
            DATA_BITS    => 8,          
            CLK_FREQ     => 115200,  
            BAUD_RATE    => 115200        
        )
        port map (
            clk_i      => clk_i,
            rst_i    => rst_i,
            data_i       => data_i,
            tx_o  => tx_o,
            tx_order_i => tx_order_i,
            tx_busy_o => tx_busy_o
        );
end struct;