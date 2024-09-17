import time
import csv
import numpy as np
import random as random
from itertools import combinations
from itertools import groupby
from itertools import permutations
from collections import Counter
from collections import defaultdict
# from scipy.stats import norm
import copy
import datetime
import os
import glob

import math
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import Polygon, Arc

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
    ['232344', '242343', '224343', '332442', '223434', '242433', '232443', '223344', '323424', '223443', '232434',
     '224334', '224433', '242334'],  # Gelb, Rot, Grün
    ['114343', '313414', '131344', '114334', '131443', '141334', '113434', '114433', '141343', '113443', '131434',
     '331441', '113344', '141433'],  # Blau, Rot, Grün
    ['112424', '212414', '141422', '112442', '141224', '121442', '114242', '112244', '121424', '114224', '141242',
     '221441', '114422', '121244']]  # Blau, Gelb, Grün

# alle 56 Spielsteine codiert, Priorität bei der Rotation: blau, gelb, rot, (grün)
tiles_complete = ['112323', '212313', '131322', '112332', '131223', '121332', '113232',
                  '112233', '121323', '113223', '131232', '221331', '113322', '121233',
                  '232344', '242343', '224343', '332442', '223434', '242433', '232443',  # 242433 anstatt 243324
                  '223344', '323424', '223443', '232434', '224334', '224433', '242334',
                  '114343', '313414', '131344', '114334', '131443', '141334', '113434',
                  '114433', '141343', '113443', '131434', '331441', '113344', '141433',
                  '112424', '212414', '141422', '112442', '141224', '121442', '114242',
                  '112244', '121424', '114224', '141242', '221441', '114422', '121244']

tiles_triple_cross = ['123123', '132132',  # die nicht verwendeten Steine mit drei geraden Verbindungen
                      '234234', '243243',
                      '134134', '143143',
                      '124124', '142142']

permutation = (8, 4, 10, 13, 1, 11, 7, 14, 6, 5, 9, 2, 3, 12,
               31, 32, 18, 16, 17, 19, 33, 21, 35, 15, 34, 22, 23, 20,
               38, 40, 36, 26, 41, 27, 37, 28, 39, 30, 42, 24, 25, 29,
               55, 50, 53, 47, 54, 46, 56, 45, 44, 49, 51, 48, 43, 52)  # Indizes der Tiles nach offizieller Def.

blue_tiles = [6, 7, 8, 13, 14, 39, 40, 41, 42, 43]  # Pyramide mit blauer Linie
red_tiles = [4, 5, 10, 11, 15, 16, 18, 19, 24, 25, 26, 27, 28, 29, 30]  # Pyramide mit roter Linie
green_tiles = [32, 33, 34, 35, 36, 37, 38, 45, 46, 47]
white_tiles = [*range(48, 57)]
yellow_tiles = [1, 2, 3, 9, 12, 17, 20, 21, 22, 23, 31, 44]

blue_rainbow = [[0, 2, 3, 9, 10, 11, 22, 23, 24, 25], [3, 6, 32, 38, 0, 8, 7, 36, 29, 54],
                ['112332', '113232', '131443', '131434', '112323', '121323', '112233', '141343', '313414', '114422'],
                [1, 1, 2, 3, 1, 0, 0, 1, 2, 1]]  # blue_tiles in Känguru-Notation
red_rainbow = [[0, 2, 3, 9, 10, 11, 22, 23, 24, 25, 41, 42, 43, 44, 45],
               [17, 37, 33, 5, 19, 1, 35, 39, 40, 16, 41, 9, 2, 31, 23],
               ['332442', '113443', '141334', '121332', '243324', '212313',
                '114433', '331441', '113344', '224343', '141433', '113223',
                '131322', '114334', '223443'], [4, 3, 1, 4, 3, 3, 5, 0, 0, 4, 1, 1, 5, 1, 1]]

pyramid1 = [21, 3, 15, 13, 5, 2, 35, 9, 18, 17, 33, 20, 10, 12, 8]  # in offizieller Notation auf Rückseite
pyramid2 = [23, 45, 25, 28, 16, 15, 13, 5, 30, 31, 33, 19, 20, 8, 7]
pyramid3 = [23, 45, 47, 49, 5, 51, 50, 6, 39, 33, 19, 54, 53, 55, 41]  # zwei Linien

Xtreme = [38, 30, 25, 42, 26, 40, 27, 12, 6, 7]  # offizielle Notation, Pyramide mit blauer/roter Linie
Xtreme_pyramid = [[0, 2, 3, 9, 10, 11, 22, 23, 24, 25], [28, 37, 40, 38, 31, 29, 33, 13, 8, 6]]  # Felder, Fliesen

# Erstellen einer Liste aller Kombinationen von 7 Elementen aus dem Vektor mit den Einträgen von 0 bis 13
# Codierung für alle möglichen Puzzles, mathematisch 14C7
all_puzzles = list(combinations([*range(14)], 7))
# all_puzzles = [list(k) for k in list(combinations([*range(14)], 7))]

parts = ((7, 0, 0, 0), (6, 1, 0, 0), (5, 2, 0, 0), (4, 3, 0, 0), (5, 1, 1, 0), (4, 2, 1, 0),
         (3, 3, 1, 0), (3, 2, 2, 0), (4, 1, 1, 1), (3, 2, 1, 1), (2, 2, 2, 1))
# Puzzles pro Partition ohne Permutation der Farbsets
puzz = [np.prod([math.comb(14, k) for k in part]) for part in parts]
# Äquivalenzklassen pro Partition
eqnums = (354, 10993, 46757, 92936, 99728, 642254, 467368, 758816, 232220, 1633820, 885538)

solc = (math.factorial(7) * (6 ** 7) * 1 / 6)  # Alle möglichen Anordnungen einer Blume

# Kombinationen der 4 Arten (xxx, xlx, xl, xc)
tile_type_combos = [(0, 0, 1, 6), (0, 0, 2, 5), (0, 0, 3, 4), (0, 1, 0, 6), (0, 1, 1, 5), (0, 1, 2, 4), (0, 1, 3, 3),
                    (0, 2, 0, 5), (0, 2, 1, 4), (0, 2, 2, 3), (0, 2, 3, 2), (0, 3, 0, 4), (0, 3, 1, 3), (0, 3, 2, 2),
                    (0, 3, 3, 1), (1, 0, 0, 6), (1, 0, 1, 5), (1, 0, 2, 4), (1, 0, 3, 3), (1, 1, 0, 5), (1, 1, 1, 4),
                    (1, 1, 2, 3), (1, 1, 3, 2), (1, 2, 0, 4), (1, 2, 1, 3), (1, 2, 2, 2), (1, 2, 3, 1), (1, 3, 0, 3),
                    (1, 3, 1, 2), (1, 3, 2, 1), (1, 3, 3, 0), (2, 0, 0, 5), (2, 0, 1, 4), (2, 0, 2, 3), (2, 0, 3, 2),
                    (2, 1, 0, 4), (2, 1, 1, 3), (2, 1, 2, 2), (2, 1, 3, 1), (2, 2, 0, 3), (2, 2, 1, 2), (2, 2, 2, 1),
                    (2, 2, 3, 0), (2, 3, 0, 2), (2, 3, 1, 1), (2, 3, 2, 0)]

# Anzahl Puzzles der Steintyp-Kombination
ncombs = (3, 18, 15, 3, 54, 135, 60, 18, 135, 180, 45, 15, 60, 45, 6, 2, 36, 90, 40, 36,
          270, 360, 90, 90, 360, 270, 36, 40, 90, 36, 2, 6, 45, 60, 15, 45, 180, 135, 18, 60, 135, 54, 3, 15, 18, 3)

# Anzahl Lösungen der 354 Äquivalenzklassen
nsols = (495, 438, 460, 481, 419, 447, 477, 456, 466, 442, 418, 490, 519, 478, 437, 517, 510, 343, 366, 479, 524, 468,
         426, 498, 470, 521, 474, 500, 428, 464, 514, 452, 502, 439, 400, 440, 493, 549, 572, 547, 501, 516, 556, 497,
         412, 416, 567, 404, 471, 409, 505, 488, 360, 293, 457, 446, 367, 475, 536, 364, 436, 527, 385, 518, 559, 492,
         458, 298, 476, 420, 462, 558, 480, 534, 312, 506, 602, 538, 454, 448, 472, 390, 429, 482, 395, 463, 513, 604,
         410, 377, 449, 363, 374, 376, 459, 453, 329, 356, 288, 539, 361, 324, 317, 236, 229, 427, 264, 551, 531, 499,
         316, 484, 415, 313, 417, 368, 310, 379, 318, 553, 467, 184, 268, 349, 348, 408, 365, 406, 441, 292, 431, 512,
         362, 335, 444, 445, 537, 393, 469, 557, 682, 520, 570, 511, 461, 291, 403, 533, 425, 372, 494, 423, 528, 451,
         455, 397, 434, 504, 574, 380, 278, 508, 382, 296, 286, 222, 302, 212, 614, 342, 634, 332, 548, 414, 764, 496,
         560, 326, 522, 338, 402, 592, 392, 486, 352, 398, 430, 344, 194, 180, 162, 388, 450, 580, 720, 386, 566)

tile_type_combo_avg = (344, 304, 262, 460, 401, 361, 302, 474, 450, 424, 376, 487, 485, 495, 512, 502, 442, 406, 357, 478, 458, 437,
                       396, 481, 474, 472, 458, 475, 487, 505, 566, 516, 479, 467, 442, 488, 477, 483, 493, 473, 477, 495, 574, 446,
                       457, 466)  # Schätzung für die Anzahl der Lösungen der Puzzles der 46 Kategorien


def generate_pairings(n):
    """Erstellt die 135135 verschiedenen Verklebungen von Vorder- und Rückseite der n = 14 Spielsteine"""

    def perfect_matchings(nums):
        if len(nums) == 2:
            yield [tuple(nums)]
        else:
            first = nums[0]
            for i in range(1, len(nums)):
                pair = (first, nums[i])
                remaining = nums[1:i] + nums[i + 1:]
                for rest in perfect_matchings(remaining):
                    yield [pair] + rest

    numbers = list(range(n))
    temp = list(perfect_matchings(numbers))
    pairings_tuple = [tuple(k[i] for k in f for i in range(2)) for f in temp]
    return pairings_tuple


def generate_tiles(tile_set):
    """
    Aus den ersten 14 Spielsteine die weiteren 42 generieren
    :param tile_set: die ersten 14 Steine codiert
    :return: array mit allen 56 Steinen richtig codiert
    """
    tiles_compl = [[list(tile_set[z]) for z in range(14)] for _ in range(4)]

    # def shift_tile(tile, offset: int):
    #     """
    #     :param tile: eine Liste mit den Farben des Spielsteins
    #     :param offset: um wie viele Stellen wird die Codierung von rechts nach links verschoben
    #     :return: das verschobene Tile
    #     """
    #     return [tile[(i + offset) % 6] for i in range(6)]
    #
    # def sort_sol(tile):
    #     """
    #     Stein-codierung richtig verschieben
    #     :param tile: Codierung eines Steins
    #     :return: korrekte Codierung
    #     """
    #     for j in range(1, 4):
    #         distance, index = get_dist(tile, j)
    #         # if 0 < distance < 3:
    #         #     tile = shift_tile(tile, index)
    #         #     break
    #         if distance in [1, 2, 4, 5]:
    #             if distance < 4:
    #                 tile = shift_tile(tile, index)
    #             else:
    #                 tile = shift_tile(tile, -index)
    #             break
    #     return tile

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


def read_num_sols_per_puzzle(filename=None):
    """Liest die Textdatei mit den Lösungen pro Puzzle aus"""
    if filename is None:
        filename = "3432.txt"
    sols_pp = []
    with open(filename, 'r') as file:
        lines = file.readlines()
    for line in lines:
        sols_pp.append(int(line))
    return tuple(sols_pp)


def read_sols_per_pairing(csv_filename=None):
    """Lösungen pro Paarung aus csv-Datei auslesen in Liste"""
    if csv_filename is None:
        csv_filename = "sols_135135_pairings.csv"
    spps = []
    with open(csv_filename, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            spps.append(int(row[1]))  # Stelle sicher, dass die Werte als Integer gespeichert werden
    return tuple(spps)


def read_sols_from_file(filename, standard=0):
    """Liest .txt aus mit Lösungen in jeder Zeile und gibt diese als list aus"""

    # def parse_line(line):
    #     """Parses a single line of the text file into a structured solution."""
    #     elements = line.strip()[1:-1].split("], [")
    #     parsed_elements = [
    #         list(map(int, elements[0][1:].split(", "))),
    #         elements[1][1:-1].split("', '"),
    #         list(map(int, elements[2][0:-1].split(", ")))
    #     ]
    #     return parsed_elements

    #
    with open(filename, 'r') as file:
        lines = file.readlines()
    #
    sols = [parse_line(line) for line in lines]
    sols = standardize_sols(sols)
    if not standard:
        if len(sols[0]) == 3:  # Eintrag für die Felder einfügen
            for sol in sols:
                sol.insert(0, [*range(len(sol[0]))])
    return sols


def write_rating_csv(directory, csv_path=None):
    """Alle Lösungen in einem Ordner bewerten und daraus csv-Dateien generieren"""

    def rate_sol(line_loop_data):
        """Funktion zur Bewertung einer Lösung, Schleifen werden doppelt gewertet im Vergleich zu Linien"""
        rating = sum([i[0] for i in line_loop_data]) + 2 * sum([i[1] for i in line_loop_data])  # Linien: Schleife 1:2
        return rating

    text_files = glob.glob(os.path.join(directory, '*.txt'))
    for text_file in text_files:
        raw_data = []
        ratings = []
        sols = read_sols_from_file(text_file, standard=0)
        for index, cand in enumerate(sols):  # Lösungen bewerten und ordnen
            raw_data.append(get_longest_connection(cand))
            ratings.append(rate_sol(raw_data[-1]))
        filename = f"{text_file.split('__')[0]}_{len(raw_data)}_{max(ratings)}.csv"
        if csv_path is not None:
            filename = os.path.join(csv_path, filename)
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            for k in range(len(ratings)):
                writer.writerow([sols[k], raw_data[k], ratings[k]])
    return None


def calc_sols_per_pairing(pairings, puzzle_list, sols_per_puzzle=None, write_csv=1, csv_path=None, top=100):
    """
    Gibt die Anzahl der Lösungen pro möglicher Verklebung an
    :param csv_path: Pfad für die csv-Datei angeben
    :param pairings: die 135135 möglichen Verklebungen, List von Tupeln
    :param sols_per_puzzle: Tupel mit Lösungen pro 3432 Puzzles
    :param puzzle_list: Liste der Tupel der 3432 möglichen Puzzles, all_puzzles
    :param write_csv: die Ergebnisse in eine csv-Datei schreiben
    :param top: die top n Verklebungn mit den meisten Lösungen
    :return: Liste mit 135135 Einträgen, erster Eintrag ist die Känguru-Verklebung mit 57.455 Lösungen
    """
    if sols_per_puzzle is None:
        sols_per_puzzle = read_num_sols_per_puzzle("3432.txt")
    sols_per_pairing = []  # die Anzahl der Lösungen je Paarung von Steinen, für Känguruversion 57.455
    for index, pairing in enumerate(pairings):  # für jede Paarung
        print(index)
        puzzles = get_puzzles(pairing)  # die 128 möglichen Puzzles pro Paarung holen, insgesamt 3432 versch. Puzzles
        sols_per_curr_pairing = 0
        for puzzle in puzzles:  # je mit der aktuellen Paarung möglichem Puzzle
            puzzle_index = puzzle_list.index(puzzle)  # Index des betrachteten Puzzles in der Liste der 3432 Puzzles
            sols_per_curr_pairing += sols_per_puzzle[puzzle_index]  # Anzahl Lösungen d. akt. Puzzles aus Liste addieren
        sols_per_pairing.append(sols_per_curr_pairing)  # Gesamtzahl der Lösungen der Verklebung der Ausgabe hinzufg.
    if write_csv:
        filename = 'sols_135135_pairings.csv'
        if csv_path is not None:
            filename = os.path.join(csv_path, filename)
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            for k in range(len(sols_per_pairing)):
                writer.writerow([pairings[k], sols_per_pairing[k]])
    spp_zippo = list(zip(pairings, sols_per_pairing))
    spp_zippo = sorted(spp_zippo, key=lambda x: x[1], reverse=True)  # Liste Paarung/Lösungen absteigend sortieren
    return spp_zippo[:top]


def write_class_data(eqs=None, sols_per_puzzle=None, filename='equivalence_classes.csv'):
    """Extrahiert die Kategorien, Summe der Lösungen,
     Indizes und Anzahl der Puzzles und speichert sie in einer CSV-Datei."""
    # Sicherstellen, dass die Äquivalenzklassen und Lösungsanzahlen generiert wurden
    if eqs is None:
        eqs = gen_classes()  # Äquivalenzklassen generieren
    if sols_per_puzzle is None:
        sols_per_puzzle = read_num_sols_per_puzzle()  # Anzahl Lösungen pro Puzzle laden
    # Sammeln der Daten für jede Klasse
    data_to_write = []
    for eq_class, puzzles in eqs.items():
        puzzle_indices = sorted([all_puzzles.index(p) for p in puzzles])  # Indizes der Puzzles in dieser Klasse
        total_solutions = sols_per_puzzle[puzzle_indices[0]]
        category = categorize_puzzle(
            all_puzzles[puzzle_indices[0]])  # (alle in der Klasse haben die gleiche Kategorie)
        num_puzzles = len(puzzles)  # Anzahl der Puzzles in der Klasse
        data_to_write.append([category, total_solutions, puzzle_indices, num_puzzles])  # Daten speichern
    data_to_write.sort(key=lambda x: (tile_type_combos.index(x[0]), -x[1]))
    # Schreiben in CSV-Datei
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Kategorie', 'Anzahl Loesungen', 'Indizes der Puzzles', 'Anzahl der Puzzles'])  # Header
        for row in data_to_write:
            writer.writerow(row)


def read_best_sols(filename, top=None):
    """
    Sucht aus einer Textdatei mit Lösungen die mit den längsten Linien/Schleifen heraus und gibt diese
    sortiert aus
    :param filename: Dateiname
    :param top: nur die top x Lösungen ausgeben
    :return: zip-Array mit (lsg, rating)
    """

    def rate_sol(line_loop_data):
        """Funktion zur Bewertung einer Lösung, Schleifen werden doppelt gewertet im Vergleich zu Linien"""
        rating = sum([k[0] for k in line_loop_data]) + 2 * sum([k[1] for k in line_loop_data])  # Linien: Schleife 1:2
        return rating

    ratings = []

    sols = read_sols_from_file(filename, standard=0)
    if top is None:  # Wie viele Lösungen sollen ausgegeben werden
        top = len(sols)
    for index, cand in enumerate(sols):  # Lösungen bewerten und ordnen
        data = get_longest_connection(cand)
        ratings.append(rate_sol(data))
    cand_rating_zip = list(zip(sols, ratings))
    cand_rating_zip = sorted(cand_rating_zip, key=lambda x: x[1], reverse=True)
    for t in range(top):
        print(cand_rating_zip[t])
    # print(cand_rating_zip)


def plot_pairing_landscape(csv_filename=None, n=5):
    """Anzahl der Lösungen der 135135 Verklebungen plotten"""
    if csv_filename is None:
        csv_filename = "sols_135135_pairings.csv"
    spps = read_sols_per_pairing(csv_filename)
    fig, ax = plt.subplots()
    ax.scatter(range(len(spps)), spps, s=3)
    ax.set_xlabel('Pairing')
    ax.set_ylabel('Solutions')
    # Setze den MaxNLocator auf der y-Achse
    ax.yaxis.set_major_locator(MaxNLocator(n))
    plt.show(block=False)


def plot_puzzle_landscape(sols_filename=None, n=10):
    """Anzahl Lösungen der 3432 Puzzles plotten"""
    if sols_filename is None:
        sols_filename = "3432.txt"
    sols_per_puzzle = read_num_sols_per_puzzle(sols_filename)
    fig, ax = plt.subplots()
    ax.scatter(range(len(sols_per_puzzle)), sols_per_puzzle, s=3)
    ax.plot(range(len(sols_per_puzzle)), [np.mean(sols_per_puzzle) for _ in range(len(sols_per_puzzle))], c='red')
    ax.set_xlabel('Puzzle Nr.')
    ax.set_ylabel('Lösungen')
    # Setze den MaxNLocator auf der y-Achse
    ax.yaxis.set_major_locator(MaxNLocator(n))
    plt.show()


def t2kang(tile_list, perm=None):
    """
    Stein-Liste von offizieller Notation in Känguru-Notation umwandeln
    :param tile_list: List der Steine in offizieller Notation
    :param perm: Permutation, welche die Notationen aufeinander abbildet
    :return: Känguru-Notation
    """
    if perm is None:
        perm = permutation
    out = [perm.index(k) for k in tile_list]
    return out


def kang2t(tile_list, perm=None):
    """
    Stein-Liste von Känguru-Notation in offizielle Notation umwandeln
    :param tile_list: List der Steine in offizieller Notation
    :param perm: Permutation, welche die Notationen aufeinander abbildet
    :return: offizielle Notation als Liste
    """
    if perm is None:
        perm = permutation
    out = [perm[k] for k in tile_list]
    return out


def col_in_tile(tile, col):
    """Farbe in Fliese enthalten ja/nein"""
    if str(col) in tile:
        return True
    return False


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


def shift_tile(tile, offset: int):
    """
    :param tile: eine Liste mit den Farben des Spielsteins
    :param offset: um wie viele Stellen wird die Codierung von rechts nach links verschoben
    :return: das verschobene Tile
    """
    return [tile[(i + offset) % 6] for i in range(6)]


# def sort_sol(tile):
#     """
#     Stein-codierung richtig verschieben
#     :param tile: Codierung eines Steins
#     :return: korrekte Codierung
#     """
#     for j in range(1, 4):
#         distance, index = get_dist(tile, j)
#         # if 0 < distance < 3:
#         #     tile = shift_tile(tile, index)
#         #     break
#         if distance in [1, 2, 4, 5]:
#             if distance < 4:
#                 tile = shift_tile(tile, index)
#             else:
#                 tile = shift_tile(tile, -index)
#             break
#     return tile


def sort_sol(tile):  # TESTEN!!!
    """
    Stein-codierung richtig verschieben
    :param tile: Codierung eines Steins
    :return: korrekte Codierung
    """
    for j in range(1, 4):
        distance, index = get_dist(tile, j)
        # if 0 < distance < 3:
        #     tile = shift_tile(tile, index)
        #     break
        if distance in [1, 2, 4, 5]:
            if distance < 4:
                tile = shift_tile(tile, index)
            else:
                tile = shift_tile(tile, index + distance)
            break
    return tile


# def rotate_sol(sol, n_rotations=1):  # bei allg. Lsg.: Ringe um den Ursprung verwenden
#     """
#     Eine eingegebene Lösung wird um eine Position im UZS rotiert
#     :param n_rotations: Anzahl der Rotationen, im UZS, falls > 0, gegen UZS, falls < 0, default 1
#     :param sol: Lösung
#     :return: rotierte Lösung
#     """
#
#     def shift_tiles(outer_tiles, offset: int):
#         """
#         :param outer_tiles: eine Liste mit den Nummern der Spielsteine
#         :param offset: um wie viele Stellen werden die Steine von rechts nach links (vlnr für offset < 0) verschoben
#         :return: die verschobenen Steine
#         """
#         return [outer_tiles[(i + offset) % 6] for i in range(6)]
#
#     tile_list = [*range(1, 7)]
#     sol_rot = copy.deepcopy(sol)
#     perm = shift_tiles(tile_list, n_rotations)
#     for j in range(1, 7):  # äußere Steine werden n_rotations Positionen in der Systematik weitergeschoben
#         sol_rot[0][j] = sol[0][perm[j - 1]]  # [(j + 4) % 6 + 1] gegen UZS
#         sol_rot[1][j] = sol[1][perm[j - 1]]  # [(j % 6) + 1] im UZS
#         sol_rot[2][j] = sol[2][perm[j - 1]]  # es muss noch rotiert werden
#     for t in range(7):  # alle (auch mittleren) Steine um n_rotations Positionen im/gegen UZS rotieren
#         sol_rot[2][t] = (sol_rot[2][t] + n_rotations) % 6
#     return sol_rot


def rotate_sol(sol, n_rotations=1):  # bei allg. Lsg.: Ringe um den Ursprung verwenden
    """
    Eine eingegebene Lösung wird um eine Position im UZS rotiert
    :param n_rotations: Anzahl der Rotationen, im UZS, falls > 0, gegen UZS, falls < 0, default 1
    :param sol: Lösung
    :return: rotierte Lösung
    """

    # def shift_tiles(outer_tiles, offset: int):
    #     """
    #     :param outer_tiles: eine Liste mit den Nummern der Spielsteine
    #     :param offset: um wie viele Stellen werden die Steine von rechts nach links (vlnr für offset < 0) verschoben
    #     :return: die verschobenen Steine
    #     """
    #     return [outer_tiles[(i + offset) % 6] for i in range(6)]
    #
    def update_field(field, ort=1):
        """Den Feldindex eines Steins aktualisieren, bool ort True, falls im UZS"""
        num = 1
        increment = 6
        if field == 0:
            return 0
        while num < field:
            if num + increment > field:
                break
            else:
                num += increment
            increment += 6
        if ort:
            if field == num:
                return num + increment - 1
            else:
                return field - 1
        else:
            if field == num + increment - 1:
                return num
            else:
                return field + 1

    #
    sol_rot = copy.deepcopy(sol)
    if len(sol_rot) == 3:
        tile_list = [*range(1, 7)]
        perm = shift_tile(tile_list, n_rotations)
        for j in range(1, 7):  # äußere Steine werden n_rotations Positionen in der Systematik weitergeschoben
            sol_rot[0][j] = sol[0][perm[j - 1]]  # [(j + 4) % 6 + 1] gegen UZS
            sol_rot[1][j] = sol[1][perm[j - 1]]  # [(j % 6) + 1] im UZS
            sol_rot[2][j] = sol[2][perm[j - 1]]  # es muss noch rotiert werden
        for t in range(7):  # alle (auch mittleren) Steine um n_rotations Positionen im/gegen UZS rotieren
            sol_rot[2][t] = (sol_rot[2][t] + n_rotations) % 6
    else:
        for k in range(len(sol[0])):
            for f in range(abs(n_rotations)):
                sol_rot[0][k] = update_field(sol_rot[0][k], np.sign(n_rotations) == 1)  # Steine weiterschieben
            sol_rot[3][k] = (sol_rot[3][k] + n_rotations) % 6  # Steine rotieren
    return sol_rot


def std(solution):  # sinnlos, Standardisierung ist für Lösungen mit Länge 4 nicht eindeutig
    """Lösung einheitlich formatieren, Orientierung des mittleren Steins ist 0"""
    temp_sol = copy.deepcopy(solution)
    out = rotate_sol(temp_sol, n_rotations=6 - solution[-1][0])
    return out


def standardize_sols(solutions):
    """Lösungen so rotieren, dass die Orientierung des mittleren Steins (Nr. 0) gleich 0 ist"""
    std_sols = []
    for solution in solutions:
        std_sols.append(std(solution))
    return std_sols


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
    plt.show(block=False)


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


def subplot_puzzles(puzzles=None, solutions=None, filename=None, grid_shape=None):
    """
    Plottet mehrere Puzzles als Subplots in einem einzigen Plot. Entweder puzzles angeben, Lösungen werden aus Datei
    solutions.txt gelesen, oder solutions direkt angeben
    :param solutions: Lösungen als Liste
    :param puzzles: Liste von Puzzles, die geplottet werden sollen
    :param filename: Dateiname, falls die Lösungen aus einer Datei gelesen werden sollen
    :param grid_shape: Form des Gitters für die Subplots (z.B. (2, 3) für 2 Zeilen und 3 Spalten)
    """

    #
    # def parse_line(line):
    #     """Parst eine einzelne Zeile der Textdatei in eine strukturierte Lösung."""
    #     elements = line.strip()[1:-1].split("], [")
    #     parsed_elements = [
    #         list(map(int, elements[0][1:].split(", "))),
    #         elements[1][1:-1].split("', '"),
    #         list(map(int, elements[2][0:-1].split(", ")))
    #     ]
    #     return parsed_elements
    #
    def read_sols(txt_filename=None):
        """Liest die Lösungen aus einer Datei."""
        if txt_filename is None:
            txt_filename = "solutions.txt"
        with open(txt_filename, 'r') as file:
            lines = file.readlines()
        return [parse_line(line) for line in lines]

    #
    if solutions is None:
        sols = read_sols(filename)
        puzzle_sols = [sols[all_puzzles.index(j)] for j in puzzles]
    else:
        puzzle_sols = solutions
    if grid_shape is None:
        # Automatische Bestimmung der Grid-Form, basierend auf der Anzahl der Puzzles
        if solutions is None:
            n_puzzles = len(puzzles)
        else:
            n_puzzles = len(solutions)
        cols = int(np.ceil(np.sqrt(n_puzzles)))
        rows = int(np.ceil(n_puzzles / cols))
    else:
        rows, cols = grid_shape
    fig, axes = plt.subplots(rows, cols, figsize=(3 * cols, 3 * rows))
    for idx, puzzle in enumerate(puzzle_sols):
        ax = axes.flat[idx] if rows * cols > 1 else axes
        draw_sol_on_axis(ax, puzzle)
    plt.tight_layout()
    plt.show(block=False)


def draw_sol_on_axis(ax, solution):
    """
    Zeichnet eine einzelne Lösung auf eine bestimmte Achse.
    :param ax: Matplotlib-Achse, auf die die Lösung gezeichnet wird
    :param solution: Lösung, welche geplottet werden soll
    """
    if len(solution) == 3:
        solution.insert(0, [*range(len(solution[0]))])
    plot_size = np.round(np.log2(len(solution[0])) + 3)  # Die Anzahl der hinzukommenden Steine pro Umlauf ist ca.
    # die Anzahl aller vorherigen Steine
    tile_size = 0.55
    #
    for index, tile in enumerate(solution[2]):
        tile_pos = solution[0][index]
        tile_orientation = solution[3][index]
        draw_hexagon(ax, tile_pos, tile_orientation, tile, tile_size)
    #
    ax.axis('equal')
    ax.axis('off')
    # ax.set_title(f"Puzzle {all_puzzles.index(tuple(sorted(solution[1])))}", fontsize=10)


def get_puzzles(tile_combo, all_tiles=None):
    """
    Von einer Variante der 7 Steine mit Vorder- und Rückseite die 2^7 = 128 Möglichkeiten,
    die Seiten der Steine zu kombinieren ausgeben als Vektoren mit den Steinenummern
    :param all_tiles: Codierung der 56 bzw. 14 Steine
    :param tile_combo: Liste mit 14 Einträgen, je zwei aufeinanderfolgende Stein-Nummern sind verklebt
    :return: alle Steinkombinationen aus Vorder- und Rückseiten, die mit dieser "Verklebung" möglich sind
    """

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
            for _ in range(leading_zero_digit - len(result)):
                result.append("0")
        result = result[::-1]
        return ''.join(result)

    if all_tiles is None:
        all_tiles = tiles_complete
    output_puzzles = []
    output_tile_nums = []
    for i in range(128):
        logical = d2b(i, 7)
        output_tile_nums.append(tuple(sorted(tile_combo[2 * k + int(logical[k])] for k in range(7))))
        # output_puzzles.append([all_tiles[k] for k in output_tile_nums[-1]])
    # return output_puzzles, output_tile_nums
    return output_tile_nums


def getColor(tile, edge, orientation):
    """
    Die Farbe einer Kante eines Steins ausgeben als int mit definierter Codierung
    :param tile: Codierung des Steins
    :param edge: Kante des Steins
    :param orientation: Rotation des Steins
    :return: Farbcode
    """
    return int(tile[(edge + orientation) % 6])


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


def gen_puzzle_from_sets(set_distribution):
    """Puzzle generieren mit Verteilung (a, b, c, d) auf die 4 Farbsets"""
    puzzle = []
    for set_index, set_num in enumerate(set_distribution):
        set_indices = random.sample([*range(set_index * 14, (set_index + 1) * 14)], k=set_num)
        puzzle += sorted(set_indices)
    return tuple(puzzle)


def gen_cand(curr, val=None, max_err=None, swap_and_rotate=1, swap_or_rotate=0,
             # anzahl swaps, rotationen von temperatur abh, und relativer Richtigkeit?!!!!
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
    """  # Positionen der Steine verändern, längste Linie einer Farbe bestimmen, Fitnessfkt anpassen

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
        # print(f"num_error_tiles: {num_error_tiles}")
        # print(f"swap_indices: {swap_indices}")
        # print(f"n_swaps: {n_swaps}")
        # print(f"most_frequent_error_tiles: {most_frequent_error_tiles}")
        # print(f"num available_swaps: {num_available_swaps}")
    swap_indices_permutation = list(np.random.permutation(swap_indices))
    # print(f"swap_indices: {swap_indices}")
    # print(f"swap_i_perm: {swap_indices_permutation}")
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
            # n_shifts = 7
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


def get_outer_fields(sol):  # fehlt: Berechnung Anzahl Berührpunkte der angrenzenden Felder mit der aktuellen Lösung
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
    # Anzahl Aussenkanten?, mit max_errors normalisieren?
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


# evtl bei 1/2 Fehler neuen Kandidaten berechnen durch Vertauschung von 2/3 Steinen?
def simulated_annealing(init_sol, n_iter, temp, param=1, morphy=0,
                        adapt_operations=0, write_data=1, print_iteration=0, cool_f=None):
    """
    Simulated annealing Algorithmus
    :param cool_f: Abkühlungsparameter
    :param adapt_operations: Anzahl Tauschs/Rotationen dynamisch anpassen mit aktueller Fehleranzahl
    :param init_sol: Startlösung
    :param n_iter: Anzahl der Schritte im Algorithmus
    :param temp: Starttemperatur
    :param param: ermöglicht Anpassungen der Temperatur (besser: direkt temp anpassen)
    :param morphy: Soll der Algorithmus versuchen, die Form der Lösung zu verändern?
    :param write_data: Sollen Daten geschrieben werden?
    :param print_iteration: Sollen Schritte geprintet werden?
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
    if obj(init_sol) == 0:
        return [init_sol, obj(init_sol), [[0] * n_iter for _ in range(10)]]
    temperatures = [get_temp(temp, k, cooling=cool_f) for k in range(n_iter)]
    data = []
    if write_data:
        data = [[0] * n_iter for _ in range(10)]
        data[0] = [*range(n_iter)]
        data[1] = temperatures
    best_sol = copy.deepcopy(init_sol)  # beste Lösung, wird am Schluss ausgegeben
    best_val = obj(best_sol)
    curr_sol, curr_val = best_sol, best_val
    max_obj = max_errors(init_sol)
    for i in range(n_iter):
        t1 = time.perf_counter()
        if best_val == 0:
            break
        cand_sol = gen_cand(curr_sol, curr_val, max_obj, swap_and_rotate=1, swap_or_rotate=0,
                            adapt_operations=adapt_operations, morphing=morphy)
        t2 = time.perf_counter()
        cand_val = obj(cand_sol)
        t3 = time.perf_counter()
        diff = cand_val - curr_val
        if print_iteration:
            print(f"Iteration #{i}, Differenz cand - curr: {diff}")
        if cand_val - best_val < 0:
            best_sol, best_val = cand_sol, cand_val
        t = temperatures[i]
        p = 0
        if diff < 0:
            p = 1
        else:
            if param is not None:
                p = calc_acceptance(param * diff, t)  # multiplikativer Parameter Optimierung? Tradeoff wenige Schritte,
            # aber seltenes Lösungsfinden
            else:
                p = np.exp(- diff / (max_obj * t))  # schlechte Idee
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
        # print(f"SIM: gen_cand: {t2 - t1}, obj: {t3 - t2}, elapsed: {t4 - t1}")
    return [best_sol, best_val, data]


def sa2(init_sol, n_iter, temp, restart_threshold=3000, max_restarts=5, focus_errors=1, morphy=0,
        adapt_operations=1, write_data=1, print_iteration=0, cool_f=None):
    # Temperatur erhöhen, falls lange Zeit keine Verbesserung stattgefunden hat, Temperatur anhalten und mehrere
    # Schritte durchführen, die Steine, welche Fehler verursachen vertauschen
    """
    Simulated annealing Algorithmus
    :param focus_errors: Generieren der Kandidaten fokussiert die Fliesen, an welchen die Fehler auftreten
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
    temp_obj = obj(best_sol, out_edges=focus_errors)
    if focus_errors:
        best_val, curr_err_edges = temp_obj
    else:
        best_val, curr_err_edges = temp_obj, None
    curr_sol, curr_val = best_sol, best_val
    max_obj = max_errors(init_sol)
    steps_at_temp = 0
    t = temperatures[0]
    temp_index = 0
    restarts = 0
    failed_steps = 0
    restart_best_val = max_obj
    for i in range(n_iter):
        if best_val == 0:
            break
        cand_sol = gen_cand(curr_sol, curr_val, max_obj, swap_and_rotate=1, swap_or_rotate=0,
                            adapt_operations=adapt_operations, morphing=morphy, err_edges=curr_err_edges)
        temp_obj = obj(cand_sol, out_edges=focus_errors)
        if focus_errors:
            cand_val, cand_err_edges = temp_obj
        else:
            cand_val, cand_err_edges = temp_obj, None
        diff = cand_val - curr_val
        if print_iteration:
            print(f"Iteration #{i}, Differenz cand - curr: {diff}")
        if cand_val - restart_best_val < 0:
            restart_best_val = cand_val
            failed_steps = 0  # Schritte zurücksetzen, solange Verbesserung pro Neustart eintritt
        if cand_val - best_val < 0:
            best_sol, best_val = cand_sol, cand_val
            restart_best_val = best_val
            failed_steps = 0
        if steps_at_temp == 0:
            # print("new temp")
            t = temperatures[temp_index]
            try:
                exp_val = np.exp((max_obj - best_val) / max(t, 1e-10))
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
                    restart_best_val = max_obj
                # else:
                # break  # Algorithmus wird abgebrochen
        print(f"fs: {failed_steps}")
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
    return [best_sol, best_val, data]


def sa3(init_sol, n_iter, temp, restart_threshold=3000, max_restarts=5, focus_errors=1, focus_color=None, morphy=0,
        adapt_operations=1, write_data=1, print_iteration=0, cool_f=None, print_params=1):
    # Temperatur erhöhen, falls lange Zeit keine Verbesserung stattgefunden hat, Temperatur anhalten und mehrere
    # Schritte durchführen, die Steine, welche Fehler verursachen vertauschen
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
                    print("leaving focus_mode")
                    focus_mode = 0
                else:
                    curr_val = focus_obj
                    if focus_errors:
                        curr_err_edges = focus_tiles
                    else:
                        curr_err_edges = None
                    print("entering focus_mode")
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
        print(f"obj: {objective}")
        if focus_color is not None:
            lens, included_tiles = get_longest_connection(cand_sol, focol=focus_color, fields=True)
            focus_tiles = [init_sol[0].index(item) for item in init_sol[0] if
                           item not in included_tiles[focus_color - 1][0]]
            focus_obj = n_tiles_with_focus_col - lens[focus_color - 1][0]
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


def plot_counter(counter):
    """Plot mit den keys und Werten eines counters plotten"""
    # Sortiere die keys für die x-Werte
    x_values = sorted(counter.keys())
    y_values = [counter[x] for x in x_values]
    plt.figure(figsize=(10, 6))
    plt.bar(x_values, y_values, color='red', alpha=0.7)
    plt.xlabel('Fehleranzahl')
    plt.ylabel('Häufigkeit')
    plt.title('Verteilung der Fehleranzahl')
    plt.xticks(x_values)
    plt.ticklabel_format(axis='y', style='sci', scilimits=(6, 6))
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    for i in range(min(len([val for val in y_values if val < 1e6]), len(x_values))):  # Falls y < 1e6
        plt.text(x_values[i], y_values[i], str(y_values[i]), ha='center', va='bottom')
    plt.show()


def random_sol_mean(n_gens, n_tiles=7, all_tiles=None, puzzle=None):
    """
    Zum Vergleich werden n_gens zufällige Lösungen generiert, und die beste Fehleranzahl ausgegeben
    :param puzzle: optionale Angabe eines Puzzles
    :param n_tiles: die Anzahl der aufsteigend verwendeten Steine
    :param n_gens: Anzahl der Generierungen einer zufälligen Lösung
    :param all_tiles: Codierung aller Spielsteine
    :return: Print
    """
    standard = False
    if n_tiles == 7:
        standard = True
    if all_tiles is None:
        all_tiles = tiles_complete
    evaluations_sum = 0
    best = n_tiles * 3  # obere Schranke für die Anzahl der Fehler
    for k in range(n_gens):
        if puzzle is None:
            sol = gen_random_sol(n_tiles=n_tiles, kangaroo=0, sample=0,
                                 ascending=0, randomness=1, standard=standard)
        else:
            sol = gen_start_sol(puzzle, standard=standard)
        sol_eval = obj(sol)
        if sol_eval < best:
            best = sol_eval
        if sol_eval == 0:
            print(f"Lösung: {sol}")
        evaluations_sum += sol_eval
    result = evaluations_sum / n_gens
    print(f"Durchschnittsfehleranzahl bei zufälliger Generierung von {n_gens} Lösungen: {result}")
    print(f"Beste Fehleranzahl bei zufälliger Generierung von {n_gens} Lösungen: {best}")


def find_temp(steps, lim_low, lim_up, stepsize, n_runs, sol=None, all_tiles=None):
    """
    Den Parameter, der bestimmt, wie schnell die Annahmewahrscheinlichkeit für schlechtere Lösungen sinkt
    versuchen zu optimieren
    :param sol: eine beliebige Lösung
    :param steps: Schritte Alg.
    :param lim_low: untere Grenze der Starttemperatur
    :param lim_up: obere Grenze
    :param stepsize: Schrittweite des Parameters
    :param n_runs: Anzahl Durchläufe pro Parameter-Kandidat
    :param all_tiles: Codierung aller Spielsteine
    :return: array mit Ergebnissen, kann geplottet werden
    """
    if all_tiles is None:
        all_tiles = tiles_complete
    temperatures = np.arange(lim_low, lim_up, stepsize)
    temp_results = [[0] * len(temperatures) for _ in range(3)]
    for index, temp in enumerate(temperatures):
        sol_found = 0
        sum_steps = 0
        for k in range(n_runs):
            if sol is None:
                sol = gen_random_sol(n_tiles=7, kangaroo=0, sample=1, ascending=0, randomness=0, standard=1)
            _, _, data = simulated_annealing(sol, steps, temp, param=1, morphy=0,
                                             adapt_operations=0, write_data=1, print_iteration=0)
            if 0 in data[3]:
                sol_found += 1
                sum_steps += data[3].index(0)  # Anzahl der Schritte bis zum Finden der Lösung
        temp_results[0][index] = temp  # param ändert nur Temperatur durch Skalar
        temp_results[1][index] = sol_found / n_runs
        temp_results[2][index] = sum_steps / int(sol_found) if sol_found != 0 else 0  # n_runs
    return temp_results


def plot_temp_over_rate(temp_results):
    """find_temp results plotten"""
    plt.plot(temp_results[0], temp_results[1])
    plt.xlabel('Starting temperature')
    plt.ylabel('% of successful runs')
    plt.ylim(0, 1.1)
    # plt.legend()
    # plt.title(datetime.datetime.now().time())
    plt.title("14C7, swap-and-rotate=1, Abstufung obj: 1")
    plt.show()


def plot_temp_over_n_steps(temp_results):
    """find_temp results plotten"""
    plt.plot(temp_results[0], temp_results[2])
    plt.xlabel('Starting temperature')
    plt.ylabel('# of steps to solution if successful')
    plt.ylim(0, max(temp_results[2]))
    # plt.legend()
    # plt.title(datetime.datetime.now().time())
    plt.title("14C7, swap-and-rotate=1, Abstufung obj: 1")
    plt.show(block=False)


def solve_flowers(puzzles, all_tiles, n_iter, temp, write_file=0, filename="solutions.txt", path=None):
    """
    Versucht alle Blumenpuzzles zu lösen (eine Lösung zu finden)
    :param path: Pfad zum Abspeichern der Lösungen
    :param puzzles: alle 3432 möglichen Blumenpuzzles
    :param all_tiles: die Codierung aller 56 Steine
    :param n_iter: Schrittanzahl
    :param temp: Temp. Alg.
    :param write_file: boolean Lösungen in .txt schreiben
    :param filename: Textdateiname
    :return: array mit Lösungen [0] und Fehlerwert [1]
    """
    flower_results = [[0] * len(puzzles) for _ in range(4)]
    for index, puzzle in enumerate(puzzles):
        attempts = 0
        opt_val = 1
        opt_sol = []
        datastream = []
        starting_sol = gen_start_sol(list(puzzle), standard=1, all_tiles=all_tiles)
        while opt_val > 0 and attempts < 10:
            opt_sol, opt_val, datastream = simulated_annealing(starting_sol, n_iter, temp,
                                                               morphy=0, write_data=1)
            attempts += 1
        flower_results[0][index] = opt_sol  # Optimallösung
        flower_results[1][index] = opt_val  # bester Fehlerwert
        if opt_val == 0:
            flower_results[2][index] = datastream[3].index(0)  # Anzahl Schritte bis zur Lösung, falls erfolgreich
        else:
            flower_results[2][index] = -1
        flower_results[3][index] = attempts
        print(index)
    flower_results[0] = standardize_sols(flower_results[0])
    if write_file:
        if path is not None:
            filename = os.path.join(path, filename)
        with open(filename, 'w') as file:
            # file.write("Lösungen für 3432 Puzzles\n\n")
            for k in range(len(flower_results[0])):
                line = str(flower_results[0][k])
                file.writelines(line)
                file.writelines("\n")
    return flower_results


def plot_flower_results(flower_results):
    """
    Plottet Anzahl der Schritte bis zum Finden der Lösung aller Puzzles
    :param flower_results: Ergebnisse aus solve_flowers
    :return:
    """
    plt.scatter([*range(0, len(flower_results[0]))], flower_results[2])
    plt.xlabel('Puzzle No.')
    plt.ylabel('# of steps if successful')
    plt.ylim(0, max(flower_results[2]))
    # plt.legend()
    plt.title(datetime.datetime.now().time())
    plt.show()


def plot_flower_attempts(flower_results):
    """
    Plottet für jedes Puzzle die Anzahl der Versuche bis zum Finden einer Lösung
    :param flower_results: Ergebnisse aus solve_flowers
    :return:
    """
    plt.plot([*range(0, len(flower_results[0]))], flower_results[3])
    plt.xlabel('Puzzle No.')
    plt.ylabel('# of attempts to solution')
    plt.ylim(1, max(flower_results[3]))
    # plt.legend()
    plt.title(datetime.datetime.now().time())
    plt.show()


def find_all_flower_sols(puzzle, attempts, n_iter, temp,
                         write_file=0, filename=None, all_tiles=None):
    """
    Findet so viele verschiedene Lösungen eines Blumenpuzzles wie möglich
    :param puzzle: Steinnummern, welche das Puzzle definieren, als array
    :param attempts: Anzahl der Durchläufe
    :param all_tiles: array mit allen 56 Codierungen der Steine
    :param n_iter: Schrittanzahl Alg.
    :param temp: Temperatur Alg.
    :param write_file: boolean, ob Lösungen in .txt geschrieben werden sollen
    :param filename: Name der Textdatei
    :return: array mit den gefundenen Lösungen
    """
    if all_tiles is None:
        all_tiles = tiles_complete
    solutions = [[] for _ in range(2)]
    for k in range(attempts):
        # print(f"Versuch {k}")
        starting_sol = gen_start_sol(list(puzzle), standard=0, fields=None,  # standard=1, falls blumen gelöst werden
                                     all_tiles=all_tiles)  # nur einmal generieren?
        opt_sol, opt_val, _ = simulated_annealing(starting_sol, n_iter, temp, morphy=0, write_data=0)
        if opt_val == 0:
            if len(solutions[0]) == 0:
                solutions[0].append(std(opt_sol))
                solutions[1].append(k + 1)
            else:
                if std(opt_sol) not in solutions[0]:
                    solutions[0].append(std(opt_sol))
                    solutions[1].append(k + 1)
    # solutions[0] = standardize_sols(solutions[0])
    print(f"Gefundene Lösungen: {len(solutions[0])}")
    if len(solutions[0]) > 0:
        print(f"Letzter erfolgreicher Durchlauf: {solutions[1][-1]}")  # wann wurde die letzte Lösung gefunden
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
    return solutions[0]


def find_unsolvable_flower(attempts_to_solve, attempts_to_search, n_iter, temp):
    """
    Versucht, ein Blumenpuzzle zu finden, welches auch nach 10 Anläufen nicht gelöst werden kann, Verdacht
    auf Unlösbarkeit?
    :param attempts_to_solve: Maximale Versuche, bis Unlösbarkeit angenommen wird und Funktion abbricht
    :param attempts_to_search: Anzahl an Kandidaten die auf Unlösbarkeit untersucht werden
    :param n_iter: Anzahl Schritte für den Algorithmus
    :param temp: Temperatur
    :return: "Unlösbares" Puzzle oder maximale Anzahl an Versuchen bis zur Lösung
    """
    max_attempts = 0
    max_sol = []
    for k in range(attempts_to_search):
        print(f"Attempt #{k}")
        sol = gen_random_sol(n_tiles=7, kangaroo=0, sample=0, ascending=0, randomness=1, standard=1)
        sol_val = obj(sol)
        counter = 0
        while counter < attempts_to_solve and sol_val > 0:
            sol, sol_val, _ = simulated_annealing(sol, n_iter, temp, morphy=0, adapt_operations=0, write_data=0)
            counter += 1
            if counter > max_attempts:
                max_attempts = counter
                max_sol = sol
        if counter == attempts_to_solve:
            sol.insert(0, [*range(7)])
            print(sol)
            return
    print(f"Kein unlösbares Puzzles gefunden, meiste Versuche: {max_attempts} für: {max_sol}")


def find_minimum_sols(attempts_to_search, attempts_to_solve, threshold, n_iter, temp, path=None):
    """
    Blumen mit möglichst wenigen Lösungen finden
    :param attempts_to_search: Versuche, eine entsprechende Blume zu finden
    :param attempts_to_solve: Anzahl Versuche, Blume zu lösen
    :param threshold: obere Grenze für die Anzahl der Lösungen
    :param n_iter:
    :param temp:
    :param path: Pfad für .txt-Datei
    :return:
    """

    def gen_mixed_puzzle():
        pz = []
        counter_ = 7
        for i in range(4):
            if counter_ == 0:
                break
            if i < 3:
                random_counter = np.random.randint(1, 4)
            else:
                random_counter = counter_
            pz += random.sample([*range(i * 14, (i + 1) * 14)], k=min(counter_, random_counter))
            counter_ -= min(counter_, random_counter)
        return pz

    #
    for k in range(attempts_to_search):
        sols = []
        print(f"Attempt #{k}")
        puzzle = gen_mixed_puzzle()
        sol = gen_start_sol(puzzle, standard=1)
        sol_val = obj(sol)
        attempts_counter = 0
        while attempts_counter < attempts_to_solve:
            sol, sol_val, _ = simulated_annealing(sol, n_iter, temp, morphy=0, adapt_operations=0, write_data=0)
            if sol_val == 0 and std(sol) not in sols:
                sols.append(std(sol))
            if len(sols) > threshold:
                break
            attempts_counter += 1
        if attempts_counter < attempts_to_solve:  # nur falls mit break aus der while Schleife gegangen wurde
            continue
        filename = f"{len(sols)}__{attempts_to_search}.txt"
        if path is not None:
            filename = os.path.join(path, filename)
        with open(filename, 'w') as file:
            if len(sols) == 0:
                file.write(str(sol) + '\n')
            for line in sols:
                file.write(str(line) + '\n')
        break


def parse_line(line):
    """Parst eine einzelne Zeile der Textdatei (string) in eine strukturierte Lösung."""
    elements = line.strip()[1:-1].split("], [")
    parsed_elements = [
        list(map(int, elements[0][1:].split(", "))),
        elements[1][1:-1].split("', '"),
        list(map(int, elements[2][0:-1].split(", ")))
    ]
    return parsed_elements


def elim_ident(filename):
    """
    Eliminiert doppelte Einträge in einer Textdatei.

    :param filename: Der Name der Textdatei.
    :return: Keine.
    """

    # def parse_line(line):
    #     """Parses a single line of the text file into a structured solution."""
    #     elements = line.strip()[1:-1].split("], [")
    #     parsed_elements = [
    #         list(map(int, elements[0][1:].split(", "))),
    #         elements[1][1:-1].split("', '"),
    #         list(map(int, elements[2][0:-1].split(", ")))
    #     ]
    #     return parsed_elements

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


# def std(solution, standard=1):
#     """Lösung einheitlich formatieren, Orientierung des mittleren Steins ist 0"""
#     if not standard:
#         temp_sol = copy.deepcopy(solution[1:])
#     else:
#         temp_sol = copy.deepcopy(solution)
#     out = rotate_sol(temp_sol, n_rotations=6 - solution[-1][0])
#     if not standard:
#         out.insert(0, [*range(len(out[0]))])
#     return out


def find_sol_rand(runs, puzzle=None, conf=0.95):
    """
    Versucht, von einem Puzzle eine Lösung durch reines Ausprobieren aller Möglichkeiten zu finden
    :param runs: Anzahl der Versuche (ein Versuch läuft bis eine Lösung gefunden wurde)
    :param puzzle: optional ein Puzzle welches gelöst werden soll
    :param conf: Konfidenz für die Angabe der Anzahl der Lösungen des Puzzles auf Grundlage der durchschnittlichen
                 Anzahl an benötigten Schritten bis zum Finden einer Lösung
    :return: Durchschnittswert bis zum Finden einer Lösung, Generierungen bis Lösung pro Versuch als array
    """
    attempts = 0
    steps = []
    if puzzle is None:
        curr = gen_random_sol(n_tiles=7, kangaroo=1, sample=0, ascending=0, randomness=0, standard=1)
    else:
        curr = gen_start_sol(puzzle, standard=1)
    for i in range(runs):
        run_steps = 0
        print(i)
        current_score = 1
        # curr = []
        while current_score > 0:
            curr = gen_start_sol(curr[0], standard=1)
            current_score = obj(curr)
            run_steps += 1
        print(curr)
        attempts += run_steps
        steps.append(run_steps)
    avg = attempts // runs
    std_var = np.std(steps)
    print(f"Anzahl Lsg. approx: {solc // avg:.0f}, Konfidenzintervall auf {conf}:"
          f" +/- {(np.sqrt(1 - conf) * solc) / std_var:.0f}")
    print(f"Mittelwert: {avg}")
    print(f"Standardabweichung: {std_var:.0f}")
    print(steps)
    return avg, steps


def find_pyramid_rand(attempts, all_tiles=None):
    """
    Das unsolved Loop Puzzle durch zufällige Generierungen versuchen zu lösen
    :param attempts: Versuche
    :param all_tiles: Steine
    :return: Plot
    """
    if all_tiles is None:
        all_tiles = tiles_complete
    data = [[] for _ in range(2)]
    pyramid_fields = [0, 1, 2, 3, 9, 10, 11, 22, 23, 24, 25, 41, 42, 43, 44, 45, 66, 67, 68, 69, 70, 71,
                      97, 98, 99, 100, 101, 102, 103, 134, 135, 136, 137, 138, 139, 140, 141, 177, 178, 179,
                      180, 181, 182, 183, 184, 185, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235]

    opt_val = obj(gen_start_sol([*range(56)], fields=pyramid_fields))
    for k in range(attempts):
        cand = gen_start_sol([*range(56)], fields=pyramid_fields)
        cand_val = obj(cand)
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
    plt.show(block=False)
    return None


def flower_one_tile(all_tiles=None):
    """Blumen mit nur einem einzigen Stein finden"""
    if all_tiles is None:
        all_tiles = tiles_complete
    vals = []
    for k in range(len(all_tiles)):
        print(f"Blume: {k}")
        sol = gen_start_sol([k for _ in range(7)], standard=1, all_tiles=all_tiles)
        sol, val, _ = simulated_annealing(sol, 25000, 500, param=1, morphy=0,
                                          adapt_operations=0, write_data=0, print_iteration=0)
        sol = std(sol)
        draw_sol(sol)
        vals.append(val)
        print(val)
    for g in range(4):
        print(vals[g * 14:g * 14 + 14])
    print("\n")
    print(sum(vals))


def try_puzzle(sol, steps, temp, attempts=-1):
    """Versucht ein Puzzle zu lösen, bis es fehlerfrei ist oder die optionale Anzahl der
     maximalen Versuche überschritten wurde"""
    itcounter = 0
    dolo = 1
    best_dolo = obj(sol)
    best_solo = sol
    solo = sol
    while dolo > 0:
        itcounter += 1
        solo, dolo, _ = simulated_annealing(sol, steps, temp, morphy=0, write_data=0, print_iteration=False)
        print(f"it: {itcounter}, obj: {dolo}")
        if dolo < best_dolo:
            best_solo = solo
            best_dolo = dolo
        if itcounter == attempts:
            print(f"No solution found after {itcounter} attempts")
            print(f"Best val: {best_dolo}, sol: {best_solo}")
            return
    print(solo)


def calc_all_sols_prob(n, k):
    """Wahrscheinlichkeit, nach k (erfolgreichen) Durchläufen von
     einem Puzzle mit n Lösungen alle einmal gefunden zu haben"""
    if k < 5 * n:
        return 0
    total_sum = 0
    for i in range(1, n + 1):
        term = ((-1) ** (n - i)) * math.comb(n, i) * ((i / n) ** k)
        total_sum += term
    return total_sum


def calc_all_sols_expected(n):
    """Erwartungswert berechnen für die Anzahl der Versuche bis zum einmaligen Finden jeder der n Lösungen"""

    def harmonic_number(m):
        """Berechnet die n-te harmonische Zahl"""
        return sum(1 / k for k in range(1, m + 1))

    return int(n * harmonic_number(n))


def plot_probabilities(n1, n2, cutoff1, cutoff2, max_k1, max_k2):
    """Sammelbild-Problem-Wahrscheinlichkeiten plotten"""

    def calc_all_sols_prob_with_cutoff(n, k, cutoff):
        """Wahrscheinlichkeit mit unterer Grenze. Setzt die Wahrscheinlichkeit auf Null, wenn k < cutoff."""
        if k < cutoff:
            return 0
        return calc_all_sols_prob(n, k)

    ks1 = list(range(0, max_k1 + 1, 20))  # Nur alle 10 Schritte berechnen
    ks2 = list(range(0, max_k2 + 1, 20))  # Nur alle 10 Schritte berechnen
    probs1 = [calc_all_sols_prob_with_cutoff(n1, k, cutoff1) for k in ks1]
    probs2 = [calc_all_sols_prob_with_cutoff(n2, k, cutoff2) for k in ks2]
    plt.plot(ks1, probs1, label=f'n={n1}')
    plt.plot(ks2, probs2, label=f'n={n2}')
    plt.axhline(y=0.99, color='r', linestyle='--', label='P = 0.99')
    plt.xlim(0, 10000)
    plt.xlabel('Versuche')
    plt.ylabel('Wahrscheinlichkeit')
    # plt.title('Probability of Finding All Solutions')
    plt.legend()
    plt.grid(True)
    plt.show()


# def examine_pairings(all_pairings):
#     """Paarung(en) untersuchen"""
#     results = [[] for _ in range(3)]
#     used_puzzles = []
#     sols_per_puzzle = read_num_sols_per_puzzle()
#     for pairing in all_pairings:
#         puzzles = get_puzzles(pairing)
#         pindices = [all_puzzles.index(i) for i in puzzles]
#         for p in pindices:
#             if p not in used_puzzles:
#                 used_puzzles.append(p)
#         spp = [sols_per_puzzle[k] for k in pindices]
#         results[0].append(min(spp))
#         results[1].append(max(spp))
#         results[2].append(np.var(spp))
#     return results, len(used_puzzles)


def bootstrap(sample, n_resamples=1000, conf=0.95, resample_size=None):
    """
    Aus einer Stichprobe ein Konfidenzintervall erstellen durch Bootstrap (Perzentil-Methode)
    :param resample_size: wie groß soll die Bootstrap-SP sein?
    :param sample: Stichprobe
    :param n_resamples: Anzahl an Ziehungen aus der SP
    :param conf: Konfidenzniveau
    :return: Konfidenzintervall, Mittelwert und Varianz der neuen Stichproben
    """
    bootstrap_means = []
    if resample_size is None:
        resample_size = len(sample)
    for _ in range(n_resamples):
        bootstrap_sample = np.random.choice(sample, size=resample_size, replace=True)
        bootstrap_means.append(np.mean(bootstrap_sample))
    conf_int = solc / np.percentile(bootstrap_means, [(1 - conf) / 2 * 100, (conf + ((1 - conf) / 2)) * 100])
    bootstrap_mm = np.mean(bootstrap_means)
    bootstrap_std = np.std(bootstrap_means)
    return [conf_int, bootstrap_mm, bootstrap_std]


def find_indices(lst, val):
    """Alle Indizes eines Wertes in einer Liste ausgeben"""
    return [index for index, num in enumerate(lst) if num == val]


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


def dissect_sol_numbers(filename=None, sols_per_puzzle=None):
    """Es gibt math.comb(14, 7) = 3432 Puzzles mit zwischen 162 und 764 Lösungen, insgesamt gibt es 197 verschiedene
    Anzahlen an Lösungen. Auf welche Typen von Steinen verteilen sich die 197 Anzahlen, Vermutung: eine Zahl gehört
    zu einer eindeutigen Kombination an Stein-Typen"""
    tile_type_freqs = []
    if sols_per_puzzle is None:
        sols_per_puzzle = read_num_sols_per_puzzle(filename)
    counter = Counter(sols_per_puzzle)  # dict mit Anzahl Lösungen und auftretender Häufigkeit
    num_sols = [el for el, count in counter.most_common()]  # die einzigartigen Anzahlen an Lösungen
    for num in num_sols:
        indices = find_indices(sols_per_puzzle, num)  # Puzzle Nummern mit bestimmter Anzahl an Lösungen
        puzzles = [all_puzzles[i] for i in indices]  # Steinnummern der betreffenden Puzzles
        categories = [categorize_puzzle(j) for j in puzzles]  # Klassierung der Puzzles in Form [ccc, clc, xl, xc]
        tile_type_freqs.append(Counter(categories))  # Klassierungen durchzählen
    return tile_type_freqs


def dissect_tile_type_combos(filename=None, sols_per_puzzle=None):
    """Die 46 verschiedenen Zusammensetzungen der 7 Steine untersuchen auf die Anzahl der Lösungen der damit
    auftretenden Puzzles"""
    if sols_per_puzzle is None:
        sols_per_puzzle = read_num_sols_per_puzzle(filename)
    all_cats = [categorize_puzzle(i) for i in all_puzzles]  # die 3432 Puzzles kategorisieren
    type_sols_table = []
    for tcomb in tile_type_combos:
        indices = find_indices(all_cats, tcomb)  # jede Kombination suchen
        num_sols = [sols_per_puzzle[j] for j in indices]  # Anzahl Lösungen speichern
        freqs = Counter(num_sols)  # Häufigkeiten analysieren
        type_sols_table.append(freqs)
    return type_sols_table


def get_sols_per_pairing(pairing, filename=None, sols_per_puzzle=None):
    """Liste ausgeben mit den Anzahlen der Lösungen der 128 Puzzles einer Verklebung"""
    spp = []
    if sols_per_puzzle is None:
        sols_per_puzzle = read_num_sols_per_puzzle(filename)
    puzzles = get_puzzles(pairing)
    for puzzle in puzzles:
        index = all_puzzles.index(puzzle)
        spp.append(sols_per_puzzle[index])
    return spp


def weighted_sol_avg_tile_type_combo():
    """Gewichteten Durchschnitt an Lösungen für jeden der 46 Typen
    Counter({222: 6, 342: 6, 180: 3}) für Typ (0, 0, 3, 4) wird zu
    (222 * 6 + 342 * 6 + 180 * 3) / (6 + 6 + 3) = 261.6
    als tile_type_combo_avg definiert"""
    tt = dissect_tile_type_combos(None)
    type_avg = []
    for index, counter in enumerate(tt):
        temp_list = list(counter.items())
        weighted_sum = 0
        for val, fq in temp_list:
            weighted_sum += val * fq
        type_avg.append(weighted_sum // ncombs[index])
    return type_avg


def estimate_sols_tile_type_combo(puzzle):
    """Die Anzahl der Lösungen eines Puzzles schätzen über die Zusammensetzung der Arten der Steine"""
    ttype = categorize_puzzle(puzzle)
    return tile_type_combo_avg[tile_type_combos.index(ttype)]


def plot_sols_vs_type_estimation(filename=None, sols_per_puzzle=None):
    """Plot: Tatsächliche Lösungszahl vs. Vorhersagen der Schätzung über Steinzusammensetzung des Puzzles"""
    if sols_per_puzzle is None:
        sols_per_puzzle = read_num_sols_per_puzzle(filename)
    estimations = [estimate_sols_tile_type_combo(p) for p in all_puzzles]
    plt.figure(figsize=(10, 6))
    plt.plot(sols_per_puzzle, label='Tatsächliche Lösungszahl', marker='o')
    plt.plot(estimations, label='Vorhersage', marker='x')
    plt.xlabel('Datenpunkt')
    plt.ylabel('Lösungen')
    plt.title('Tatsächliche Lösungen vs. Vorhersagen der Schätzung')
    plt.legend()
    plt.show()


def print_sol_numbers(sn=None):
    """Tabelle mit Anzahl der Lösungen und der Zusammensetzung aus den Kombinationen zeilenweise ausgeben"""
    if sn is None:
        sn = dissect_sol_numbers()
    for index, n in enumerate(sn):
        print(f"{nsols[index]}: {n}")


def print_tile_type_combos(tt):
    """Tabelle mit den Typen der Zusammensetzung der Puzzles und den Anzahlen der Lösungen ausgeben"""
    if tt is None:
        tt = dissect_tile_type_combos()

    def sort_counters(counter_list):
        sorted_counters = []
        for counter in counter_list:
            sorted_items = sorted(counter.items(), key=lambda x: (-x[1], -x[0]))  # Sortieren nach Anzahl und Schlüssel
            sorted_counters.append(sorted_items)
        return sorted_counters

    stt = sort_counters(tt)
    for index, t in enumerate(stt):
        print(f"{tile_type_combos[index]}: {t}")


def cat_all_puzzles():
    """Alle 3432 Puzzles einteilen in die 46 Kategorien (ccc, clc, xl, xc)"""
    return [categorize_puzzle(i) for i in all_puzzles]


def count_puzzle_curves(puzzle, ncolors=3):
    """Anzahl der 120/60/0-Grad Kurven eines Puzzles"""
    curve_nums = [[0, 0, 0] for _ in range(ncolors)]  # pro Puzzle
    tile_codes = [tiles_complete[i] for i in puzzle]
    for tile in tile_codes:
        for color in range(1, 5):
            if str(color) in tile:
                dist, _ = get_dist(tile, color)
                if dist > 3:
                    dist = 6 - dist
                curve_nums[color - 1][dist - 1] += 1
    return curve_nums


def count_all_puzzles_curves():
    """3432 Puzzles nach Kurven kategorisieren"""
    return [count_puzzle_curves(puzzle) for puzzle in all_puzzles]


def get_curves_from_cat(type_combo, ncolors=3, sols_per_puzzle=None, filename=None):
    """
    Gibt die Anzahl der 120/60/0-Grad Kurven einer Kategorie mit ihren zugehörigen Lösungssummen an
    :param type_combo: (ccc, clc, xl, xc)
    :param ncolors: Anzahl der Farben, default 3
    :param filename: Dateiname mit Anzahl der Lösungen pro Puzzle
    :param sols_per_puzzle: Lösungen pro Puzzle
    :return:
    """
    tt = dissect_tile_type_combos()
    if sols_per_puzzle is None:
        sols_per_puzzle = read_num_sols_per_puzzle(filename)
    num_sols = [el for el, count in tt[tile_type_combos.index(type_combo)].most_common()]
    all_cats = cat_all_puzzles()
    curve_per_all_sols = []
    for num in num_sols:
        curve_per_sols = []  # pro Anzahl Lösungen
        puzzles = [all_puzzles[i] for i in find_indices(all_cats, type_combo) if sols_per_puzzle[i] == num]
        for puzzle in puzzles:
            curve_nums = count_puzzle_curves(puzzle, ncolors)
            curve_per_sols.append(curve_nums)
        curve_per_all_sols.append(curve_per_sols)
    return curve_per_all_sols


def calc_sum_types(type_combo):
    """Kurven zählen aus einer Zusammensetzung (ccc, clc, xl, xc)"""
    vecs = np.array([[3, 0, 0], [2, 0, 1], [1, 2, 0], [0, 2, 1]])
    res = np.array([0, 0, 0])
    for index, tt in enumerate(type_combo):
        res += tt * vecs[index]
    return tuple(res)


# def plot_sols_distribution_with_normal(filename=None):
#     """
#     Plottet die relative Häufigkeit der eindeutigen Werte aus `sols_per_puzzle` (Anzahl Lösungen)
#     und eine Normalverteilungsdichtefunktion.
#     """
#     sols_per_puzzle = read_num_sols_per_puzzle(filename)
#     sn = count_elt_freq(sols_per_puzzle)
#     # Berechnung von Mittelwert und Standardabweichung
#     mean = np.mean(sols_per_puzzle)
#     std_dev = np.std(sols_per_puzzle)
#     # Berechnung der relativen Häufigkeiten
#     total = len(sols_per_puzzle)
#     rel_freq = {k: v / total for k, v in sn.items()}
#     # Erstellen der x-Werte für den Normalverteilungsplot
#     x_values = np.linspace(min(sols_per_puzzle), max(sols_per_puzzle), 100)
#     normal_distribution = norm.pdf(x_values, mean, std_dev)
#     # Plotten der relativen Häufigkeitsverteilung
#     plt.figure(figsize=(10, 6))
#     plt.bar(rel_freq.keys(), rel_freq.values(), width=0.9, alpha=0.6, label='Relative Häufigkeit der Lösungssumme')
#     # Plotten der Normalverteilungsdichtefunktion
#     plt.plot(x_values, normal_distribution, color='red', label='Normalverteilungsdichtefunktion')
#     # Achsenbeschriftungen und Titel
#     plt.xlabel('Werte')
#     plt.ylabel('Relative Häufigkeit / Dichte')
#     plt.title('Verteilung der Lösungsanzahl mit Normalverteilungsdichtefunktion')
#     plt.legend()
#     # Plot anzeigen
#     plt.show(block=False)


def get_puzzle_sols(puzzle, filename=None, sols_per_puzzle=None):
    """Anzahl Lösungen eines Puzzles ausgeben"""
    if sols_per_puzzle is None:
        sols_per_puzzle = read_num_sols_per_puzzle(filename)
    return sols_per_puzzle[all_puzzles.index(puzzle)]


def get_puzzles_of_cat(cat, numsols=None, filename=None, sols_per_puzzle=None):
    """Puzzles einer Kategorie (optional: Anzahl Lsg) ausgeben"""
    all_cats = cat_all_puzzles()  # die 3432 Puzzles kategorisieren
    if sols_per_puzzle is None:
        sols_per_puzzle = read_num_sols_per_puzzle(filename)
    if numsols is not None:
        return [all_puzzles[i] for i in find_indices(all_cats, cat) if sols_per_puzzle[i] == numsols]
    else:
        return [all_puzzles[i] for i in find_indices(all_cats, cat)]


def gen_classes():
    """Alle 3432 Puzzles in Äquivalenzklassen bezüglich Permutation der Farben und Spiegelung der Steine einteilen"""
    # Alle möglichen Permutationen der Farben
    perms = list(permutations('123'))

    def mirror(tile):
        """Funktion zum Spiegeln eines Steins (Reihenfolge umkehren)"""
        return tile[::-1]

    #
    #
    # def sort_sol(tile):  # TESTEN!!!
    #     """
    #     Stein-codierung richtig verschieben
    #     :param tile: Codierung eines Steins
    #     :return: korrekte Codierung
    #     """
    #     for j in range(1, 4):
    #         distance, index = get_dist(tile, j)
    #         # if 0 < distance < 3:
    #         #     tile = shift_tile(tile, index)
    #         #     break
    #         if distance in [1, 2, 4, 5]:
    #             if distance < 4:
    #                 tile = shift_tile(tile, index)
    #             else:
    #                 tile = shift_tile(tile, index + distance)
    #             break
    #     return tile

    def apply_permutation(tile, perm):
        """Funktion zum Anwenden einer Farbpermutation auf einen Stein"""
        return ''.join(perm[int(color) - 1] for color in tile)

    # def generate_equivalent_tiles(tile):
    #     """Funktion zum Generieren aller äquivalenten Steine eines gegebenen Steins"""
    #     equivalent_tiles = set()
    #     for perm in perms:
    #         # Ursprünglicher Stein
    #         permuted_tile = apply_permutation(tile, perm)
    #         sorted_tile = sort_sol(permuted_tile)  # Sortiere den Stein
    #         sorted_tile = ''.join(sorted_tile)  # Join zurück zu einem String
    #         equivalent_tiles.add(sorted_tile)
    #         # Gespiegelter Stein
    #         mirrored_tile = mirror(permuted_tile)
    #         sorted_mirrored_tile = sort_sol(mirrored_tile)  # Sortiere den Stein
    #         sorted_mirrored_tile = ''.join(sorted_mirrored_tile)  # Join zurück zu einem String
    #         equivalent_tiles.add(sorted_mirrored_tile)
    #     return equivalent_tiles

    def generate_equivalent_puzzles(pz):
        """Funktion zum Generieren aller äquivalenten Puzzles"""
        equivalent_puzzles = set()
        for perm in perms:
            # Anwenden der Permutation auf alle Steine im Puzzle
            permuted_puzzle = tuple(
                sorted(tiles.index(''.join(sort_sol(apply_permutation(tiles[i], perm)))) for i in pz))
            equivalent_puzzles.add(permuted_puzzle)
            # Spiegeln der permutierten Steine
            mirrored_puzzle = tuple(
                sorted(tiles.index(''.join(sort_sol(mirror(apply_permutation(tiles[i], perm))))) for i in pz))
            equivalent_puzzles.add(mirrored_puzzle)
        return equivalent_puzzles

    # Äquivalenzklassen bilden
    equivalence_classes = defaultdict(set)
    for puzzle in all_puzzles:
        eq_puzzles = generate_equivalent_puzzles(puzzle)
        # Finde eine kanonische Darstellung (z.B. das lexikographisch kleinste Puzzle)
        canonical_puzzle = min(eq_puzzles)
        equivalence_classes[canonical_puzzle].update(eq_puzzles)
    return equivalence_classes


def find_eq_class(puzzle, classes=None):
    """
    Findet die Äquivalenzklasse eines gegebenen Puzzles.
    :param classes: Äquivalenzklassen
    :param puzzle: Tuple oder Liste, das die Indizes des Puzzles darstellt.
    :return: Äquivalenzklasse des Puzzles (Liste der Puzzles, die äquivalent sind)
    """
    if classes is None:
        classes = gen_classes()
    for key in classes:
        if puzzle in classes[key]:
            # return classes[key]
            return key
    return None  # Falls das Puzzle in keiner Äquivalenzklasse gefunden wird


def printl(array):
    """Elemente zeilenweise ausgeben"""
    for i in array:
        print(i)


def dissect_classes(tt=None, eqs=None):
    """Die Klassen mit 18, 24 oder 30 Puzzles weiter aufspalten"""
    dissection = [[] for _ in range(3)]
    if eqs is None:
        eqs = gen_classes()
    if tt is None:
        tt = dissect_tile_type_combos()
    for index, cat in enumerate(tt):
        for key in list(cat):
            if cat[key] in (18, 24, 30):
                pocs = get_puzzles_of_cat(tile_type_combos[index], key)
                reps = set([find_eq_class(puzzle, eqs) for puzzle in pocs])
                lengths = []
                for rep in reps:
                    lengths.append(len(eqs[rep]))
                dissection[0].append(tile_type_combos[index])
                dissection[1].append(key)
                dissection[2].append(lengths)
    return dissection


def sum_sols_per_class(equivalence_classes, sols_per_puzzle=None):
    """
    Berechnet die Anzahl der Lösungen der Puzzles in jeder Äquivalenzklasse,
    indem die Anzahl der Lösungen nur einmal pro Repräsentant geholt wird.

    :param equivalence_classes: Dictionary der Äquivalenzklassen mit Repräsentanten als Schlüssel.
    :param sols_per_puzzle: Liste der Anzahl der Lösungen für jedes Puzzle.
    :return: Dictionary mit der Summe der Lösungen pro Äquivalenzklasse.
    """
    if sols_per_puzzle is None:
        sols_per_puzzle = read_num_sols_per_puzzle()
    total_solutions = []
    for rep in equivalence_classes.keys():
        # Die Anzahl der Lösungen des Repräsentanten holen
        solutions_count = sols_per_puzzle[all_puzzles.index(rep)]
        # Die Anzahl der Lösungen mit der Anzahl der Puzzles in dieser Klasse multiplizieren
        total_solutions.append(solutions_count)
    return total_solutions


def get_tile_set_distribution(puzzle):
    """Die Zusammensetzung aus den 4 Farbsets eines Puzzles finden"""
    out = []
    for j in range(1, 5):
        out.append(len([i for i in puzzle if (j - 1) * 14 <= i < j * 14]))
    return out


def similarity(solution1, solution2):
    """
    Berechnet die Ähnlichkeit zwischen zwei Lösungen.
    :param solution1: Erste Lösung als Liste [Positionen, Rotationen, andere Daten]
    :param solution2: Zweite Lösung als Liste [Positionen, Rotationen, andere Daten]
    :return: Anzahl der Differenzen (Position + Rotation)
    """
    matches = 0
    shifts = np.array([len(solution1), len(solution2)]) - np.array([3, 3])
    n_tiles = len(solution1[0])
    for i in range(n_tiles):
        if solution1[shifts[0]][i] == solution2[shifts[1]][i] and \
                solution1[shifts[0] + 1][i] == solution2[shifts[1] + 1][i]:
            matches += 1
    return n_tiles - matches


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
    candidates = [[[13, 28, 8, 32, 22, 47, 53], ['121233', '114343', '121323', '131443', '323424', '121442', '221441'],
                   [2, 4, 3, 0, 2, 5, 4]],
                  [[53, 1, 4, 29, 16, 17, 31], ['221441', '212313', '131223', '313414', '224343', '332442', '114334'],
                   [0, 3, 0, 2, 2, 3, 5]],
                  [[8, 40, 31, 7, 5, 2, 39], ['121323', '113344', '114334', '112233', '121332', '131322', '331441'],
                   [2, 3, 0, 4, 4, 1, 4]],
                  [[9, 22, 48, 19, 33, 53, 1], ['113223', '323424', '114242', '242433', '141334', '221441', '212313'],
                   [2, 3, 5, 5, 3, 0, 5]],  # gelöst, Fehler in Codierung von Stein 19
                  [[28, 32, 52, 13, 53, 17, 3], ['114343', '131443', '141242', '121233', '221441', '332442', '112332'],
                   [4, 1, 2, 3, 5, 2, 2]]]  # der letzte wurde in 50 Versuchen nicht gelöst
    rand_sol_big = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
                    [37, 33, 30, 40, 48, 23, 1, 47, 15, 16, 4, 43, 29, 18, 50, 6, 24, 0, 39],
                    ['113443', '141334', '131344', '113344', '114242', '223443', '212313', '121442',
                     '242343', '224343', '131223', '212414', '313414', '223434', '121424', '113232',
                     '232434', '112323', '331441'],
                    [1, 3, 3, 0, 5, 3, 3, 3, 4, 0, 3, 2, 4, 1, 0, 3, 5, 2, 5]]
    unsol_pyr = [[0, 1, 2, 3, 9, 10, 11, 22, 23, 24, 25, 41, 42, 43, 44, 45, 66, 67, 68, 69, 70, 71,
                  97, 98, 99, 100, 101, 102, 103, 134, 135, 136, 137, 138, 139, 140, 141, 177, 178, 179,
                  180, 181, 182, 183, 184, 185, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235],
                 [28, 48, 31, 45, 39, 30, 47, 22, 1, 3, 34, 40, 51, 24, 13, 52, 6, 29, 27, 41, 38, 12, 10, 53,
                  4, 32, 55, 21, 16, 17, 23, 14, 49, 18, 26, 8, 54, 2, 36, 25, 5, 20, 37, 46, 15, 9, 44, 35,
                  33, 43, 11, 7, 50, 42, 0, 19],
                 ['114343', '114242', '114334', '112442', '331441', '131344', '121442', '323424', '212313',
                  '112332', '113434', '113344', '114224', '232434', '121233', '141242', '113232', '313414',
                  '242334', '141433', '131434', '113322', '131232', '221441', '131223', '131443', '121244',
                  '223344', '224343', '332442', '223443', '232344', '112244', '223434', '224433', '121323',
                  '114422', '131322', '141343', '224334', '121332', '232443', '113443', '141224', '242343',
                  '113223', '141422', '114433', '141334', '212414', '221331', '112233', '121424', '112424',
                  '112323', '242433'],
                 [1, 1, 4, 3, 2, 1, 5, 3, 4, 4, 5, 0, 2, 0, 5, 5, 3, 5, 2, 3, 2, 1, 1,
                  0, 4, 2, 5, 1, 3, 4, 2, 5, 2, 0, 0, 3, 5, 0, 1, 5, 2, 0, 0, 3, 0, 5,
                  4, 3, 0, 4, 1, 4, 0, 5, 1, 4]]
    dauli = [[0, 2, 3, 9, 10, 11, 22, 23, 24, 25, 41, 42, 43, 44, 45],
             [5, 17, 1, 31, 41, 9, 39, 40, 35, 2, 19, 33, 37, 23, 16],
             ['121332', '332442', '212313', '114334', '141433', '113223', '331441', '113344', '114433', '131322',
              '243324', '141334', '113443', '223443', '224343'], [2, 2, 0, 4, 2, 5, 5, 1, 2, 3, 4, 5, 0, 3, 1]]
    # rot_sol = rotate_sol(solution)
    # draw_sol(solution)
    # draw_sol(rot_sol, tiles)

    # Lösung durch Zufall finden, daraus Funktion schreiben, welche die durchschnittliche Anzahl der Schritte
    # bis zur ersten fehlerfreien Lösung ausgibt
    # avg, vals = find_sol_rand((9, 31, 40, 41, 47, 50, 51))  # (0, 1, 3, 4, 7, 10, 13): 764, (0, 1, 3, 6, 8, 9, 10): 164

    temperature = 500
    steps = 25000

    # Simulated annealing mit Blumenpuzzle
    # opt_sol, opt_val, datastream = simulated_annealing(rand_sol, 5000, temp=500, morphy=0, adapt_operations=0)
    # draw_sol(opt_sol)
    # print(f"Fehleranzahl der besten Lösung: {opt_val}")
    # # print(opt_sol)
    # print_best_sols(datastream)
    # # plot_t_over_steps(datastream)
    # plot_p_over_steps(datastream, 1)
    # # plot_val_over_steps(datastream)
    # plot_cand_curr_over_steps(datastream)
    # # random_sol_mean(steps, 7, tiles, all_puzzles[0])

    # Bestimmen des Annahme-Wk-Parameters durch Ausprobieren
    # test_datastream = find_temp(steps=25000, lim_low=100, lim_up=2500, stepsize=100, n_runs=30)
    # plot_temp_over_n_steps(test_datastream)
    # plot_temp_over_rate(test_datastream)

    # Löst alle 14C7 Blumenpuzzles, 10 Versuche pro Puzzle
    # flower_results = solve_flowers(all_puzzles, tiles, steps, temperature, 6, write_file=1)
    # plot_flower_results(flower_results)
    # print(f"Summe aller Fehler: {sum(flower_results[1])}")
    # die Summe aller Fehler, wenn 0 wurden alle Puzzles gelöst
    # plot_flower_attempts(flower_results)
    # gen_flower_sol_file(flower_results)

    # Möglichst viele Lösungen einer Blume finden
    # all_sols = find_all_flower_sols(rand_sol[0], 10000, steps, temperature, 6, write_file=1)
    # all_sols = find_all_flower_sols(all_puzzles[0], 10000, steps, temperature, 6, write_file=1)

    # Simulated annealing von allgemeinen Puzzles mit unterschiedlicher Tile-Anzahl und Formen
    # big_sol = gen_random_sol(n_tiles=7, kangaroo=0, sample=0, ascending=0, randomness=1)
    # opt_sol, opt_val, datastream = simulated_annealing(rsx_unsol, steps, temperature, 1)
    # draw_sol(opt_sol)
    # print(f"Fehleranzahl der besten Lösung: {opt_val}")
    # print(opt_sol)
    # print_best_sols(datastream)
    # plot_t_over_steps(datastream)
    # plot_p_over_steps(datastream, 1)
    # # plot_val_over_steps(datastream)
    # plot_cand_curr_over_steps(datastream)

    # cando = gen_cand(temp, 12, 137, 1, 0, 0, 1, err_edges=obj(temp, out_edges=1)[1])
    # print(get_longest_connection(unsol_pyr, 3))
    # Versuch, unlösbare Puzzles zu finden (Blumen)
    # find_unsolvable_flower(attempts_to_solve=10, attempts_to_search=100, n_iter=20000, temp=500, param=1)
    # solo, dolo, data = sa2(init_sol=blue_rainbow, n_iter=5000, temp=6, focus_errors=1, restart_threshold=3000,
    #                        max_restarts=5, morphy=0, adapt_operations=1, write_data=1, print_iteration=0, cool_f=0.9990)
    solo, dolo, data = sa3(init_sol=blue_rainbow, n_iter=5000, temp=6, focus_errors=1, restart_threshold=3000,
                           focus_color=1, max_restarts=0, morphy=0, adapt_operations=1, write_data=1,
                           print_iteration=1, cool_f=0.9990, print_params=1)
    # draw_sol(solo)
    print_best_sols(data)
    plot_cand_curr_over_steps(data)
    plot_val_over_steps(data)
    plot_p_over_steps(data, 0)
    # plot_t_over_steps(data)
    # print(get_longest_connection(solo))

    # Blumen mit jeweils nur dem gleichen Stein versuchen zu lösen
    # flower_one_tile(tiles_complete)

    # try_puzzle(start_sol, 20000, 500, 1, 50)

    # find_all_flower_sols([0, 2, 4, 6, 8], 500, 20000, 500, 5, 1)

    # pairings = generate_pairings(14)
    # spp = calc_sols_per_pairing(pairings=pairings, puzzle_list=all_puzzles)
    # print(spp[:10])

    # find_minimum_sols(1, 50, 40, 20000, 500, 6)

    # dissect_sol_numbers()
    # dissect_classes()


if __name__ == "__main__":
    main()
