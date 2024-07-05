# Tantrix Puzzle Solver with Simulated Annealing

## Overview

This project involves solving the Tantrix puzzle using a simulated annealing algorithm. The Tantrix puzzle is a tile-based game that requires arranging hexagonal tiles in a specific way to match colored edges. The goal of this project is to use simulated annealing to find optimal or near-optimal solutions for given Tantrix puzzles.

## Files

- **main.py**: Contains the primary functions and implementations for solving the Tantrix puzzle using simulated annealing.
- **main_parallel.py**: Implements parallel processing to enhance the performance of the puzzle-solving algorithm, leveraging multiple CPU cores.

## Simulated Annealing Algorithm

Simulated annealing is a probabilistic technique for approximating the global optimum of a given function. In the context of the Tantrix puzzle, the algorithm attempts to minimize the number of mismatched edges between adjacent tiles.