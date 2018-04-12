class Deck():

    cards_in_deck = {}
    cards = 0
    cards_played = {}

    def __init__(self, path):
        with open(path, 'r') as deck_list:
            for line in deck_list:
                line = line.replace('\n', '')
                if line:
                    count, card = line.split(' ', maxsplit=1)
                    self.cards_in_deck[card] = int(count)
                    self.cards += int(count)

    def card_drawn(self, card):
        for key in self.cards_in_deck:
            # print(key.lower())
            # print(card.lower())
            if card.lower() in key.lower():
                if key in self.cards_played.keys():
                    self.cards_played[key] += 1
                else:
                    self.cards_played[key] = 1
                self.cards_in_deck[key] -= 1
                self.cards -= 1
            else:
                pass

    def cards_draw_chance(self):
        print('\n')
        chance_list = []
        for key in self.cards_in_deck:
            if self.cards > 0:
                card_draw_pct = round(self.cards_in_deck[key] / self.cards, 4) * 100
                chance_str = "{} {} in deck --> {:.2f}%".format(self.cards_in_deck[key], key, card_draw_pct)
                chance_list.append((chance_str, card_draw_pct))
        chance_list = [item[0] for item in sorted(chance_list, key=lambda x: x[1], reverse=True)]
        for item in chance_list:
            print(item)

