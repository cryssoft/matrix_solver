#!/usr/bin/python3
"""
solver-003.py

Cellular automata-style solver to find the minimum path length through a rectangular
grid (with or without voids, walls, etc.) to a particular cell.  Might or might not
run in O(n^2) time.  I'll have to give that some more thought.

Wrote this as a proof-of-concept after watching: https://www.youtube.com/watch?v=09HTNGlkS0s&t=1748s

Definitely an eye-catching title to the video.  A* search is great for what it does
best, but it's not always the right answer.

This version just does text input but HTML5/SVG output.

This version adds a second matrix to show the direction through the path as well as
the path length for each cell.

NOTE:  Letting the cellular automata simulations re-calculate every path length in every
loop can be substantially slower, but it fixes some conditions that produce non-optimal
paths.  For the 10x20-walls.dat run, it was roughly 11% from 0.008121 to 0.009066 seconds.
"""

from sys  import argv as g_argv          #  global variables get a g_ prefix
from time import perf_counter


def get_dimensions(p_argv: list[str]) -> tuple[int]:
    """
    Tries to convert the first two command-line arguments into rows/columns in
    integer form.  If that fails in any way, This should throw an exception.
    Main validates the actual answers (a little bit).
    """
    return((int(p_argv[1]), int(p_argv[2])))


def fill_matrix_from_file(p_filename: str) -> list[list[int]]:
    """
    Simple loop to read the data from a file.  We're not doing any sanity cheecking
    here yet.  If the file exists and is readable, good.  Try to treat each row as a
    comma-separated list of integer values.  If anything fails to convert to an int,
    it will throw an exception.
    """
    l_return: list[list[int]] = []

    with open(p_filename, 'r') as l_file:
        for l_data in l_file:
            l_return.append([int(p_x) for p_x in l_data.strip().split(',')])

    return(l_return)


def init_path_directions(p_matrix_directions: list[list[int]]) -> list[list[str]]:
    """
    Trivial function to initialize a second matrix of empty strings to correspond to
    the input matrix we filled in the function above.  An empty string will indicate
    no path length/direction from this cell yet (redundantly).  We'll replace the empty
    strings with letters/combinations to indicate the path out of the cell as we decide
    on our shortest path out.
    """
    l_return: list[list[str]] = []

    for l_row in range(len(p_matrix_directions)):
        l_return.append([])
        for l_col in range(len(p_matrix_directions[l_row])):
            l_return[l_row].append('')

    return(l_return)


def validate_dimensions(p_rows: int, p_cols: int, p_matrix_paths: list[list[int]]) -> bool:
    """
    Checks the dimensions of the matrix.  Must be row+2 by cols+2.  We're currently
    hoping that the person who entered the data did it right.
    """
    l_return: bool = True

    if (len(p_matrix_paths)) != (p_rows + 2):
        l_return = False
    else:
        l_ctr: int = 0
        while ((l_return is True) and (l_ctr < (p_rows + 2))):
            if (len(p_matrix_paths[l_ctr]) != (p_cols + 2)):
                l_return = False
                break
            else:
                l_ctr += 1

    return(l_return)


def min_adjacent_w_diagonals(p_row: int, p_col: int, p_matrix_paths: list[list[int]], p_matrix_directions: list[list[str]]) -> int:
    """
    Computes the minimum path length from "adjacent" cells.  In this case,
    "adjacent" is row, column, or diagonal that touches the current cell.
    For example, cell 1,1 (first in the real matrix data) is adjacent to:
        (0,0) (0,1) (0,2)
        (1,0) (1,1) (1,2)
        (2,0) (2,1) (2,2)
    There's no need to check against our current value, but it makes the
    loops simpler.
    """
    l_directions: list[list[str]] = [['NW', 'N', 'NE'], ['W','','E'],['SW','S','SE']]
    l_min: int = p_matrix_paths[p_row][p_col]

    for l_row in range(p_row-1,p_row+2):
        for l_col in range(p_col-1,p_col+2):
            if ((p_matrix_paths[l_row][l_col] + 1) < l_min):
                l_min = p_matrix_paths[l_row][l_col] + 1
                p_matrix_directions[p_row][p_col] = l_directions[l_row-p_row+1][l_col-p_col+1]

    return(l_min)


def min_adjacent_wo_diagonals(p_row: int, p_col: int, p_matrix_paths: list[list[int]], p_matrix_directions: list[list[str]]) -> int:
    """
    Computes the minimum path length from "adjacent" cells.  In this case,
    "adjacent" is row or column ONLY that touches the current cell.
    For example, cell 1,1 (first in the real matrix data) is adjacent to:
              (0,1)
        (1,0) (1,1) (1,2)
              (2,1)
    There's no need to check against our current value, but it makes the
    loop simpler.
    """
    l_directions: list[list[str]] = [['NW', 'N', 'NE'], ['W','','E'],['SW','S','SE']]
    l_min: int = p_matrix_paths[p_row][p_col]

    if (p_matrix_paths[p_row-1][p_col] < l_min):
        l_min = p_matrix_paths[p_row-1][p_col] + 1
        p_matrix_directions[p_row][p_col] = 'N'
    for l_col in range(p_col-1,p_col+2):
        if ((p_matrix_paths[p_row][l_col] + 1) < l_min):
            l_min = p_matrix_paths[p_row][l_col] + 1
            p_matrix_directions[p_row][p_col] = l_directions[1][l_col-p_col+1]
    if (p_matrix_paths[p_row+1][p_col] < l_min):
        l_min = p_matrix_paths[p_row+1][p_col] + 1
        p_matrix_directions[p_row][p_col] = 'S'

    return(l_min)


def update_matrix(p_rows: int, p_cols: int, p_matrix_paths: list[list[int]], p_matrix_directions: list[list[str]]) -> int:
    """
    Go through the "real" matrix data (starting at (1,1), going to (rows,cols) and
    see if any path length(s) change during this loop.  If so, keep making changes
    until all path lengths are stable.

    NOTE:  Changing the <= to == in the first IF test speeds things up by never
    re-calculating the shortest path, but that can lead to non-optiomal paths
    because of the simple loops over rows/columns.
    """
    l_changes: int = 0

    for l_row in range(1,p_rows+1):
        for l_col in range(1,p_cols+1):
            if (p_matrix_paths[l_row][l_col] <= ((p_rows * p_cols) + 1)):     ###  change the re-calculation strategy here
                l_new = min_adjacent_w_diagonals(l_row, l_col, p_matrix_paths, p_matrix_directions)    ###  change the adjacency algorithm here
                if (l_new != p_matrix_paths[l_row][l_col]):
                    p_matrix_paths[l_row][l_col] = l_new
                    l_changes += 1

    return(l_changes)


def html_write_headings() -> None:
    """
    Trivial function to dump out some HTML headings and stuff.
    """
    print('<html>')
    print('  <head>')
    print('    <style>')
    print('path { fill: green; stroke-width: 1; stroke: green; }')
    print('rect.blocked { fill: black; stroke-width: 1; stroke: black; }')
    print('rect.destination { fill: yellow; stroke-width: 1; stroke: black; }')
    print('rect.empty { fill: white; stroke-width: 1; stroke: black; }')
    print('rect.full { fill: cyan; stroke-width: 1; stroke: black; }')
    print('text.path { fill: red; text-anchor: middle; }')
    print('    </style>')
    print('  </head>')
    print('  <body>')

    return


def html_svg_add_direction_arrow_to(p_x: int, p_y: int, p_x_step: int, p_y_step: int, p_direction: str) -> None:
    """
    Kind of a pain in the butt, but it calculates the position to draw a small arrow on the side/corner
    where it need to go according to where we first found our shortest path neighbor.

    This one assumes that we're modeling the to/destination rather than from/source.
    """
    if (p_direction == 'NW'):
        print(f'<path d="M{p_x+4} {p_y+4} L{p_x+10} {p_y+4} L{p_x+4} {p_y+10} Z" />')
    elif (p_direction == 'N'):
        print(f'<path d="M{p_x+(p_x_step/2)} {p_y+2} L{p_x+(p_x_step/2)+4} {p_y+6} L{p_x+(p_x_step/2)-4} {p_y+6} Z" />')
    elif (p_direction == 'NE'):
        print(f'<path d="M{p_x+p_x_step-4} {p_y+4} L{p_x+p_x_step-10} {p_y+4} L{p_x+p_x_step-4} {p_y+10} Z" />')
    elif (p_direction == 'W'):
        print(f'<path d="M{p_x+2} {p_y+(p_y_step/2)} L{p_x+6} {p_y+(p_y_step/2)-4} L{p_x+6} {p_y+(p_y_step/2)+4} Z" />')
    elif (p_direction == ''):
        pass
    elif (p_direction == 'E'):
        print(f'<path d="M{p_x+p_x_step-2} {p_y+(p_y_step/2)} L{p_x+p_x_step-6} {p_y+(p_y_step/2)-4} L{p_x+p_x_step-6} {p_y+(p_y_step/2)+4} Z" />')
    elif (p_direction == 'SW'):
        print(f'<path d="M{p_x+4} {p_y+p_y_step-4} L{p_x+10} {p_y+p_y_step-4} L{p_x+4} {p_y+p_y_step-10} Z" />')
    elif (p_direction == 'S'):
        print(f'<path d="M{p_x+(p_x_step/2)} {p_y+p_y_step-2} L{p_x+(p_x_step/2)+4} {p_y+p_y_step-6} L{p_x+(p_x_step/2)-4} {p_y+p_y_step-6} Z" />')
    elif (p_direction == 'SE'):
        print(f'<path d="M{p_x+p_x_step-4} {p_y+p_y_step-4} L{p_x+p_x_step-10} {p_y+p_y_step-4} L{p_x+p_x_step-4} {p_y+p_y_step-10} Z" />')
    else:
        pass

    return

def html_svg_write_matrix(p_rows: int, p_cols: int, p_heading: str, p_matrix_paths: list[list[int]], p_matrix_directions: list[list[str]]) -> None:
    """
    This replaces the text print version with a simplified SVG graphic (HTML5) that uses the internal CSS
    directives to save some space in the output file.
    """
    l_x_start: int = 20
    l_y_start: int = 40
    l_y: int = l_y_start
    l_x_step: int = 40
    l_y_step: int = 40

    print(f'<p><svg width="{(p_cols+2)*l_x_step+(l_x_step*2)}" height="{(p_rows+2)*l_y_step+l_y_step}">')
    print(f'<text x="5" y="25">(0,0)</text>')
    print(f'<text x="{(p_cols+2)*l_x_step+(l_x_step-10)}" y="25" style="text-anchor: end">{p_heading}</text>')

    for l_row in range(p_rows+2):
        l_x: int = l_x_start
        for l_col in range(p_cols+2):
            if (p_matrix_paths[l_row][l_col] == 0):
                l_class: str = 'destination'
            elif (p_matrix_paths[l_row][l_col] == ((p_rows*p_cols)+1)):
                l_class: str = 'empty'
            elif (p_matrix_paths[l_row][l_col] == ((p_rows*p_cols)+2)):
                l_class: str = 'blocked'
            else:
                l_class: str = 'full'
            print(f'<rect x="{l_x}" y="{l_y}" height="{l_y_step}" width="{l_x_step}" class="{l_class}"/>')
            print(f'<text x="{l_x+l_x_step/2}" y="{l_y+25}" class="path">{p_matrix_paths[l_row][l_col]}</text>')
            if (p_matrix_directions[l_row][l_col] != ''):
                html_svg_add_direction_arrow_to(l_x, l_y, l_x_step, l_y_step, p_matrix_directions[l_row][l_col])
            l_x += l_x_step
        l_y += l_y_step

    print('</svg></p>')

    return


def html_write_footings() -> None:
    """
    Trivial function to dump out some HTML footings and stuff.
    """
    print('  </body>')
    print('</html>')

    return


def main(p_argv: list[str]) -> None:
    """
    Some argument and input checking, then do the main solving loop.

    This ASSumes (you know what that does!) that the destination cell has a value of
    zero, edge cells all have a value of ((row*cols)+2) or greater, forbidden/blocked/full
    cells also have a value of ((rows*cols)+2) or greater, and "empty" cells start with a
    value of ((rows*cols)+1) to make sure they're longer than the longest possible path
    length through (rows*cols) cells.

    If an "empty" cell is completely blocked off, it will keep its original value.  It
    can't get to the destination anyway.

    There are two different "adjacency" definitions.  You change a letter in update_matrix
    to call a different function to allow or dis-allow diagonal moves.  Doing something
    like "diagonal moves only if not going between touching cells" would require a bit more
    work but would still be possible.
    """
    if (len(p_argv) != 4):
        print('USAGE:  solver-001.py row# col# filename')
        return

    l_rows, l_cols = get_dimensions(p_argv)
    if ((l_rows <= 0) or (l_cols <= 0)):
        print('ERROR:  row# and col# must be integers > zero')
        return

    l_matrix_paths: list[list[int]] = fill_matrix_from_file(p_argv[3])
    if validate_dimensions(l_rows, l_cols, l_matrix_paths):
        l_matrix_directions: list[list[str]] = init_path_directions(l_matrix_paths)
        l_changes: int = 999
        l_loop: int = 0
        html_write_headings()
        html_svg_write_matrix(l_rows, l_cols, f'Starting', l_matrix_paths, l_matrix_directions)
        l_time0 = perf_counter()
        while (l_changes > 0):
            l_changes: int = update_matrix(l_rows, l_cols, l_matrix_paths, l_matrix_directions)
            if (l_changes > 0):
                html_svg_write_matrix(l_rows, l_cols, f'After loop {l_loop}', l_matrix_paths, l_matrix_directions)
            l_loop += 1
        l_time1 = perf_counter()
        print(f'<p>Seconds in main loop w/ HTML output = {l_time1-l_time0:.6f}</p>')
        html_write_footings()
    else:
        print('ERROR:  Failed to load and/or validate matrix data')

    return


if (__name__ == '__main__'):
    main(g_argv)
