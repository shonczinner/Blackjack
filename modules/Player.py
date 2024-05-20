class Player:
  def __init__(self):
    # A player has cash, and hands (possibly multiple due to splitting)
    self.chips = 100
    self.hands = []

  def __str__(self):
    s = ''
    s += f"Player has {self.chips} chips.\n"
    if len(self.hands)>0:
      s += "Player hands:\n"
      for i,hand in enumerate(self.hands):
        s+= f"Hand {i}: {hand}\n"
    return s

  def reset_hands(self):
    self.hands = []