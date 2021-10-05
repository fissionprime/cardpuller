#card pulling simulator for duel links
import math
import random
import matplotlib.pyplot as plt


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
extras = [boxstats[1][i] - (math.floor(boxstats[1][i] / boxstats[0][i]) * boxstats[0][i])
          for i in range(len(boxstats[0]))]

class box():
    def __init__(self):
        self.list = []
        for i, count in enumerate(boxstats[1]):
            while count:
                for index in range(0, boxstats[0][i]):
                    if not count:
                        break
                    self.list.append(card(rarities[i], index,(index < extras[i])))
                    count -= 1
        random.shuffle(self.list)
    def pull_pack(self):
        pack = []
        for i, card in enumerate(self.list):
            if card.rarity == "N":
                pack.append(self.list.pop(i))
                break
        for i, card in enumerate(self.list):
            if card.rarity in ["N", "R"]:
                pack.append(self.list.pop(i))
                break
        for i, card in enumerate(self.list):
            if card.rarity in ["R", "SR", "UR"]:
                pack.append(self.list.pop(i))
                break
        return pack

    def reset(self):
        self.__init__()

class card():
    def __init__(self, rarity: str, index: int, extra: bool):
        self.rarity = rarity
        self.index = index
        self.extra = extra

def pull_for_card(box: box, rarity: str, extra: bool=False, copies: int=1):
    #randomly pick a card that fits the specifications
    packs_opened = 0
    index = None
    if not extra:
        index = random.randint(extras[rarities.index(rarity)], boxstats[0][rarities.index(rarity)] - 1)
    else:
        index = random.randint(0, extras[rarities.index(rarity)] - 1)
    while True:
        pack = box.pull_pack()
        packs_opened += 1
        for card in pack:
            if card.rarity == rarity and card.index == index:
                copies -= 1
                if copies == 0:
                    return packs_opened

newbox = box()
trials = []
for i in range(10000):
    trials.append(pull_for_card(newbox, "UR"))
    newbox.reset()

fig, ax = plt.subplots(tight_layout=True)
hist = ax.hist(trials, bins=packs_in_box //2)
plt.show()
#[print(card.rarity,',', card.index,',', card.extra) for card in newbox.list]
#print(pull_for_card(newbox, "N"))