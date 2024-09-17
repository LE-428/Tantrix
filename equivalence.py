from itertools import permutations, combinations
from collections import defaultdict
import multiprocessing
import hashlib
import csv
import os

tiles = ['112323', '212313', '131322', '112332', '131223', '121332', '113232',
         '112233', '121323', '113223', '131232', '221331', '113322', '121233',
         '232344', '242343', '224343', '332442', '223434', '242433', '232443',
         '223344', '323424', '223443', '232434', '224334', '224433', '242334',
         '114343', '313414', '131344', '114334', '131443', '141334', '113434',
         '114433', '141343', '113443', '131434', '331441', '113344', '141433',
         '112424', '212414', '141422', '112442', '141224', '121442', '114242',
         '112244', '121424', '114224', '141242', '221441', '114422', '121244']

n = 14
r = 7
perms = list(permutations('1234'))


def hash_puzzle(puzzle):
    """Generiert einen Hash für ein Puzzle."""
    puzzle_str = ''.join(map(str, puzzle))
    return hashlib.md5(puzzle_str.encode('utf-8')).hexdigest()


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
    for f in range(6):
        if tile[f] == str(col):
            indices.append(f)
    dist = indices[1] - indices[0]
    return dist, indices[0]


def shift_tile(tile, offset: int):
    """
    :param tile: eine Liste mit den Farben des Spielsteins
    :param offset: um wie viele Stellen wird die Codierung von rechts nach links verschoben
    :return: das verschobene Tile
    """
    return [tile[(i + offset) % 6] for i in range(6)]


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


def mirror(tile):
    """Funktion zum Spiegeln eines Steins (Reihenfolge umkehren)"""
    return tile[::-1]


def apply_permutation(tile, perm):
    """Funktion zum Anwenden einer Farbpermutation auf einen Stein"""
    return ''.join(perm[int(color) - 1] for color in tile)


def generate_equivalent_puzzles(puzzle):
    """Funktion zum Generieren aller äquivalenten Puzzles"""
    equivalent_puzzles = set()
    for perm in perms:
        # Anwenden der Permutation auf alle Steine im Puzzle
        permuted_puzzle = tuple(
            sorted(tiles.index(''.join(sort_sol(apply_permutation(tiles[i], perm)))) for i in puzzle))
        equivalent_puzzles.add(permuted_puzzle)
        # Spiegeln der permutierten Steine
        mirrored_puzzle = tuple(
            sorted(tiles.index(''.join(sort_sol(mirror(apply_permutation(tiles[i], perm))))) for i in puzzle))
        equivalent_puzzles.add(mirrored_puzzle)
    return min(equivalent_puzzles), len(equivalent_puzzles)


def get_tile_set_distribution(puzzle):
    """Die Zusammensetzung aus den 4 Farbsets eines Puzzles finden"""
    parts = (
        (7, 0, 0, 0), (6, 1, 0, 0), (5, 2, 0, 0), (4, 3, 0, 0), (3, 3, 1, 0), (3, 2, 1, 1), (5, 1, 1, 0), (4, 2, 1, 0),
        (3, 2, 2, 0), (4, 1, 1, 1), (2, 2, 2, 1))
    out = []
    for j in range(1, 5):
        out.append(len([i for i in puzzle if (j - 1) * 14 <= i < j * 14]))
    return parts.index(tuple(sorted(out, reverse=True)))


def write_csv(col1, col2, filename=None, path=None):
    """
    Erstellt eine CSV-Datei
    
    :param path: optionaler Pfad
    :param filename: Name der zu erstellenden CSV-Datei.
    :param col1: Liste der Werte für die erste Spalte.
    :param col2: Liste der Werte für die zweite Spalte.
    """
    if filename is None:
        filename = "eqc_4870784.csv"
    if path is not None:
        filename = os.path.join(path, filename)
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Col1', 'Col2'])  # Kopfzeile
        for i in range(len(col1)):
            row = [col1[i], col2[i]]
            writer.writerow(row)


def gen_classes(puzzles):
    """Alle Puzzles in Äquivalenzklassen bezüglich Permutation der Farben und Spiegelung der Steine einteilen"""
    equivalence_representatives = set()
    eqlns = []
    parts = []
    # visited_hashes = set()
    index = 0
    while len(puzzles) != 0:
        index += 1
        # print(index)
        if index % 100000 == 0:
            print(index)
        puzzle = puzzles.pop()
        canonical_puzzle, len_class = generate_equivalent_puzzles(puzzle)
        # if hash_puzzle(puzzle) in visited_hashes:
        #     continue
        # eq_puzzles_hashes = generate_equivalent_puzzles(puzzle)
        # for hashi in eq_puzzles_hashes:
        #     visited_hashes.add(hashi)
        # canonical_puzzle_hash = min(eq_puzzles_hashes)
        canonical_puzzle_hash = hash_puzzle(canonical_puzzle)
        # Wenn der kanonische Hash bereits existiert, überspringen
        if canonical_puzzle_hash in equivalence_representatives:
            continue
        # Füge den Repräsentanten hinzu
        equivalence_representatives.add(canonical_puzzle_hash)
        eqlns.append(len_class)
        parts.append(get_tile_set_distribution(canonical_puzzle))
    write_csv(eqlns, parts, path='G:\\Tantrix\\Loesungen\\debug\\')
    return equivalence_representatives


def gen_classes_worker(all_puzzles_chunk):
    """Funktion, die von jedem Worker-Prozess ausgeführt wird und den Speicher durch schrittweises Abarbeiten der
    Puzzles optimiert."""
    local_data = {}  # Dict zum Speichern von {hash: (len_class, partition)}
    print(f"worker started: {len(all_puzzles_chunk)} puzzles")
    while all_puzzles_chunk:
        puzzle = all_puzzles_chunk.pop()  # Nimm das letzte Puzzle aus dem Chunk und lösche es, um Speicher freizugeben
        canonical_puzzle, len_class = generate_equivalent_puzzles(puzzle)
        canonical_puzzle_hash = hash_puzzle(canonical_puzzle)
        if canonical_puzzle_hash in local_data:
            continue
        partition = get_tile_set_distribution(canonical_puzzle)
        local_data[canonical_puzzle_hash] = (len_class, partition)
    return local_data


def combine_results(results):
    """Funktion zum Zusammenführen der Ergebnisse aller Worker."""
    final_reps = set()
    final_lens = defaultdict(int)
    final_parts = defaultdict(int)
    for local_data in results:
        for rep_hash, (len_class, partition) in local_data.items():
            if rep_hash not in final_reps:
                final_reps.add(rep_hash)
                final_lens[len_class] += 1
                final_parts[partition] += 1
    return final_reps, final_lens, final_parts


def create_chunks(all_puzz, cores):
    """
    Teilt die Liste `all_puzzles` in Chunks auf und löscht die betreffenden Einträge aus `all_puzzles`,
    um den Speicherverbrauch zu minimieren.
    """
    chunk_size = len(all_puzz) // cores  # Bestimme die Größe jedes Chunks
    chunks = []
    for _ in range(cores):
        chunk = all_puzz[:chunk_size]  # Nimm den nächsten Chunk
        all_puzz = all_puzz[chunk_size:]  # Entferne den Chunk aus all_puzzles
        chunks.append(chunk)  # Füge den Chunk der Liste hinzu
        del chunk  # Lösche den Chunk aus dem RAM
    # Verarbeite den Rest, falls `all_puzzles` nicht genau durch `cores` teilbar ist
    if all_puzz:
        chunks.append(all_puzz)  # Der letzte Chunk enthält den Rest
        del all_puzz
    return chunks


def gen_classes_parallel(puzzles):
    """Alle Puzzles parallel in Äquivalenzklassen einteilen."""
    cores = multiprocessing.cpu_count()
    print("erstelle chunks...")
    chunks = create_chunks(puzzles, cores)  # Teile all_puzzles in Chunks auf und lösche die entsprechenden Einträge
    print("chunks erstellt")
    input_args = []
    for _ in range(len(chunks)):
        input_args.append((chunks.pop()))
    print("input_args erstellt")
    with multiprocessing.Pool(cores) as pool:
        results = pool.map(gen_classes_worker, input_args)
    final_reps, final_lens, final_parts = combine_results(results)
    return final_reps, final_lens, final_parts


# Aufruf der Funktion für die 231 Millionen Puzzles
if __name__ == "__main__":
    all_puzzles = list(combinations(range(n), r))
    print("all_puzzles angelegt")
    equivalence_classes, eq_lens, partitions = gen_classes_parallel(all_puzzles)
    print(eq_lens)
    print(partitions)
