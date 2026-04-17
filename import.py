import random

coin = random.choice(["heads", "tails"])
print(coin)


from random import choice

coin = choice(["heads", "tails"])
print(coin)


import random

number = random.randint(1, 10)
print(number)

import random

cards = ["jack", "queen", "king"]
random.shuffle(cards)
for card in cards:
    print(card)