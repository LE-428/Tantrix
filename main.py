import time

import numpy as np
import random as random
from itertools import combinations
from itertools import groupby
import copy
import datetime

import math
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Arc
from matplotlib.lines import Line2D

# to do: allgemeine Lösungen zulassen, funktionen verallgemeinern, alle 14C7 Blumen lösen

tiles = ["112323", "212313",  # Die Spielsteine werden codiert mit der Reihenfolge aus der Känguru-Anleitung
         "131322", "112332",  # Blau: 1, Gelb: 2, Rot: 3
         "131223", "121332",  # Der Stein wird so rotiert, dass die blaue Kurve an Rotation 0 steht und nach rechts
         "113232", "112233",  # abknickt, falls blau gerade wird gelb betrachtet
         "121323", "113223",  # Die Steine werden gegen den UZS von Orientation 0 an codiert
         "131232", "221331",
         "113322", "121233"]  # jeweils zwei Steine in einer Reihe sind in der Känguru-Version auf einem Stein

tile_sets = [
    ['112323', '212313', '131322', '112332', '131223', '121332', '113232', '112233', '121323', '113223', '131232',
     '221331', '113322', '121233'],  # Blau, Gelb, Rot
    ['232344', '242343', '224343', '332442', '223434', '243324', '232443', '223344', '323424', '223443', '232434',
     '224334', '224433', '242334'],  # Gelb, Rot, Grün
    ['114343', '313414', '131344', '114334', '131443', '141334', '113434', '114433', '141343', '113443', '131434',
     '331441', '113344', '141433'],  # Blau, Rot, Grün
    ['112424', '212414', '141422', '112442', '141224', '121442', '114242', '112244', '121424', '114224', '141242',
     '221441', '114422', '121244']]  # Blau, Gelb, Grün

# alle 56 Spielsteine codiert, Priorität bei der Rotation: blau, gelb, rot
tiles_complete = ['112323', '212313', '131322', '112332', '131223', '121332', '113232',
                  '112233', '121323', '113223', '131232', '221331', '113322', '121233',
                  '232344', '242343', '224343', '332442', '223434', '243324', '232443',
                  '223344', '323424', '223443', '232434', '224334', '224433', '242334',
                  '114343', '313414', '131344', '114334', '131443', '141334', '113434',
                  '114433', '141343', '113443', '131434', '331441', '113344', '141433',
                  '112424', '212414', '141422', '112442', '141224', '121442', '114242',
                  '112244', '121424', '114224', '141242', '221441', '114422', '121244']

tiles_front_back = [[] * 7 for _ in range(2)]  # Liste der Spielsteine mit Vorder- und Rückseite in jeweils
tiles_front_back[0] = [tiles[2 * i] for i in range(7)]  # einer Zeile
tiles_front_back[1] = [tiles[2 * i + 1] for i in range(7)]
tiles_front_back_indices = [[] * 7 for _ in range(2)]
tiles_front_back_indices[0] = [2 * i for i in range(7)]
tiles_front_back_indices[1] = [2 * i + 1 for i in range(7)]

# Erstellen Sie eine Liste aller Kombinationen von 7 Elementen aus dem Vektor mit den Einträgen von 0 bis 13
# Codierung für alle möglichen Puzzles, mathematisch 14C7
all_puzzles = list(combinations([*range(14)], 7))


def get_dist(tile, col):
    """
    Abstand von einer Farbe in der Codierung, Beispiel "121323", get_dist(_, 1) liefert 2
    :param tile: Codierung eines Steins
    :param col: gesuchte Farbe
    :return: Abstand im array zwischen den beiden farbigen Kanten
    """
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


def generate_tiles(tile_set):
    """
    Aus den ersten 14 Spielsteine die weiteren 42 generieren
    :param tile_set: die ersten 14 Steine codiert
    :return: array mit allen 56 Steinen richtig codiert
    """
    tiles_compl = [[list(tile_set[z]) for z in range(14)] for _ in range(4)]

    def shift_tile(tile, offset: int):
        """
        :param tile: eine Liste mit den Farben des Spielsteins
        :param offset: um wie viele Stellen wird die Codierung von rechts nach links verschoben
        :return: das verschobene Tile
        """
        return [tile[(i + offset) % 6] for i in range(6)]

    def sort_sol(tile):
        """
        Stein-codierung richtig verschieben
        :param tile: Codierung eines Steins
        :return: korrekte Codierung
        """
        for j in range(1, 4):
            distance, index = get_dist(tile, j)
            if 0 < distance < 3:
                tile = shift_tile(tile, index)
                break
        return tile

    def create_tiles(t_set, all_tiles):
        """
        Alle übrigen 42 Steine erstellen durch schrittweises Ersetzen der drei Farben in der ersten 14 Steinen
        :param t_set:
        :param all_tiles:
        :return:
        """
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


def gen_cand_morph(curr, swap_and_rotate=1, morphing=0):
    """
    Generiere einen Kandidaten für allgemeine Formen von Lösungen
    Dieselben Tiles vertauschen und rotieren? (swap_and_rotate=1 setzen, liefert bessere Ergebnisse)
    :param curr: Eingangslösung
    :param swap_and_rotate: boolean, default True
    :param morphing: Form der Lösung verändern, default False 
    :return: Ausgangslösung
    """  # Positionen der Steine verändern, allgemeine Lösungen, längste Linie einer Farbe bestimmen, Fitnessfkt anpassen

    def sort_neighbors(zippo):
        zippo = [el for el in zippo if el[0] != 0]  # Stein auf Feld 0 herausnehmen, dieser soll immer fix bleiben
        # Sortieren der gezippten Liste basierend auf den Elementen der zweiten Elemente in absteigender Reihenfolge
        sorted_zippo = sorted(zippo, key=lambda x: x[1], reverse=True)
        return sorted_zippo

    def update_solution(sol):
        out_zippo, nbr_zippo = get_outer_fields(sol)
        out_zippo = sort_neighbors(out_zippo)  # äußere Felder mit Anzahl an nicht-verbundenen Kanten
        nbr_zippo = sort_neighbors(nbr_zippo)
        return out_zippo, nbr_zippo

    def shuffle_equal_tiles(zippo):
        grouped = {u: list(v) for u, v in groupby(zippo, key=lambda x: x[1])}
        # Permutiere die Tupel innerhalb jeder Gruppe
        for u in grouped:
            random.shuffle(grouped[u])
        # Füge die permutierten Gruppen wieder zusammen, wobei die Reihenfolge der Gruppen beibehalten wird
        result = [item for sublist in grouped.values() for item in sublist]
        return result

    cand = copy.deepcopy(curr)  # Umkopieren, da sonst die current Lösung verändert wird
    n_tiles = len(cand[0])
    n_swaps = np.random.randint(0, n_tiles + 1)  # Anzahl der Vertauschungen
    standard = 0
    if morphing:  # Felder nach freien Nachbarn absteigend ordnen, dann Zufallszahl n_shifts ziehen, die ersten n_shift
        # Felder verwenden und verschieben, das neue Feld aus den nbrs (freien Feldern löschen), Feld 0 nicht shiften
        out_zip, nbr_zip = update_solution(cand)
        n_shifts = np.random.randint(0, len(out_zip))  # Anzahl der Verschiebungen von Steinen
        for k in range(n_shifts):  # die Listen dann updaten? mit get_neigbor und Vergleich mit nbr
            old_field = out_zip[k][0]  # Feld, welches aus der Lösung genommen und geändert wird
            old_index = cand[0].index(old_field)  # Index des alten Feldes in der Lösung
            # temp_sol = [sol[:old_index] + sol[old_index + 1:] for sol in cand]  # ohne altes Feld betrachten
            # _, temp_nbr_zip = update_solution(temp_sol)
            new_field = nbr_zip[k][0]  # temp_nbr_zip
            cand[0][old_index] = new_field  # Feld verändern
            out_zip, nbr_zip = update_solution(cand)
            [out_zip, nbr_zip] = [shuffle_equal_tiles(out_zip), shuffle_equal_tiles(nbr_zip)]
    if len(cand) == 3:
        cand.insert(0, [*range(n_tiles)])
        standard = 1
    if swap_and_rotate:
        n_rotations = n_swaps
    else:
        n_rotations = np.random.randint(0, n_tiles + 1)  # Anzahl der Rotationen
    swap_indices = random.sample([*range(0, n_tiles)], k=n_swaps)  # Indizes der zu vertauschenden Steine,
    # für Blume ([*range(0, 7)], k=n_swaps)
    swap_indices_permutation = np.random.permutation(swap_indices)
    swap_tiles_perm = [cand[1][k] for k in swap_indices_permutation]  # Permutation der betroffenen Steine
    rotations = np.random.choice(6, n_rotations)  # Rotationen der Steine festlegen
    if swap_and_rotate:
        rotation_indices = swap_indices
        for z in range(len(swap_indices)):
            if swap_indices[z] == swap_indices_permutation[z] and len(swap_indices) > 1:  # Falls Stein auf sich selbst
                # abgebildet wird, und mehr als 1 Stein vertauscht wird, wird dieser Stein nicht rotiert, sonst schon
                rotations[z] = 0
    else:
        rotation_indices = random.sample([*range(0, n_tiles)], k=n_rotations)  # Indizes der zu rotierenden Steine
    tiles_copy = copy.deepcopy(cand[2])
    for k, rot in enumerate(rotation_indices):
        cand[3][rot] = (cand[3][rot] + rotations[k]) % 6
    for j, swap in enumerate(swap_indices):
        cand[1][swap] = swap_tiles_perm[j]
        cand[2][swap] = tiles_copy[swap_indices_permutation[j]]
    # print(f"Anzahl der Vertauschungen/Rotationen: {n_swaps}, {n_rotations}")
    if standard:
        return cand[1:]
    return cand


def rotate_sol(sol, n_rotations=1):  # bei allg. Lsg.: Ringe um den Ursprung verwenden
    """
    Eine eingegebene Lösung wird um eine Position im UZS rotiert
    :param n_rotations: Anzahl der Rotationen, im UZS falls > 0, gegen UZS falls < 0, default 1
    :param sol: Lösung
    :return: rotierte Lösung
    """

    def shift_tiles(outer_tiles, offset: int):
        """
        :param outer_tiles: eine Liste mit den Nummern der Spielsteine
        :param offset: um wie viele Stellen werden die Steine von rechts nach links (vlnr für offset < 0) verschoben
        :return: die verschobenen Steine
        """
        return [outer_tiles[(i + offset) % 6] for i in range(6)]

    tile_list = [*range(1, 7)]
    sol_rot = copy.deepcopy(sol)
    permutation = shift_tiles(tile_list, n_rotations)
    for j in range(1, 7):  # äußere Steine werden n_rotations Positionen in der Systematik weitergeschoben
        sol_rot[0][j] = sol[0][permutation[j - 1]]  # [(j + 4) % 6 + 1] gegen UZS
        sol_rot[1][j] = sol[1][permutation[j - 1]]  # [(j % 6) + 1] im UZS
        sol_rot[2][j] = sol[2][permutation[j - 1]]  # es muss noch rotiert werden
    for t in range(7):  # alle (auch mittleren) Steine um n_rotations Positionen im/gegen UZS rotieren
        sol_rot[2][t] = (sol_rot[2][t] + n_rotations) % 6
    return sol_rot


def d2b(decimal, leading_zero_digit=0):
    """
    Zahl im Dezimalsystem in Binär umwandeln, Möglichkeit, vorne Nullen
    anzuhängen, wird genutzt um später aus den 7 Steinen mit Vorder- und
    Rückseite alle Kombinationen zu erhalten (Vorderseite: 0, Rückseite:1)
    :param decimal: Zahl im Dezimalsystem
    :param leading_zero_digit: bis zu welcher binären Stelle soll die Ausgabe mit führenden Nullen erfolgen
    :return: Bitstring
    """
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


def get_coords_from_pos(pos):
    """
    Gibt die Koordinaten der Felder der Spielsteine in dem Hexagon-Koordinatensystem an (auch für weitere Steine mit
    Position 7 und größer
    :param pos: die Position des Spielsteins in der definierten Systematik (mit 0 startend in der Mitte, dann nach
                unten gehend gegen den UZS durchnummeriert
    :return: Koordinaten im Hexagon-KoSy
    """
    if pos == 0:
        return np.array([0, 0])

    def step(sd, stepsize):
        crds = np.array([0, 0])
        if sd == 0:
            crds += np.array([stepsize, 0])
        elif sd == 1:
            crds += np.array([stepsize, stepsize])
        elif sd == 2:
            crds += np.array([0, stepsize])
        elif sd == 3:
            crds += np.array([-stepsize, 0])
        elif sd == 4:
            crds += np.array([-stepsize, - stepsize])
        elif sd == 5:
            crds += np.array([0, -stepsize])
        return crds

    ring = 0
    total_positions = 0
    while total_positions < pos:
        ring += 1
        total_positions += 6 * ring
    pos_in_ring = pos - (total_positions - 6 * ring) - 1
    side_length = ring
    coords = np.array([-ring, -ring])
    side = pos_in_ring // side_length
    offset = pos_in_ring % side_length
    side_counter = 0
    while side_counter != side:
        coords += step(side_counter, side_length)
        side_counter += 1
    coords += step(side, offset)
    return coords


def get_pos_from_coords(coords):
    """
    Aus der Position auf dem Spielfeld die Koordinaten im Hexa-System erhalten
    :param coords: Koordinaten im Hexagon-KoSy
    :return: die Position des Spielsteins in der definierten Systematik (mit 0 startend in der Mitte, dann nach
                unten gehend gegen den UZS durchnummeriert
    """
    start_coords = np.array([0, 0])
    if np.array_equal(coords, start_coords):
        return 0
    pos = 1
    x, y = coords
    if x == y and y < 0:
        return pos + (abs(x) * (abs(x) - 1) * 3)
        # coords += np.array([1, 1])
        # x, y = [coords[i] for i in range(2)]
        # pos += 1
    while not np.array_equal(coords, start_coords):
        moving_dir = np.array([0, 0])
        if x == 0:
            # if y > 0:
            moving_dir = np.array([1, 0]) * np.sign(y)
            # elif y < 0:
            #     moving_dir = np.array([-1, 0])
        elif y == 0:
            # if x > 0:
            moving_dir = np.array([-1, -1]) * np.sign(x)
            # elif x < 0:
            #     moving_dir = np.array([1, 1])
        elif x == y:
            return pos + (abs(x) * (abs(x) - 1) * 3) + (3 * abs(x))
            # moving_dir = np.array([0, np.sign(x) * (-1)])
        elif x < 0 < y or x > 0 > y:
            moving_dir = np.array([1, 1]) * np.sign(y)
        elif np.sign(x) == np.sign(y) and x != y:
            if abs(y) > abs(x):
                moving_dir = np.array([np.sign(x) * 1, 0])
            else:
                moving_dir = np.array([0, np.sign(x) * (-1)])
        coords += moving_dir
        x, y = coords
        pos += 1
        if x == y and x < 0:
            return pos + (abs(x) * (abs(x) - 1) * 3)
            # if x == y and x == -1:
            #     pos += 1
            # coords += np.array([1, 1])
            # x, y = [coords[i] for i in range(2)]
    return pos


def get_neighbor(field_number, edge):
    """
    Die Position bzw. Feld-Nummer eines an der angegebenen Kante benachbarten Feldes ausgeben
    :param field_number: das betrachtete Feld
    :param edge: die Kante des betrachteten Feldes, welche eine gemeinsame Kante mit den Nachbarn ist
    :return: die Postion des Nachbarn in der definierten Systematik
    """
    # t1 = time.perf_counter()
    tile_coords = get_coords_from_pos(field_number)
    # t2 = time.perf_counter()
    direction_map = {
        0: np.array([-1, -1]),
        1: np.array([0, -1]),
        2: np.array([1, 0]),
        3: np.array([1, 1]),
        4: np.array([0, 1]),
        5: np.array([-1, 0])
    }
    target_coords = tile_coords + direction_map[edge]
    nbr = get_pos_from_coords(target_coords)
    # t3 = time.perf_counter()
    # print(f"pos2coords: {t2 - t1}, coords2pos: {t3 - t2}")
    return nbr


def getCoordinates(pos):
    """
    Koordinaten von dem System der Sechseckmittelpunkte umrechnen in kartesische Koordinaten,
    die dann geplottet werden
    :param pos: Position im Hexagon-KoSy der Systematik folgend
    :return: kartesische Koordinaten
    """
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


def draw_sol(solution):
    """
    Die Lösung plotten, jedes Tile in der Lösung wird betrachtet und einzeln
    geplottet nach der Orientierung und den Farbcodes
    :param solution: Lösung, welche geplottet werden soll
    :return: Matplotlib-Plot
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    # Größe und Position der Steine festlegen
    tile_size = 0.55

    # Für jeden Stein in der Lösung
    for index, tile in enumerate(solution[1]):
        tile_orientation = solution[2][index]  # HIER WEITER ANPASSEN
        # Zeichne die Kanten des Steins
        draw_hexagon(ax, index, tile_orientation, tile, tile_size)

    ax.axis('equal')
    ax.axis('off')
    plt.title(f"{datetime.datetime.now().time()}, {objective(solution)} Fehler")
    plt.show()


def draw_sol_gen(solution):
    """
    Die allgemeine Lösung plotten, jedes Tile in der Lösung wird betrachtet und einzeln
    geplottet nach der Orientierung und den Farbcodes
    :param solution: Lösung, welche geplottet werden soll
    :return: Matplotlib-Plot
    """
    plot_size = np.round(np.log2(len(solution[0])) + 3)  # Die Anzahl der hinzukommmenden Steine pro Umlauf ist
    # ca. die Anzahl aller vorherigen Steine
    fig, ax = plt.subplots(figsize=(8 / 6 * plot_size, plot_size))
    # Größe und Position der Steine festlegen
    tile_size = 0.55
    # Für jeden Stein in der Lösung
    for index, tile in enumerate(solution[2]):
        tile_pos = solution[0][index]
        tile_orientation = solution[3][index]
        # Zeichne die Kanten des Steins
        draw_hexagon(ax, tile_pos, tile_orientation, tile, tile_size)
    ax.axis('equal')
    ax.axis('off')
    plt.title(f"{datetime.datetime.now().time()}, {obj_gen(solution)} Fehler")
    plt.show()


# def draw_hexagon(ax, position, orientation, tile, size=0.55):
#     """
#     Hexagon in den Plot einzeichnen
#     :param ax: Matplotlib-Objekt
#     :param position: Position laut Systematik
#     :param orientation: Rotation des Steins auf dem Feld
#     :param tile: Codierung des Steins
#     :param size: Größe des Sechsecks
#     :return: Matplotlib-Plot
#     """
#     colors = {'1': 'blue', '2': 'yellow', '3': 'red', '4': 'green'}
#     x, y = getCoordinates(position)
#
#     angles = np.arange(- 2 / 3 * np.pi, 4 / 3 * np.pi, np.pi / 3)
#     for edge in range(0, 6):
#         x_start = x + size * np.cos(angles[edge])
#         y_start = y + size * np.sin(angles[edge])
#         x_end = x + size * np.cos(angles[(edge + 1) % 6])
#         y_end = y + size * np.sin(angles[(edge + 1) % 6])
#
#         color = colors[str(getColor(tile, edge, orientation))]
#
#         ax.plot([x_start, x_end], [y_start, y_end], color=color, linewidth=3)


# def draw_hexagon(ax, position, orientation, tile, size=0.55):
#     """
#     Hexagon in den Plot einzeichnen
#     :param ax: Matplotlib-Objekt
#     :param position: Position laut Systematik
#     :param orientation: Rotation des Steins auf dem Feld
#     :param tile: Codierung des Steins
#     :param size: Größe des Sechsecks
#     :return: Matplotlib-Plot
#     """
#
#     def find_pairs(tl):
#         """Die Kantenpaare einer Farbe finden und ausgeben"""
#         prs = []
#         for k in range(1, 5):
#             if str(k) in tl:
#                 pair = [i for i, col in enumerate(tl) if col == str(k)]
#                 pair.append(k)
#                 prs.append(pair)
#         return prs
#
#     def get_angle(tile, color):
#         """Den Winkel des Bogens zwischen den beiden Kanten einer Farbe ausgeben"""
#         temp, _ = get_dist(tile, color)
#         return np.deg2rad(temp * 60)
#
#     def draw_semicircle(ax, x1, y1, x2, y2, sangle, eangle, color='black', lw=1):
#         """
#         draw a semicircle between the points x1,y1 and x2,y2
#         the semicircle is drawn to the left of the segment
#         """
#         ax = ax or plt.gca()
#         # startangle = float(np.arctan2(y2 - y1, x2 - x1))
#         diameter = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)  # Euclidian distance
#         ax.add_patch(Arc(((x1 + x2) / 2, (y1 + y2) / 2), diameter, diameter, theta1=sangle, theta2=eangle,
#                          edgecolor=color, lw=lw))
#
#     colors = {'1': 'blue', '2': 'yellow', '3': 'red', '4': 'green'}
#     x, y = getCoordinates(position)
#     angles = np.arange(- 2 / 3 * np.pi, 4 / 3 * np.pi, np.pi / 3)
#     pairs = find_pairs(tile)
#     hexagon = np.array([[x + size * np.cos(angles[edge]), y + size * np.sin(angles[edge])] for edge in range(6)])
#     edge_angles = [float(np.arctan2(hexagon[(k + 1) % 6][1] - hexagon[k][1],
#                                     hexagon[(k + 1) % 6][0] - hexagon[1][0])) for k in range(6)]
#     centers = [hexagon[k] + ((hexagon[(k + 1) % 6] - hexagon[k]) / 2) for k in range(6)]
#     for edge in range(6):
#         # x_start = x + size * np.cos(angles[edge])
#         # y_start = y + size * np.sin(angles[edge])
#         # x_end = x + size * np.cos(angles[(edge + 1) % 6])
#         # y_end = y + size * np.sin(angles[(edge + 1) % 6])
#         color = colors[str(getColor(tile, edge, orientation))]
#         # color = "black"
#         # ax.plot([x_start, x_end], [y_start, y_end], color=color, linewidth=3)
#         ax.plot([hexagon[edge][0], hexagon[(edge + 1) % 6][0]], [hexagon[edge][1], hexagon[(edge + 1) % 6][1]],
#                 color=color, linewidth=3)
#         if edge == 0:
#             ax.plot([centers[edge][0], centers[(edge + 1) % 6][0]], [centers[edge][1], centers[(edge + 1) % 6][1]],
#                     color=color, marker="v")
#     for edge_pair in pairs:
#         arc_color = colors[str(getColor(tile, edge_pair[0], orientation))]
#         arc_angle = get_angle(tile, edge_pair[2])
#         startangle = edge_angles[(edge_pair[0] + orientation) % 6]
#         endangle = startangle + arc_angle
#         draw_semicircle(ax, x1=centers[edge_pair[0]][0], y1=centers[edge_pair[0]][1],
#                         x2=centers[edge_pair[1]][0], y2=centers[edge_pair[1]][1],
#                         sangle=startangle, eangle=endangle, color=arc_color, lw=5)

def draw_hexagon(ax, position, orientation, tile, size=0.55):
    """
    Hexagon in den Plot einzeichnen
    :param ax: Matplotlib-Objekt
    :param position: Position laut Systematik
    :param orientation: Rotation des Steins auf dem Feld
    :param tile: Codierung des Steins
    :param size: Größe des Sechsecks
    :return: Matplotlib-Plot
    """

    def find_pairs(tl):
        """
        Die Kantenpaare einer Farbe finden und ausgeben
        :param tl: Tile
        :return: [Kante 1, Kante 2, Farbe: int, Distanz (1,2,3)]
        """
        prs = []
        for k in range(1, 5):
            if str(k) in tl:
                pair = [i for i, col in enumerate(tl) if col == str(k)]
                dist, _ = get_dist(tl, k)
                pair.append(k)
                pair.append(dist)
                prs.append(pair)
        return prs

    def get_middle_edge(edge1, edge2):
        """
        Gibt die mittlere Kante zwischen zwei Kanten zurück, die eine Kante voneinander entfernt sind.
        :param edge1: Erste Kante (int zwischen 0 und 5)
        :param edge2: Zweite Kante (int zwischen 0 und 5)
        :return: Mittlere Kante (int)
        """
        # Sortiere die Kanten in aufsteigender Reihenfolge
        edge1, edge2 = sorted([edge1, edge2])
        # Überprüfen, ob die Kanten eine Kante voneinander entfernt sind
        if (edge2 - edge1) == 2:
            return (edge1 + 1) % 6
        elif (edge2 - edge1) == 4:
            return (edge2 + 1) % 6
        else:
            raise ValueError("Die Kanten sind nicht eine Kante voneinander entfernt.")

    colors = {'1': 'blue', '2': 'yellow', '3': 'red', '4': 'green'}
    x, y = getCoordinates(position)
    angles = np.arange(- 2 / 3 * np.pi, 4 / 3 * np.pi, np.pi / 3)
    pairs = find_pairs(tile)
    hexagon = np.array([[x + size * np.cos(angles[edge]), y + size * np.sin(angles[edge])] for edge in range(6)])
    centers = [hexagon[k] + ((hexagon[(k + 1) % 6] - hexagon[k]) / 2) for k in range(6)]
    # Zeichne das Hexagon mit schwarzer Füllung
    hex_patch = Polygon(hexagon, closed=True, fill=True, edgecolor='black', facecolor='black')
    ax.add_patch(hex_patch)
    # for edge in range(6):
    #     # color = colors[str(getColor(tile, edge, orientation))]
    #     color = "black"
    #     ax.plot([hexagon[edge][0], hexagon[(edge + 1) % 6][0]], [hexagon[edge][1], hexagon[(edge + 1) % 6][1]],
    #             color=color, linewidth=3)
    for edge_pair in pairs:
        start = centers[(edge_pair[0] - orientation) % 6]
        end = centers[(edge_pair[1] - orientation) % 6]  # - orientation???
        color = colors[str(edge_pair[2])]
        if edge_pair[3] == 3:  # Distanz 3, gerade Verbindung
            dist = np.linalg.norm(end - start)
            if dist > size:
                scale_factor = size / dist + 0.29
                start = start + (end - start) * (1 - scale_factor) / 2
                end = end - (end - start) * (1 - scale_factor) / 2
            ax.plot([start[0], end[0]], [start[1], end[1]], color=color, lw=10)
            continue
        else:
            if edge_pair[3] == 1:  # aneinanderliegende Kanten, Distanz 1, Mittelpunkt des Kreises ist die Ecke des Hexagon
                center = hexagon[(edge_pair[1] - orientation) % 6]
            else:
                nbg_edge = (get_middle_edge(edge_pair[0], edge_pair[1]) - orientation) % 6
                # die Kante zwischen den beiden gleichgefärbten  # (edge_pair[0] + edge_pair[1]) + 4 % 6
                nbr = get_neighbor(position, nbg_edge)
                center = getCoordinates(nbr)
            radius = np.sqrt((start[0] - center[0])**2 + (start[1] - center[1])**2)
            angle1 = np.degrees(np.arctan2(start[1] - center[1], start[0] - center[0]))
            angle2 = np.degrees(np.arctan2(end[1] - center[1], end[0] - center[0]))
            # Stelle sicher, dass der Winkel im Bereich [0, 360) ist
            angle1 = angle1 % 360
            angle2 = angle2 % 360
            # Berechne die Start- und Endwinkel des Kreissegments
            start_angle = min(angle1, angle2)
            end_angle = max(angle1, angle2)
            # Berechne die Bogenlänge und stelle sicher, dass der Bogen der kürzere ist
            if end_angle - start_angle > 180:
                start_angle, end_angle = end_angle, start_angle
                start_angle += 360
            # Zeichne das Kreissegment
            arc = Arc(center, 2 * radius, 2 * radius, theta1=start_angle, theta2=end_angle, edgecolor=color, lw=10)
            ax.add_patch(arc)


def get_puzzles(tile_combo):
    """
    Von einer Variante der 7 Steine mit Vorder- und Rückseite die 2^7 = 128 Möglichkeiten,
    die Seiten der Steine zu kombinieren ausgeben als Vektoren mit den Steinenummern
    :param tile_combo: Array mit Dimensionen [2, 7], tiles_front_back
    :return: alle Steinkombinationen aus Vorder- und Rückseiten, die mit dieser "Verklebung" möglich sind
    """
    output_puzzles = []
    for i in range(128):
        logical = d2b(i, 7)
        output_puzzles.append([tile_combo[int(logical[k])][k] for k in range(7)])
    return output_puzzles


def getColor(tile, edge, orientation):
    """
    Die Farbe einer Kante eines Steins ausgeben als int mit definierter Codierung
    :param tile: Codierung des Steins
    :param edge: Kante des Steins
    :param orientation: Rotation des Steins
    :return: Farbcode
    """
    return int(tile[(edge + orientation) % 6])


def gen_random_sol(all_tiles, n_tiles=7, kangaroo=1, sample=0, ascending=0, randomness=0, standard=0):
    """
    Funktion für die zufällige Generierung einer allgemeinen Lösung mit variabler Anzahl an Steinen
    :param all_tiles: Codierung aller 56 Steine
    :param n_tiles: Anzahl der verwendeten Steine
    :param kangaroo: Falls kangaroo=1 (für n_tiles=7), werden nur mit der Känguru-Version legbare Lösungen gezogen
    :param sample: Falls sample=1 und n_tiles > 14 werden die n_tiles - 14 Steine zufällig aus allen übrigen 42 Steinen
                   gezogen, sample=1 und n_tiles < 15 entspricht 14C(n_tiles)
    :param ascending: Falls ascending=1, werden die ersten n_tiles Spielsteine aus dem all_tiles array entnommen
    :param randomness: Falls randomness=1, werden alle Steine komplett zufällig aus den 56 gezogen
    :param standard: Lösung ohne Felder-array ausgeben, falls standard=1
    :return: array mit zufällig generierter Lösung
    """
    sol_arr = [[] * n_tiles for _ in range(4)]

    def get_tiles(num, kang, asc, rnd, smpl):
        if num == 7:
            if kang:
                return [(i * 2) + random.randint(0, 1) for i in range(7)]
        elif num > 14:
            if smpl:
                return [*range(14)] + random.sample([*range(14, 56)], k=num - 14)
        if smpl:
            return random.sample([*range(0, 14)], k=num)
        if asc:
            return [*range(num)]
        if rnd:
            return random.sample([*range(0, 56)], k=num)
        return random.sample([*range(0, 56)], k=num)

    tiles_vec = get_tiles(num=n_tiles, kang=kangaroo, smpl=sample, asc=ascending, rnd=randomness)
    sol_arr[0] = [*range(n_tiles)]  # die Spielfelder werden nach der Systematik aufsteigend verwendet, für n_tiles=19
    # werden zwei Umläufe um die Mitte erreicht
    sol_arr[1] = tiles_vec
    sol_arr[2] = [all_tiles[i] for i in tiles_vec]
    sol_arr[3] = [int(random.uniform(0, 6)) for _ in range(n_tiles)]
    if standard:
        return sol_arr[1:]
    return sol_arr


def gen_start_sol(combo, all_tiles, standard=0):
    """
    Eine Startlösung generieren ausgehend von einer beliebigen Kombination der Spielsteine
    :param standard: Lösung ohne Einträge der Felder generieren
    :param combo: array mit Steine-Nummern
    :param all_tiles: array mit Codierung aller Steine
    :return: array mit Startlösung
    """
    sol = [[] * len(combo) for _ in range(4)]
    sol[0] = [*range(0, len(combo))]
    sol[1] = list(np.random.permutation(combo))
    sol[2] = [all_tiles[k] for k in sol[1]]
    sol[3] = [int(random.uniform(0, 6)) for _ in range(len(combo))]
    if standard:
        return sol[1:]
    return sol


def objective(sol):
    """
    Fitnessfunktion, welche die Anzahl der Fehler, also nicht übereinstimmender Farben an der Kanten
    der Steine zählt
    :param sol: Lösung
    :return: Ausgabe
    """
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


def obj_gen(sol):  # die Kompaktheit der Lösung eingehen lassen, Ringe um 0 mit aufsteigenden Straftermen
    """
    Objective-Funktion für verallgemeinerte Lösungen (nicht nur für Blumen), gibt die Anzahl der Fehler an
    (Vorgehen: für jedes Tile die 6 Nachbarn betrachten und die Fehler zählen), langsamer als im Blumen-Fall
    :param sol: Lösung
    :return: Fehleranzahl
    """
    # t1 = time.perf_counter()
    mismatches = 0
    # Caches für Positionen und Farben
    tile_positions = {sol[0][index]: index for index in range(len(sol[0]))}
    tile_colors = [
        [getColor(sol[2][index], edge, sol[3][index]) for edge in range(6)]
        for index in range(len(sol[0]))
    ]
    visited_edges = set()  # Set für besuchte Kantenpaare
    # t2 = time.perf_counter()
    # Fehler zählen
    for index in range(len(sol[0])):
        for edge in range(6):
            if (index, edge) not in visited_edges:
                # t3 = time.perf_counter()
                neighbor_field = get_neighbor(sol[0][index], edge)
                # t4 = time.perf_counter()
                if neighbor_field in tile_positions:
                    neighbor_index = tile_positions[neighbor_field]
                    if tile_colors[index][edge] != tile_colors[neighbor_index][(edge + 3) % 6]:
                        mismatches += 1
                    visited_edges.add((index, edge))
                    visited_edges.add((neighbor_index, (edge + 3) % 6))
                # t5 = time.perf_counter()
                # print(f"init: {t2 - t1}, neigh: {t4 - t3}, rest_loop: {t5 - t4}")
    return mismatches


def get_outer_fields(sol):  # fehlt: Berechnung Anzahl Berührpunkte der angrenzenden Felder mit der aktuellen Lösung
    outer_fields = []  # Aktualisierung nach jedem Shift?
    nbr_fields = []
    outer_open_edges = []
    nbr_closed_edges = []
    out_zip = list(zip(outer_fields, outer_open_edges))
    nbr_zip = list(zip(nbr_fields, nbr_closed_edges))
    for field in sol[0]:
        open_edges_counter = 0
        for edge in range(6):
            nbr = get_neighbor(field, edge)
            if nbr not in sol[0]:
                if field not in outer_fields:
                    outer_fields.append(field)
                if nbr not in nbr_fields:
                    nbr_fields.append(nbr)
                    nbr_closed_edges.append(1)
                else:
                    index = nbr_fields.index(nbr)
                    nbr_closed_edges[index] += 1
                # break
                open_edges_counter += 1
        outer_open_edges.append(open_edges_counter)
        outer_open_edges = [field for field in outer_open_edges if field > 0]
        out_zip = list(zip(outer_fields, outer_open_edges))
        nbr_zip = list(zip(nbr_fields, nbr_closed_edges))
    return out_zip, nbr_zip


def plot_p_over_steps(data):
    """
    Die Annahmewahrscheinlichkeit für eine schlechtere Lösung im Verlauf des Algorithmus plotten
    :param data: array mit Daten
    :return: Plot
    """
    colors = {'0': 'blue', '1': 'green', '2': 'red', '3': 'cyan', '4': 'magenta', '5': 'yellow',
              '6': 'orange', '7': 'lime', '8': 'indigo', '9': 'pink', '10': 'skyblue', '11': 'salmon',
              '12': 'brown'}  # Farben automatisch anpassen ja nach max(Fehler) in den Daten, Regenbogenverlauf? Warum Code mies langsam?
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


def plot_val_over_steps(data):
    """
    Fehleranzahl der besten Lösung über die Iterationen plotten (best_val)
    :param data: array mit Daten
    :return: Plot
    """
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


def get_temp(temp, step):
    """
    Temperatur berechnen des Systems abhängig von Ausgangstemperatur und Anzahl der getätigten Schritte (= Zeit)
    :param temp: Eingangstemperatur
    :param step: Schrittanzahl
    :return: Ausgangstemperatur
    """
    t = temp / (0.2 * float(step + 1))
    return t


def calc_acceptance(diff, temp):
    """
    Wahrscheinlichkeit, dass der aktuelle Kandidat als current Lösung übernommen wird, Berechnung auf Grundlage der
    Bewertung durch die objective-Funktion und die Temperatur (geringere Temperatur entspricht geringerer Wk, dass
    ein schlechterer Kandidat übernommen wird
    :param diff: Differenz zwischen candidate und current Lösungen
    :param temp: Temperatur
    :return: Wahrscheinlichkeit p, ist 1, falls diff = 0, also wird bei keiner Verbesserung trotzdem zu dem neuen
             Kandidaten gewechselt
    """
    prob = np.exp(- diff / temp)
    return prob


# Abbruchkriterium, wenn 0 Fehler
# evtl bei 1/2 Fehler neuen Kandidaten berechnen durch Vertauschung von 2/3 Steinen?
# Mit dieser Funktion wird der simulated annealing Algorithmus durchgeführt, Eingangsparameter sind eine Startlösung,
# die Anzahl der Schritte und eine Anfangstemperatur, ausgegeben wird der beste Kandidat
def simulated_annealing(init_sol, n_iter, temp, param=1.0, write_data=1):
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
    if objective(init_sol) == 0:
        return [init_sol, objective(init_sol), [[0] * n_iter for _ in range(10)]]
    temperatures = [get_temp(temp, k) for k in range(n_iter)]
    data = []
    if write_data:
        data = [[0] * n_iter for _ in range(10)]
        data[0] = [*range(n_iter)]
        data[1] = temperatures
    best_sol = copy.deepcopy(init_sol)  # beste Lösung, wird am Schluss ausgegeben
    best_val = objective(best_sol)
    curr_sol, curr_val = best_sol, best_val
    for i in range(n_iter):
        t1 = time.perf_counter()
        if best_val == 0:
            break
        cand_sol = gen_cand_morph(curr_sol, 1, 0)
        t2 = time.perf_counter()
        cand_val = objective(cand_sol)
        t3 = time.perf_counter()
        diff = cand_val - curr_val
        # print("Iteration #{i}, Differenz cand - curr: {diff}")
        if cand_val - best_val < 0:
            best_sol = cand_sol
            best_val = cand_val
        t = temperatures[i]
        if diff < 0:
            p = 1
        else:
            p = calc_acceptance(param * diff, t)  # multiplikativer Parameter Optimierung? Tradeoff wenige Schritte,
            # aber seltenes Lösungsfinden
        if np.random.rand() < p:
            # if diff > 0:
            #     print("WORSE SOLUTION ACCEPTED")
            curr_sol, curr_val = cand_sol, cand_val
        if write_data:
            data[2][i] = p
            data[3][i] = best_val
            data[4][i] = best_sol
            data[5][i] = curr_val
            data[6][i] = curr_sol
            data[7][i] = cand_val
            data[8][i] = cand_sol
            data[9][i] = diff
        t4 = time.perf_counter()
        # print(f"SIM: gen_cand: {t2 - t1}, obj_gen: {t3 - t2}, elapsed: {t4 - t1}")
    return [best_sol, best_val, data]


def sim_ann_gen(init_sol, n_iter: int, temp: int, param=5.0, morphing=0, write_data=1):
    """
    Simulated annealing Algorithmus
    :param init_sol: Startlösung
    :param n_iter: Anzahl der Schritte im Algorithmus
    :param temp: Starttemperatur
    :param param: Abkühlungsparameter, sorgt dafür, dass schneller nur noch bessere Lösungen akzeptiert werden
    :param morphing: Soll der Algorithmus versuchen, die Form der Lösung zu verändern?
    :param write_data: Sollen Daten geschrieben werden?
    :return: Data-Array mit 10 Zeilen
            [0] Anzahl der Schritte
            [1] Temperatur (temp)
            [2] Annahmewahrscheinlichkeit einer schlechteren Lösung (p)
            [3] Fehleranzahl der besten Lösung (best_val)
            [4] Beste Lösung (best_sol)
            [5] Fehleranzahl der aktuellen Lösung (curr_val)
            [6] Aktuelle Lösung (curr_sol)
            [7] Fehleranzahl des aktuellen Kandidaten (cand_val)
            [8] Kandidat (cand_sol)
            [9] Differenz (diff = cand_val - curr_val)
    """
    if obj_gen(init_sol) == 0:
        return [init_sol, obj_gen(init_sol), [[0] * n_iter for _ in range(10)]]
    temperatures = [get_temp(temp, k) for k in range(n_iter)]
    data = []
    if write_data:
        data = [[0] * n_iter for _ in range(10)]
        data[0] = [*range(n_iter)]
        data[1] = temperatures
    best_sol = copy.deepcopy(init_sol)  # beste Lösung, wird am Schluss ausgegeben
    best_val = obj_gen(best_sol)
    curr_sol, curr_val = best_sol, best_val
    for i in range(n_iter):
        # t1 = time.perf_counter()
        if best_val == 0:
            break
        cand_sol = gen_cand_morph(curr_sol, 1, morphing)
        # t2 = time.perf_counter()
        cand_val = obj_gen(cand_sol)
        # t3 = time.perf_counter()
        diff = cand_val - curr_val
        print(f"Iteration #{i}, Differenz cand - curr: {diff}")
        if cand_val - best_val < 0:
            best_sol = cand_sol
            best_val = cand_val
        t = temperatures[i]
        if diff < 0:
            p = 1
        else:
            p = calc_acceptance(param * diff, t)  # multiplikativer Parameter Optimierung? Tradeoff wenige Schritte,
            # aber seltenes Lösungsfinden
        if np.random.rand() < p:
            curr_sol, curr_val = cand_sol, cand_val
        if write_data:
            data[2][i] = p
            data[3][i] = best_val
            data[4][i] = best_sol
            data[5][i] = curr_val
            data[6][i] = curr_sol
            data[7][i] = cand_val
            data[8][i] = cand_sol
            data[9][i] = diff
        # t4 = time.perf_counter()
        # print(f"SIM-G: gen_cand: {t2 - t1}, obj_gen: {t3 - t2}, elapsed: {t4 - t1}")
    return [best_sol, best_val, data]


def random_sol_mean(n_gens, all_tiles):
    """
    Zum Vergleich werden n_gens zufällige Lösungen generiert, und die beste Fehleranzahl ausgegeben
    :param n_gens: Anzahl der Generierungen einer zufälligen Lösung
    :param all_tiles: Codierung aller Spielsteine
    :return: Print
    """
    evaluations_sum = 0
    best = 100
    for k in range(n_gens):
        sol = gen_random_sol(all_tiles, n_tiles=7, kangaroo=0, sample=1, ascending=0, randomness=0, standard=1)
        sol_eval = objective(sol)
        if sol_eval < best:
            best = sol_eval
        evaluations_sum += sol_eval
    result = evaluations_sum / n_gens
    print(f"Durchschnittsfehleranzahl bei zufälliger Generierung von {n_gens} Lösungen: {result}")
    print(f"Beste Fehleranzahl bei zufälliger Generierung von {n_gens} Lösungen: {best}")


def print_best_sols(data):
    """
    Gibt die Kandidaten auf dem Weg zur Lösung aus (die ersten mit einer geringeren neuen Fehleranzahl)
    :param data: array mit Daten aus dem Algorithmus
    :return: Print-Ausgabe
    """
    visited = []
    for k in range(len(data[4])):
        if data[4][k] not in visited:
            visited.append(data[4][k])
            print(f"Iteration: {k} \n candidate: {data[4][k]}")


def find_param(sol, steps, temp, lim_low, lim_up, stepsize, n_runs, all_tiles):
    """
    Den Parameter, der bestimmt, wie schnell die Annahmewahrscheinlichkeit für schlechtere Lösungen sinkt
    versuchen zu optimieren
    :param sol: Eine beliebige Lösung
    :param steps: Schritte Alg.
    :param temp: Temp. Alg.
    :param lim_low: untere Grenze des Parameters
    :param lim_up: obere Grenze
    :param stepsize: Schrittweite des Parameters
    :param n_runs: Anzahl Durchläufe pro Parameter-Kandidat
    :param all_tiles: Codierung aller Spielsteine
    :return: array mit Ergebnissen, kann geplottet werden
    """
    params = np.arange(lim_low, lim_up, stepsize)
    results = [[0] * len(params) for _ in range(3)]
    for index, param in enumerate(params):
        sol_found = 0
        sum_steps = 0
        for k in range(n_runs):
            sol = gen_random_sol(all_tiles, n_tiles=7, kangaroo=0, sample=1, ascending=0, randomness=0, standard=1)
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


def solve_flowers(puzzles, all_tiles, n_iter, temp, param=1.0, write_file=0, filename="solutions.txt"):
    """
    Versucht alle Blumenpuzzles zu lösen (eine Lösung zu finden)
    :param puzzles: alle 3432 möglichen Blumenpuzzles
    :param all_tiles: die Codierung aller 56 Steine
    :param n_iter: Schrittanzahl
    :param temp: Temp. Alg.
    :param param: Ann. Wk. Alg.
    :param write_file: boolean Lösungen in .txt schreiben
    :param filename: Textdateiname
    :return: array mit Lösungen
    """
    results = [[0] * len(puzzles) for _ in range(4)]
    for index, puzzle in enumerate(puzzles):
        attempts = 0
        opt_val = 1
        opt_sol = []
        datastream = []
        starting_sol = gen_start_sol(list(puzzle), all_tiles, 1)
        while opt_val > 0 and attempts < 10:
            opt_sol, opt_val, datastream = simulated_annealing(starting_sol, n_iter, temp, param)
            attempts += 1
        results[0][index] = opt_sol  # Optimallösung
        results[1][index] = opt_val  # bester Fehlerwert
        if opt_val == 0:
            results[2][index] = datastream[3].index(0)  # Anzahl Schritte bis zur Lösung, falls erfolgreich
        else:
            results[2][index] = -1
        results[3][index] = attempts
        print(index)
    results[0] = standardize_sols(results[0])
    if write_file:
        with open(filename, 'w') as file:
            # file.write("Lösungen für 3432 Puzzles\n\n")
            for k in range(len(results[0])):
                line = str(results[0][k])
                file.writelines(line)
                file.writelines("\n")
    return results


def plot_flower_results(res):
    """
    Plottet Anzahl der Schritte bis zum Finden der Lösung aller Puzzles
    :param res: Lösung
    :return:
    """
    plt.scatter([*range(0, len(res[0]))], res[2])
    plt.xlabel('Puzzle No.')
    plt.ylabel('# of steps if successful')
    plt.ylim(0, max(res[2]))
    # plt.legend()
    plt.title(datetime.datetime.now().time())
    plt.show()


def plot_flower_attempts(res):
    """
    Plottet für jedes Puzzle die Anzahl der Versuche bis zum Finden einer Lösung
    :param res: Lösung
    :return:
    """
    plt.plot([*range(0, len(res[0]))], res[3])
    plt.xlabel('Puzzle No.')
    plt.ylabel('# of attempts to solution')
    plt.ylim(1, max(res[3]))
    # plt.legend()
    plt.title(datetime.datetime.now().time())
    plt.show()


def find_all_flower_sols(puzzle, attempts, all_tiles, n_iter, temp, param=1.0, write_file=0, filename=None):
    """
    Findet so viele verschiedene Lösungen eines Blumenpuzzles wie möglich
    :param puzzle: Steinnummern, welche das Puzzle definieren, als array
    :param attempts: Anzahl der Durchläufe
    :param all_tiles: array mit allen 56 Codierungen der Steine
    :param n_iter: Schrittanzahl Alg.
    :param temp: Temperatur Alg.
    :param param: Ann.wk. Alg.
    :param write_file: boolean, ob Lösungen in .txt geschrieben werden sollen
    :param filename: Name der Textdatei
    :return: array mit den gefundenen Lösungen
    """
    solutions = [[] for _ in range(2)]
    for k in range(attempts):
        print(k)
        starting_sol = gen_start_sol(list(puzzle), all_tiles, standard=1)
        opt_sol, opt_val, _ = simulated_annealing(starting_sol, n_iter, temp, param, write_data=0)
        if opt_val == 0:
            if len(solutions[0]) == 0:
                solutions[0].append(std(opt_sol))
                solutions[1].append(k + 1)
            else:
                if opt_sol not in solutions[0]:
                    solutions[0].append(std(opt_sol))
                    solutions[1].append(k + 1)
    # solutions[0] = standardize_sols(solutions[0])
    print(len(solutions[0]))
    print(solutions[1][-1])  # wann wurde die letzte Lösung gefunden
    if write_file:
        if filename is None:
            filename = '_'.join([str(sorted(puzzle)[k]) for k in range(len(puzzle))]) + \
                       f"__{attempts}_{len(solutions[0])}" + ".txt"  # '2_17_32_36_38_41_54__2000_17.txt'
        with open(filename, 'w') as file:
            # file.write(f"Lösungen für Puzzle {str(puzzle)}\n\n")
            for k in range(len(solutions[0])):
                line = str(solutions[0][k])
                file.writelines(line)
                file.writelines("\n")
    return solutions


def find_unsolvable(attempts_to_solve, attempts_to_search, n_iter, temp, param):
    """
    Versucht, ein Blumenpuzzle zu finden, welches auch nach 10 Anläufen nicht gelöst werden kann, Verdacht
    auf Unlösbarkeit?
    :param attempts_to_solve: Maximale Versuche, bis Unlösbarkeit angenommen wird und Funktion abbricht
    :param attempts_to_search: Anzahl an Kandidaten die auf Unlösbarkeit untersucht werden
    :param n_iter: Anzahl Schritte für den Algorithmus
    :param temp: Temperatur
    :param param: Annahme-Wk Parameter
    :return: "Unlösbares" Puzzle oder maximale Anzahl an Versuchen bis zur Lösung
    """
    max_attempts = 0
    for k in range(attempts_to_search):
        print(f"Attempt #{k}")
        sol = gen_random_sol(tiles_complete, n_tiles=7, kangaroo=0, sample=0, ascending=0, randomness=1)
        sol_val = obj_gen(sol)
        counter = 0
        while counter < attempts_to_solve and sol_val > 0:
            sol, sol_val, _ = sim_ann_gen(sol, n_iter, temp, param)
            counter += 1
            if counter > max_attempts:
                max_attempts = counter
        if counter == attempts_to_solve:
            print(sol)
            return
    print(f"Kein unlösbares Puzzles gefunden, meiste Versuche: {max_attempts}")


def elim_ident(filename):
    """
    Eliminiert doppelte Einträge in einer Textdatei.

    :param filename: Der Name der Textdatei.
    :return: Keine.
    """

    def parse_line(line):
        """Parses a single line of the text file into a structured solution."""
        elements = line.strip()[1:-1].split("], [")
        parsed_elements = [
            list(map(int, elements[0][1:].split(", "))),
            elements[1][1:-1].split("', '"),
            list(map(int, elements[2][0:-1].split(", ")))
        ]
        return parsed_elements

    with open(filename, 'r') as file:
        lines = file.readlines()

    sols = [parse_line(line) for line in lines]
    sols = standardize_sols(sols)
    sols_uniq = []
    for sol in sols:
        if sol not in sols_uniq:
            sols_uniq.append(sol)

    with open(filename, 'w') as file:
        for sol in sols_uniq:
            file.write(str(sol) + '\n')


def std(solution):
    """Lösung einheitlich formatieren, Orientierung des mittleren Steins ist 0"""
    temp_sol = copy.deepcopy(solution)
    return rotate_sol(temp_sol, n_rotations=6 - solution[-1][0])


def standardize_sols(solutions):
    """Lösungen so rotieren, dass die Orientierung des mittleren Steins (Nr. 0) gleich 0 ist"""
    std_sols = []
    for solution in solutions:
        std_sols.append(std(solution))
    return std_sols


def find_sol_rand(runs, all_tiles, puzzle=None, conf=0.95):
    """
    Versucht, von einem Puzzle eine Lösung durch pures Ausprobieren aller Möglichkeiten zu finden
    :param runs: Anzahl der Versuche (ein Versuch läuft bis eine Lösung gefunden wurde)
    :param all_tiles: Alle Spielsteine codiert
    :param puzzle: optional ein Puzzle welches gelöst werden soll
    :param conf: Konfidenz für die Angabe der Anzahl der Lösungen des Puzzles auf Grundlage der durchschnittlichen Anzahl
                 an benötigten Schritten bis zum Finden einer Lösung
    :return: Durchnittswert bis zum Finden einer Lösung, Generierungen bis Lösung pro Versuch als array
    """
    attempts = 0
    steps = []
    if puzzle is None:
        curr = gen_random_sol(tiles_complete, n_tiles=7, kangaroo=1, sample=0, ascending=0, randomness=0, standard=1)
    else:
        curr = gen_start_sol(puzzle, all_tiles, 1)
    for i in range(runs):
        run_steps = 0
        print(i)
        current_score = 1
        # curr = []
        while current_score > 0:
            curr = gen_start_sol(curr[0], all_tiles, 1)
            current_score = objective(curr)
            run_steps += 1
        print(curr)
        attempts += run_steps
        steps.append(run_steps)
    sol_complete = (math.factorial(7) * (6 ** 7) * 1 / 6)
    avg = attempts // runs
    std_var = np.std(steps)
    print(f"Anzahl Lsg. approx: {sol_complete // avg:.0f}, Konfidenzintervall auf {conf}:"
          f" +/- {(np.sqrt(1 - conf) * sol_complete) / std_var:.0f}")
    print(f"Mittelwert: {avg}")
    print(f"Standardabweichung: {std_var:.0f}")
    print(steps)
    return avg, steps


def random_pyramid(attempts, all_tiles):
    """
    Das unsolved Loop Puzzle durch zuföllige Generierungen versuchen zu lösen
    :param attempts: Versuche
    :param all_tiles: Steine
    :return: Plot
    """
    data = [[] for _ in range(2)]

    def gen_sol():
        sol = [[] for _ in range(4)]
        sol[0] = [0, 1, 2, 3, 10, 11, 12, 24, 25, 26, 27, 44, 45, 46, 47, 48, 69, 70, 71, 72, 73, 74, 100, 101,
                  102, 103, 104, 105, 106, 137, 138, 139, 140, 141, 142, 143, 144, 180, 181, 182, 183, 184,
                  185, 186, 187, 188, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238]
        sol[1] = list(np.random.permutation([*range(56)]))
        sol[2] = [all_tiles[i] for i in sol[1]]
        sol[3] = [int(random.uniform(0, 6)) for _ in range(56)]
        return sol

    opt_val = obj_gen(gen_sol())
    for k in range(attempts):
        cand = gen_sol()
        cand_val = obj_gen(cand)
        if cand_val < opt_val:
            opt_val = cand_val
        data[0].append(k)
        data[1].append(opt_val)
        if opt_val == 0:
            break
    plt.plot(data[0], data[1])
    plt.xlabel('Iteration')
    plt.ylabel('Objective')
    plt.ylim(0, max(data[1]))
    # plt.legend()
    plt.title(datetime.datetime.now().time())
    plt.show()
    return None


def flower_one_tile(all_tiles):
    vals = []
    for k in range(len(all_tiles)):
        print(f"Blume: {k}")
        sol = gen_start_sol([k for _ in range(7)], tiles_complete, 1)
        sol, val, _ = simulated_annealing(sol, 25000, 500, 5, 1)
        # draw_solution(sol)
        vals.append(val)
        print(val)
    for g in range(4):
        print(vals[g * 14:g * 14 + 14])
    print("\n")
    print(sum(vals))


def main():
    solution = [[1, 2, 5, 7, 9, 11, 12],
                ['212313', '131322', '121332', '112233', '113223', '221331', '113322'], [0, 2, 2, 3, 5, 4, 0]]
    # start_sol = random_sol_gen(tiles_complete, n_tiles=7, kangaroo=1, sample=0, ascending=0, randomness=0, standard=1)
    # start_sol = [[6, 4, 8, 11, 3, 1, 12], ['113232', '131223', '121323', '221331', '112332', '212313', '113322'],
    #              [2, 4, 3, 5, 2, 3, 5]]  # 1 Fehler
    start_sol = [[1, 3, 4, 6, 8, 11, 12], ['212313', '112332', '131223', '113232', '121323', '221331', '113322'],
                 [2, 2, 4, 5, 2, 4, 5]]
    rand_sol = [[32, 41, 54, 2, 17, 36, 38], ['131443', '141433', '114422', '131322', '332442', '141343', '131434'],
                [5, 5, 1, 3, 1, 4, 5]]  # 12 Fehler
    solx = [[0, 1, 2, 3, 4, 5, 6],
            [1, 2, 5, 7, 9, 11, 12],
            ['212313', '131322', '121332', '112233', '113223', '221331', '113322'], [0, 2, 2, 3, 5, 4, 0]]
    rsx = [[0, 1, 2, 3, 4, 5, 6], [32, 41, 54, 2, 17, 36, 38],
           ['131443', '141433', '114422', '131322', '332442', '141343', '131434'],
           [5, 5, 1, 3, 1, 4, 5]]
    unsol = [[0, 1, 2, 3, 4, 5, 6], [51, 41, 50, 47, 9, 40, 31],
             ['114224', '141433', '121424', '121442', '113223', '113344', '114334'], [3, 1, 0, 4, 0, 0, 3]]
    rand_sol_big = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
                    [37, 33, 30, 40, 48, 23, 1, 47, 15, 16, 4, 43, 29, 18, 50, 6, 24, 0, 39],
                    ['113443', '141334', '131344', '113344', '114242', '223443', '212313', '121442',
                     '242343', '224343', '131223', '212414', '313414', '223434', '121424', '113232',
                     '232434', '112323', '331441'],
                    [1, 3, 3, 0, 5, 3, 3, 3, 4, 0, 3, 2, 4, 1, 0, 3, 5, 2, 5]]
    unsolvable_pyramid = [[0, 1, 2, 3, 10, 11, 12, 24, 25, 26, 27, 44, 45, 46, 47, 48, 69, 70, 71, 72, 73, 74, 100, 101,
                           102, 103, 104, 105, 106, 137, 138, 139, 140, 141, 142, 143, 144, 180, 181, 182, 183, 184,
                           185, 186, 187, 188, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238],
                          [28, 48, 31, 45, 39, 30, 47, 22, 1, 3, 34, 40, 51, 24, 13, 52, 6, 29, 27, 41, 38, 12, 10, 53,
                           4, 32, 55, 21, 16, 17, 23, 14, 49, 18, 26, 8, 54, 2, 36, 25, 5, 20, 37, 46, 15, 9, 44, 35,
                           33, 43, 11, 7, 50, 42, 0, 19],
                          ['114343', '114242', '114334', '112442', '331441', '131344', '121442', '323424', '212313',
                           '112332', '113434', '113344', '114224', '232434', '121233', '141242', '113232', '313414',
                           '242334', '141433', '131434', '113322', '131232', '221441', '131223', '131443', '121244',
                           '223344', '224343', '332442', '223443', '232344', '112244', '223434', '224433', '121323',
                           '114422', '131322', '141343', '224334', '121332', '232443', '113443', '141224', '242343',
                           '113223', '141422', '114433', '141334', '212414', '221331', '112233', '121424', '112424',
                           '112323', '243324'],
                          [1, 1, 4, 3, 2, 1, 5, 3, 4, 4, 5, 0, 2, 0, 5, 5, 3, 5, 2, 3, 2, 1, 1,
                           0, 4, 2, 5, 1, 3, 4, 2, 5, 2, 0, 0, 3, 5, 0, 1, 5, 2, 0, 0, 3, 0, 5,
                           4, 3, 0, 4, 1, 4, 0, 5, 1, 4]]
    # rot_sol = rotate_sol(solution)
    # draw_solution(solution)
    # draw_solution(rot_sol, tiles)

    # Lösung durch Zufall finden, daraus Funktion schreiben, welche die durchschnittliche Anzahl der Schritte
    # bis zur ersten fehlerfreien Lösung ausgibt
    # avg, vals = find_sol_rand(3, tiles_complete, all_puzzles[0])

    temperature = 500
    steps = 25000

    # Simulated annealing mit Blumenpuzzle
    # opt_sol, opt_val, datastream = simulated_annealing(start_sol, steps, temperature, 5)
    # draw_solution(opt_sol)
    # print(f"Fehleranzahl der besten Lösung: {opt_val}")
    # print(opt_sol)
    # print_best_sols(datastream)
    # # plot_t_over_steps(datastream)
    # # plot_p_over_steps(datastream)
    # plot_val_over_steps(datastream)
    # plot_cand_curr_over_steps(datastream)
    # random_sol_mean(steps, tiles)

    # Bestimmen des Annahme-Wk-Parameters durch Ausprobieren
    # test_datastream = find_param(start_sol, 25000, 500, 0.5, 8.0, 0.5, 100, tiles)
    # plot_param_over_steps(test_datastream)
    # plot_param_over_rate(test_datastream)

    # Löst alle 14C7 Blumenpuzzles, 10 Versuche pro Puzzle
    # flower_results = solve_flowers(all_puzzles, tiles, steps, temperature, 6, write_file=1)
    # plot_flower_results(flower_results)
    # print(f"Summe aller Fehler: {sum(flower_results[1])}")
    # die Summe aller Fehler, wenn 0 wurden alle Puzzles gelöst
    # plot_flower_attempts(flower_results)
    # gen_flower_sol_file(flower_results)

    # Möglichst viele Lösungen einer Blume finden
    # all_sols = find_all_flower_sols(rand_sol[0], 10000, tiles_complete, steps, temperature, 6, write_file=1)
    # all_sols = find_all_flower_sols(all_puzzles[0], 10000, tiles_complete, steps, temperature, 6, write_file=1)

    # Simulated annealing von allgemeinen Puzzles mit unterschiedlicher Tile-Anzahl und Formen
    # big_sol = random_sol_gen(tiles_complete, n_tiles=7, kangaroo=0, sample=0, ascending=0, randomness=1)
    # opt_sol, opt_val, datastream = sim_ann_gen(rsx_unsol, steps, temperature, 5)
    # draw_sol_gen(opt_sol)
    # print(f"Fehleranzahl der besten Lösung: {opt_val}")
    # print(opt_sol)
    # print_best_sols(datastream)
    # # plot_t_over_steps(datastream)
    # # plot_p_over_steps(datastream)
    # # plot_val_over_steps(datastream)
    # plot_cand_curr_over_steps(datastream)

    # find_unsolvable(attempts_to_solve=10, attempts_to_search=100, n_iter=20000, temp=500, param=5)
    # elim_ident("")

    # solo, dolo, data = sim_ann_gen(unsolvable_pyramid, 1000, 50, 10, 1)
    # draw_sol_gen(solo)
    # plot_cand_curr_over_steps(data)
    # plot_val_over_steps(data)


    draw_sol_gen(solx)


if __name__ == "__main__":
    main()
