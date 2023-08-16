# laser-test-grid
Python-based test patch grid generator for materials testing with laser cutting/engraving.
Outputs gcode file to current working directory, creating or overwriting `test-grid.nc`.


## Usage
Install Python, then run from the command line.

`python generate-test-grid.py [-fill] [-p "csv"] [-s "csv"] [-pass N] [-w N] [-lpmm N]`

- `-fill`: enable fill/engrave mode (default is cut mode)
- `-p <list>`: set power levels (default 100,200,400,700,1000)
- `-s <list>`: set speed levels (default 2000,4000,6000,8000,10000)
- `-pass <int>`: set number of passes (default 1)
- `-w <float>`: set size of test patch (default 10.0)
- `-lines <float>`: set line density for fill mode (default 3.0)


## Notes
- All test patches are square and include a 10% margin.
- Cut/outline mode outlines each square; Fill/engrave mode fills each square.
- Total size of test grid depends on patch size multiplied by number of power and speed levels
- Spaces are allowed in arguments only if quoted. Use either `-p 100,200,300` or `-p "100, 200, 300"`
- Units are not specified in the output file and will be assigned by the machine. Typical values are:
    - power: 0 to 1000
    - speed: mm/min
    - width: mm
    - lines: lines/mm


## Examples

`python generate-test-grid.py`<br />
Generates a grid using default settings (5×5, cut mode, power from 100–1000 and speed from 100–1000)

`python generate-test-grid.py -p 200,400,800 -s 1000,2000,4000,8000`<br />
Generates a 3×4 grid of square cuts with power from 200–800 and speed from 1000–8000.

`python generate-test-grid.py -fill -p 100,200,300,400,500 -s 1500,3000,6000,10000,20000`<br />
Generates a 5×5 grid of engraving patches with power from 100–500 and speed from 1500–20000.


## No warranty
This software is provided freely, as-is, without warranty. See [license](LICENSE.md).
