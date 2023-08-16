# GCode laser cut test grid generator
# Michael Niggel
# See README.md

import sys
from datetime import datetime

# defaults
power_list = [100, 200, 400, 700, 1000]
speed_list = [2000, 4000, 6000, 8000, 10000]
passes = 1
width = 10.0
lines = 3.0

inset = 0.1 # margin as percentage of width
filename = 'test-grid.nc'
fill_mode = False

def gcode_header(meta):
    header = '; Laser test grid\n'
    header += F'; Generated {datetime.now()}\n'
    for line in meta:
        header += F'; {line}\n'
    header += 'G90\n'
    return header

def gcode_footer():
    return 'G0 X0 Y0 Z0\n'

def draw_square(origin_x, origin_y, distance, power, speed, passes=1):
    x_min = origin_x + distance * inset
    x_max = origin_x + distance * (1 - inset)
    y_min = origin_y + distance * inset
    y_max = origin_y + distance * (1 - inset)

    gcode = 'M4 S0\n'
    gcode += 'S0\n'
    gcode += F'G0X{x_min}Y{y_min}\n'
    gcode += F'S{power}\n'
    for _ in range(passes):
        gcode += F'G1X{x_max}F{speed}\n'
        gcode += F'Y{y_max}\n'
        gcode += F'X{x_min}\n'
        gcode += F'Y{y_min}\n'
    gcode += 'S0\n'
    gcode += 'M5 S0\n'
    return gcode

def draw_fill(origin_x, origin_y, distance, power, speed, passes=1):
    x_min = origin_x + (distance * inset) + 0.5/lines
    x_max = origin_x + (distance * (1 - inset)) - 0.5/lines
    y_min = origin_y + (distance * inset) + 0.5/lines
    y_max = origin_y + (distance * (1 - inset)) - 0.5/lines

    gcode = F'G0 X{x_min} Y{y_min} F{speed}\n'
    gcode += 'M4 S0\n'

    y = y_min

    while y < y_max:
        gcode += F'G1 X{x_max}S{power}\n'
        gcode += 'S0\n'
        y += (1/lines)
        if y < y_max:
            gcode += F'G0 X{x_max} Y{y} S0\n'
            gcode += F'G1 X{x_min} S{power}\n'
            gcode += 'S0\n'
            y += (1/lines)
            gcode += F'G0 X{x_min} Y{y} S0\n'

    gcode += 'S0\n'
    gcode += 'M5 S0\n'
    return gcode

def draw_grid(powers, speeds):
    gcode = ''
    for p_idx, power in enumerate(powers):
        for s_idx, speed in enumerate(speeds):
            if fill_mode:
                gcode += draw_fill(width * p_idx, width * s_idx, width, power, speed)
            else:
                gcode += draw_square(width * p_idx, width * s_idx, width, power, speed)
    return gcode

# parse command line args
CMDARG_POWER_LIST = '-p'
CMDARG_SPEED_LIST = '-s'
CMDARG_PASSES = '-pass'
CMDARG_WIDTH = '-w'
CMDARG_LINES = '-lines'
CMDARG_FILL = '-fill'

if __name__ == '__main__' and len(sys.argv) > 1:
    if CMDARG_POWER_LIST in sys.argv:
        power_arg_idx = sys.argv.index(CMDARG_POWER_LIST) + 1
        if power_arg_idx < len(sys.argv):
            try:
                power_list = [int(s) for s in sys.argv[power_arg_idx].split(',')]
            except:
                print("Invalid argument for -p")
                sys.exit(1)

    if CMDARG_SPEED_LIST in sys.argv:
        speed_arg_idx = sys.argv.index(CMDARG_SPEED_LIST) + 1
        if speed_arg_idx < len(sys.argv):
            try:
                speed_list = [int(s) for s in sys.argv[speed_arg_idx].split(',')]
            except:
                print("Invalid argument for -s")
                sys.exit(1)

    if CMDARG_PASSES in sys.argv:
        pass_arg_idx = sys.argv.index(CMDARG_PASSES) + 1
        if pass_arg_idx < len(sys.argv):
            try:
                passes = int(sys.argv[pass_arg_idx])
            except:
                print("Invalid argument for -pass")
                sys.exit(1)

    if CMDARG_WIDTH in sys.argv:
        width_arg_idx = sys.argv.index(CMDARG_WIDTH) + 1
        if width_arg_idx < len(sys.argv):
            try:
                width = float(sys.argv[width_arg_idx])
            except:
                print("Invalid argument for -w")
                sys.exit(1)

    if CMDARG_LINES in sys.argv:
        lines_arg_idx = sys.argv.index(CMDARG_LINES) + 1
        if lines_arg_idx < len(sys.argv):
            try:
                lines = float(sys.argv[lines_arg_idx])
            except:
                print("Invalid argument for -lines")
                sys.exit(1)

    if CMDARG_FILL in sys.argv:
        fill_mode = True

# collect meta
print(F"\nGrenerating {filename}")
meta = []
if fill_mode:
    meta.append("Mode: Fill/engrave")
    meta.append(F"Lines/mm: {lines}")
else:
    meta.append("Mode: Outline/cut")
meta.append(F"Powers: {power_list}")
meta.append(F"Speeds: {speed_list}")
meta.append(F"Passes: {passes}")
meta.append(F"Output size: {width * len(power_list)}mm x {width * len(speed_list)}mm")

for line in meta:
    print(line)

# run generator
output = gcode_header(meta)
for idx in range(passes):
    output += F"; pass #{idx + 1}\n"
    output += draw_grid(power_list, speed_list)
output += gcode_footer()

# write file
with open(filename, 'w') as file:
    file.write(output)
