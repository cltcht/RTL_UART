library ieee;
  use ieee.std_logic_1164.all;
  use ieee.numeric_std.all;

entity uart_tx is
    generic (
        DATA_BITS    : integer := 12;
        CLK_FREQ     : integer := 115200;  -- frequency of FPGA
        BAUD_RATE    : integer := 115200   -- Uart frequency
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

     -- latch to save data_i while doing UART transactions
    signal b : std_logic_vector((DATA_BITS-1) downto 0);

    -- CLK_FREQ / BAUD_RATE = Clk hits per bit being sent
    signal bit_count : integer range 0 to DATA_BITS+2;

    --flags
    signal frame_sent : std_logic; --flag to know if dataframe has been sent before tx_order reset
    signal is_busy : std_logic;    -- flag to know if component is busy
    signal b_saved : std_logic;    --flag to know if data has been saved in latch
begin

tx_busy_o <= is_busy;
process(clk_i, rst_i)
begin
    if rst_i = '1' then --reset system
        tx_o <= '1';
        is_busy <= '0';
        --internal signals
        b <= (others => '0');
        b_saved <= '0';
        bit_count <= 0;
        frame_sent <= '0';

        
    elsif rising_edge(clk_i) then
        -- FRAME State : Nothing to send, nothing is being sent
            if (tx_order_i = '0') and (frame_sent = '0') and (is_busy = '0') then
                --Reset for next UART Tx
                b <= (others => '0');
                b_saved <= '0';
                bit_count <= 0;
        -- FRAME State : Frame isn't being sent/already sent, received order
            elsif (tx_order_i = '1') and (frame_sent = '0') and (is_busy = '0') then
                if b_saved = '0' then
                    b <= data_i; --saving data in a latch for safety as anything can happen to data_i
                    b_saved <= '1';
                    is_busy <= '1'; --starting Tx
                end if ;

        -- FRAME State : Frame is being sent
            elsif (is_busy = '1') and (frame_sent = '0') then
                -- Sending i-th bit

                 
                    if bit_count = 0 then   
                        tx_o <= '0'; --START bit
                        bit_count <= bit_count +1;
                    
                    elsif bit_count < DATA_BITS + 1 then --"START + DATA" = DATA_BITS + 1 
                        tx_o <= b(bit_count-1);
                        bit_count <= bit_count + 1;
                        

                    elsif bit_count < DATA_BITS + 2 then --"START + DATA + STOP" = DATA_BITS + 2
                        tx_o <= '1'; --STOP bit
                        bit_count <= bit_count + 1;
                    else
                        frame_sent <= '1';

                    end if;
                

                
        -- FRAME State : Already sent, waiting for tx_order_i reset
        -- for safety do not release busy flag here
            elsif (tx_order_i = '1') and (frame_sent = '1') and (is_busy = '1') then
                --Reset for next UART Tx
                b <= (others => '0');
                b_saved <= '0';
                bit_count <= 0;

        -- FRAME State : Already sent, tx_order_i was resetted 
        -- => can reset frame_sent safely and release busy flag
            elsif (tx_order_i = '0') and (frame_sent = '1') and (is_busy = '1') then
                frame_sent <= '0';
                is_busy <= '0';
                --Reset for next UART Tx
                b <= (others => '0');
                b_saved <= '0';
                bit_count <= 0;
            end if;

    end if;

end process;

end architecture rtl_uart_tx;