class Hand:
  def __init__(self):
    self.cards = []
    self.has_ace = False # If hand contains any ace
    self.useable_ace = False # If hand has any ace which counts as 10
    self.simple_score = 0 #score counting all aces 1
    self.score = 0 #score counting an ace as 10 if doing so doesn't cause bust
    self.bet = None # the amount of chips bet on this hand
    self.done = False # whether a hand is still getting more cards

  def reset(self):
    self.cards = []
    self.has_ace = False # If hand contains any ace
    self.useable_ace = False # If hand has any ace which counts as 10
    self.simple_score = 0 #score counting all aces 1
    self.score = 0 #score counting an ace as 10 if doing so doesn't cause bust
    self.done = False
    self.bet = None

  @classmethod
  def from_simple_score(cls,simple_score,useable_ace):
    self = cls()
    self.useable_ace = useable_ace
    # Assume that if there's a useable ace, there's at least one ace
    # Otherwise assume there is none.
    self.has_ace = useable_ace
    self.simple_score = simple_score
    self.score = simple_score if not useable_ace else simple_score + 10
    return self

  def add_simple_cards(self,values):
    for value in value:
      self.add_simple_card(value)

 
  def add_simple_card(self,value):
    """
    Adds a card of a specific value assuming we don't care about the actual card, just its value
    """
    assert value in range(0,11), "value to add must be one of 1,...,10"
    if value == 1:
        self.has_ace = True

    self.simple_score+=value

    if self.has_ace and self.simple_score<=11:
      self.score = self.simple_score+10
      self.useable_ace = True
    else:
      self.score = self.simple_score
      self.useable_ace = False

  def add_cards(self,cards):
    for card in cards:
      self.add_card(card)

  def add_card(self,card):
    self.cards.append(card)
    if card.name == 'A':
        self.has_ace = True

    self.simple_score+=card.value

    if self.has_ace and self.simple_score<=11:
      self.score = self.simple_score+10
      self.useable_ace = True
    else:
      self.score = self.simple_score
      self.useable_ace = False

  def is_bust(self):
    return self.score > 21

  def is_blackjack(self):
    return len(self.cards) == 2 and self.score == 21

  def simple_hand_str(self):
    return f"{self.simple_score},{int(self.useable_ace)}"

  def __str__(self):
    s = ''
    if self.bet is not None:
      s+=f"Bet: {self.bet}, "
    s += "Hand: "+', '.join([str(card) for card in self.cards])
    if self.done:
      s+='#'
    return s

  @staticmethod
  def get_sorted_simple_hands_str():
    """
    Get sorted simple hands (simple_score, useable ace) as strings.

    Returns:
        list: A list of strings representing simple blackjack hands, sorted in descending order by simple_score and useable ace.
    """
    hands = Hand.generate_simple_hands()
    sorted_hands = [(hand.simple_score,hand.useable_ace) for hand in hands]
    sorted_hands.sort(reverse=True)
    sorted_str_hands = [Hand.from_simple_score(*hand).simple_hand_str() for hand in sorted_hands]
    return sorted_str_hands

  @staticmethod
  def generate_simple_hands():
    """
    Generate simple blackjack hands.

    Returns:
        list: A list of tuples representing simple blackjack hands. Each tuple contains
        two elements:
            1. The "simple_score" of the hand counting any aces as 1.
            2. A binary value indicating whether the "simple_score" is 11 or less
               and an ace is available to count as 11 rather than 1 and doing so
               wouldn't cause bust.

    Notes:
        - The hands are generated to represent all possible combinations of sums (from 1 to 21)
          and the presence or absence of a usable Ace.
        - A usable Ace adds 10 to the hand's sum if it does not result in the sum exceeding 21.
        - The generated hands cover both scenarios with and without a usable Ace.
    """
    hands = []
    for i in range(1,12):
      hands.append(Hand.from_simple_score(i,1))
    for i in range(23):
      hands.append(Hand.from_simple_score(i,0))
    return hands

  @staticmethod
  def simple_hand_to_string(hand):
    """
    Given a hand, this returns the simple hand string.
    """
    return hand.simple_hand_str()

  @staticmethod
  def string_to_simple_hand(str_hand):
    """
    Given a simple hand as a string, returns a hand from it.
    """
    simple_score, useable_ace = map(int, str_hand.split(','))
    return Hand.from_simple_score(simple_score, useable_ace)

  @staticmethod
  def get_single_card_simple_hands_str():
    """
    Returns a list of strings corresponding to 'simple hands' (simple score, useable ace)
    that are possibly the result of a single card.
    """
          
    return ['1,1']+[','.join(map(str,(x,0))) for x in range(2,11)]

  @staticmethod
  def get_pair_simple_hands_str():
    """
    Returns a list of strings corresponding to 'simple hands' (simple score, useable ace)
    that are possibly pairs of two cards of identical value.
    """
    return ['2,1']+[','.join(map(str,(2*x,0))) for x in range(2,11)]