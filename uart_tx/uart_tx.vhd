library ieee;
  use ieee.std_logic_1164.all;
  use ieee.numeric_std.all;

entity uart_tx is
    generic (
        DATA_BITS    : integer := 12;
        CLK_FREQ     : integer := 115200;  -- fréquence horloge système
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
end entity uart_tx;

architecture rtl_uart_tx of uart_tx is

     -- latch pour enregistrer data_i durant la communication UART
    signal b : std_logic_vector((DATA_BITS-1) downto 0);
    signal b_saved : integer range 0 to 1; --booléen pour indiquer si les data ont étés sauvés

    -- Rapport CLK_FREQ / BAUD_RATE = nombre de coups d'horloge par bit
    constant CLKS_PER_BIT : integer := CLK_FREQ / BAUD_RATE; -- 1 coup d'horloge / bit envoye

    signal clk_count : integer range 0 to CLKS_PER_BIT - 1;
    signal bit_count : integer range 0 to DATA_BITS+2;

begin

process(clk_i, rst_i)
begin
    if rst_i = '1' then
        tx_o <= '1';
        tx_busy_o <= '0';
        --internal signals
        b <= (others => '0');
        b_saved <= 0;
        clk_count <= 0 ;
        bit_count <= 0;

        
    elsif rising_edge(clk_i) then

            if tx_order_i = '1' then
                if b_saved = 0 then
                    b <= data_i;
                    b_saved <= 1;
                    tx_busy_o <= '1';
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
                        

                    elsif bit_count < DATA_BITS + 2 then 
                        tx_o <= '1'; --STOP bit
                        bit_count <= bit_count + 1;
                    else
                        tx_busy_o <= '0';

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

end architecture rtl_uart_tx;