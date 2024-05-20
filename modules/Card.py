import numpy as np

VALID_CARD_NAMES = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALID_CARD_SUITS = ['H', 'D', 'S', 'C']

class Card:
  def __init__(self,name,suit=None):
    assert name in VALID_CARD_NAMES, "Invalid card name"
    assert suit in VALID_CARD_SUITS + [None], "Invalid card suit"
    self.name = name
    self.suit = suit
    self.value = self.name_to_value(name)

  @staticmethod
  def name_to_value(name):
    assert name in VALID_CARD_NAMES, "Invalid card name"
    if name=='A':
      return 1
    if name in ['J','Q','K']:
      return 10
    else:
      return int(name)

  @staticmethod
  def suit_to_symbol(suit):
    assert suit in VALID_CARD_SUITS + [None], "Invalid card suit"
    if suit=='H':
      return "♥"
    if suit=='D':
      return '♦'
    if suit == 'S':
      return '♠'
    if suit =='C':
      return '♣'

    return ''

  def __str__(self):
    return self.name+self.suit_to_symbol(self.suit)

