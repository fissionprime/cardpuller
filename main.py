#card pulling simulator for duel links
import math
import random
import matplotlib.pyplot as plt
import matplotlib.lines as lines
from scipy.special import comb
import numpy as np

#info on desired cards
desired_rarity = 'R'
desired_copies = 3
#does the desired card have extra copies in the box?
desired_extra = False
#set logging to True if you want each simulated box pull recorded to a txt file
logging = True

#some info about the box contents
packs_in_box = 180
UR_count = 9
UR_names = 9
SR_count = 22
SR_names = 11
R_count = 168
R_names = 28
N_count = 341
N_names = 42

boxstats = [[UR_names, SR_names, R_names, N_names], [UR_count, SR_count, R_count, N_count]]
rarities = ["UR", "SR", "R", "N"]
#extra refers to R and N cards which the box contains one more copy of, relative to the others in the box
extras = [boxstats[1][i] - (math.floor(boxstats[1][i] / boxstats[0][i]) * boxstats[0][i])
          for i in range(len(boxstats[0]))]
#this is basically for debugging purposes
indices = []

class box():
    def __init__(self):
        self.packs = packs_in_box
        self.list = []
        #the number of packs with 2 R+ cards plus the number with 2 N cards
        #is equal to the total number of packs in the box
        self.doublerares = sum(boxstats[1][:3]) - packs_in_box
        self.doublecommons = packs_in_box - self.doublerares
        for i, count in enumerate(boxstats[1]):
            while count:
                for index in range(0, boxstats[0][i]):
                    if not count:
                        break
                    self.list.append(card(rarities[i], index,(index < extras[i])))
                    count -= 1
        random.shuffle(self.list)
    def pull_pack(self):
        self.packs -= 1
        pack = []
        foundcard = False
        for i, card in enumerate(self.list):
            if card.rarity == "N":
                foundcard = True
                pack.append(self.list.pop(i))
                break
        if not foundcard:
            print("failed to find card 1 to add to pack")
            [print(card.rarity, ',', card.index, ',', card.extra) for card in self.list]
        foundcard = False
        for i, card in enumerate(self.list):
            if card.rarity in ["N", "R"]:
                if card.rarity == 'R':
                    #check if we still have extra R+ cards
                    if not self.doublerares:
                        #if there aren't enough R cards left, prevent this pack from containing more than 1
                        continue
                    self.doublerares -= 1
                else:
                    if not self.doublecommons:
                        continue
                    self.doublecommons -= 1
                foundcard = True
                pack.append(self.list.pop(i))
                break
        if not foundcard:
            print("failed to find card 2 to add to pack")
            [print(card.rarity, ',', card.index, ',', card.extra) for card in self.list]
        foundcard = False
        for i, card in enumerate(self.list):
            if card.rarity in ["R", "SR", "UR"]:
                foundcard = True
                pack.append(self.list.pop(i))
                break
        if not foundcard:
            print("failed to find card 3 to add to pack")
            [print(card.rarity, ',', card.index, ',', card.extra) for card in self.list]
        foundcard = False
        if len(pack) < 3:
            print("Something went wrong. Pack has less than 3 cards.")
        return pack

    def reset(self):
        self.__init__()

class card():
    def __init__(self, rarity: str, index: int, extra: bool):
        self.rarity = rarity
        self.index = index
        self.extra = extra

def pull_for_card(box: box, rarity: str, extra: bool=False, copies: int=1, outfile=None):
    #randomly pick a card that fits the specifications
    packs_opened = 0
    index = None
    if not extra:
        index = random.randint(extras[rarities.index(rarity)], boxstats[0][rarities.index(rarity)] - 1)
    else:
        index = random.randint(0, extras[rarities.index(rarity)] - 1)
    indices.append(index)
    #now pull until we find a copy of the card we chose
    cardspulled = []
    while True:
        pack = box.pull_pack()
        packinfo = []
        packs_opened += 1
        for card in pack:
            packinfo.append({"rarity": card.rarity, "index": card.index})
            if card.rarity == rarity and card.index == index:
                copies -= 1
        if copies <= 0:
            cardspulled.append(packinfo)
            break
            #return packs_opened
        cardspulled.append(packinfo)
    #log the results of the box pull to a file
    if outfile:
        with open(outfile, "w") as file:
            for pack in cardspulled:
                file.write(str(pack) + "\n")

            file.write("remaining packs: %i\n" % (len(box.list) / 3))
            remaining = [str(card.rarity) + ', ' + str(card.index)+ ', '+ str(card.extra) for card in box.list]
            file.write("\n".join(str(line) for line in remaining))
    return packs_opened

#define some functions to calculate hypergeometric probabilities
def hypergeom_pmf(N, A, n, x):
    '''
    Probability Mass Function for Hypergeometric Distribution
    Taken from John DeJesus
    :param N: population size
    :param A: total number of desired items in N
    :param n: number of draws made from N
    :param x: number of desired items in our draw of n items
    :returns: PMF computed at x
    '''
    Achoosex = comb(A, x)
    NAchoosenx = comb(N - A, n - x)
    Nchoosen = comb(N, n)

    return (Achoosex) * NAchoosenx / Nchoosen


def hypergeom_cdf(N, A, n, t, min_value=None):
    '''
    Cumulative Density Funtion for Hypergeometric Distribution
    also from John DeJesus
    :param N: population size
    :param A: total number of desired items in N
    :param n: number of draws made from N
    :param t: number of desired items in our draw of n items up to t
    :returns: CDF computed up to t
    '''
    if min_value:
        return np.sum([hypergeom_pmf(N, A, n, x) for x in range(min_value, t + 1)])

    return np.sum([hypergeom_pmf(N, A, n, x) for x in range(t + 1)])

newbox = box()
trials = []
#set the parameters for how many trials and what card we're looking for
#then simulate pulling for the card a lot of times
if logging:
    for i in range(1000):
        trials.append(pull_for_card(newbox, desired_rarity, extra=desired_extra,
                                    copies=desired_copies, outfile="logs/trial" + str(i) + ".txt"))
        newbox.reset()
else:
    for i in range(1000):
        trials.append(pull_for_card(newbox, desired_rarity, extra=desired_extra,
                                    copies=desired_copies))
        newbox.reset()

#now calculate the theoretical probability distribution (ignoring pack logic)
theoretical = []
desired_rarity = rarities.index(desired_rarity)
numcards = boxstats[1][desired_rarity] / boxstats[0][desired_rarity]
if desired_extra:
    numcards = math.ceil(numcards)
else:
    numcards = math.floor(numcards)
for i in range(1, packs_in_box+1):
    theoretical.append(hypergeom_cdf(packs_in_box*3, numcards, i*3, numcards, desired_copies))


fig, ax = plt.subplots(1, 2,sharex=True, tight_layout=True)
hist, bins, patches = ax[0].hist(trials, bins=range(1,packs_in_box+1), density=True)
cumulative, bins2, patches2 = ax[1].hist(trials, bins=bins,
                                       cumulative=True, density=True, histtype='step',
                                         label='Simulated')
ax[1].plot(bins, theoretical, 'k--', label='Theoretical')
ax[1].add_artist(lines.Line2D([0,180], [0.5, 0.5], c='red'))
plt.xlim([0,180])
plt.show()
#[print(card.rarity,',', card.index,',', card.extra) for card in newbox.list]
#print(pull_for_card(newbox, "N"))