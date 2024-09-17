import itertools
import random

import numpy as np
from collections import Counter
import multiprocessing
import matplotlib.pyplot as plt

# Beispielhafte Auswahl an 7 Fliesen (ersetze dies durch deine tatsächlichen Fliesen)
tiles_complete = ['112323', '212313', '131322', '112332', '131223', '121332', '113232',
                  '112233', '121323', '113223', '131232', '221331', '113322', '121233',
                  '232344', '242343', '224343', '332442', '223434', '242433', '232443',  # 242433 anstatt 243324
                  '223344', '323424', '223443', '232434', '224334', '224433', '242334',
                  '114343', '313414', '131344', '114334', '131443', '141334', '113434',
                  '114433', '141343', '113443', '131434', '331441', '113344', '141433',
                  '112424', '212414', '141422', '112442', '141224', '121442', '114242',
                  '112244', '121424', '114224', '141242', '221441', '114422', '121244']

parts = ((7, 0, 0, 0), (6, 1, 0, 0), (5, 2, 0, 0), (4, 3, 0, 0), (3, 3, 1, 0), (3, 2, 1, 1),
         (5, 1, 1, 0), (4, 2, 1, 0), (3, 2, 2, 0), (4, 1, 1, 1), (2, 2, 2, 1))


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


def getColor(tile, edge, orientation):
    """
    Die Farbe einer Kante eines Steins ausgeben als int mit definierter Codierung
    :param tile: Codierung des Steins
    :param edge: Kante des Steins
    :param orientation: Rotation des Steins
    :return: Farbcode
    """
    return int(tile[(edge + orientation) % 6])


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


def generate_and_update_counter(perm, counter, ex=0):
    """Generiert alle Anordnungen für eine Permutation und aktualisiert den Fehlerzähler."""
    for rotations in itertools.product(range(6), repeat=len(perm) - 1):  # 6
        # Die erste Kachel bleibt ohne Rotation
        arrangement = (
            [tiles_complete.index(tile) for tile in perm],  # Index der Fliesen in der Permutation
            perm,  # Die Permutation selbst
            [0] + list(rotations)  # 0 für die erste Fliese, Rotation für die anderen
        )
        
        errors = obj(arrangement, early_exit=ex)
        counter[errors] += 1
        

def stream_evaluation(tile_nums, chunk_size=5040, perms=None, early_ex=0):
    """Generiert und bewertet alle Anordnungen und zählt die Fehlerhäufigkeit."""
    if perms is None:
        tiles = [tiles_complete[i] for i in tile_nums]
        perms = itertools.permutations(tiles, len(tile_nums))  # 7
    counter = Counter()
    index = 0
    for perm in perms:
        index += 1
        # print(f"{index}/{chunk_size}")
        generate_and_update_counter(perm, counter, early_ex)
    return counter


def parallel_evaluation(tile_nums, chunk_size=5040, early_ex=0):
    """Startet die parallele Bewertung der Anordnungen."""
    cores = multiprocessing.cpu_count()
    tiles = [tiles_complete[i] for i in tile_nums]
    perms = list(itertools.permutations(tiles, len(tile_nums)))
    # counter = Counter()
    chunked_perms = [perms[i:i + chunk_size] for i in range(0, sum(1 for _ in perms), chunk_size)]
    with multiprocessing.Pool(cores) as pool:
        input_args = [(tiles_complete, chunk_size, chunked_perms[c], early_ex) for c in range(len(chunked_perms))]
        # Aufteilen der Arbeit auf die Kerne
        results = pool.starmap(stream_evaluation, input_args)
    # Zusammenführen der Ergebnisse der parallelen Ausführung
    fin_cntr = Counter()
    for result in results:
        fin_cntr.update(result)
    return fin_cntr


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
    plt.show(block=False)


def gen_puzzle_from_sets(set_distribution):
    """Puzzle generieren mit Verteilung (a, b, c, d) auf die 4 Farbsets"""
    puzzle = []
    for set_index, set_num in enumerate(set_distribution):
        set_indices = random.sample([*range(set_index * 14, (set_index + 1) * 14)], k=set_num)
        puzzle += sorted(set_indices)
    return tuple(puzzle)


def estimate_sols_per_partition(sample_size=100):
    """Durchschnittliche Anzahl der Lösungen pro Puzzle schätzen für die 11 Partitionen aus den
    Farbsets"""
    results = []
    for part in parts:
        print(f"starting partition {part} ...")
        part_cand_num_sols = []
        for i in range(sample_size):
            print(f"{i}/{sample_size}")
            cand = gen_puzzle_from_sets(part)
            counter = parallel_evaluation(cand, chunk_size=50, early_ex=1)
            part_cand_num_sols.append(counter[0])  # fehlerfreie Lösungen
        results.append(np.mean(part_cand_num_sols))
    return results


if __name__ == "__main__":
    # final_counter = parallel_evaluation((0, 2, 3, 4, 6, 10, 11), 50, early_ex=1)  # 450 Lösungen
    # final_counter = stream_evaluation((0, 2, 3, 4, 6, 10, 11))
    # print(final_counter)
    # plot_counter(final_counter)
    res = estimate_sols_per_partition(sample_size=10)
    print(res)
