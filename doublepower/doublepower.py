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


def get_paired_formations(formation):
    return list(all_pairs(formation))


def get_ranked_paired_formations(paired_formation, formation):
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


def get_double_strength(pair, players):
    lr_strength = players[pair[0]]['strength']['left'] + players[pair[1]]['strength']['right']
    rl_strength = players[pair[0]]['strength']['right'] + players[pair[1]]['strength']['left']
    return lr_strength if lr_strength > rl_strength else rl_strength


def get_formation_strength(rpf, players):
    return sum([get_double_strength(pair, players) for pair in rpf])


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


def print_ranked_paired_formation(rpf, players, formation=None):
    total_strength = get_formation_strength(rpf, players)
    if formation is not None:
        output = [
            f'[{get_rank(pair[0], formation)}] + [{get_rank(pair[1], formation)}]'
            f' = [{get_double_rank(pair,formation):>2}]'
            f' [strength = {get_double_strength(pair, players)}]'
            for pair in rpf
        ]

        print(f'{output[0]:<40}{output[1]:<40}{output[2]:<40}'
              f'   [total strength = {total_strength}]'
              )
    else:
        output = []
        for pair in rpf:
            double_strength_string = f' [strength = {get_double_strength(pair, players)}]'
            output.append(f'{pair[0]:>25} + {pair[1]:<25}{double_strength_string:<20}')

        print(f'{output[0]:<70} || {output[1]:<70} || {output[2]:<70}'
              f'   [total strength = {total_strength}]'
              )


def filter_ranked_paired_formations(rpf, players):
    pass


def main():
    with open('players_info.json', 'r', encoding='utf-8') as f:
        players = json.load(f)

    print_players('List of players:', players)

    # input_ranks = input('Please enter available players:\n')
    input_ranks = "1 2 5 7 8 11"
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
        paired_formations = get_paired_formations(formation)

        # List of all ranked paired formations:
        # This includes swapped positions due to same double ranks
        ranked_paired_formations = []
        for paired_formation in paired_formations:
            ranked_paired_formations.extend(get_ranked_paired_formations(paired_formation, formation))

        for ranked_paired_formation in ranked_paired_formations:
            print_ranked_paired_formation(ranked_paired_formation, players, formation)

        # Collect all ranked paired formations from all possible formations (more than 6 players available)
        all_ranked_paired_formations.extend(ranked_paired_formations)

    formation_strengths = [get_formation_strength(rpf, players) for rpf in all_ranked_paired_formations]
    max_total_strength = max(formation_strengths)
    max_total_strength_formations = [rpf for _, rpf in
                                     sorted(zip(formation_strengths, all_ranked_paired_formations), reverse=True)]
    print('\n\n')
    print(f'Max. formation strength: {max_total_strength}')
    for rpf in max_total_strength_formations[:min([len(max_total_strength_formations), 20])]:
        print_ranked_paired_formation(rpf, players)



if __name__ == '__main__':
    main()



