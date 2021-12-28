# card pulling simulator for duel links
import json
import math
import random
import matplotlib.pyplot as plt
import matplotlib.lines as lines
from scipy.special import comb
import numpy as np
from scipy.stats import multivariate_hypergeom
from functools import reduce

# info on desired cards
targets = [{'rarity': 'R', 'copies': 1}, {'rarity': 'SR', 'copies': 1},
           {'rarity': 'UR', 'copies': 1}, {'rarity': 'N', 'copies': 3, 'extra': True}]
# desired_rarity = 'SR'
# desired_copies = 2
# does the desired card have extra copies in the box?
# desired_extra = False
# set logging to True if you want each simulated box pull recorded to a txt file
logging = False
# number of simulations you want to run
numtrials = 1000

# some info about the box contents
packs_in_box = 180
from numpy.random import default_rng
rng = default_rng(123)


class card:
    def __init__(self, rarity: str, index: int, extra: bool):
        self.rarity = rarity
        self.index = index
        self.extra = extra

class box:
    def __init__(self, packs):
        self.packs = packs
        f = open('cardpuller/box_sizes.json')
        self.template = json.load(f)[str(packs)]
        self.boxstats = [[self.template["UR_distinct"], self.template['SR_distinct'], self.template['R_distinct'], self.template['N_distinct']],
                         [self.template['UR_total'], self.template['SR_total'], self.template['R_total'], self.template['N_total']]]
        self.rarities = ["UR", "SR", "R", "N"]
        # extra refers to R and N cards which the box contains one more copy of, relative to the others in the box
        self.extras = [self.boxstats[1][i] - (math.floor(self.boxstats[1][i] / self.boxstats[0][i]) * self.boxstats[0][i])
                  for i in range(len(self.boxstats[0]))]
        self.card_list = []
        # the number of packs with 2 R+ cards plus the number with 2 N cards
        # is equal to the total number of packs in the box
        self.double_rares = sum(self.boxstats[1][:3]) - self.template['packs_total']
        self.double_commons = self.template['packs_total'] - self.double_rares
        self.third_pack_rares = self.template['R_total'] - self.double_rares

    def populate(self):
        if self.packs == 0:
            return
        self.card_dict = {
            i: {} for i in self.rarities
        }
        for i, remaining in enumerate(self.boxstats[1]):
            while remaining:
                for index in range(0, self.boxstats[0][i]):
                    if not remaining:
                        break
                    self.card_list.append(card(self.rarities[i], index, (index < self.extras[i])))
                    if self.card_dict[self.rarities[i]].get(index, False):
                        self.card_dict[self.rarities[i]][index] += 1
                    else:
                        self.card_dict[self.rarities[i]][index] = 1
                    remaining -= 1
        random.shuffle(self.card_list)
        self.max_copies = max([max(list(self.card_dict.values())[i].values()) for i in range(len(self.card_dict))])

        # assemble the packs then shuffle them
        allpacks = []
        while self.packs:
            pack = self.pull_pack()
            currpack = []
            for Card in pack:
                currpack.append({'rarity': Card.rarity, 'index': Card.index})
            allpacks.append(currpack)
        random.shuffle(allpacks)
        self.pack_list = allpacks

    def pick_target_cards(self, targets):
        # assign indices to all the cards we are looking for
        cardpool = [[[i for i in range(self.extras[0])], [i for i in range(self.extras[1])],
                     [i for i in range(self.extras[2])], [i for i in range(self.extras[3])]],
                    [[i for i in range(self.extras[0], self.template['UR_distinct'])], [i for i in range(self.extras[1], self.template['SR_distinct'])],
                     [i for i in range(self.extras[2], self.template['R_distinct'])], [i for i in range(self.extras[3], self.template['N_distinct'])]]]

        howmanydistinct = [[0] * 4 for i in range(2)]
        for card in targets:
            extra = card.get('extra', False)
            if extra:
                howmanydistinct[0][self.rarities.index(card['rarity'])] += 1
            else:
                howmanydistinct[1][self.rarities.index(card['rarity'])] += 1

        indices = [[[]] * 4 for i in range(2)]
        for i, extraornah in enumerate(indices):
            for j, rarity in enumerate(extraornah):
                indices[i][j] = random.sample(cardpool[i][j], k=howmanydistinct[i][j])

        for card in targets:
            extra = card.get('extra', False)
            if extra:
                card['index'] = indices[0][self.rarities.index(card['rarity'])].pop()
            else:
                card['index'] = indices[1][self.rarities.index(card['rarity'])].pop()

    def pull_pack(self):
        if not self.packs:
            raise ValueError("quantity cannot be more copies than are contained in the box")
        self.packs -= 1
        pack = []
        foundcard = False
        mandatory_N = None

        # helper function to sort dictionary by value
        def by_value(item):
            return item[1]

        if self.packs < self.max_copies:
            N_most_copies = sorted(self.card_dict['N'].items(), key=by_value, reverse=True)[0]
            if N_most_copies[1] > self.packs:
                mandatory_N = N_most_copies[0]
                # print(self.packs,mandatory_N, N_most_copies[1])
                # print(self.card_dict['N'])
        for i, card in enumerate(self.card_list):
            if card.rarity == "N":
                # if we must include a specific N card check if we found it
                if mandatory_N or mandatory_N == 0:
                    if card.index != mandatory_N:
                        continue
                foundcard = True
                self.card_dict[card.rarity][card.index] -= 1
                pack.append(self.card_list.pop(i))
                break
        if not foundcard:
            print("failed to find card 1 to add to pack")
            [print(card.rarity, ',', card.index, ',', card.extra) for card in self.card_list]
        foundcard = False
        mandatory_N = None
        mandatory_R = None
        if self.packs < self.max_copies:
            N_most_copies = sorted(self.card_dict['N'].items(), key=by_value, reverse=True)[0]
            # only force include a specific R card in slot 2 if there are two R cards
            # with # copies greater than # packs since a single mandatory R card just goes to slot 3
            R_most_copies = sorted(self.card_dict['R'].items(), key=by_value, reverse=True)[1]
            if N_most_copies[1] > self.packs:
                mandatory_N = N_most_copies[0]
            if R_most_copies[1] > self.packs:
                mandatory_R = R_most_copies[0]
        # if self.packs == 1:
        #     print(self.card_dict)
        for i, card in enumerate(self.card_list):
            if card.rarity in ["N", "R"]:
                if mandatory_N or mandatory_N == 0:
                    if card.index != mandatory_N or card.rarity != 'N':
                        continue
                if card.rarity == 'R':
                    if mandatory_R or mandatory_R == 0:
                        if card.index != mandatory_R or card.rarity != 'R':
                            continue
                    # check if we still have extra R+ cards
                    if not self.double_rares:
                        # if there aren't enough R cards left, prevent this pack from containing more than 1
                        continue
                    self.double_rares -= 1
                else:
                    if not self.double_commons:
                        continue
                    # make sure we aren't doubling up the same card in a pack
                    if card.index == pack[0].index:
                        continue
                    self.double_commons -= 1
                foundcard = True
                self.card_dict[card.rarity][card.index] -= 1
                pack.append(self.card_list.pop(i))
                break
        if not foundcard:
            print("failed to find card 2 to add to pack")
            print(self.packs)
            [print(card.rarity, ',', card.index, ',', card.extra) for card in self.card_list]
        foundcard = False
        mandatory_R = None
        if self.packs < self.max_copies:
            R_most_copies = sorted(self.card_dict['R'].items(), key=by_value, reverse=True)[0]
            if R_most_copies[1] > self.packs:
                mandatory_R = R_most_copies[0]
        for i, card in enumerate(self.card_list):
            if card.rarity in ["R", "SR", "UR"]:
                if mandatory_R or mandatory_R == 0:
                    if card.index != mandatory_R or card.rarity != 'R':
                        continue
                if card.rarity == 'R':
                    if not self.third_pack_rares:
                        continue
                    # check if card is a duplicate from earlier in the pack
                    try:
                        if card.index == pack[1].index and card.rarity == pack[1].rarity:
                            continue
                    except IndexError:
                        break
                    self.third_pack_rares -= 1
                foundcard = True
                self.card_dict[card.rarity][card.index] -= 1
                pack.append(self.card_list.pop(i))
                break
        if not foundcard:
            print("failed to find card 3 to add to pack")
            [print(card.rarity, ',', card.index, ',', card.extra) for card in self.card_list]
        foundcard = False
        if len(pack) < 3:
            print("Something went wrong. Pack has less than 3 cards.")
        return pack

    def pull_pack2(self):
        # alternative implementation that ignores pack logic for testing purposes
        if not self.packs:
            raise ValueError("quantity cannot be more copies than are contained in the box")
        self.packs -= 1
        pack = []
        for i in range(3):
            pack.append(self.card_list.pop())
        return pack

    def reset(self):
        self.__init__(self.template['packs_total'])
        self.populate()

    def pull_for_cards(self, targets, outfile=None):
        # an alternate implementation where we construct legal packs then randomize the order  

    
        opened = 0
        for pack in self.pack_list:
            opened += 1
            foundtarget = False
            for card in pack:
                for target in targets:
                    if card['rarity'] == target['rarity'] and card['index'] == target['index']:
                        if not target.get('found', False):
                            target['found'] = 1
                        else:
                            target['found'] += 1
                        # trigger the sentinel when we find the desired copies of one of our targets
                        if target['found'] >= target['copies']:
                            foundtarget = True
                            # also skip the rest of the loop since all target cards are distinct
                            break
            if foundtarget:
                alltargets = True
                for target in targets:
                    if target.get('found', False) < target['copies']:
                        # if we haven't found enough of this card set sentinel to false
                        alltargets = False
                if alltargets:
                    # success!
                    for target in targets:
                        del target['found']
                    break
                foundtarget = False
    
        # log our results
        if outfile:
            with open(outfile, "w") as file:
                for i, pack in enumerate(self.pack_list):
                    if i == opened:
                        file.write("All targets found in desired quantities. Targets: " + str(targets) + '\n')
                    if pack[1]['rarity'] == 'R':
                        file.write(str(pack) + " double rare \n")
                    else:
                        file.write(str(pack) + "\n")
        return opened

    def pull_for_cards2(self, targets):
        box_log = {
            i: {} for i in self.rarities
        }
        for i, pack in enumerate(self.pack_list):
            for card in pack:
                if box_log[card['rarity']].get(card['index'], False):
                    box_log[card['rarity']][card['index']].append(i + 1)
                else:
                    box_log[card['rarity']][card['index']] = [i + 1]
        self.box_log = box_log
        most_packs = 1
        for card in targets:
            packs_for_this_card = box_log[card['rarity']][card['index']][card['copies'] - 1]
            if packs_for_this_card > most_packs: most_packs = packs_for_this_card
        return most_packs


    def hypergeom_probs(self, targets):
        mingoal = []
        copies_in_box = []
        for card in targets:
            mingoal.append(card['copies'])
            if card.get('extra', False):
                copies_in_box.append(math.ceil(self.boxstats[1][self.rarities.index(card['rarity'])]
                                         / self.boxstats[0][self.rarities.index(card['rarity'])]))
            else:
                copies_in_box.append(math.floor(self.boxstats[1][self.rarities.index(card['rarity'])]
                                          / self.boxstats[0][self.rarities.index(card['rarity'])]))
        othercards = (self.template['packs_total'] * 3) - sum(copies_in_box)
        copies_in_box.append(othercards)
        
        cdf = []
        permutations = []
        means_by_pack = []
        variance_by_pack = []
        # here we calculate all the permutations in which we have found our target cards in desired quantities
        ranges = [[mingoal[i], copies_in_box[i] + 1] for i in range(len(mingoal))]
        operations = reduce(lambda a, b: a * b, (p[1] - p[0] for p in ranges)) - 1
        result = [i[0] for i in ranges]
        pos = len(ranges) - 1
        increments = 0
        permutations.append(list(result))
        while increments < operations:
            if result[pos] == ranges[pos][1] - 1:
                result[pos] = ranges[pos][0]
                pos -= 1
            else:
                result[pos] += 1
                increments += 1
                pos = len(ranges) - 1  # increment the innermost loop
                permutations.append(list(result))
        
        for pack in range(1, self.template['packs_total'] + 1):
            dist = multivariate_hypergeom(m=copies_in_box, n=pack * 3)
            totalprob = 0.0
            for case in permutations:
                case.append(pack * 3 - sum(case))
                totalprob += dist.pmf(x=case)
                case.pop()
            cdf.append(totalprob)
            means_by_pack.append(dist.mean()[:-1])
            variance_by_pack.append(dist.var()[:-1])

        pmf = [cdf[0]] + [cdf[i] - cdf[i - 1] for i in range(1, len(cdf))]
        return pmf, cdf, np.asarray(means_by_pack), np.asarray(variance_by_pack)








# define some functions to calculate hypergeometric probabilities
# main()
'''
newbox = box(180)
newbox.pick_target_cards(targets)
trials = []
# set the parameters for how many trials and what card we're looking for
# then simulate pulling for the card a lot of times
for i in range(numtrials):
    if logging:
        trials.append(pull_for_cards(newbox, targets, outfile="logs/trial" + str(i) + ".txt"))
        newbox.reset()
    else:
        trials.append(pull_for_cards(newbox, targets))
        newbox.reset()

fig, ax = plt.subplots(1, 2, sharex=True, tight_layout=True)
hist, bins, patches = ax[0].hist(trials, bins=range(1, newbox.template['packs_total'] + 2), density=True)
cumulative, bins2, patches2 = ax[1].hist(trials, bins=bins,
                                         cumulative=True, density=True, histtype='step',
                                         label='Simulated')
ax[1].plot(bins[:-1], cdf, 'k--', label='Theoretical')
ax[0].plot(bins[:-1], pmf, 'k--', label='Theoretical')
ax[1].add_artist(lines.Line2D([0, 180], [0.5, 0.5], c='red'))
ax[1].legend(loc='lower right')
ax[1].set_title("Chance After N Packs")
ax[0].set_title("Chance of Finding Last Card in Pack N")
plt.xlim([0, 180])
plt.show()
# [print(card.rarity,',', card.index,',', card.extra) for card in newbox.list]
# print(pull_for_card(newbox, "N"))
'''