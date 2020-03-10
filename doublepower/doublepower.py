import itertools
import json


def all_pairs(formation):
    if len(formation) < 2:
        yield []
        return
    if len(formation) % 2 == 1:
        # Handle odd length list
        for i in range(len(formation)):
            for result in all_pairs(formation[:i] + formation[i + 1:]):
                yield result
    else:
        p1 = formation[0]
        for i in range(1, len(formation)):
            pair = (p1, formation[i])
            for rest in all_pairs(formation[1:i] + formation[i + 1:]):
                yield [pair] + rest


def get_all_formations(available_players):
    return list(itertools.combinations(available_players, 6))


def get_ranked_formation(formation):
    return [(name, rank) for name, rank in zip(formation, range(1, 7))]


def get_all_paired_formations(formation):
    return list(all_pairs(formation))


def get_all_ranked_paired_formations(paired_formation, formation):
    min_single_ranks = [min(get_rank(pair[0], formation), get_rank(pair[1], formation)) for pair in paired_formation]
    ranks = [get_double_rank(pair, formation) for pair in paired_formation]
    ranked_paired_formation = [pair for _, _, pair in sorted(zip(ranks, min_single_ranks, paired_formation))]
    ranks.sort()

    if ranks[0] == ranks[1]:
        if ranks[1] == ranks[2]:
            formation_variations = [
                [0, 1, 2],
                [0, 2, 1],
                [1, 0, 2],
                [2, 0, 1]
            ]
        else:
            formation_variations = [
                [0, 1, 2],
                [1, 0, 2]
            ]
    else:
        if ranks[1] == ranks[2]:
            formation_variations = [
                [0, 1, 2],
                [0, 2, 1]
            ]
        else:
            formation_variations = [
                [0, 1, 2]
            ]
    ranked_paired_formations = []
    for i, j, k in formation_variations:
        ranked_paired_formations.append(
            [ranked_paired_formation[i], ranked_paired_formation[j], ranked_paired_formation[k]]
        )
    return ranked_paired_formations


def get_rank(player, formation):
    return formation.index(player) + 1


def get_double_rank(pair, formation):
    ranked_formation = get_ranked_formation(formation)
    pair = [player for player in ranked_formation if player[0] in pair]
    return pair[0][1] + pair[1][1]


def sort_by_sum(pairs, positions):
    sums = [positions[p[0]] + positions[p[1]] for p in pairs]
    return [(p[0], p[1], s) for s, p in sorted(zip(sums, pairs))]


def print_players(header, players):
    print()
    print(header)
    print(30 * '-')
    for name, info in players.items():
        print(f'{info["rank"]:>2}: {name}')


def print_ranked_formation(formation):
    ranked_formation = get_ranked_formation(formation)
    output = f'[{str(ranked_formation[0][1])}] {ranked_formation[0][0]:<30}'
    for rf in ranked_formation[1:]:
        output += f'[{str(rf[1])}] {rf[0]:<30}'
    print()
    print('Formation:')
    print(210 * '-')
    print(output)
    print(210 * '-')


def print_ranked_paired_formation(rpf, formation):
    output_sums = [f'[{get_double_rank(pair, formation):>2}]' for pair in rpf]
    output_pairs = [f'{pair[0]} + {pair[1]}' for pair in rpf]
    print(f'{output_sums[0]:<6}{output_sums[1]:<6}{output_sums[2]:<6}{output_pairs[0]:<60}{output_pairs[1]:<60}{output_pairs[2]:<60}')


def main():
    with open('players_info.json', 'r', encoding='utf-8') as f:
        players = json.load(f)

    print_players('List of players:', players)

    # input_ranks = input('Please enter available players:\n')
    input_ranks = "1 2 3 4 5 7 9"
    available_ranks = [int(p.strip()) for p in input_ranks.split()]
    available_players = {name: info for name, info in players.items() for rk in available_ranks if info['rank'] == rk}

    # Validate input
    if len(available_players) < 6:
        RuntimeError('Not sufficient players selected!')

    print_players('Available players:', available_players)

    # Evaluate all possible formations of 6 players out of all available players
    formations = get_all_formations(available_players.keys())

    # Evaluate all paired formations from all possible formations
    all_ranked_paired_formations = []
    for formation in formations:
        print_ranked_formation(formation)

        # List of paired formations out of formations of 6 players (all possible pairs)
        paired_formations = get_all_paired_formations(formation)
        ranked_paired_formations = []
        for paired_formation in paired_formations:
            ranked_paired_formations.extend(get_all_ranked_paired_formations(paired_formation, formation))

        for ranked_paired_formation in ranked_paired_formations:
            print_ranked_paired_formation(ranked_paired_formation, formation)

        all_ranked_paired_formations.extend(ranked_paired_formations)

    test = 42


if __name__ == '__main__':
    main()



