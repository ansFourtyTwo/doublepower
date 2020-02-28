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


def double_rank_sum(pair):
    return pair[0][1] + pair[1][1]


def sort_by_sum(pairs, positions):
    sums = [positions[p[0]] + positions[p[1]] for p in pairs]
    return [(p[0], p[1], s) for s, p in sorted(zip(sums, pairs))]


def print_paired_formation(pf):
    pairs = [("(" + p[0][0] + " | " + p[1][0] + ")", double_rank_sum(p)) for p in pf]

    for p in pairs:
        print(f'{p[0]}, Sum: {p[1]}')
    print()


def main():
    with open('players_info.json', 'r', encoding='utf-8') as f:
        players = json.load(f)

    print('List of players:')
    print('------------------------------------------')
    for name, info in players.items():
        print(f'{info["rank"]:>2}: {name}')

    # input_ranks = input('Please enter available players:\n')
    input_ranks = "1 2 3 4 5 7 9"
    available_ranks = [int(p.strip()) for p in input_ranks.split()]
    available_players = [name for name, info in players.items() for rk in available_ranks if info['rank'] == rk]

    # Validate input
    if len(available_players) < 6:
        RuntimeError('Not sufficient players selected!')

    print()
    print('Available players:')
    print('------------------------------------------')
    for ap in available_players:
        print(f'{players[ap]["rank"]:>2}: {ap}')

    # Evaluate all possible formations of 6 players out of all available players
    formations = list(itertools.combinations(available_players, 6))

    # Evaluate all paired formations from all possible formations
    paired_formations = []
    for formation in formations:
        formation = [(name, rank) for name, rank in zip(formation, range(1, 7))]
        paired_formations.extend(list(all_pairs(formation)))

    for pf in paired_formations:
        print_paired_formation(pf)


if __name__ == '__main__':
    main()



