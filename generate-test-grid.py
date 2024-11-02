# GCode laser cut test grid generator
# Michael Niggel
# See README.md

import sys
from datetime import datetime

# defaults
power_list = [100, 200, 400, 700, 1000]
speed_list = [2000, 4000, 6000, 8000, 10000]
passes = [1, 2, 3]
width = 10.0
lines = [3.0, 6.0]
types = ['power', 'speed']
limit = 1000.0

inset = 0.1 # margin as percentage of width
filename = 'test-grid.nc'
fill_mode = False
help_mode = False

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

def draw_fill(origin_x, origin_y, distance, power, speed, line_density, passes=1):
    x_min = origin_x + (distance * inset) + 0.5/line_density
    x_max = origin_x + (distance * (1 - inset)) - 0.5/line_density
    y_min = origin_y + (distance * inset) + 0.5/line_density
    y_max = origin_y + (distance * (1 - inset)) - 0.5/line_density

    gcode = F'G0 X{x_min} Y{y_min} F{speed}\n'
    gcode += 'M4 S0\n'

    y = y_min

    while y < y_max:
        gcode += F'G1 X{x_max}S{power}\n'
        gcode += 'S0\n'
        y += (1/line_density)
        if y < y_max:
            gcode += F'G0 X{x_max} Y{y} S0\n'
            gcode += F'G1 X{x_min} S{power}\n'
            gcode += 'S0\n'
            y += (1/line_density)
            gcode += F'G0 X{x_min} Y{y} S0\n'

    gcode += 'S0\n'
    gcode += 'M5 S0\n'
    return gcode

def draw_grid(x_type, y_type):
    x_type = x_type or 'power'
    y_type = y_type or 'speed'

    power = power_list[0]
    speed = speed_list[0]
    pass_num = passes[0]
    line_density = lines[0]

    if x_type == 'power':
        x_len = len(power_list)
    elif x_type == 'speed':
        x_len = len(speed_list)
    elif x_type == 'pass':
        x_len = len(passes)
    elif x_type == 'lines':
        x_len = len(line_density)

    if y_type == 'power':
        y_len = len(power_list)
    elif y_type == 'speed':
        y_len = len(speed_list)
    elif y_type == 'pass':
        y_len = len(passes)
    elif y_type == 'lines':
        y_len = len(line_density)

    gcode = ''
    for x in range(x_len):
        if x_type == 'power':
            power = power_list[x]
        elif x_type == 'speed':
            speed = speed_list[x]
        elif x_type == 'pass':
            pass_num = passes[x]
        elif x_type == 'lines':
            line_density = lines[x]

        for y in range(y_len):
            if y_type == 'power':
                power = power_list[y]
            elif y_type == 'speed':
                speed = speed_list[y]
            elif y_type == 'pass':
                pass_num = passes[y]
            elif y_type == 'lines':
                line_density = lines[y]

            if (power / speed) <= limit:
                if fill_mode:
                    gcode += draw_fill(width * x, width * y, width, power, speed, line_density, pass_num)
                else:
                    gcode += draw_square(width * x, width * y, width, power, speed, pass_num)
    return gcode

# parse command line args
CMDARG_HELP = '-?'
CMDARG_POWER_LIST = '-p'
CMDARG_SPEED_LIST = '-s'
CMDARG_PASSES = '-pass'
CMDARG_WIDTH = '-w'
CMDARG_LINES = '-lines'
CMDARG_FILL = '-fill'
CMDARG_TYPES = '-xy'
CMDARG_LIMIT = '-limit'
CMDARG_INSET = '-inset'

if __name__ == '__main__' and len(sys.argv) > 1:
    if CMDARG_HELP in sys.argv:
        help_mode = True

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
                passes = [int(n) for n in sys.argv[pass_arg_idx].split(',')]
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
                lines = [float(n) for n in sys.argv[lines_arg_idx].split(',')]
            except:
                print("Invalid argument for -lines")
                sys.exit(1)

    if CMDARG_FILL in sys.argv:
        fill_mode = True

    if CMDARG_TYPES in sys.argv:
        types_arg_idx = sys.argv.index(CMDARG_TYPES) + 1
        if types_arg_idx < len(sys.argv):
            try:
                types = [s for s in sys.argv[types_arg_idx].split(',')]
                values = ['power', 'speed', 'pass', 'lines']
                if len(types) != 2:
                    raise
                for x in types:
                    if x not in values:
                        raise
            except:
                print("Invalid argument for -xy")
                sys.exit(1)

    if CMDARG_LIMIT in sys.argv:
        limit_arg_idx = sys.argv.index(CMDARG_LIMIT) + 1
        if limit_arg_idx < len(sys.argv):
            try:
                limit = float(sys.argv[limit_arg_idx])
            except:
                print("Invalid argument for -max")
                sys.exit(1)

    if CMDARG_INSET in sys.argv:
        gap_arg_idx = sys.argv.index(CMDARG_INSET) + 1
        if gap_arg_idx < len(sys.argv):
            try:
                inset = float(sys.argv[gap_arg_idx])
                if inset >= 0.5:
                    print("inset must be < 0.5")
                    sys.exit(1)
            except:
                print("Invalid argument for -inset")
                sys.exit(1)

# collect meta
print(F"\nGrenerating {filename}")
meta = []
if fill_mode:
    meta.append("Mode: Fill/engrave")
    if 'lines' in types:
        meta.append(F"Lines/mm: {lines}")
    else:
        meta.append(F"Lines/mm: {lines[0]}")
else:
    meta.append("Mode: Outline/cut")

if 'power' in types:
    meta.append(F"Powers: {power_list}")
else:
    meta.append(F"Power: {power_list[0]}")

if 'speed' in types:
    meta.append(F"Speeds: {speed_list}")
else:
    meta.append(F"Speed: {speed_list[0]}")

if 'pass' in types:
    meta.append(F"Passes: {passes}")
else:
    meta.append(F"Passes: {passes[0]}")

meta.append(F"Output size: {width * len(power_list)}mm x {width * len(speed_list)}mm")
meta.append(F"Columns: {types[0]} Rows: {types[1]}")
if limit < 1000:
    meta.append(F"Limit: {limit} pwr/mm/s")

if not help_mode:
    for line in meta:
        print(line)

if help_mode or (__name__ == '__main__' and len(sys.argv) <= 1):
    print("\n\nUsage:")
    print("-p <list>: powers to test")
    print("-s <list>: speeds to test (mm/min)")
    print("-pass <#>: number of passes")
    print("-w <#>: size of test patch (mm)")
    print("-inset <#>: margin on each patch (pct of w)")
    print("-lines <#>: fill mode density (lines/mm)")
    print("-fill: switch to fill/engrave mode (default is outline/cut)")
    print("-limit <#>: Limits maximum energy at power/speed")
    print("-xy <list>: axis mode (power/speed/pass/lines)")

if not help_mode:
    # run generator
    output = gcode_header(meta)
    output += draw_grid(types[0], types[1])
    output += gcode_footer()

    # write file
    with open(filename, 'w') as file:
        file.write(output)
