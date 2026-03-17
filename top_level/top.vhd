library ieee;
  use ieee.std_logic_1164.all;
  use ieee.numeric_std.all;
package ../uart_rx/uart_rx.vhd;



entity top is
    generic (
        DATA_BITS : integer := 12;
        CLK_UART_RX_FREQ : integer 50_000_000;
        BAUD_RX_RATE : integer 115200;
    );
    port (
        clk_i      : in  std_logic;
        rst_i      : in  std_logic;
        --UART_RX
        uart_rx_data_i : in std_logic_vector((DATA_BITS-1) downto 0);
        
        --UART_TX
        uart_tx_data_o : in std_logic_vector((DATA_BITS-1) downto 0)
        
    );
end entity top;

architecture rtl_top of top is

     -- latch pour enregistrer uart_rx_data_i 
    signal b : std_logic_vector((DATA_BITS-1) downto 0);
    signal b_saved : integer range 0 to 1; --booléen pour indiquer si les data ont étés sauvés

    -- Rapport CLKS_RX_PER_BIT / BAUD_RX_RATE = nombre de coups d'horloge Rx par bit reçu
    constant CLKS_RX_PER_BIT : integer := CLK_UART_RX_FREQ / BAUD_RX_RATE; -- 1 coup d'horloge / bit envoye

    component uart_rx is
    generic (
        DATA_BITS    : integer := 12;
        CLK_FREQ     : integer := 50_000_000;  -- fréquence horloge système
        BAUD_RATE    : integer := 115200
    );
    port (
        clk_i  : in  std_logic;
        rst_i  : in  std_logic;
        rx_i   : in  std_logic;
        data_o : out std_logic_vector((DATA_BITS-1) downto 0);
        flag_rx_o : out std_logic
    );
    end component;

begin

process(clk_i, rst_i)
begin
    if rst_i = '1' then
        tx_o <= '1';
        flag_tx_o <= '0';
        --internal signals
        b <= (others => '0');
        clk_count <= 0 ;
        bit_count <= 0;

        
    elsif rising_edge(clk_i) then

            if tx_order_i = '1' then
                if b_saved = 0 then
                    b <= data_i;
                    b_saved <= 1;
                    flag_tx_o <= '0';
                end if ;


                -- Envoi d'un bit
                if clk_count < CLKS_PER_BIT -1 then -- CLKS_PER_BIT = 1
                    clk_count <= clk_count + 1;

                else 
                    if bit_count = 0 then   
                        tx_o <= '0'; --START bit
                        bit_count <= bit_count +1;
                    
                    elsif bit_count < DATA_BITS + 1 then --"START + DATA" = DATA_BITS + 1 
                        tx_o <= b(bit_count-1);
                        bit_count <= bit_count + 1;
                        

                    else 
                        tx_o <= '1'; --STOP bit
                        flag_tx_o <= '1';

                        --Reset for next UART Tx
                        b <= (others => '0');
                        b_saved <= 0;
                        clk_count <= 0 ;
                        bit_count <= 0;


                    end if;
                clk_count <= 0; --reset for next bit

                end if;
            
            end if;

    end if;

end process;

end architecture top;