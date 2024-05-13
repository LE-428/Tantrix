import numpy as np
import random as random
from itertools import combinations
import copy
import datetime

# import math
import matplotlib.pyplot as plt

# to do: allgemeine Lösungen zulassen, funktionen verallgemeinern, alle 14C7 Blumen lösen

tiles = ["112323", "212313",  # Die Spielsteine werden codiert mit der Reihenfolge aus der Känguru-Anleitung
         "131322", "112332",  # Blau: 1, Gelb: 2, Rot: 3
         "131223", "121332",  # Der Stein wird so rotiert, dass die blaue Kurve an Rotation 0 steht und nach rechts
         "113232", "112233",  # abknickt, falls blau gerade wird gelb betrachtet
         "121323", "113223",  # Die Steine werden gegen den UZS von Orientation 0 an codiert
         "131232", "221331",
         "113322", "121233"]  # jeweils zwei Steine in einer Reihe sind in der Känguru-Version auf einem Stein

tiles_complete = [
    ['112323', '212313', '131322', '112332', '131223', '121332', '113232', '112233', '121323', '113223', '131232',
     '221331', '113322', '121233'],  # Blau, Gelb, Rot
    ['232344', '242343', '224343', '332442', '223434', '243324', '232443', '223344', '323424', '223443', '232434',
     '224334', '224433', '242334'],  # Gelb, Rot, Grün
    ['114343', '313414', '131344', '114334', '131443', '141334', '113434', '114433', '141343', '113443', '131434',
     '331441', '113344', '141433'],  # Blau, Rot, Grün
    ['112424', '212414', '141422', '112442', '141224', '121442', '114242', '112244', '121424', '114224', '141242',
     '221441', '114422', '121244']]  # Blau, Gelb, Grün

tiles_front_back = [[0] * 7 for _ in range(2)]  # Liste der Spielsteine mit Vorder- und Rückseite in jeweils
tiles_front_back[0] = [tiles[2 * i] for i in range(7)]  # einer Zeile
tiles_front_back[1] = [tiles[2 * i + 1] for i in range(7)]
tiles_front_back_indices = [[0] * 7 for _ in range(2)]
tiles_front_back_indices[0] = [2 * i for i in range(7)]
tiles_front_back_indices[1] = [2 * i + 1 for i in range(7)]

# Erstellen Sie eine Liste aller Kombinationen von 7 Elementen aus dem Vektor mit den Einträgen von 0 bis 13
# Codierung für alle möglichen Puzzles, mathematisch 14C7
all_puzzles = list(combinations([*range(14)], 7))


# Aus den ersten 14 Spielsteine die weiteren 42 generieren
def generate_tiles(tile_set):
    tiles_compl = [[list(tile_set[z]) for z in range(14)] for _ in range(4)]

    def shift_tile(tile, offset):  # vrnl schieben
        temp = copy.deepcopy(tile)
        for i in range(6):
            temp[i] = tile[(i + offset) % 6]
        return temp

    def get_dist(tile, col):
        indices = []  # Problem: was wenn Farbe nicht in tile enthalten?
        for r in range(6):
            if tile[r] == str(col):
                indices.append(r)
        if len(indices) == 0:
            return -1, -1
        else:
            dist = indices[1] - indices[0]
        if dist > 3:
            dist = 6 - dist
        return dist, indices[0]

    def sort_sol(tile):
        for j in range(1, 4):
            distance, index = get_dist(tile, j)
            if 0 < distance < 3:
                tile = shift_tile(tile, index)
                break
        return tile

    def create_tiles(t_set, all_tiles):
        for k in range(1, 4):
            for t in range(14):
                for g in range(6):
                    if t_set[t][g] == str(k):
                        all_tiles[k][t][g] = '4'
        return all_tiles

    tiles_compl = create_tiles(tile_set, tiles_compl)
    for u in range(4):
        for v in range(14):
            tiles_compl[u][v] = sort_sol(tiles_compl[u][v])
            tiles_compl[u][v] = ''.join(tiles_compl[u][v])
    return tiles_compl


# Dieselben Tiles vertauschen und rotieren? (swap_and_rotate, liefert bessere Ergebnisse)
# Fehler lokalisieren und diese Tiles dann vertauschen?
# Basierend auf der aktuellen Lösung einen neuen Lösungskandidaten
# erstellen, es werden eine zufällige Anzahl an Steinen vertauscht
# und anschließend eine zufällige Anzahl an Steinen zufällig rotiert
def generate_candidate(curr, swap_and_rotate=1):
    cand = copy.deepcopy(curr)  # Umkopieren, da sonst die current Lösung verändert wird
    n_swaps = np.random.randint(0, 8)  # Anzahl der Vertauschungen
    if swap_and_rotate:
        n_rotations = n_swaps
    else:
        n_rotations = np.random.randint(0, 8)  # Anzahl der Rotationen
    swap_indices = random.sample([*range(0, 7)], k=n_swaps)  # Indizes der zu vertauschenden Steine
    swap_indices_permutation = np.random.permutation(swap_indices)
    swap_tiles_perm = [cand[0][k] for k in swap_indices_permutation]  # Permutation der betroffenen Steine
    rotations = np.random.choice(6, n_rotations)  # Anzahl der Rotationen der Steine festlegen
    if swap_and_rotate:
        rotation_indices = swap_indices
        for z in range(len(swap_indices)):
            if swap_indices[z] == swap_indices_permutation[z] and len(swap_indices) > 1:  # Falls nicht vertauscht wird
                # , wird wenigstens rotiert
                rotations[z] = 0
    else:
        rotation_indices = random.sample([*range(0, 7)], k=n_rotations)  # Indizes der zu rotierenden Steine
    # swap_tiles = [curr[0][k] for k in swap_indices]
    # rotation_tiles = [curr[0][k] for k in rotation_indices]
    tiles_copy = copy.deepcopy(curr[1])

    def print_params():
        print("Anzahl der Vertauschungen: ", n_swaps)
        print("Anzahl der Rotationen: ", n_rotations)
        # print("Indizes der zu vertauschenden Steine: ", swap_indices)
        # print("Indizes der zu rotierenden Steine: ", rotation_indices)
        # print("Permutation der vertauschten Indizes: ", swap_indices_permutation)
        # print("Permutation der betroffenen Steine: ", swap_tiles_perm)
        # print("Anzahl der Rotationen der Steine: ", rotations)
        # print("Kandidat vor Veränderung: ", curr)
        # print("Kandidat nach Veränderung: ", cand)

    for k, rot in enumerate(rotation_indices):
        cand[2][rot] = (cand[2][rot] + rotations[k]) % 6
    for j, swap in enumerate(swap_indices):
        cand[0][swap] = swap_tiles_perm[j]
        cand[1][swap] = tiles_copy[swap_indices_permutation[j]]
    # if objective(cand) < objective(curr):
    #     print_params()
    print_params()
    return cand


# Eine eingegebene Lösung wird um eine Position im UZS rotiert
def rotate_sol(sol):
    sol_rot = copy.deepcopy(sol)
    pre_pos = copy.deepcopy(sol_rot[0])
    pre_tiles = copy.deepcopy(sol_rot[1])
    pre_rot = copy.deepcopy(sol_rot[2])
    for j in range(1, 6):  # äußere Steine werden eine Position in der Systematik weitergeschoben (absteigend)
        sol_rot[0][j] = pre_pos[j + 1]
        sol_rot[1][j] = pre_tiles[j + 1]
        sol_rot[2][j] = pre_rot[j + 1]  # es muss noch rotiert werden
    sol_rot[0][6] = pre_pos[1]  # Für den letzten Stein manuell kopieren, da sonst unschön
    sol_rot[1][6] = pre_tiles[1]
    sol_rot[2][6] = pre_rot[1]
    for t in range(7):  # alle (auch mittleren) Steine um eine Position im UZS rotieren
        sol_rot[2][t] = (sol_rot[2][t] + 1) % 6
    return sol_rot


# Zwei Lösungen vergleichen, und überprüfen, ob sie bis auf Rotation des gesamten Puzzles identisch sind, ein Puzzle
# fünfmal gedreht (der mittlere Stein wird einmal rotiert im UZS, alle anderen Steine werden um ein Feld weiter-
# gesetzt und ebenfalls um eine Kante im UZS rotiert, dann wird verglichen
def solutions_equiv(sol1, sol2):
    rotator = copy.deepcopy(sol1)
    for _ in range(1, 6):  # die erste Lösung wird insgesamt fünfmal rotiert im UZS
        rotator = rotate_sol(rotator)
        if rotator == sol2:
            return True
    return False


# Zahl im Dezimalsystem in Binär umwandeln, Möglichkeit, vorne Nullen
# anzuhängen, wird genutzt um später aus den 7 Steinen mit Vorder- und
# Rückseite alle Kombinationen zu erhalten (Vorderseite: 0, Rückseite:1)
def d2b(decimal, leading_zero_digit=0):
    integer = copy.deepcopy(decimal)
    result = []
    while integer > 0:
        if integer % 2 == 1:
            result.append("1")
            integer = (integer - 1) / 2
        else:
            result.append("0")
            integer = integer / 2
    if len(result) < leading_zero_digit:
        for i in range(leading_zero_digit - len(result)):
            result.append("0")
    result = result[::-1]
    return ''.join(result)


# Gibt die Koordinaten der Felder der Spielsteine in dem Hexagon-Koordinatensystem an (auch für weitere Steine mit
# Position 7 und größer
def get_coords_from_pos(pos):
    full_circles = 0
    start_coords = np.array([0, 0])
    coords = np.array([0, 0])
    moving_dir = np.array([0, 0])
    for k in range(pos):
        x = coords[0]
        y = coords[1]
        if x == 0:
            if y > 0:
                moving_dir = np.array([-1, -1])
            elif y < 0:
                moving_dir = np.array([1, 1])
        if y == 0:
            if x > 0:
                moving_dir = np.array([0, 1])
            elif x < 0:
                moving_dir = np.array([0, -1])
        if abs(x) == full_circles and abs(y) == full_circles:
            moving_dir = np.array([np.sign(x) * (-1), 0])
        coords += moving_dir
        if np.array_equal(coords, start_coords):
            coords += np.array([-1, -1])
            start_coords = copy.deepcopy(coords)
            full_circles += 1
    return coords


# Aus der Position auf dem Spielfeld die Koordinaten im Hexa-System erhalten
def get_pos_from_coords(coords):
    start_coords = np.array([0, 0])
    pos = 0
    x, y = [coords[i] for i in range(2)]
    if x == y and y < 0:
        coords += np.array([1, 1])
        x, y = [coords[i] for i in range(2)]
        pos += 1
    while not np.array_equal(coords, start_coords):
        moving_dir = np.array([0, 0])
        if x == 0:
            if y > 0:
                moving_dir = np.array([1, 0])
            elif y < 0:
                moving_dir = np.array([-1, 0])
        elif y == 0:
            if x > 0:
                moving_dir = np.array([-1, -1])
            elif x < 0:
                moving_dir = np.array([1, 1])
        elif x == y:
            moving_dir = np.array([0, np.sign(x) * (-1)])
        elif x < 0 < y or x > 0 > y:
            moving_dir = np.array([1, 1]) * np.sign(y)
        elif np.sign(x) == np.sign(y) and x != y:
            if abs(y) > abs(x):
                moving_dir = np.array([np.sign(x) * 1, 0])
            else:
                moving_dir = np.array([0, np.sign(x) * (-1)])
        coords += moving_dir
        x, y = [coords[i] for i in range(2)]
        pos += 1
        if x == y and x < 0:
            if x == y and x == -1:
                pos += 1
            coords += np.array([1, 1])
            x, y = [coords[i] for i in range(2)]
    return pos


def get_neighbor(field_number, edge):
    tile_coords = get_coords_from_pos(field_number)
    moving_dir = 0
    if edge == 0:
        moving_dir = np.array([-1, -1])
    elif edge == 1:
        moving_dir = np.array([0, -1])
    elif edge == 2:
        moving_dir = np.array([1, 0])
    elif edge == 3:
        moving_dir = np.array([1, 1])
    elif edge == 4:
        moving_dir = np.array([0, 1])
    elif edge == 5:
        moving_dir = np.array([-1, 0])
    target_coords = tile_coords + moving_dir
    target_pos = get_pos_from_coords(target_coords)
    return target_pos


# Koordinaten von dem System der Sechseckmittelpunkte umrechnen in kartesisch
def getCoordinates(pos):
    # hex_coords = np.array([[0, 0], [-1, -1], [0, -1], [1, 0], [1, 1], [0, 1], [-1, 0]])
    # coords = hex_coords[pos]
    coords = get_coords_from_pos(pos)

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
def draw_solution(solution, all_tiles):
    fig, ax = plt.subplots(figsize=(8, 6))

    # Größe und Position der Steine festlegen
    tile_size = 0.55

    # Für jeden Stein in der Lösung
    for i, tile_index in enumerate(solution[0]):
        tile_orientation = solution[2][i]
        tile = all_tiles[tile_index]

        # Zeichne die Vorderseite des Steins
        draw_hexagon(ax, i, tile_orientation, tile, tile_size)

    ax.axis('equal')
    ax.axis('off')
    plt.title(datetime.datetime.now().time())
    plt.show()


def draw_hexagon(ax, position, orientation, tile, size=0.55):
    colors = {'1': 'blue', '2': 'yellow', '3': 'red', '4': 'green'}
    x, y = getCoordinates(position)

    angles = np.arange(- 2 / 3 * np.pi, 4 / 3 * np.pi, np.pi / 3)
    for edge in range(0, 6):
        x_start = x + size * np.cos(angles[edge])
        y_start = y + size * np.sin(angles[edge])
        x_end = x + size * np.cos(angles[(edge + 1) % 6])
        y_end = y + size * np.sin(angles[(edge + 1) % 6])

        color = colors[str(getColor(tile, edge, orientation))]

        ax.plot([x_start, x_end], [y_start, y_end], color=color, linewidth=3)


# Von einer Variante der 7 Steine mit Vorder- und Rückseite die 2^7 = 128 Möglichkeiten,
# die Seiten der Steine zu kombinieren ausgeben als Vektoren mit den Steinenummern
def get_puzzles(tile_combo):
    output_puzzles = []
    for i in range(128):
        logical = d2b(i, 7)
        output_puzzles.append([tile_combo[int(logical[k])][k] for k in range(7)])
    return output_puzzles


#  Die Farbe einer Kante eines Steins ausgeben als int mit obiger Codierung
def getColor(tile, edge, orientation):
    return int(tile[(edge + orientation) % 6])


# allgemeine Form der Lösung für andere Puzzles: Länge n (für n Steine), zusätzliche
# Zeile für die Positionen der Steine
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
    sol_arr[2] = [int(random.uniform(0, 6)) for _ in range(1, 8)]
    return sol_arr


# Eine Startlösung generieren ausgehend von einer Kombination mit 7 Elementen aus den 14 Seiten
def create_starting_sol(combo, all_tiles):
    sol = [[0] * 7 for _ in range(3)]
    sol[0] = combo
    sol[1] = [all_tiles[k] for k in combo]
    sol[2] = [int(random.uniform(0, 6)) for _ in range(1, 8)]
    return sol


# Fitnessfunktion, welche die Anzahl der Fehler, also nicht übereinstimmender Farben an der Kanten
# der Steine zählt
def objective(sol):
    mismatches = 0
    for i in range(0, 7):  # jeden Stein der Blume einmal betrachten
        if i == 0:  # der mittlere Stein
            for edge in range(0, 6):  # alle 6 Nachbarsteine werden betrachtet
                if getColor(sol[1][i], edge, sol[2][i]) != \
                        getColor(sol[1][edge + 1], (edge + 3) % 6, sol[2][edge + 1]):
                    mismatches += 1
        elif i < 6:
            if getColor(sol[1][i], (i + 1) % 6, sol[2][i]) != getColor(sol[1][i + 1],
                                                                       (i + 4) % 6, sol[2][i + 1]):
                mismatches += 1
        else:  # i = 6
            if getColor(sol[1][i], (i + 1) % 6, sol[2][i]) != getColor(sol[1][1], (i + 4) % 6,
                                                                       sol[2][1]):
                mismatches += 1
    return mismatches


# Objective-Funktion für verallgemeinerte Lösungen (nicht nur für Blumen), gibt die Anzahl der Fehler an
# Für alle Formen von Puzzles die Anzahl der Fehler berechnen (Vorgehen:
# für jedes Tile die 6 Nachbarn betrachten und die Fehler zählen, der insgesamte Fehler sind dann
# die Summe der addierten Fehler /2
def obj_general(sol):
    mismatches = 0
    # Für Lösungen der Form [[Spielfeldindizes], [Steinindizes], [Codierung der Steine], [Rotation der Steine]]
    for index, tile in enumerate(sol[1]):  # Für jedes tile
        for edge in range(0, 6):  # Für jede edge des tile
            if get_neighbor(sol[0][index], edge) in sol[0]:  # Falls der Nachbar von tile an der edge existiert
                neighbor_index = sol[0].index(get_neighbor(sol[0][index], edge))  # Spielfeldindex des Nachbarn
                if getColor(sol[2][index], edge, sol[3][index]) != \
                        getColor(sol[2][neighbor_index], (edge + 3) % 6, sol[3][neighbor_index]):
                    mismatches += 1  # hier weiter
    return int(mismatches / 2)  # jeder Fehler wird immer doppelt gezählt,
    # da er von jedem Stein aus einmal betrachtet wird


# Die Annahmewahrscheinlichkeit für eine schlechtere Lösung im Verlauf des Algorithmus
def plot_p_over_steps(data):
    colors = {'0': 'blue', '1': 'green', '2': 'red', '3': 'cyan', '4': 'magenta', '5': 'yellow',
              '6': 'orange', '7': 'lime', '8': 'indigo', '9': 'pink', '10': 'skyblue', '11': 'salmon', '12': 'brown'}
    color = [0 for _ in range(len(data[9]))]
    index_list = [[0] for _ in range(13)]
    for index, k in enumerate(data[9]):
        if k <= 0:
            color[index] = colors[str(0)]
            index_list[0].append(index)
        else:
            color[index] = colors[str(k)]
            index_list[k].append(index)
    for err, col in colors.items():
        plt.scatter([data[0][int(g)] for g in index_list[int(err)]], [data[2][int(j)] for j in index_list[int(err)]],
                    s=0.2, color=col)

    # plt.scatter(data[0], data[2], s=0.2, color=color)
    plt.xlabel('Iteration')
    plt.ylabel('Acceptance probability')
    legend_labels = []
    for errors, color_code in colors.items():
        legend_labels.append(f'{errors}: {color_code}')
    lgnd = plt.legend(legend_labels, loc='upper right', title="diff: color")
    for handle in lgnd.legend_handles:
        handle.set_sizes([6.0])
    plt.title("p in Abhängigkeit von Fehlerdiff. "
              "zw. Kandidaten und aktueller Lösung")
    plt.show()


def plot_t_over_steps(data):
    plt.plot(data[0], data[1])
    plt.xlabel('Iteration')
    plt.ylabel('Temperature')
    # plt.legend()
    plt.show()


# Fehleranzahl der besten Lösung über die Iterationen plotten (best_val)
def plot_val_over_steps(data):
    plt.plot(data[0], data[3])
    plt.xlabel('Iteration')
    plt.ylabel('Objective')
    plt.ylim(0, max(data[7]))
    # plt.legend()
    plt.title(datetime.datetime.now().time())
    plt.show()


def plot_cand_curr_over_steps(data):
    figure, axis = plt.subplots(2)

    axis[0].plot(data[0], data[5], label='curr_val')
    axis[1].plot(data[0], data[7], label='cand_val')

    axis[0].legend()
    axis[1].legend()

    for ax in axis.flat:
        ax.set(xlabel='Iteration', ylabel='Objective')

    # Hide x labels and tick labels for top plots and y ticks for right plots.
    for ax in axis.flat:
        ax.label_outer()
    axis[0].set_ylim(0, max(data[7]))  # 12 für Blume
    axis[1].set_ylim(0, max(data[7]))

    plt.title(datetime.datetime.now().time())
    plt.show()


# Temperatur berechnen des Systems abhängig von Ausgangstemperatur und Anzahl der getätigten Schritte (= Zeit)
def get_temp(temp, step):
    t = temp / (0.2 * float(step + 1))
    return t


# Wahrscheinlichkeit, dass der aktuelle Kandidat als current Lösung übernommen wird, berechnen, auf Grundlage der
# Bewertung durch die objective-Funktion und die Temperatur (geringere Temperatur entpricht geringerer Wk, dass
# ein schlechterer Kandidat übernommen wird
def calc_acceptance(diff, temp):
    prob = np.exp(- diff / temp)
    return prob


# Abbruchkriterium, wenn 0 Fehler
# evtl bei 1/2 Fehler neuen Kandidaten berechnen durch Vertauschung von 2/3 Steinen?
# Mit dieser Funktion wird der simulated annealing Algorithmus durchgeführt, Eingangsparameter sind eine Startlösung,
# die Anzahl der Schritte und eine Anfangstemperatur, ausgegeben wird der beste Kandidat
def simulated_annealing(init_sol, n_iter, temp, param=1.0):
    # Data-Array mit 10 Zeilen
    # [0] Anzahl der Schritte
    # [1] Temperatur (temp)
    # [2] Annahmewahrscheinlichkeit einer schlechteren Lösung (p)
    # [3] Fehleranzahl der besten Lösung (best_val)
    # [4] Beste Lösung (best_sol)
    # [5] Fehleranzahl der aktuellen Lösung (curr_val)
    # [6] Aktuelle Lösung (curr_sol)
    # [7] Fehleranzahl des aktuellen Kandidaten (cand_val)
    # [8] Kandidat (cand_sol)
    # [9] Differenz (diff = cand_val - curr_val)
    data = [[0] * n_iter for _ in range(10)]
    if objective(init_sol) == 0:
        return [init_sol, objective(init_sol), data]
    data[0] = [*range(n_iter)]
    data[1] = [get_temp(temp, k) for k in range(n_iter)]

    best_sol = copy.deepcopy(init_sol)  # beste Lösung, wird am Schluss ausgegeben
    best_val = objective(best_sol)
    curr_sol, curr_val = best_sol, best_val
    for i in range(n_iter):
        if best_val == 0:
            break
        cand_sol = generate_candidate(curr_sol, 1)
        cand_val = objective(cand_sol)
        diff = cand_val - curr_val
        print("Iteration #{}, Differenz cand - curr: {}".format(i, diff))
        if cand_val - best_val < 0:
            best_sol = cand_sol
            best_val = cand_val
        t = data[1][i]
        if diff < 0:
            p = 1
        else:
            p = calc_acceptance(param * diff, t)  # multiplikativer Parameter Optimierung? Tradeoff wenige Schritte,
            # aber seltenes Lösungsfinden
        if np.random.rand() < p:
            if diff > 0:
                print("WORSE SOLUTION ACCEPTED")
            curr_sol, curr_val = cand_sol, cand_val
        # p = calc_acceptance(abs(diff), t)
        # if diff < 0 or np.random.rand() < p:
        #     if diff > 0:
        #         print("Worse solution accepted")
        #     curr_sol, curr_val = cand_sol, cand_val
        data[2][i] = p
        data[3][i] = best_val
        data[4][i] = best_sol
        data[5][i] = curr_val
        data[6][i] = curr_sol
        data[7][i] = cand_val
        data[8][i] = cand_sol
        data[9][i] = diff
    return [best_sol, best_val, data]


# Zum Vergleich werden n_gens zufällige Lösungen generiert, und die beste Fehleranzahl ausgegeben
def random_sol_mean(n_gens, all_tiles):
    evaluations_sum = 0
    best = 100
    for k in range(n_gens):
        sol = randomSol(all_tiles)
        sol_eval = objective(sol)
        if sol_eval < best:
            best = sol_eval
        evaluations_sum += sol_eval
    result = evaluations_sum / n_gens
    print("Durchschnittsfehleranzahl bei zufälliger Generierung von {} Lösungen: {}".format(n_gens, result))
    print("Beste Fehleranzahl bei zufälliger Generierung von {} Lösungen: {}".format(n_gens, best))


# Gibt die Kandidaten auf dem Weg zur Lösung aus (die ersten mit einer geringeren neuen Fehleranzahl)
def print_best_sols(data):
    visited = []
    for k in range(len(data[4])):
        if data[4][k] not in visited:
            visited.append(data[4][k])
            print("Iteration: {} \n candidate: {}".format(k, data[4][k]))


# Der Parameter, der bestimmt, wie schnell die Annahmewahrscheinlichkeit für schlechtere Lösungen sinkt
def find_param(sol, steps, temp, lim_low, lim_up, stepsize, n_runs, all_tiles):
    params = np.arange(lim_low, lim_up, stepsize)
    results = [[0] * len(params) for _ in range(3)]
    for index, param in enumerate(params):
        sol_found = 0
        sum_steps = 0
        for k in range(n_runs):
            sol = randomSol(all_tiles)
            _, _, data = simulated_annealing(sol, steps, temp, param)
            if 0 in data[3]:
                sol_found += 1
                sum_steps += data[3].index(0)  # Anzahl der Schritte bis zum Finden der Lösung
        results[0][index] = param
        results[1][index] = sol_found / n_runs
        results[2][index] = sum_steps / int(sol_found) if sol_found != 0 else 0  # n_runs
    return results


def plot_param_over_rate(res):
    plt.plot(res[0], res[1])
    plt.xlabel('Parameter value')
    plt.ylabel('% of successful runs')
    plt.ylim(0, 1)
    # plt.legend()
    plt.title(datetime.datetime.now().time())
    plt.show()


def plot_param_over_steps(res):
    plt.plot(res[0], res[2])
    plt.xlabel('Parameter value')
    plt.ylabel('# of steps to solution if successful')
    plt.ylim(0, max(res[2]))
    # plt.legend()
    plt.title(datetime.datetime.now().time())
    plt.show()


def main():
    # np.set_printoptions(suppress=True, precision=5)
    solution = [[1, 2, 5, 7, 9, 11, 12],
                ['212313', '131322', '121332', '112233', '113223', '221331', '113322'], [0, 2, 2, 3, 5, 4, 0]]
    solx = [[0, 1, 2, 3, 4, 5, 6],
            [1, 2, 5, 7, 9, 11, 12],
            ['212313', '131322', '121332', '112233', '113223', '221331', '113322'], [0, 2, 2, 3, 5, 4, 0]]
    # rot_sol = rotate_sol(solution)
    # draw_solution(solution, tiles)
    # draw_solution(rot_sol, tiles
    # current_score = 12
    # current_solution = []
    # while current_score > 0:
    #     current_solution = randomSol(tiles, 1)
    #     print(current_solution)
    #     print("Value of the objective function of the current solution: \n")
    #     current_score = objective(current_solution)
    #     print(current_score)
    # draw_solution(current_solution, tiles)
    # print(objective(solution))

    temperature = 500
    steps = 25000
    # start_sol = randomSol(tiles, 1)
    # start_sol = [[6, 4, 8, 11, 3, 1, 12], ['113232', '131223', '121323', '221331', '112332', '212313', '113322'],
    #              [2, 4, 3, 5, 2, 3, 5]]  # 1 Fehler
    start_sol = [[1, 3, 4, 6, 8, 11, 12], ['212313', '112332', '131223', '113232', '121323', '221331', '113322'],
                 [2, 2, 4, 5, 2, 4, 5]]
    opt_sol, opt_val, datastream = simulated_annealing(start_sol, steps, temperature, 5)
    draw_solution(opt_sol, tiles)
    print("Fehleranzahl der besten Lösung: {}".format(opt_val))
    print(opt_sol)
    print_best_sols(datastream)
    # plot_t_over_steps(datastream)
    # plot_p_over_steps(datastream)
    plot_val_over_steps(datastream)
    plot_cand_curr_over_steps(datastream)
    # random_sol_mean(steps, tiles)

    # Bestimmen des Parameters durch Ausprobieren
    # test_datastream = find_param(start_sol, 25000, 500, 0.5, 8.0, 0.5, 100, tiles)
    # plot_param_over_steps(test_datastream)
    # plot_param_over_rate(test_datastream)

    # generate_tiles(tiles)


if __name__ == "__main__":
    main()
