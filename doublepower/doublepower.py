import itertools
import json


class DoublePower:

    def __init__(self, player_info_file):
        # Load players_info
        with open(player_info_file, 'r', encoding='utf-8') as f:
            self.players_info = json.load(f)

        # Query for available players_info
        self.available_players = self.query_available_players()

    def query_available_players(self):
        valid_input = False
        available_players = None
        while not valid_input:
            self.print_players('List of players_info:')
            # input_ranks = input('\nPlease enter available players_info (Space separated rank numbers): ')
            input_ranks = "1 2 3 4 5 6 7"
            try:
                available_ranks = sorted(list(set([int(p.strip()) for p in input_ranks.split()])))
            except ValueError:
                print('Invalid input! Please provide space separated numbers according to above given table!')
                continue

            # Generate list of available players_info
            available_players = [name for name, info in self.players_info.items() for rk in available_ranks if
                                 info['rank'] == rk]

            # Validate for length of dictionary (At least 6 players_info required)
            if len(available_players) < 6:
                print('Not sufficient players_info selected! Please provide at least 6 players!')
                continue

            valid_input = True

        self.print_players('Available players:', available_players)
        return available_players

    ##########################################################################
    # Formatted printing
    ##########################################################################

    def print_players(self, header, player_names=None):
        print()
        print(header)
        print(30 * '-')
        # If a list of player names is provided only print players_info from that list
        if player_names:
            for name in player_names:
                info = self.players_info[name]
                print(f'{info["rank"]:>2}: {name}')

        # Otherwise print all players_info
        else:
            for name, info in self.players_info.items():
                print(f'{info["rank"]:>2}: {name}')

    def print_ranked_paired_formation(self, ranked_paired_formation, form=None):
        total_strength = self.get_ranked_paired_formation_strength(ranked_paired_formation)
        if form is None:
            output = []
            for pair in ranked_paired_formation:
                double_strength_string = f' [strength = {self.get_double_strength(pair)}]'
                output.append(f'{pair[0]:>25} + {pair[1]:<25}{double_strength_string:<20}')

            print(f'{output[0]:<70} || {output[1]:<70} || {output[2]:<70}'
                  f'   [total strength = {total_strength}]'
                  )
        else:
            output = [
                f'[{form.get_rank(pair[0])}] + [{form.get_rank(pair[1])}]'
                f' = [{form.get_double_rank(pair):>2}]'
                f' [strength = {self.get_double_strength(pair)}]'
                for pair in ranked_paired_formation
            ]

            print(f'{output[0]:<40}{output[1]:<40}{output[2]:<40}'
                  f'   [total strength = {total_strength}]'
                  )

    def print_formations_info(self):
        all_fs = self.get_all_formations()
        for f in all_fs:
            print(f)
            f_rpfs = f.get_all_ranked_paired_formations()
            for rpf in f_rpfs:
                self.print_ranked_paired_formation(rpf, f)

    def print_strongest_formations(self, n):
        strongest_rpfs = self.get_strongest_formations(n)
        for rpf in strongest_rpfs:
            self.print_ranked_paired_formation(rpf)

    ##########################################################################
    # Combinatorics
    ##########################################################################

    def get_all_formations(self):
        formation_list = list(itertools.combinations(self.available_players, 6))
        return [Formation(f) for f in formation_list]

    def get_all_ranked_paired_formations(self):
        formations = self.get_all_formations()
        all_rpfs = []
        for f in formations:
            f_rpfs = f.get_all_ranked_paired_formations()
            all_rpfs.extend(f_rpfs)
        return all_rpfs

    ##########################################################################
    # Analysis functions
    ##########################################################################

    def get_double_strength(self, pair):
        """

        :param pair: A 2-tuple holding player names
        :return: The maximum strength a double pair can achieve
        """
        lr_strength = self.players_info[pair[0]]['strength']['left'] + self.players_info[pair[1]]['strength']['right']
        rl_strength = self.players_info[pair[0]]['strength']['right'] + self.players_info[pair[1]]['strength']['left']
        return lr_strength if lr_strength > rl_strength else rl_strength

    def get_ranked_paired_formation_strength(self, ranked_paired_formation):
        return sum([self.get_double_strength(pair) for pair in ranked_paired_formation])

    def get_max_formation_strength(self):
        formation_strengths = [self.print_ranked_paired_formation(rpf) for rpf in
                               self.get_all_ranked_paired_formations()]
        return max(formation_strengths)

    def get_strongest_formations(self, n):
        all_rpfs = self.get_all_ranked_paired_formations()

        # Display N entries or all available entries
        n = min([n, len(all_rpfs)])

        rpfs_strengths = [self.get_ranked_paired_formation_strength(rpf) for rpf in all_rpfs]
        strength_sorted_rpfs = [rpf for _, rpf in sorted(zip(rpfs_strengths, all_rpfs), reverse=True)]
        return strength_sorted_rpfs[:n]


class Formation:
    def __init__(self, players):
        self.players = players

    def __str__(self):
        ranked_formation = self.get_ranked_formation()
        output = f'[{str(ranked_formation[0][1])}] {ranked_formation[0][0]:<30}'
        for rf in ranked_formation[1:]:
            output += f'[{str(rf[1])}] {rf[0]:<30}'

        header = 'FORMATION:'
        separator = 210 * '-'

        return f'\n{separator}\n{header:^210}\n{separator}\n{output}\n{separator}'

    ##########################################################################
    # Combinatorics
    ##########################################################################

    def get_ranked_formation(self):
        return [(name, rank) for name, rank in zip(self.players, range(1, 7))]

    @staticmethod
    def all_pairs(players):
        if len(players) < 2:
            yield []
            return
        if len(players) % 2 == 1:
            # Handle odd length list
            for i in range(len(players)):
                for result in Formation.all_pairs(players[:i] + players[i + 1:]):
                    yield result
        else:
            p1 = players[0]
            for i in range(1, len(players)):
                pair = (p1, players[i])
                for rest in Formation.all_pairs(players[1:i] + players[i + 1:]):
                    yield [pair] + rest

    def get_paired_formations(self):
        return list(self.all_pairs(self.players))

    def get_ranked_paired_formations(self, paired_formation):

        # Two-leveled sorting of pairs
        # 1. By the double rank according to the formation
        # 2. By the minimum single rank for each pair (in case of equality of double rank)
        min_single_ranks = [min(self.get_rank(pair[0]), self.get_rank(pair[1])) for pair in paired_formation]
        double_ranks = [self.get_double_rank(pair) for pair in paired_formation]
        ranked_paired_formation = [pair for _, _, pair in sorted(zip(double_ranks, min_single_ranks, paired_formation))]
        double_ranks.sort()

        if double_ranks[0] == double_ranks[1]:
            if double_ranks[1] == double_ranks[2]:
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
            if double_ranks[1] == double_ranks[2]:
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

    def get_all_ranked_paired_formations(self):
        all_ranked_paired_formations = []
        for paired_formation in self.get_paired_formations():
            all_ranked_paired_formations.extend(self.get_ranked_paired_formations(paired_formation))
        return all_ranked_paired_formations

    ##########################################################################
    # Analysis functions
    ##########################################################################

    def get_rank(self, player):
        return self.players.index(player) + 1 if player in self.players else None

    def get_double_rank(self, pair):
        """

        :param pair: A 2-tuple holding player names
        :return: The sum of ranks according to the given formation
        """
        ranked_formation = self.get_ranked_formation()
        pair = [player for player in ranked_formation if player[0] in pair]
        return pair[0][1] + pair[1][1]


if __name__ == '__main__':
    # Load players info
    dp = DoublePower('players_info.json')

    # Give an overview over possible formations and respective paired ranked formations
    dp.print_formations_info()

    dp.print_strongest_formations(20)
