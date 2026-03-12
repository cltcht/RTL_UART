library ieee;
  use ieee.std_logic_1164.all;
  use ieee.numeric_std.all;

entity reg8 is port(
    clk_i : in std_logic;
    rst_i : in std_logic;

    d_i : in std_logic_vector(7 downto 0);
    q_o : out std_logic_vector(7 downto 0)
);
end entity reg8;

architecture rtl_reg8 of reg8 is

signal b : std_logic_vector(7 downto 0); -- bascules
begin

    process(clk_i, rst_i)
    begin
        if rst_i = '1' then
            q_o <= (others => '0');
        elsif rising_edge(clk_i) then
--           for i in 0 to 7 loop
--               b(i) <= d_i(i);
--               q_o(i) <= b(i); 
--            end loop;
            q_o <= d_i;
           
        end if;
    end process;

end architecture rtl_reg8;