# import numpy as np
import random as random

import math
import matplotlib.pyplot as plt

def draw_solution(solution, tiles):
    fig, ax = plt.subplots(figsize=(8, 6))

    # Größe und Position der Steine festlegen
    tile_size = 1.0
    positions = [(0, 0), (0.75, 1.3), (2.25, 1.3), (3, 0), (2.25, -1.3), (0.75, -1.3), (-0.75, -1.3)]

    # Für jeden Stein in der Lösung
    for i, tile_index in enumerate(solution[0]):
        x, y = positions[i]
        tile_orientation = solution[2][i]
        tile = tiles[tile_index]

        # Zeichne die Vorderseite des Steins
        draw_tile(ax, x, y, tile_size, tile_orientation, tile)

    ax.axis('equal')
    ax.axis('off')
    plt.show()

def draw_tile(ax, x, y, size, orientation, tile):
    colors = {'1': 'blue', '2': 'yellow', '3': 'red'}

    # Kantenverbindungen des Steins
    connections = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]

    # Orientierung des Steins anpassen
    if orientation > 0:
        tile = tile[-orientation:] + tile[:-orientation]

    # Steinkanten zeichnen
    for edge_index, color_code in enumerate(tile):
        start_x, start_y = x + size * 0.5 * math.cos(math.pi / 3 * edge_index), y + size * 0.5 * math.sin(math.pi / 3 * edge_index)
        end_x, end_y = x + size * 0.5 * math.cos(math.pi / 3 * (edge_index + 1)), y + size * 0.5 * math.sin(math.pi / 3 * (edge_index + 1))

        color = colors[color_code]
        ax.plot([start_x, end_x], [start_y, end_y], color=color, linewidth=3)

# # Beispielaufruf
solution = [[0, 2, 4, 7, 8, 11, 12], ['112323', '131322', '131223', '112233', '121323', '221331', '113322'], [4, 1, 1, 3, 2, 5, 4]]
tiles = ["112323", "212313", "131322", "112332", "131223", "121332", "113232", "112233", "121323", "113223", "131232", "221331", "113322", "121233"]
draw_solution(solution, tiles)


tiles = ["112323", "212313",  # Die Spielsteine werden codiert mit der Rhflg aus der Känguru-Anleitung
         "131322", "112332",  # Blau: 1, Gelb: 2, Rot: 3
         "131223", "121332",  # Der Stein wird so rotiert, dass die blaue Kurve an Rotation 0 steht und nach rechts
         "113232", "112233",  # abknickt, falls blau gerade wird gelb betrachtet
         "121323", "113223",  # Die Steine werden gegen den UZS von Orientation 0 an codiert
         "131232", "221331",
         "113322", "121233"]  # jeweils zwei Steine in einer Reihe sind in der Känguru-Version auf einem Stein


tiles_front_back = [[0] * 7 for _ in range(2)]  # Liste der Spielsteine mit Vorder- und Rückseite in jeweils
tiles_front_back[0] = [tiles[2 * i] for i in range(7)]  # einer Zeile
tiles_front_back[1] = [tiles[2 * i + 1] for i in range(7)]



def getColor(tile, edge, orientation):
    return int(tile[(edge + orientation) % 6])


def randomSol(all_tiles, tile_bool=0):
    sol_arr = [[0] * 7 for _ in range(3)]
    if tile_bool == 0:
        tiles_vec = random.sample([*range(0, 14)], k=7)
    elif tile_bool == 1:
        tiles_vec = [(i * 2) + random.randint(0, 1) for i in range(7)]
    sol_arr[0] = tiles_vec
    sol_arr[1] = [all_tiles[i] for i in tiles_vec]
    sol_arr[2] = [int(random.uniform(0, 6)) for i in range(1, 8)]
    return sol_arr



def objective(curr_sol):
    mismatches = 0
    for i in range(0, 7):  # jeden Stein der Blume einmal betrachten
        if i == 0:  # der mittlere Stein
            for edge in range(0, 6):  # alle 6 Nachbarsteine werden betrachtet
                if getColor(curr_sol[1][i], edge, curr_sol[2][i]) != \
                        getColor(curr_sol[1][edge + 1], (edge + 3) % 6, curr_sol[2][edge + 1]):
                    mismatches += 1
        elif i < 6:
            if getColor(curr_sol[1][i], (i + 1) % 6, curr_sol[2][i]) != getColor(curr_sol[1][i + 1],
                                                                                 (i + 3) % 6, curr_sol[2][i + 1]):
                mismatches += 1
        else:  # i = 6
            if getColor(curr_sol[1][i], (i + 1) % 6, curr_sol[2][i]) != getColor(curr_sol[1][1], (i + 3) % 6,
                                                                                 curr_sol[2][1]):
                mismatches += 1
    return mismatches




def main():
    # np.set_printoptions(suppress=True, precision=5)
    # color = getColor('212313', 5, 3)
    # print(color)
    # print(type(color))
    current_score = 12
    current_solution = []
    while current_score > 3:
        current_solution = randomSol(tiles, 1)
        print(current_solution)
        print("Value of the objective function of the current solution: \n")
        current_score = objective(current_solution)
        print(current_score)
    # draw_solution(current_solution, tiles)

if __name__ == "__main__":
    main()
