library ieee;
  use ieee.std_logic_1164.all;
  use ieee.numeric_std.all;

entity uart_rx is
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
end entity uart_rx;

architecture rtl_uart_rx of uart_rx is

    type uart_state_t is (IDLE, START, DATA, STOP);
    signal state     : uart_state_t;
    signal b : std_logic_vector((DATA_BITS-1) downto 0); -- bascule pour data

    -- Rapport CLK_FREQ / BAUD_RATE = nombre de coups d'horloge par bit
    constant CLKS_PER_BIT : integer := CLK_FREQ / BAUD_RATE; -- 434 coups d'horloges de Rx / bit reçu de Tx

    signal clk_count : integer range 0 to CLKS_PER_BIT - 1;
    signal data_bit_count : integer range 0 to DATA_BITS;

begin

process(clk_i, rst_i)
begin
    if rst_i = '1' then
        state <= IDLE;
        clk_count <= 0;
        flag_rx_o <= '0';
        data_o <= (others => '0');
        b <= (others => '0');
    elsif rising_edge(clk_i) then
        case state is
            when IDLE =>
                if rx_i = '0' then
                    state <= START;
                    clk_count <= 0;
                    flag_rx_o <= '0';
                    data_o <= (others => '0');
                else 
                    state <= IDLE; --we keep the else to avoid synthetizer putting additional latch
                end if;
            when START => 
                if clk_count < CLKS_PER_BIT/2 then -- CLKS_PER_BIT/2 = 217
                    clk_count <= clk_count+1;
                    state <= START;
                else
                    clk_count <= 0; --prepare pour DATA
                    data_bit_count <= 0; --prepare pour DATA
                    state <=  DATA;
               end if;
            when DATA  => 
                if clk_count < CLKS_PER_BIT -1 then -- CLKS_PER_BIT = 434
                    clk_count <= clk_count + 1;
                    state <= DATA;
                else
                    if data_bit_count < DATA_BITS then
                        b(DATA_BITS-1) <= rx_i;
                        
                        for i in 0 to ((DATA_BITS-1) - 1) loop
                        b(DATA_BITS-1 - (i+1)) <= b(DATA_BITS-1 - i);
                        end loop;

                        data_bit_count <= data_bit_count + 1;
                        clk_count <= 0;
                    else
                        clk_count <= 0;
                        state <= STOP;
                    end if;
                end if;

            when STOP  =>
                if clk_count < CLKS_PER_BIT/2 then
                    clk_count <= clk_count+1;
                    state <= STOP;
                else 
                    if rx_i = '1' then -- comportement normal
                        data_o <= b;
                        flag_rx_o <= '1';
                    else --problème dans la trame : STOP non reçu
                        flag_rx_o <= '0'; -- flag : erreur
                    end if;
                    state <= IDLE;
                end if;
        end case;
    end if;
end process;

end architecture rtl_uart_rx;