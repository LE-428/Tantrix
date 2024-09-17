# Tantrix Puzzle Solver with Simulated Annealing

## Overview

This project involves solving Tantrix puzzles using a simulated annealing algorithm. Tantrix is a tile-based game that requires arranging hexagonal tiles in a specific way to match colored edges. The goal of this project is to use simulated annealing to find optimal or near-optimal solutions for given Tantrix puzzles.

## Files

- **start.py**: Quick-start file can be executed directly from the command window with **python start.py**, add **-h** for help
- **main.py**: Contains the primary functions and implementations for solving the Tantrix puzzle using simulated annealing.
- **main_parallel.py**: Implements parallel processing to enhance the performance of the puzzle-solving algorithm, leveraging multiple CPU cores.
- **landscape.py**: Analyzes the fitness landscape of the Tantrix flower puzzle
- **equivalence.py**: Groups the puzzles by using symmetry and color permutations

## Data

- **solutions.txt**: One solution of every puzzle per line (3432)
- **3432.txt**: Number of solutions to the 3432 flower puzzles with 3 colors
- **sols_135135_pairings.csv**: Number of solutions combined to the 128 puzzles emerging from every pairing of the first 14 Tantrix tiles (see *calc_sols_per_pairing* in **main.py**)
- **equivalence_classes.csv**: (see *write_class_data* in **main.py**)
## Simulated Annealing Algorithm

Simulated annealing is a probabilistic technique for approximating the global optimum of a given function. In the context of the Tantrix puzzle, the algorithm attempts to minimize the number of mismatched edges between adjacent tiles.