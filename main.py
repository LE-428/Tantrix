import numpy as np
import random as random

# import math
import matplotlib.pyplot as plt


# Koordinaten von dem System der Sechseckmittelpunkte umrechnen in kartesisch
def getCoordinates(pos):
    hex_coords = np.array([[0, 0], [-1, -1], [0, -1], [1, 0], [1, 1], [0, 1], [-1, 0]])
    coords = hex_coords[pos]

    def rotation_matrix(theta):
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)
        return np.array([[cos_theta, -sin_theta],
                         [sin_theta, cos_theta]])

    b1 = np.eye(2)
    hex_matrix = np.array([rotation_matrix(np.pi / 6) @ b1[:, 0], rotation_matrix(np.pi / 3) @ b1[:, 1]])
    hex_matrix = np.transpose(hex_matrix)

    return hex_matrix @ coords


# Die Lösung plotten, jedes Tile in der Lösung wird betrachtet und einzeln
# geplottet nach der Orientierung und den Farbcodes
def draw_solution(solution, tiles):
    fig, ax = plt.subplots(figsize=(8, 6))

    # Größe und Position der Steine festlegen
    tile_size = 0.55

    # Für jeden Stein in der Lösung
    for i, tile_index in enumerate(solution[0]):
        tile_orientation = solution[2][i]
        tile = tiles[tile_index]

        # Zeichne die Vorderseite des Steins
        draw_hexagon(ax, i, tile_orientation, tile, tile_size)

    ax.axis('equal')
    ax.axis('off')
    plt.show()


def draw_hexagon(ax, position, orientation, tile, size=0.55):
    colors = {'1': 'blue', '2': 'yellow', '3': 'red'}
    x, y = getCoordinates(position)

    angles = np.arange(- 2 / 3 * np.pi, 4 / 3 * np.pi, np.pi / 3)
    for edge in range(0, 6):
        x_start = x + size * np.cos(angles[edge])
        y_start = y + size * np.sin(angles[edge])
        x_end = x + size * np.cos(angles[(edge + 1) % 6])
        y_end = y + size * np.sin(angles[(edge + 1) % 6])

        color = colors[str(getColor(tile, edge, orientation))]

        ax.plot([x_start, x_end], [y_start, y_end], color=color, linewidth=3)


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


#  Die Farbe einer Kante eines Steins ausgeben als int mit obiger Codierung
def getColor(tile, edge, orientation):
    return int(tile[(edge + orientation) % 6])


# Zufällige Lösung ausgeben, falls nur Vorder- oder Rückseite der Steine verwendet werden soll
# dann tile_bool auf 1 setzen
def randomSol(all_tiles, tile_bool=0):
    sol_arr = [[0] * 7 for _ in range(3)]
    tiles_vec = []
    if tile_bool == 0:
        tiles_vec = random.sample([*range(0, 14)], k=7)
    elif tile_bool == 1:
        tiles_vec = [(i * 2) + random.randint(0, 1) for i in range(7)]
    sol_arr[0] = tiles_vec
    sol_arr[1] = [all_tiles[i] for i in tiles_vec]
    sol_arr[2] = [int(random.uniform(0, 6)) for i in range(1, 8)]
    return sol_arr


# Fitnessfunktion, welche die Anzahl der Fehler, also nicht übereinstimmender Farben an der Kanten
# der Steine zählt
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
                                                                                 (i + 4) % 6, curr_sol[2][i + 1]):
                mismatches += 1
        else:  # i = 6
            if getColor(curr_sol[1][i], (i + 1) % 6, curr_sol[2][i]) != getColor(curr_sol[1][1], (i + 4) % 6,
                                                                                 curr_sol[2][1]):
                mismatches += 1
    return mismatches


def main():
    # np.set_printoptions(suppress=True, precision=5)
    solution = [[0, 2, 4, 7, 8, 11, 12], ['112323', '131322', '131223', '112233', '121323', '221331', '113322'], [4, 1, 1, 3, 2, 5, 4]]
    current_score = 12
    current_solution = []
    while current_score > 0:
        current_solution = randomSol(tiles, 1)
        print(current_solution)
        print("Value of the objective function of the current solution: \n")
        current_score = objective(current_solution)
        print(current_score)
    draw_solution(current_solution, tiles)
    # draw_solution(solution, tiles)
    # print(objective(solution))


if __name__ == "__main__":
    main()
