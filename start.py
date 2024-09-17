import numpy as np
import random as random
from itertools import combinations
from itertools import groupby
from collections import Counter
import copy
import ast

import datetime

import math
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Arc

import argparse

# alle 56 Spielsteine codiert, Priorität bei der Rotation: blau, gelb, rot, (grün)
tiles_complete = ['112323', '212313', '131322', '112332', '131223', '121332', '113232',
                  '112233', '121323', '113223', '131232', '221331', '113322', '121233',
                  '232344', '242343', '224343', '332442', '223434', '242433', '232443',  # 242433 anstatt 243324
                  '223344', '323424', '223443', '232434', '224334', '224433', '242334',
                  '114343', '313414', '131344', '114334', '131443', '141334', '113434',
                  '114433', '141343', '113443', '131434', '331441', '113344', '141433',
                  '112424', '212414', '141422', '112442', '141224', '121442', '114242',
                  '112244', '121424', '114224', '141242', '221441', '114422', '121244']

# Erstellen einer Liste aller Kombinationen von 7 Elementen aus dem Vektor mit den Einträgen von 0 bis 13
# Codierung für alle möglichen Puzzles, mathematisch 14C7
all_puzzles = list(combinations([*range(14)], 7))


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


def get_dist(tile, col):
    """
    Abstand von einer Farbe in der Codierung, Beispiel: get_dist("121323", 1) liefert 2
    :param tile: Codierung eines Steins
    :param col: gesuchte Farbe
    :return: Abstand im array zwischen den beiden farbigen Kanten
    """
    if str(col) not in tile:
        return 0, 0
    indices = []
    for r in range(6):
        if tile[r] == str(col):
            indices.append(r)
    dist = indices[1] - indices[0]
    return dist, indices[0]


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


def get_longest_connection(sol, focol=None, fields=False):
    """
    Findet die längsten Linien/Schleifen der Farben
    :param sol: Lösung
    :param focol: Farbe (1: blau, 2: gelb, 3: rot, 4: grün)
    :param fields: betreffenden Felder ausgeben ja/nein
    :return: [[2, 0], [2, 0], [3, 0], [2, 0]]
             [längste Linie, längste Schleife]
             1: blau, 2: gelb, 3: rot, 4: grün
    """
    if len(sol) == 3:
        sol.insert(0, [*range(len(sol[0]))])

    def nbr_check_recursive(field, edg, color, visited, solution, start_field):
        """Sucht rekursiv die angrenzenden Steine ab, ob sich die aktuelle Linie/Schleife dort fortsetzt"""
        nbr = get_neighbor(field, edg)  # Nachbarn des aktuellen Steins und Kante suchen
        if (nbr, color) in visited:  # Falls bereits besucht, Funktion verlassen
            return 0, False  # Vermeidet endlose Rekursion, wenn der Knoten bereits besucht wurde
        # visited.append((nbr, color))  # Farbe wird schon abgehakt, wenn nur die erste Kante der Farbe betrachtet wird
        if nbr not in solution[0]:  # Falls dieses Feld nicht besetzt ist, Funktion verlassen
            return 0, False  # diese Abfrage nach oben verschieben
        else:
            field_index = solution[0].index(field)
            curr_code = sol[2][field_index]
            curr_ort = sol[3][field_index]
            nbr_index = solution[0].index(nbr)
            nbr_code = sol[2][nbr_index]
            nbr_ort = sol[3][nbr_index]
            nbr_edge = (edg + 3) % 6
            if str(color) not in nbr_code:  # Falls Farbe nicht in einer Fliese enthalten ist
                visited.append((nbr, color))
                return 0, False
            if getColor(curr_code, edg, curr_ort) != getColor(nbr_code, nbr_edge, nbr_ort):
                return 0, False  # Falls Farben nicht an betreffender Kante übereinstimmen Funktion verlassen
            else:
                dist, first_app = get_dist(nbr_code, color)
                nbr_edges = [(first_app - nbr_ort) % 6, (first_app - nbr_ort + dist) % 6]
                next_edge = [e for e in nbr_edges if e != nbr_edge][0]  # Kante des nächsten Feldes, welche als Nächstes
                # betrachtet wird
                next_field = nbr
                visited.append((nbr, color))  # Hier append, da Farbe dann abgearbeitet ist
                length, looping = nbr_check_recursive(field=next_field, edg=next_edge, color=color, visited=visited,
                                                      solution=solution, start_field=start_field)  # Rekursion
                return 1 + length, looping or (nbr == start_field)  # nbr == ?

    visited_tile_color = []
    longest_conn_color = [[0, 0] for _ in range(4)]
    longest_conn_fields = [[[], []] for _ in range(4)]  # beteiligte Felder
    if focol is None:
        search_colors = range(1, 5)
    else:
        search_colors = [focol]
    for col in search_colors:  # blau 1, gelb 2, rot 3, grün 4, jede Farbe wird betrachtet
        for index in range(len(sol[0])):  # jedes Feld wird pro Farbe erneut betrachtet
            tile_field = sol[0][index]
            # tile_num = sol[1][index]
            tile_code = sol[2][index]
            tile_ort = sol[3][index]
            if str(col) in tile_code:  # Feld nur betrachten, falls die gesuchte Farbe enthalten ist
                if (tile_field, col) not in visited_tile_color:  # nur falls Farbe und Feld nicht betrachtet
                    conn_len = 0
                    loop = False  # boolean für das Finden einer Schleife
                    distance, first_appearance = get_dist(tile_code, col)
                    edge_queue = [(first_appearance - tile_ort) % 6, (first_appearance - tile_ort + distance) % 6]
                    # distance zwischen 1 und 5 belassen und dafür + tile_ort liefert gleiches ergebnis
                    for edge in edge_queue:
                        connection, loop = nbr_check_recursive(field=tile_field, edg=edge, color=col,
                                                               visited=visited_tile_color, solution=sol,
                                                               start_field=tile_field)
                        conn_len += connection
                        if loop:  # Falls eine Schleife erkannt wurde,
                            # muss nicht noch in die andere Richtung gelaufen werden
                            break
                    if not loop:
                        conn_len += 1
                    if (tile_field, col) not in visited_tile_color:
                        visited_tile_color.append((tile_field, col))
                    if conn_len > longest_conn_color[col - 1][int(loop)]:  # loop boolean indizieren
                        longest_conn_color[col - 1][int(loop)] = conn_len
                        if fields:
                            longest_conn_fields[col - 1][int(loop)] = \
                                sorted([i for (i, j) in visited_tile_color[-conn_len:]])  # Felder extrahieren
    if fields:
        return [longest_conn_color, longest_conn_fields]
    return longest_conn_color


def draw_sol(solution):
    """
    Die allgemeine Lösung plotten, jedes Tile in der Lösung wird betrachtet und einzeln
    geplottet nach der Orientierung und den Farbcodes
    :param solution: Lösung, welche geplottet werden soll
    :return: Matplotlib-Plot
    """
    if len(solution) == 3:
        solution.insert(0, [*range(len(solution[0]))])
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
    # plt.title(f"{datetime.datetime.now().time()}, {obj(solution)} Fehler")
    plt.title(f"{datetime.datetime.now():%H:%M:%S}, {obj(solution)} Fehler, {tuple(sorted(solution[1]))}, "
              f"{categorize_puzzle(tuple(sorted(solution[1])))}")
    plt.show()


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
                dst, _ = get_dist(tl, k)
                pair.append(k)
                pair.append(dst)
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
    # colors = {'1': 'white', '2': 'white', '3': 'white', '4': 'white'}
    x, y = getCoordinates(position)
    angles = np.arange(- 2 / 3 * np.pi, 4 / 3 * np.pi, np.pi / 3)
    pairs = find_pairs(tile)
    # size = 0.55  # .575
    hexagon = np.array([[x + size * np.cos(angles[edge]), y + size * np.sin(angles[edge])] for edge in range(6)])
    centers = [hexagon[k] + ((hexagon[(k + 1) % 6] - hexagon[k]) / 2) for k in range(6)]
    # Zeichne das Hexagon mit schwarzer Füllung
    hex_patch = Polygon(hexagon, closed=True, fill=True, edgecolor='black', facecolor='black')
    # ax.text(x, y, str(position), ha='center', va='center', fontsize=25, color='black', weight='medium')
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
                scale_factor = size / dist + 0.29  # 0.315
                start = start + (end - start) * (1 - scale_factor) / 2
                end = end - (end - start) * (1 - scale_factor) / 2
            ax.plot([start[0], end[0]], [start[1], end[1]], color=color, lw=10)
            continue
        else:
            if edge_pair[3] == 1 or edge_pair[3] == 5:
                # aneinanderliegende Kanten, Distanz 1, MP des Kreises ist die Ecke des Hexagons
                center = hexagon[(edge_pair[1] - orientation) % 6]
            else:  # Distanz 2 (2 oder 4), also eine Kante zw. zsmgeh. Kanten, MP ist Mitte des Nb der mittleren Kante
                nbg_edge = (get_middle_edge(edge_pair[0], edge_pair[1]) - orientation) % 6
                # die Kante zwischen den beiden gleichgefärbten  # (edge_pair[0] + edge_pair[1]) + 4 % 6
                nbr = get_neighbor(position, nbg_edge)
                center = getCoordinates(nbr)
            radius = np.sqrt((start[0] - center[0]) ** 2 + (start[1] - center[1]) ** 2)
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


def getColor(tile, edge, orientation):
    """
    Die Farbe einer Kante eines Steins ausgeben als int mit definierter Codierung
    :param tile: Codierung des Steins
    :param edge: Kante des Steins
    :param orientation: Rotation des Steins
    :return: Farbcode
    """
    return int(tile[(edge + orientation) % 6])


def col_in_tile(tile, col):
    """Farbe in Fliese enthalten ja/nein"""
    if str(col) in tile:
        return True
    return False


def categorize_puzzle(puzzle):
    """Gibt die Kategorien der enthaltenen Steine an [ccc, clc, xl, xc]"""
    out = [0 for _ in range(4)]
    for tile in puzzle:
        if tile in [7, 12, 21, 26, 35, 40, 49, 54]:  # ccc
            out[0] += 1
            continue
        elif tile in [3, 9, 11, 17, 23, 25, 31, 37, 39, 45, 51, 53]:  # clc
            out[1] += 1
            continue
        elif tile in [1, 8, 10, 15, 22, 24, 29, 36, 38, 43, 50, 52]:  # xl
            out[2] += 1
            continue
        else:  # xc
            out[3] += 1
    return tuple(out)


def gen_random_sol(n_tiles=7, kangaroo=1, sample=0, ascending=0, randomness=0, standard=0, all_tiles=None):
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
    if all_tiles is None:
        all_tiles = tiles_complete

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


def gen_start_sol(combo, fields=None, all_tiles=None, standard=0):
    """
    Eine Startlösung generieren ausgehend von einer beliebigen Kombination der Spielsteine
    :param fields: die Felder, auf welche die Steine gelegt werden, default aufsteigend zugewiesen
    :param standard: Lösung ohne Einträge der Felder generieren
    :param combo: array mit Steine-Nummern
    :param all_tiles: array mit Codierung aller Steine
    :return: array mit Startlösung
    """
    if all_tiles is None:
        all_tiles = tiles_complete
    if fields is None or len(fields) != len(combo):
        fields = [*range(0, len(combo))]
    if len(combo) == 7:
        standard = 1
    sol = [[] * len(combo) for _ in range(4)]
    sol[0] = fields
    sol[1] = list(np.random.permutation(combo))
    sol[2] = [all_tiles[k] for k in sol[1]]
    sol[3] = [int(random.uniform(0, 6)) for _ in range(len(combo))]
    if standard:
        return sol[1:]
    return sol


def gen_cand(curr, val=None, max_err=None, swap_and_rotate=1, swap_or_rotate=0,
             morphing=0, adapt_operations=0, max_swaps=None, max_rotations=None, err_edges=None):
    """
    Generiere einen Kandidaten für allgemeine Formen von Lösungen
    dieselben Tiles vertauschen und rotieren? (swap_and_rotate=1 setzen, liefert bessere Ergebnisse)
    :param err_edges: Fliesen, an welchen Fehler auftreten
    :param max_err: Maximale Anzahl an Fehler in der aktuellen Lösung
    :param adapt_operations: Anzahl der shifts/rotations anpassen an relativen Lösungsfortschritt
    :param val: Fehler der aktuellen Lösung
    :param max_rotations: Anzahl der Steine, die rotiert werden sollen
    :param max_swaps: Anzahl der Steine, die vertauscht werden sollen untereinander
    :param curr: Eingangslösung
    :param swap_and_rotate: boolean, default True
    :param swap_or_rotate: boolean, nur rotieren oder nur vertauschen als Operation
    :param morphing: Form der Lösung verändern, default False 
    :return: Ausgangslösung
    """

    def sort_neighbors(zippo):
        """Sortieren der gezippten Liste basierend auf den Elementen der zweiten Elemente in absteigender Reihenfolge"""
        zippo = [el for el in zippo if el[0] != 0]  # Stein auf Feld 0 herausnehmen, dieser soll immer fix bleiben
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
    n_swaps = 0
    n_rotations = 0
    standard = 0
    if len(cand) == 3:
        cand.insert(0, [*range(n_tiles)])
        standard = 1
    if max_swaps is not None and max_rotations is not None:
        if (max_swaps, max_rotations) < (n_tiles, n_tiles):  # Falls gültige Werte für max_swaps/max_rots
            # swap_and_rotate = 0
            n_swaps = np.random.randint(1, max_swaps + 1)  # Anzahl der Vertauschungen
            if swap_and_rotate:
                n_rotations = n_swaps
            else:
                n_rotations = np.random.randint(1, max_rotations + 1)  # Anzahl der Rotationen
    else:
        if adapt_operations:
            if val is None or max_err is None:
                val = obj(curr)
                max_err = max_errors(curr)
            rel_val = val / max_err
            max_ops = min(math.ceil(rel_val * n_tiles) + 2, n_tiles)
            n_swaps = np.random.randint(1, max_ops)
            n_rotations = np.random.randint(1, max_ops)
        else:
            n_swaps = np.random.randint(1, n_tiles + 1)  # Anzahl der Vertauschungen
            n_rotations = np.random.randint(1, n_tiles + 1)  # Anzahl der Rotationen
        if swap_and_rotate:
            n_rotations = n_swaps
    if swap_or_rotate:
        if bool(np.random.randint(0, 2)):
            n_swaps = 0
        else:
            n_rotations = 0
    swap_indices = random.sample([*range(0, n_tiles)], k=n_swaps)  # Indizes der zu vertauschenden Steine,
    # für Blume ([*range(0, 7)], k=n_swaps)
    if err_edges is not None:
        freqs = Counter(err_edges)
        most_frequent_error_tiles = [tile for tile, _ in freqs.most_common()]
        # Wähle eine zufällige Anzahl von Kacheln aus den fehlerhaften Kacheln
        # Anzahl der Kacheln, die wir aus den fehlerhaften Kacheln nehmen wollen (zwischen 0 und n_swaps)
        num_error_tiles = random.randint(0, n_swaps)
        # Nimm die 'num_error_tiles' häufigsten fehlerhaften Kacheln
        chosen_error_tiles = most_frequent_error_tiles[:num_error_tiles]
        # Filtere die swap_indices, sodass sie keine Kacheln enthalten, die bereits in chosen_error_tiles sind
        available_swap_indices = [idx for idx in swap_indices if idx not in chosen_error_tiles]
        available_chosen_indices = [idx for idx in chosen_error_tiles if idx not in swap_indices]
        # Berechne, wie viele Kacheln wir tatsächlich austauschen können
        num_available_swaps = min(len(available_swap_indices), len(available_chosen_indices))
        # Ersetze die ersten 'num_available_swaps' Kacheln in swap_indices durch chosen_error_tiles
        for i in range(num_available_swaps):
            swap_indices[swap_indices.index(available_swap_indices[i])] = available_chosen_indices[i]
        # Jetzt die neuen swap_indices mit den geänderten Kacheln
    swap_indices_permutation = list(np.random.permutation(swap_indices))
    rotations = np.random.choice(6, n_rotations)  # Rotationen der Steine festlegen
    if swap_and_rotate:
        rotation_indices = swap_indices
        for z in range(len(swap_indices)):
            if swap_indices[z] == swap_indices_permutation[z] and len(swap_indices) > 1:  # Falls Stein auf sich selbst
                # abgebildet wird, und mehr als 1 Stein vertauscht wird, wird dieser Stein nicht rotiert, sonst schon
                rotations[z] = 0
    else:
        rotation_indices = random.sample([*range(0, n_tiles)], k=n_rotations)  # Indizes der zu rotierenden Steine
    # standard = 0
    # if len(cand) == 3:
    #     cand.insert(0, [*range(n_tiles)])
    #     standard = 1
    if morphing:  # Felder nach freien Nachbarn absteigend ordnen, dann Zufallszahl n_shifts ziehen, die ersten n_shift
        # Felder verwenden und verschieben, das neue Feld aus den nbrs (freien Feldern löschen), Feld 0 nicht shiften
        if val is None or max_err is None:
            val = obj(curr)
            max_err = max_errors(curr)
        rel_val = val / max_err
        if np.random.rand() < rel_val:  # Form verändern abhängig von relativem Lösungsfortschritt
            out_zip, nbr_zip = update_solution(cand)
            [out_zip, nbr_zip] = [shuffle_equal_tiles(out_zip), shuffle_equal_tiles(nbr_zip)]
            n_shifts = np.random.randint(0, len(out_zip))  # Anzahl der Verschiebungen von Steinen
            for k in range(n_shifts):  # die Listen dann updaten? mit get_neighbor und Vergleich mit nbr
                old_field = out_zip[0][0]  # Feld, welches aus der Lösung genommen und geändert wird, [k][0]
                old_index = cand[0].index(old_field)  # Index des alten Feldes in der Lösung
                old_nbrs = [get_neighbor(old_field, edge) for edge in range(6)]
                # temp_sol = [sol[:old_index] + sol[old_index + 1:] for sol in cand]  # ohne altes Feld betrachten
                # _, temp_nbr_zip = update_solution(temp_sol)
                new_cands = [field for field, _ in nbr_zip if field not in old_nbrs]
                new_field = new_cands[0]
                # new_field = nbr_zip[0][0]  # temp_nbr_zip,
                # Problem: Neues Feld ist evtl. nicht mehr verbunden mit übrigen Feldern, da das verbindende Feld gerade
                # weggetauscht wird, nach dem Wählen des zu entfernenden Feldes muss die Nachbarliste erneut akt. werden
                cand[0][old_index] = new_field  # Feld verändern
                out_zip, nbr_zip = update_solution(cand)
                [out_zip, nbr_zip] = [shuffle_equal_tiles(out_zip), shuffle_equal_tiles(nbr_zip)]
    tiles_copy = copy.deepcopy(cand[2])
    swap_tiles_perm = [cand[1][k] for k in swap_indices_permutation]  # Permutation der betroffenen Steine
    for k, rot in enumerate(rotation_indices):
        cand[3][rot] = (cand[3][rot] + rotations[k]) % 6
    for j, swap in enumerate(swap_indices):
        cand[1][swap] = swap_tiles_perm[j]
        cand[2][swap] = tiles_copy[swap_indices_permutation[j]]
    # print(f"Anzahl der Vertauschungen/Rotationen: {n_swaps}, {n_rotations}")
    if standard:
        return cand[1:]
    return cand


def get_outer_fields(sol):
    """
    Berechnet die äußeren Felder einer Lösung und die daran angrenzenden Nachbarfelder
    :param sol: Lösung
    :return: äußere Felder mit offenen Kanten, Nachbarfelder mit verbundenen Kanten
    """
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


def get_open_edges(sol):
    """Gibt die Summe der freien Kanten einer Lösung aus, Maß für Kompaktheit der Lösung"""
    outer, _ = get_outer_fields(sol)
    output = sum([edge[1] for edge in outer])
    return output


def max_errors(sol):
    """Die maximale Anzahl an Fehlern einer Lösung bestimmen, damit den relativen Lösungsfortschritt berechnen"""
    if len(sol) == 3:
        # sol.insert(0, [*range(len(sol[0]))])
        return 12
    tile_positions = {sol[0][index]: index for index in range(len(sol[0]))}
    visited_edges = set()  # Set für besuchte Kantenpaare
    inner_edges = 0
    for index in range(len(sol[0])):
        for edge in range(6):
            if (index, edge) not in visited_edges:
                neighbor_field = get_neighbor(sol[0][index], edge)
                if neighbor_field in tile_positions:
                    neighbor_index = tile_positions[neighbor_field]
                    inner_edges += 1
                    visited_edges.add((index, edge))
                    visited_edges.add((neighbor_index, (edge + 3) % 6))
    return inner_edges


def obj(sol, discrete=1, max_err=None, out_edges=0, early_exit=0):
    """
    Objective-Funktion für verallgemeinerte Lösungen (nicht nur für Blumen), gibt die Anzahl der Fehler an
    (Vorgehen: für jedes Tile die 6 Nachbarn betrachten und die Fehler zählen), langsamer als im Blumen-Fall
    :param discrete: die Fehleranzahl diskret Abstufen mit Stufenbreite x, default 1
    :param sol: Lösung
    :param max_err: maximale Anzahl der Fehler, falls angegeben, wird relativer Lösungsfortschritt ausgegeben
    :param out_edges: (tile, edge) der fehlerhaften Fliesen ausgeben als set
    :param early_exit: Funktion verlassen, falls der erste Fehler gefunden wurde und -1 ausgeben
    :return: Fehleranzahl
    """
    mismatches = 0
    mismatched_edges = []
    if len(sol) == 3:  # für Blumen-Lösungen, schneller als die untere Variante
        outer_indices = [2, 3, 4, 5, 6, 1]
        for i in range(7):  # Betrachte jeden Stein in der Blume
            if i == 0:  # Betrachte den mittleren Stein
                for edge in range(6):  # Vergleiche den mittleren Stein mit seinen 6 Nachbarsteinen
                    color_center = getColor(sol[1][i], edge, sol[2][i])
                    color_neighbor = getColor(sol[1][edge + 1], (edge + 3) % 6, sol[2][edge + 1])
                    if color_center != color_neighbor:
                        mismatches += 1
                        mismatched_edges += [i, edge + 1]  # das Paar der betroffenen Fliesen
                        if early_exit:
                            return -1
            else:  # Betrachte die äußeren Steine
                next_index = outer_indices[i - 1]
                color_current = getColor(sol[1][i], (i + 1) % 6, sol[2][i])
                color_next = getColor(sol[1][next_index], (i + 4) % 6, sol[2][next_index])
                if color_current != color_next:
                    mismatches += 1
                    mismatched_edges += [i, next_index]
                    if early_exit:
                        return -1
        # return mismatches
    # t1 = time.perf_counter()
    # Caches für Positionen und Farben
    else:
        tile_positions = {sol[0][index]: index for index in range(len(sol[0]))}
        tile_colors = [
            [getColor(sol[2][index], edge, sol[3][index]) for edge in range(6)]
            for index in range(len(sol[0]))
        ]
        visited_edges = set()  # Set für besuchte Kantenpaare
        # t2 = time.perf_counter()
        # Fehler zählen
        for index in range(len(sol[0])):  # jedes Feld des Puzzles betrachten
            for edge in range(6):  # jede Kante des Feldes
                if (index, edge) not in visited_edges:
                    # t3 = time.perf_counter()
                    neighbor_field = get_neighbor(sol[0][index], edge)
                    # t4 = time.perf_counter()
                    if neighbor_field in tile_positions:
                        neighbor_index = tile_positions[neighbor_field]
                        if tile_colors[index][edge] != tile_colors[neighbor_index][(edge + 3) % 6]:
                            mismatches += 1
                            mismatched_edges += [index, neighbor_index]  # das Paar der betroffenen Fliesen
                            if early_exit:
                                return -1
                        visited_edges.add((index, edge))
                        visited_edges.add((neighbor_index, (edge + 3) % 6))
                    # t5 = time.perf_counter()
                    # print(f"init: {t2 - t1}, neigh: {t4 - t3}, rest_loop: {t5 - t4}")
    if mismatches > 0 and discrete > 1:
        mismatches = (mismatches // discrete) + 1  # Bsp 3, (1, 2) -> 1; (3, 4, 5) -> 2 ...
        # return out
    if max_err is not None:
        mismatches = mismatches / max_err
    if out_edges:
        return [mismatches, mismatched_edges]
    else:
        return mismatches


def get_temp(temp, step, cooling=None):
    """
    Temperatur berechnen des Systems abhängig von Ausgangstemperatur und Anzahl der getätigten Schritte (= Zeit)
    :param cooling: Abkühlungsfaktor
    :param temp: Eingangstemperatur
    :param step: Schrittanzahl
    :return: Ausgangstemperatur
    """
    if cooling is None:
        t = temp / (1 * float(step + 1))  # (0.2 * float(step + 1))
    else:
        t = cooling ** step * temp
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


def sa3(init_sol, n_iter=10000, temp=10, restart_threshold=3000, max_restarts=0, focus_errors=1, focus_color=None,
        morphy=0,
        adapt_operations=1, write_data=1, print_iteration=0, cool_f=0.9985, print_params=1):
    """
    Simulated annealing Algorithmus
    :param focus_errors: Generieren der Kandidaten fokussiert die Fliesen, an welchen die Fehler auftreten
    :param focus_color: Farbe (1: blau, 2: gelb, 3: rot, 4: grün), in welcher eine möglichst lange Linie (Schleife?)
    gebildet werden soll
    :param max_restarts: maximale Anzahl an Neustarts des Algorithmus
    :param restart_threshold: Anzahl Schritte, die keine Verbesserung der curr_sol gebracht hat, also auch d. best_sol
    :param cool_f: Abkühlungsparameter
    :param adapt_operations: Anzahl Tauschs/Rotationen dynamisch anpassen mit aktueller Fehleranzahl
    :param init_sol: Startlösung
    :param n_iter: max. Anzahl der Schritte im Algorithmus
    :param temp: Starttemperatur
    :param morphy: Soll der Algorithmus versuchen, die Form der Lösung zu verändern?
    :param write_data: Sollen Daten geschrieben werden?
    :param print_iteration: Sollen Schritte geprintet werden?
    :param print_params: Parameter des Algorithmus am Ende ausgeben
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
    if len(init_sol) == 1:  # nur Puzzle angeben als [(puzzle)]
        init_sol = gen_start_sol(init_sol[0])
    elif len(init_sol) == 2:  # Puzzle mit Feldern angeben als [(Felder), (puzzle)]
        init_sol = gen_start_sol(init_sol[1], fields=init_sol[0])
    if obj(init_sol) == 0:
        return [init_sol, obj(init_sol), [[0] * n_iter for _ in range(10)]]
    temperatures = [get_temp(temp, k, cooling=cool_f) for k in range(n_iter)]
    data = []
    if write_data:
        data = [[0] * n_iter for _ in range(10)]
        data[0] = [*range(n_iter)]
    best_sol = copy.deepcopy(init_sol)  # beste Lösung, wird am Schluss ausgegeben
    focus_obj = len(init_sol[0])
    if focus_errors:
        objective, obj_tiles = obj(best_sol, out_edges=focus_errors)
    else:
        objective, obj_tiles = obj(best_sol, out_edges=focus_errors), None
    n_tiles_with_focus_col = sum([col_in_tile(tile, focus_color) for tile in init_sol[-2]])
    if focus_color is not None:
        lens, included_tiles = get_longest_connection(init_sol, focol=focus_color, fields=True)
        focus_tiles = [init_sol[0].index(item) for item in init_sol[0] if
                       item not in included_tiles[focus_color - 1][0]]
        # init_sol.index()...,  included_tiles[focus_color - 1][1]] für loops
        focus_obj = n_tiles_with_focus_col - lens[focus_color - 1][0]
        # print(f"foc: {focus_obj}")
        if focus_errors:
            temp_obj = [focus_obj, focus_tiles]
        else:
            temp_obj = [focus_obj, None]
    else:
        temp_obj = [objective, obj_tiles]
    # best_col_val = 0
    # if focus_color is not None:
    #     best_col_val = get_longest_connection(best_sol, focol=focus_color)
    #     curr_col_val = best_col_val
    max_obj = max_errors(init_sol)
    max_combined = max_obj + n_tiles_with_focus_col - 1
    # best_combined = focus_obj + objective
    if focus_color is not None:
        best_val, curr_err_edges = max_combined, temp_obj[1]
    else:
        best_val, curr_err_edges = temp_obj
    curr_sol, curr_val = best_sol, best_val
    cand_sol, cand_val = curr_sol, curr_val
    steps_at_temp = 0
    t = temperatures[0]
    temp_index = 0
    restarts = 0
    failed_steps = 0
    restart_best_val = max_obj
    focus_mode = 1
    focus_tiles = None
    obj_tiles = None
    if focus_color is not None:
        focus_mode = 1
    for i in range(n_iter):  # ######### Schleife ab HIER ##########
        if focus_color is not None:
            if focus_obj == 0 and objective == 0:
                print("leaving loop")
                break
            if cand_val == 0:
                # if cand_val in (0, 1, 2):
                if focus_mode == 1:
                    curr_val = objective
                    if focus_errors:
                        curr_err_edges = obj_tiles
                    else:
                        curr_err_edges = None
                    # print("leaving focus_mode")
                    focus_mode = 0
                else:
                    curr_val = focus_obj
                    if focus_errors:
                        curr_err_edges = focus_tiles
                    else:
                        curr_err_edges = None
                    # print("entering focus_mode")
                    focus_mode = 1
        else:
            if objective == 0:
                break
        cand_sol = gen_cand(curr_sol, curr_val, max_obj, swap_and_rotate=1, swap_or_rotate=0,
                            adapt_operations=adapt_operations, morphing=morphy, err_edges=curr_err_edges)
        if focus_errors:
            objective, obj_tiles = obj(cand_sol, out_edges=focus_errors)
        else:
            objective, obj_tiles = obj(cand_sol, out_edges=focus_errors), None
        if print_iteration:
            print(f"obj: {objective}")
        if focus_color is not None:
            lens, included_tiles = get_longest_connection(cand_sol, focol=focus_color, fields=True)
            focus_tiles = [init_sol[0].index(item) for item in init_sol[0] if
                           item not in included_tiles[focus_color - 1][0]]
            focus_obj = n_tiles_with_focus_col - lens[focus_color - 1][0]
            if print_iteration:
                print(f"fobj: {focus_obj}")
            if focus_mode:
                if focus_errors:
                    temp_obj = [focus_obj, focus_tiles]
                else:
                    temp_obj = [focus_obj, None]
            else:
                temp_obj = [objective, obj_tiles]
        else:
            temp_obj = [objective, obj_tiles]
        # if focus_color:
        #     cand_col_val = get_longest_connection(cand_sol, focus_color)
        cand_val, cand_err_edges = temp_obj
        diff = cand_val - curr_val
        # if focus_color:
        #     col_diff = cand_col_val - curr_col_val
        if print_iteration:
            print(f"Iteration #{i}, Differenz cand - curr: {diff}")
        cand_combined_val = focus_obj + objective
        if focus_color is not None:
            if cand_combined_val < best_val:
                best_sol, best_val = cand_sol, cand_combined_val
                # print(f"{cand_sol} ### {best_combined}")
        else:
            if cand_val - best_val < 0:
                best_sol, best_val = cand_sol, cand_val
                restart_best_val = best_val
                failed_steps = 0
        if cand_val - restart_best_val < 0:
            restart_best_val = cand_val
            failed_steps = 0  # Schritte zurücksetzen, solange Verbesserung pro Neustart eintritt
        if steps_at_temp == 0:
            # print("new temp")
            t = temperatures[temp_index]
            try:
                exp_val = np.exp((max_obj - best_val) / t)
                exp_val = min(exp_val, 1e10)  # Setze eine Obergrenze (z.B. 1e10)
                steps_at_temp = min(max(int(exp_val), 1), 30)
            except OverflowError:
                steps_at_temp = 30
            # print(f"sat: {steps_at_temp}")
        steps_at_temp -= 1
        temp_index += 1
        # p = 0
        if diff < 0:
            p = 1
        else:
            p = calc_acceptance(diff, t)
        if np.random.rand() < p:
            curr_sol, curr_val = cand_sol, cand_val
            curr_err_edges = cand_err_edges
            # failed_steps = 0
        else:
            failed_steps += 1
            if failed_steps >= restart_threshold:
                if restarts < max_restarts:
                    print("restart!")
                    restarts += 1
                    temp_index = 0
                    steps_at_temp = 0
                    failed_steps = 0
                    focus_mode = 1  # Testzweck
                    if focus_color is not None:
                        restart_best_val = max_combined
                    else:
                        restart_best_val = max_obj
                # else:
                # break  # Algorithmus wird abgebrochen
        # print(f"fs: {failed_steps}")
        if write_data:
            data[1][i] = t
            data[2][i] = p
            data[3][i] = best_val
            data[4][i] = best_sol
            data[5][i] = curr_val
            data[6][i] = curr_sol
            data[7][i] = cand_val
            data[8][i] = cand_sol
            data[9][i] = diff
            # data[10][i] = best_combined
    if print_params:
        print(f"n_iter: {n_iter} \n"
              f"temp: {temp} \n"
              f"restart_threshold: {restart_threshold} \n"
              f"max_restarts: {max_restarts} \n"
              f"focus_errors: {bool(focus_errors)} \n"
              f"focus_color: {focus_color} \n"
              f"adapt_operations: {bool(adapt_operations)} \n"
              f"cool_f: {cool_f} \n"
              f"morphing: {bool(morphy)}")
    return [best_sol, best_val, data]


def plot_p_over_steps(data, standard=0):
    """
    Die Annahmewahrscheinlichkeit für eine schlechtere Lösung im Verlauf des Algorithmus plotten
    :param data: simulated annealing data
    :param standard: Blume: Standard=1, farbiger Plot der Fehler
    :return: Plot
    """
    if standard:
        colors = {'0': 'blue', '1': 'green', '2': 'red', '3': 'cyan', '4': 'magenta', '5': 'yellow',
                  '6': 'orange', '7': 'lime', '8': 'indigo', '9': 'pink', '10': 'skyblue', '11': 'salmon',
                  '12': 'brown'}  # Farben automatisch anpassen ja nach max(Fehler) in den Daten, Regenbogenverlauf?
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
            plt.scatter([data[0][int(g)] for g in index_list[int(err)]],
                        [data[2][int(j)] for j in index_list[int(err)]],
                        s=0.2, color=col)
        legend_labels = []
        for errors, color_code in colors.items():
            legend_labels.append(f'{errors}: {color_code}')
        lgnd = plt.legend(legend_labels, loc='upper right', title="diff: color")
        for handle in lgnd.legend_handles:
            handle.set_sizes([6.0])
    else:
        plt.scatter(data[0], data[2], s=0.2)
    plt.xlabel('Iteration')
    plt.ylabel('Acceptance probability')
    plt.title("p in Abhängigkeit von Fehlerdiff. "
              "zw. Kandidaten und aktueller Lösung")
    plt.show()


def plot_t_over_steps(data):
    """
    Temperatur des Algorithmus plotten
    :param data: simulated annealing data
    :return:
    """
    plt.plot(data[0], data[1])
    plt.xlabel('Iteration')
    plt.ylabel('Temperature')
    # plt.legend()
    plt.show()


def plot_val_over_steps(data, cut=False):
    """
    Fehleranzahl der besten Lösung über die Iterationen plotten (best_val)
    :param data: simulated annealing data
    :param cut: bis val 0 ist plotten
    :return: Plot
    """
    if cut:
        cut_index = int(data[3].index(0) * 1.1)  # Plot abschneiden
    else:
        cut_index = max(data[0])
    plt.plot(data[0], data[3])
    plt.xlabel('Iteration')
    plt.ylabel('Objective')
    # plt.ylim(0, max(data[7]))
    plt.ylim(0, max(data[3]))
    if cut:
        plt.xlim(0, cut_index)
    # plt.legend()
    plt.title(datetime.datetime.now().time())
    plt.show()


def plot_cand_curr_over_steps(data):
    """
    cand_val und curr_val aus dem Algorithmus plotten
    :param data: simulated annealing data
    :return:
    """
    figure, axis = plt.subplots(2)

    axis[0].plot(data[0], data[5], label='curr_val')
    axis[1].plot(data[0], data[7], label='cand_val', linewidth=1.5)

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


def print_best_sols(data):
    """
    simulated annealing data
    gibt die Kandidaten auf dem Weg zur Lösung aus (die ersten mit einer geringeren neuen Fehleranzahl)
    :param data: array mit Daten aus simulated annealing Algorithmus
    :return: Print-Ausgabe
    """
    visited = []
    for k in range(len(data[4])):
        if data[4][k] not in visited:
            visited.append(data[4][k])
            print(f"Iteration: {k} \t objective: {data[3][k]} \n candidate: {data[4][k]}")


def parse_sol(input):
    output = None
    if isinstance(input, str):
        try:
            output = ast.literal_eval(input)
        except (ValueError, SyntaxError):
            print("Ungültiges Format für das Puzzle-Argument, verwende default Puzzle")
            output = None
    return output


def main():
    # Startlösung, die wir weiterverwenden möchten
    start_sol = gen_random_sol(kangaroo=0, sample=1, standard=1)

    # ArgumentParser erstellen
    parser = argparse.ArgumentParser(description="Eingabe der Parameter für den Algorithmus")

    # Füge die optionalen Argumente hinzu, die für sa3 verwendet werden
    parser.add_argument('--puzzle', type=str, default=start_sol,
                        help="Puzzle, welches gelöst werden soll, Formatierung (string): \"[[Stein-Nummern]]\" "
                             "oder \"[[Felder], [Stein-Nummern]]\", siehe README")
    parser.add_argument('--n_iter', type=int, default=10000, help="Anzahl der Iterationen des Algorithmus, " 
                                                                  "default: 10000")
    parser.add_argument('--temp', type=float, default=10, help="Starttemperatur, default: 10")
    parser.add_argument('--restart_threshold', type=int, default=3000, help="erfolglose Iterationen-Schwellenwert "
                                                                            "für Neustart des Algorithmus, "
                                                                            "default: 3000")
    parser.add_argument('--max_restarts', type=int, default=0, help="Maximale Anzahl an Neustarts, default: 0")
    parser.add_argument('--focus_errors', type=int, default=1,
                        help="Fokussiere Fehler bei der Generierung von Kandidaten, default: 1 (True)")
    parser.add_argument('--focus_color', type=int, default=None,
                        help="Farbe mit Fokus auf zusammenhängende Linie (1: blau, 2: gelb, 3: rot, 4: grün), "
                             "default: None")
    parser.add_argument('--morphy', type=int, default=0, help="Form der Lösung verändern? default: 0 (False)")
    parser.add_argument('--adapt_operations', type=int, default=1,
                        help="Anzahl der Tauschs/Rotationen dynamisch anpassen, default: 1 (True)")
    parser.add_argument('--write_data', type=int, default=0, help="Sollen ausführliche Daten gespeichert und "
                                                                  "geplottet werden?, default: 0 (False)")
    parser.add_argument('--print_iteration', type=int, default=0, help="Sollen Iterationen in Kommandozeile "
                                                                       "geprintet werden?, default: 0 (False)")
    parser.add_argument('--cool_f', type=float, default=0.9985, help="Abkühlungsparameter, default: 0.9985")

    # Argumente parsen
    args = parser.parse_args()

    if parse_sol(args.puzzle) is not None:
        start_sol = parse_sol(args.puzzle)

    # sa3 Funktion aufrufen und die geparsten Argumente verwenden
    solo, dolo, data = sa3(init_sol=start_sol,
                           n_iter=args.n_iter,
                           temp=args.temp,
                           restart_threshold=args.restart_threshold,
                           max_restarts=args.max_restarts,
                           focus_errors=args.focus_errors,
                           focus_color=args.focus_color,
                           morphy=args.morphy,
                           adapt_operations=args.adapt_operations,
                           write_data=args.write_data,
                           print_iteration=args.print_iteration,
                           cool_f=args.cool_f)

    draw_sol(solo)
    print_best_sols(data)
    if args.write_data:
        plot_cand_curr_over_steps(data)
        plot_val_over_steps(data)
        plot_p_over_steps(data, 0)


if __name__ == "__main__":
    main()
