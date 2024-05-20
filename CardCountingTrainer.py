from modules.Deck import Deck
from modules.utilities import get_integer
from BlackjackAnalysis import BlackjackAnalysis
from ComputeEffectOfRemoval import export_EORs

import pandas as pd
import os

# Check if the files exist, otherwise say they don't exist and exit.
if (os.path.exists('effect_of_removals.csv') and
    os.path.exists('EV.csv')):
  EORs = pd.read_csv('effect_of_removals.csv',index_col='card_value')
  EV = pd.read_csv('EV.csv',index_col=0).values[0][0]
  EORs = EORs.iloc[:,0]
  HILO = (-EORs/EV).round().astype(int)
else:
    pass


class CardCountTrainer:
  def __init__(self):
    self.n_turns = 0
    self.n_correct = 0

    self.deck = Deck()
    self.count = 0

  def reset(self):
    self.n_turns = 0
    self.n_correct = 0

    self.deck = Deck()
    self.count = 0

  def print_performance(self):
    print(f"You got {self.n_correct} correct out of {self.n_turns}")

  @staticmethod
  def get_player_count():
    return get_integer("Enter the current count or 'exit' to exit\n")

  def play_game(self, n_cards = 4):
    print("The HILO count is used here:")
    print(HILO)
    while True:
      if len(self.deck.cards)<n_cards:
        self.deck.reshuffle_deck()
      print(self.deck.summary())
      print(f"The current count is {self.count}")
      cards = self.deck.draw_cards(n_cards)
      for card in cards:
        print(str(card))
        self.count += HILO[card.value]

      value = self.get_player_count()
      if value == 'exit':
        break

      if value == self.count:
        print("Correct!")
        self.n_correct+=1
      else:
        print(f"Incorrect. The count is {self.count}")

      self.n_turns+=1
    self.print_performance()

if __name__ == '__main__':
  if (os.path.exists('effect_of_removals.csv') and
      os.path.exists('EV.csv')):
    pass
  else:
    print("Necessary files do not exist. Will compute them.")
    bl1 = BlackjackAnalysis()
    bl1.compute()
    bl1.exportEV()
    bl1.exportStrategy()
    bl1.exportResults

    export_EORs()

    EORs = pd.read_csv('effect_of_removals.csv',index_col='card_value')
    EV = pd.read_csv('EV.csv',index_col=0).values[0][0]
    EORs = EORs.iloc[:,0]
    HILO = (-EORs/EV).round().astype(int)

cct = CardCountTrainer()
cct.play_game()
