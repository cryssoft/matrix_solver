#!/usr/bin/python3
"""
solver-001.py

Cellular automata-style solver to find the minimum path length through a rectangular
grid (with or without voids, walls, etc.) to a particular cell.  Might or might not
run in O(n^2) time.  I'll have to give that some more thought.

Wrote this as a proof-of-concept after watching: https://www.youtube.com/watch?v=09HTNGlkS0s&t=1748s

Definitely an eye-catching title to the video.  A* search is great for what it does
best, but it's not always the right answer.

This version just does text input and text output.
"""

from sys  import argv as g_argv          #  globals get a g_ prefix
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


def validate_dimensions(p_rows: int, p_cols: int, p_matrix: list[list[int]]) -> bool:
    """
    Checks the dimensions of the matrix.  Must be row+2 by cols+2.  We're currently
    hoping that the person who entered the data did it right.
    """
    l_return: bool = True

    if (len(p_matrix)) != (p_rows + 2):
        l_return = False
    else:
        l_ctr: int = 0
        while ((l_return is True) and (l_ctr < (p_rows + 2))):
            if (len(p_matrix[l_ctr]) != (p_cols + 2)):
                l_return = False
            else:
                l_ctr += 1

    return(l_return)


def pretty_print_matrix(p_heading: str, p_matrix: list[list[int]]) -> None:
    """
    Not super pretty, but it prints the matrix in neat-er rows with a heading.
    """
    print(p_heading)
    for l_ctr in range(len(p_matrix)):
        print(p_matrix[l_ctr])

    return


def min_adjacent_w_diagonals(p_row: int, p_col: int, p_matrix: list[list[int]]) -> int:
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
    l_min: int = p_matrix[p_row][p_col]

    for l_row in range(p_row-1,p_row+2):
        for l_col in range(p_col-1,p_col+2):
            if ((p_matrix[l_row][l_col] + 1) < l_min):
                l_min = p_matrix[l_row][l_col] + 1

    return(l_min)


def min_adjacent_wo_diagonals(p_row: int, p_col: int, p_matrix: list[list[int]]) -> int:
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
    l_min: int = p_matrix[p_row][p_col]

    if (p_matrix[p_row-1][p_col] < l_min):
        l_min = p_matrix[p_row-1][p_col] + 1
    for l_col in range(p_col-1,p_col+2):
        if ((p_matrix[p_row][l_col] + 1) < l_min):
            l_min = p_matrix[p_row][l_col] + 1
    if (p_matrix[p_row+1][p_col] < l_min):
        l_min = p_matrix[p_row+1][p_col] + 1

    return(l_min)


def update_matrix(p_rows: int, p_cols: int, p_matrix: list[list[int]]) -> int:
    """
    Go through the "real" matrix data (starting at (1,1), going to (rows,cols) and
    see if any path length(s) change during this loop.  If so, keep making changes
    until all path lengths are stable.
    """
    l_changes: int = 0

    for l_row in range(1,p_rows+1):
        for l_col in range(1,p_cols+1):
            if (p_matrix[l_row][l_col] == ((p_rows * p_cols) + 1)):
                l_new = min_adjacent_w_diagonals(l_row, l_col, p_matrix)
                if (l_new != p_matrix[l_row][l_col]):
                    p_matrix[l_row][l_col] = l_new
                    l_changes += 1

    return(l_changes)


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

    There are two different "adjacency" definitions.  You change a letter to call a 
    different function to allow or dis-allow diagonal moves.  Doing something like
    "diagonal moves only if not going between touching cells" would require a bit more
    work but would still be possible.
    """
    if (len(p_argv) != 4):
        print('USAGE:  solver-001.py row# col# filename')
        return

    l_rows, l_cols = get_dimensions(p_argv)
    if ((l_rows <= 0) or (l_cols <= 0)):
        print('ERROR:  row# and col# must be integers > zero')
        return

    l_matrix: list[list[int]] = fill_matrix_from_file(p_argv[3])
    if validate_dimensions(l_rows, l_cols, l_matrix):
        l_changes: int = 999
        l_loop: int = 0
        pretty_print_matrix(f'Starting', l_matrix)
        l_time0 = perf_counter()
        while (l_changes > 0):
            l_changes: int = update_matrix(l_rows, l_cols, l_matrix)
            l_loop += 1
        l_time1 = perf_counter()
        print(f'Seconds in main loop = {l_time1-l_time0:.6f}')
        pretty_print_matrix(f'Ending', l_matrix)
    else:
        print('ERROR:  Failed to load and/or validate matrix data')
        return


if (__name__ == '__main__'):
    main(g_argv)
