library ieee;
  use ieee.std_logic_1164.all;
  use ieee.numeric_std.all;

entity reg8 is port(
    clk_i : in std_logic;
    rst_i : in std_logic;

    d_i : in std_logic;
    q_o : out std_logic
);
end entity reg8;

architecture rtl_reg8 of reg8 is

signal b : std_logic_vector(7 downto 0); -- bascules
begin

    process(clk_i, rst_i)
    begin
        if rst_i = '1' then
            q_o <= '0';          -- reset prioritaire, indépendant de l'horloge
        elsif rising_edge(clk_i) then
           -- entree du registre : premiere bascule b(0)
           b(0) <= d_i;
           -- passage d'une bascule à une architecture
           for i in 0 to 6 loop
               b(i+1) <= b(i);
            end loop;
           -- sortie du registre : derniere bascule b(7)
           q_o <= b(7); 
        end if;
    end process;

end architecture rtl_reg8;