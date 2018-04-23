from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()


class BaseModel:
    def add_object(self, path=None, action=None, user_id=None, user_type=None, user_agent=None):
        try:
            self.created_by_id = user_id
        except AttributeError:
            print('error')
            pass
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            e = str(e)
            db.session.rollback()
            new_error = Errors()
            new_error.add_error(e, path, action, user_id, user_type, user_agent)
            return e
        return False

    def update_object(self, path=None, action=None, user_id=None, user_type=None, user_agent=None):
        try:
            self.last_updated = datetime.datetime.utcnow()
            self.last_updated_id = user_id
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            e = str(e)
            new_error = Errors()
            new_error.add_error(e, path, action, user_id, user_type, user_agent)
            return e
        return False

    def delete_object(self, path=None, action=None, user_id=None, user_type=None, user_agent=None):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            e = str(e)
            new_error = Errors()
            new_error.add_error(e, path, action, user_id, user_type, user_agent)
            return e
        return False

    def serialize(self, *excluded_attributes, exclude_password=True):
        attribute_dict = {attr: getattr(self, attr) for attr in self.__dict__.keys() if attr[0] != '_'}
        if exclude_password:
            try:
                del attribute_dict['password']
            except KeyError:
                pass
        for ex_attr in excluded_attributes:
            try:
                del attribute_dict[ex_attr]
            except KeyError:
                pass
        return attribute_dict

    def get(self, item):
        return getattr(self, item, None)

    def copy_attrs(self, model_to_copy):
        attribute_dict = {attr: getattr(model_to_copy, attr) for attr in model_to_copy.__dict__.keys()
                          if attr[0] != '_' and attr != 'created' and '_id' not in attr}
        for attr in attribute_dict:
            self.__setattr__(attr, getattr(model_to_copy, attr, None))


class Deck(db.Model, BaseModel):
    __tablename__ = 'deck'
    deck_id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.Integer, db.ForeignKey("user.user_id", ondelete="CASCADE"))

    # cards = db.relationship('Cards')

    cards_in_deck = {}
    card_count = 0
    cards_played = {}
    cards_prob = {}

    def __init__(self, path=None, cards_in_deck=None, card_count=None, cards_played=None,
                 cards_prob=None):
        if path:
            self.cards_in_deck = {}
            self.card_count = 0
            self.cards_played = {}
            self.cards_prob = {}
            with open(path, 'r') as deck_list:
                for line in deck_list:
                    line = line.replace('\n', '')
                    if line:
                        count, card = line.split(' ', maxsplit=1)
                        self.cards_in_deck[card] = int(count)
                        self.card_count += int(count)
        if cards_in_deck:
            self.cards_in_deck = cards_in_deck
        if card_count:
            self.card_count = card_count
        if cards_played:
            self.cards_played = cards_played
        if cards_prob:
            self.cards_prob = cards_prob

    def card_drawn(self, card):
        for key in self.cards_in_deck:
            # print(key.lower())
            # print(card.lower())
            if card.lower() in key.lower():
                if self.cards_in_deck[key] > 0:
                    if key in self.cards_played.keys():
                        self.cards_played[key] += 1
                    else:
                        self.cards_played[key] = 1
                    self.cards_in_deck[key] -= 1
                    self.card_count -= 1
                    self.cards_draw_chance()
                    return True
        return False
    # add combinatorics to get chances over next 3-5 turns
    def cards_draw_chance(self):
        for key in self.cards_in_deck:
            if self.card_count > 0:
                card_draw_pct = round(self.cards_in_deck[key] / self.card_count, 4) * 100
                # chance_str = "{} {} in deck --> {:.2f}%".format(self.cards_in_deck[key], key, card_draw_pct)
                self.cards_prob[key] = round(card_draw_pct, 2)

    # def load_deck(self):
    #     for card in self.cards:
    #         self.cards_in_deck[card.name] = int(card.count)
    #         self.card_count += int(card.count)

    def card_count_deck(self, card):
        if card in self.cards_in_deck.keys():
            return self.cards_in_deck[card]
        else:
            return 0

    def card_count_played(self, card):
        if card in self.cards_played.keys():
            return self.cards_played[card]
        else:
            return 0

    def card_count_probability(self, card):
        if card in self.cards_prob.keys():
            return self.cards_prob[card]
        else:
            return 0

    def set_initial_probs(self):
        for key in self.cards_in_deck:
            if self.card_count > 0:
                card_draw_pct = round(self.cards_in_deck[key] / self.card_count, 4) * 100
                self.cards_prob[key] = round(card_draw_pct, 2)


class Card(db.Model, BaseModel):
    __tablename__ = 'card'
    card_id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey("deck.deck_id", ondelete="CASCADE"))
    card_name = db.Column(db.String(100))
    card_count = db.Column(db.Integer)

    deck = db.relationship('Deck')