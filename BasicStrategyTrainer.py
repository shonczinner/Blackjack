from modules.Deck import Deck
from modules.Hand import Hand
from modules.utilities import get_selection
from BlackjackAnalysis import BlackjackAnalysis

import os
import sys
import numpy as np
import pandas as pd

# Check if the files exist, otherwise say they don't exist and exit.
if (os.path.exists('hit_matrix.csv') and
    os.path.exists('dd_matrix.csv') and
    os.path.exists('split_matrix.csv')):
    HIT_MATRIX = pd.read_csv('hit_matrix.csv',    index_col=0)
    DD_MATRIX = pd.read_csv('dd_matrix.csv',index_col=0)
    SPLIT_MATRIX = pd.read_csv('split_matrix.csv', index_col=0)
else:
    pass



class BasicStrategyTrainer:
  def __init__(self):
    self.n_turns = 0
    self.n_correct = 0

    self.wrong_hands = []
    self.wrong_hands_dealer = []
    self.wrong_actions = []
    self.correct_actions_to_wrong_hands = []

    self.player_hand = None
    self.dealer_hand = None

    self.deck = Deck()

  def print_performance(self):
    print(f"You got {self.n_correct} correct out of {self.n_turns}")

  def print_wrong_hands(self):
    if len(self.wrong_hands)<1:
      return
    
    print("Wrong hands:")
    for hand,wrong,correct,dealer_hand in zip(self.wrong_hands,self.wrong_actions,self.correct_actions_to_wrong_hands,
                                  self.wrong_hands_dealer):
      print(f"When you had {hand} and the dealer had Hand: {dealer_hand}, ?? you chose to {wrong} but the correct action was {correct}.")

  def play_game(self):
    while True:

      self.start_deal()

      print("Player hand:")
      print(str(self.player_hand))
      print("Dealer hand:")
      print("Hand: "+str(self.dealer_hand.cards[0])+", ??")
      selected_action = self.handle_action()
      if selected_action == 'exit':
        break

      self.n_turns+=1
      correct = self.get_correct_action()

      if selected_action == correct:
        self.n_correct+=1
        print("Correct!")
      else:
        print(f"Incorrect. The correct action was {correct}.")
        self.wrong_hands.append(self.player_hand)
        self.wrong_actions.append(selected_action)
        self.correct_actions_to_wrong_hands.append(correct)
        self.wrong_hands_dealer.append(self.dealer_hand)


      self.reset_hands()
    self.print_performance()
    self.print_wrong_hands()


  def handle_action(self):
    options = ['stand','hit','double']
    if self.can_split():
      options.append('split')

    options.append("exit")

    action_str = ', '.join(['\''+x+'\'' for x in options])
    action = get_selection(f"You can {action_str}. Select one.\n",
                           options)

    return action

  def reset(self):
    self.n_turns = 0
    self.n_correct = 0

    self.wrong_hands = []
    self.wrong_hands_dealer = []
    self.wrong_actions = []
    self.correct_actions_to_wrong_hands = []

    self.player_hand = None
    self.dealer_hand = None

    self.deck = Deck()


  def reset_hands(self):
    self.deck.add_to_discard(self.dealer_hand.cards)
    self.deck.add_to_discard(self.player_hand.cards)

    self.player_hand = None
    self.dealer_hand = None

  def start_deal(self):
    cards = self.deck.draw_cards(4)

    self.player_hand = Hand()
    self.player_hand.add_cards(cards[:2])

    self.dealer_hand = Hand()
    self.dealer_hand.add_cards(cards[2:])

  def get_correct_action(self):
    row = self.player_hand.simple_hand_str()
    hand = Hand()
    hand.add_card(self.dealer_hand.cards[0])
    col = hand.simple_hand_str()

    if self.can_split() and SPLIT_MATRIX.loc[row,col]:
      return 'split'

    if DD_MATRIX.loc[row,col]:
      return 'double'

    if HIT_MATRIX.loc[row,col]:
      return 'hit'

    return 'stand'

  def can_split(self):
    if self.player_hand.cards[0].value == self.player_hand.cards[1].value:
      return True

    return False

if __name__ == '__main__':
    if (os.path.exists('hit_matrix.csv') and
    os.path.exists('dd_matrix.csv') and
    os.path.exists('split_matrix.csv')):
        pass
    else:
        print("Necessary files do not exist. Will compute them.")
        bl1 = BlackjackAnalysis()
        print("Computing analysis of Blackjack.")
        bl1.compute()
        print("Saving analysis of Blackjack.")
        bl1.exportStrategy()
        bl1.exportEV()
        bl1.exportResults()
        HIT_MATRIX = pd.read_csv('hit_matrix.csv',    index_col=0)
        DD_MATRIX = pd.read_csv('dd_matrix.csv',index_col=0)
        SPLIT_MATRIX = pd.read_csv('split_matrix.csv', index_col=0)

    g = BasicStrategyTrainer()
    g.play_game()