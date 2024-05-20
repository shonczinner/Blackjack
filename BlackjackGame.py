from modules.Player import Player
from modules.Deck import Deck
from modules.Hand import Hand
from modules.utilities import get_integer, get_selection

class BlackjackGame:
  def __init__(self):
    # A game has a Player, a dealer's hand, a pot, and a Deck
    self.player = Player()

    self.dealer_hand = None
    self.dealer_revealed = False
    #bet probably needs to be changed for one per hand
    #as in a list of bets
    self.deck = Deck()

  def reset(self):
    self.deck.add_to_discard(self.dealer_hand.cards)
    for hand in self.player.hands:
      self.deck.add_to_discard(hand.cards)

    self.player.reset_hands()
    self.dealer_hand = None
    self.dealer_revealed = False

  def get_bet(self):
   bet = get_integer(f"Enter your bet (1-{self.player.chips}). 0 will exit."+"\n",self.player.chips)
   print("")
   return bet


  def start_deal(self):
    cards = self.deck.draw_cards(4)

    self.player.hands.append(Hand())
    self.player.hands[0].add_cards(cards[:2])

    self.dealer_hand = Hand()
    self.dealer_hand.add_cards(cards[2:])

  def __str__(self):
    s = ''
    if self.dealer_hand is not None:
      s += "The dealer's hand:\n"
      if not self.dealer_revealed:
        s += f"{self.dealer_hand.cards[0]}, ??\n"
      else:
        s += str(self.dealer_hand)+"\n"
    s += str(self.player)
    s += self.deck.summary()+"\n"
    return s

  def stand(self,hand):
    hand.done = True

  def hit(self,hand):
    card = self.deck.draw_card()
    hand.add_card(card)
    if hand.is_bust():
      hand.done = True
      print('You busted.')

  def double(self,hand):
    bet = hand.bet
    hand.bet += bet
    self.player.chips-=bet
    self.hit(hand)
    hand.done = True

  def split(self,hand):
    cards = hand.cards
    hand1 = Hand()

    bet = hand.bet

    hand1.bet = bet
    self.player.chips -= bet

    hand.reset()
    hand.bet = bet
    hand.add_card(cards[0])

    hand1.add_card(cards[1])

    cards = self.deck.draw_cards(2)
    hand.add_card(cards[0])
    hand1.add_card(cards[1])

    if hand.cards[0].value == 1:
      hand.done = True
      hand1.done = True

    self.player.hands.append(hand1)


  def handle_action(self,hand):
    options = ['stand','hit']
    if self.can_double(hand):
      options.append('double down')
    if self.can_split(hand):
      options.append('split')

    action_str = ', '.join(['\''+x+'\'' for x in options])
    action = get_selection(f"You can {action_str}. Select one.\n",
                           options)

    print("")

    if action == 'stand':
      self.stand(hand)

    if action == 'hit':
      self.hit(hand)

    if action == 'double down' and 'double down' in options:
      self.double(hand)

    if action == 'split' and 'split' in options:
      self.split(hand)

  def deal_dealer(self):
    while(self.dealer_hand.score<17):
      card = self.deck.draw_card()
      self.dealer_hand.add_card(card)

  def play_game(self):
    while True:
      print(str(self))
      bet = self.get_bet()
      if bet == 0:
        break

      self.start_deal()
      self.player.hands[0].bet = bet
      self.player.chips -= bet

      if self.dealer_hand.is_blackjack():
        self.dealer_revealed = True
        print(str(self))
        self.payout()
        self.reset()
        continue

      print(str(self))

      i = 0
      while i<len(self.player.hands):
        hand = self.player.hands[i]
        while not hand.done:
          print(str(hand))
          self.handle_action(hand)
        i+=1

      #only if not every hand busted
      self.deal_dealer()
      self.dealer_revealed = True
      print(str(self))

      self.payout()
      self.reset()
    print(str(self))


  def payout(self):
    dealer_blackjack = self.dealer_hand.is_blackjack()
    for i,hand in enumerate(self.player.hands):
      if hand.is_bust() or (hand.score<self.dealer_hand.score and not self.dealer_hand.is_bust()) or (dealer_blackjack
                                                                 and not hand.is_blackjack()):
        #ways to lose
        print(f"The player lost {hand.bet} chips on Hand {i}.")
      elif hand.is_blackjack() and dealer_blackjack or hand.score == self.dealer_hand.score:
        # ways to draw
        print(f"The player drew on Hand {i}.")
        self.player.chips+=hand.bet
      elif hand.is_blackjack():
        #blackjack
        print(f"The player won {hand.bet*1.5} chips with blackjack on Hand {i}.")
        self.player.chips+=2.5*hand.bet
      else:
        #you won
        print(f"The player won {hand.bet} chips on Hand {i}.")
        self.player.chips+=2*hand.bet


  def can_double(self,hand):
    if len(hand.cards)!=2 or self.player.chips<hand.bet:
      return False

    return True


  def can_split(self,hand):
    if len(hand.cards)!=2 or self.player.chips<hand.bet:
      return False

    if hand.cards[0].value == hand.cards[1].value:
      return True

    return False
  

if __name__ == '__main__':
    g = BlackjackGame()
    g.play_game()
