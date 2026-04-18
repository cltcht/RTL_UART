# RTL_UART
Building UART communication RTL components from scratch in VHDL.
  

## 0 - Summary
Personnal project to train on cocotb coroutines on UART firmware.  
RTL is written in `VHDL`.  


Tests are written with `cocotb` `Python` package and `ghdl` simulator.  
Results are displayed using `gtkwaves` and `Tcl` scripts.  
An automatic report is written in LaTeX using `PdfLatex`.  


## 1 - RTL Structure :

### Tx component


| Port       | i/o | Purpose                    |
|:-----------|:---:|:--------------------------:|
| clk_i      | in  | Clock                      |
| rst_i      | in  | Reset                      |
| data_i     | in  | Data to send within UART frame |
| tx_order_i | in  | Tx order                   |
| tx_o       | out | Uart Frame output          |
| tx_busy_o  | out | Component is busy sending  |

### Rx component


| Port       | i/o | Purpose                     |
|:-----------|:---:|:---------------------------:|
| clk_i      | in  | Clock                       |
| rst_i      | in  | Reset                       |
| rx_i       | in  | Uart Frame input            |
| data_o     | out | Data received within UART frame |
| flag_rx_o  | out | New data has been received  |


	
## 2 - Test details

#### Unitary test : *Tx component*

Relevant file : `uart_tx/uart_tx.vhd`
_________________
Sanity check `cocotb` test routines :
_________________
- `late_reset` : Sends random tx order signals before reset. Tx shouldn't happen if reset is up.
- `tx_busy` : Sends random tx order signals while uart is busy. Tx shouldn't happen if device is busy.
_________________

Regular Tx `cocotb` test routines :
_________________
- `send_two_frames_trivial_data` : Sets 0x000 and 0xFFF as input of Tx component. Validates the coherence of the UART frame output.
- `send_hundred_frames_random_data` : Sets random data as input of Tx component. Validates the coherence of the UART frame output.

_________________

#### Unitary test : *Rx component*

Relevant file : `uart_rx/uart_rx.vhd`
__________________
Regular Rx `cocotb` test routines :
__________________
- `get_two_frames_trivial_data` : Rx component receives frames as input with 0x000 and 0xFFF as data.  
Validates the coherence of the data output.
- `get_hundred_frames_random_data` : Rx component receives hundred frames as input with random data.  
Validates the coherence of the data output.

__________________
#### Global test : *External looping*
__________________

Relevant files : `top_level/top.vhd` `uart_tx/uart_tx.vhd` `uart_rx/uart_rx.vhd`

*RTL architecture definition :*

![RTL architecture](top_level.png)  
  

- `uart_top_looping_two_frames_trivial_data` : Sets 0x000 and 0xFFF as input of Tx component.  
Validates the coherence of the Rx component data output.
- `uart_top_looping_ten_frames_random_data` : Sets ten frames with random data as input of Tx component.  Validates the coherence of the Rx component data output.

## 3 - Setting up environment

Install miniconda using [following tutorial](https://www.anaconda.com/docs/getting-started/miniconda/main).  

In shell execute following command : `conda env create -f environment.yml`.

Install following libraries in order to compile the code :  
`sudo apt install ghdl gtkwave`

>**Warning** `pip install ghdl` installs a package named "ghdl" that's not related to RTL simulation please use `apt`

Activate Python environment with `conda activate rtl`

## 4 - Running tests !

To run the tests execute :
- `./run_sim uart_tx`
- `./run_sim uart_rx`
- `./run_sim top_level`  

Running scripts will execute `Tcl` scripts to enhance plots, *see /xxx/wave_xxx.tcl*

Test results can be seen in console or in report.

Test report is written as `report_uart.pdf` file.