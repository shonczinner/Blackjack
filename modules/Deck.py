from modules.Card import Card, VALID_CARD_NAMES, VALID_CARD_SUITS
import numpy as np

class Deck:
  def __init__(self,unshuffled = False):
    self.cards = self.create_deck()
    self.discarded_cards = []
    if not unshuffled:
      self.shuffle_deck()

  def create_deck(self):
    return [Card(name,suit) for name in VALID_CARD_NAMES for suit in VALID_CARD_SUITS]

  def shuffle_deck(self):
    np.random.shuffle(self.cards)

  def reshuffle_deck(self):
    self.cards = self.create_deck()
    self.discarded_cards = []
    self.shuffle_deck()

  def draw_cards(self,n):
    assert n>0, "need to draw more than 0 cards"
    return [self.draw_card() for _ in range(n)]

  def draw_card(self):
      if len(self.cards) == 0:
          # If the deck is empty, reshuffle the discard pile into the deck
          self.cards.extend(self.discarded_cards)
          self.discarded_cards = []
          self.shuffle_deck()

      # Draw a card from the top of the deck and remove it from the deck
      drawn_card = self.cards.pop(0)
      return drawn_card

  def add_to_discard(self, card_or_cards):
      if isinstance(card_or_cards, list):
          self.discarded_cards.extend(card_or_cards)
      else:
          self.discarded_cards.append(card_or_cards)

  def summary(self):
    return f"The deck has {len(self.cards)} cards remaining."