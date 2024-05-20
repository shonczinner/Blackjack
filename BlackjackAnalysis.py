from modules.Card import Card
from modules.Hand import Hand
import pandas as pd
import numpy as np
import os

class BlackjackAnalysis():
  def __init__(self,card_probs=None):
    # card_probs is dictionary with 10 values
    # keys are 1-10 denoting the Ace-2,3,4...,9,Face card
    # values are the respective probabilities
    if card_probs is not None:
      self.card_probs = card_probs
    else:
      self.card_probs = {k:v for k,v in zip([1+x for x in range(10)],[4/52]*9+[16/52])}

    # D_probs gives the probability of a dealer starting with the 10 possible
    # starting hands
    self.D_probs = pd.DataFrame.from_dict({ str(k)+',1' if k==1 else str(k)+',0':v for k,v in self.card_probs.items()},
                       orient='index').iloc[:,0]

    # hands are defined as tuples (sum (before using ace), usuable ace)
    # useable ace: 1
    # no useable ace: 0
    # sum == 0 means no cards
    # A useable ace adds 10 to the score if it doesn't make the score over 21

    self.hands = Hand.generate_simple_hands()

    # Stores the hands as strings to use as indices for matrices and iterating over
    self.str_hands = [hand.simple_hand_str() for hand in self.hands]

    # Certain calculations here are essentially dynamic programming.
    # Note that the sum of a hand (with ace value = 1) can only go up from hitting
    # Therefore if you have the probability of ending up with sum X2 from sum X1
    # you can easily get the probability of ending up with sum X2 from X0<X1.
    # So it's useful to have the hands sorted by sum to iterate over backwards.
    self.sorted_str_hands = Hand.get_sorted_simple_hands_str()

    self.strategy_present = False
    self.hit_matrix = None
    self.dd_matrix = None
    self.split_matrix = None

    self.analysis_present = False
    self.hit_transition_matrix = None
    self.dealer_end_tm = None
    self.dealer_ps = None
    self.dealer_ps2 = None
    self.dealer_ps_nn = None
    self.dealer_cs_nn = None

    self.E_hold = None
    self.E_hit = None
    self.E_M = None
    self.E_dd = None
    self.E_split = None
    self.E_nosplit = None

    self.natural_prob = None
    self.hole_pair_probs = None
    self.hole_hand_probs = None

    self.EVD = None
    self.EV = None

    self.EX2_hold = None
    self.EX2_hit = None
    self.EX2_M = None
    self.EX2_dd = None
    self.EX2_split = None
    self.EX2_nosplit = None
    self.EX2D = None
    self.V = None

  def compute(self,computeStrategy=True):
    assert computeStrategy or self.strategy_present, "Analysis can't be done without having a strategy or computing one"
    # hit_transition_matrix is a stochastic matrix denoting the probability of going
    # from a hand to the next hand after hitting (receiving another card)
    self.hit_transition_matrix = self.compute_hit_transition_matrix()

    # dealer_end_tm is a stochastic matrix denoting the probability of going from a hand
    # to the *final* hand after following how dealers must hit/stand
    self.dealer_end_tm = self.f_dealer_end_tm()

    # dealer_ps is a stochastic matrix denoting the probability of going from
    # one of the 10 possible startings hands to the possible final hands after
    # following how dealers must hit/stand.
    # The possible final hands are 17,18,...,21,>21 (denoted 22)
    self.dealer_ps = self.f_dealer_ps()

    # dealer_ps2 is the same as dealer_ps except a column is added to differentiate
    # between 21 and a *natural* 21.  A natural 21 is "blackjack" or 21 in two cards.
    # This distinction is necessary since when the dealer has a natural, the
    # player is not given an opportunity to hit in order to possibly draw.
    # The player automatically draws if they also have a natural. Otherwise,
    # they lose.
    self.dealer_ps2 = self.f_dealer_ps2()

    # dealer_ps is a stochastic matrix denoting the *conditional* probability of going from
    # one of the 10 possible startings hands to the possible final hands after
    # following how dealers must hit/stand *given* the dealer doesn't have a natural.
    # See above for motivation.
    self.dealer_ps_nn = self.f_dealer_ps_nn()

    # dealer_cs_nn is a matrix denoting the cumalative probability of going from
    # one of the 10 possible starting hands to the possible final hands after
    # following how dealers must hit/stand *given* the dealer doesn't have a natural.
    # For clarification dealer_ps_nn gives,
    # P(dealer ends with sum = xT |start with hand x0 and dealer doesn't get a natural)
    # dealer_cs_nn gives,
    # P(dealer ends with sum <= xT |start with hand x0 and dealer doesn't get a natural)
    # This is used as part of determining the probability of beating the dealer.
    # (having a sum greater than the dealer)
    self.dealer_cs_nn = self.dealer_ps_nn.cumsum(axis=1)

    # E_hold gives the expected value of holding for a specific hand of the player and
    # specific hand showing for the dealer.
    # Winning has value +1, drawing has value 0, and losing has value -1.
    self.E_hold = self.f_E_hold()

    # E_hit gives the expected value *hitting exactly once and then holding*
    # for a specific hand of the player and a specific hand showing for the dealer.
    self.E_hit = self.f_E_hit()

    if computeStrategy:
      # hit_matrix is true when you should hit for a specific hand of the player
      # and specific hand showing for the dealer.
      # It checks whether the expected value of hitting once and then holding
      # is greater than the expected value of just holding.
      # >= is used because if hitting once and then holding is just as good,
      # you may as well hit (and hitting twice might be even better than holding)
      # np.isclose is added due to floating point error
      self.hit_matrix = ((self.E_hit>=self.E_hold)|
                         np.isclose(self.E_hit,self.E_hold,atol=1e-9))

    # E_M gives the expected value of following the hitting strategy calculated
    # above at a specific hand for the player and specific hand showing for the dealer.
    self.E_M = self.f_E_M()

    # E_dd gives the expected value of doubling down at a specific hand for the
    # player and specific hand showing for the dealer. Doubling down doubles your bet
    # but limits you to only be allowed to draw hit once and then hold. That's exactly
    # double what we calculated as E_hit.
    self.E_dd = 2*self.E_hit

    if computeStrategy:
      # dd_matrix is true when you should double down for a specific hand of the player
      # and specific hand showing for the dealer.
      # It checks whether the expected value of doubling down is greater than
      # the expected value of following the hitting strategy calculated above.
      self.dd_matrix = self.E_dd>self.E_M

    # E_split gives the expected value of splitting at a possible splitting hand of the player
    # and specific hand showing for the dealer.
    # Possible splitting hands are when sum is multiple of two, and there is no ace
    # unless the sum is two, in which case there is a useable ace.
    # Splitting divides a hand of two cards of equal value into two individual hands
    # and bets the current bet on each new hand.
    # When aces are split, only one more card may be drawn.
    self.E_split = self.f_E_split()

    # E_split gives the expected values of not splitting and instead following
    # the hitting and doubling down strategy computed above at a possible
    # splitting hand of the player and specific hand showing for the dealer.
    # It's essentially just the element wise maximum of E_M and E_dd.
    self.E_nosplit = self.f_E_nosplit()

    if computeStrategy:
      # split_matrix is true when you should split at a possible splitting hand
      # of the player of the player and specific hand showing for the dealer.
      # It checks whether the expected value of splitting  is greater than
      # the expected value of following not splitting strategy calculated above.
      self.split_matrix = self.E_split>self.E_nosplit

    #EV stuff
    # natural_prob is the probability of getting 21 in two cards
    # aka blackjack.
    # hole_pair_probs is the probability of getting a pair in your first two cards.
    # hole_hand_probs is the remaining probability of other hands. Aka the
    # probability of a certain hand minus the probability that its a natural or a pair
    # the "hole" in blackjack is your first two cards.
    (self.natural_prob,
     self.hole_pair_probs,
     self.hole_hand_probs) = self.compute_hole_probs()

    # EVD is the expected value for each specific hand shown by the dealer.
    self.EVD = self.f_EVD()
    # EV is the expected value of playing a hand of blackjack.
    self.EV = self.EVD.multiply(self.D_probs).sum()

    # These are used to calculate the variance instead of expected values.
    # They are computed quite similarly. The identity Var(X)=E(X**2)-(E(X))**2
    # is quite useful here. First E(X**2) is calculated. Then finally the identity
    # is used to find the variance.
    self.EX2_hold = self.f_E_hold(X2=True)
    self.EX2_hit = self.f_E_hit(X2=True)
    self.EX2_M = self.f_E_M(X2=True)
    self.EX2_dd = 4*self.EX2_hit #E((2X)**2)=4E(X**2)
    self.EX2_split = self.f_E_split(X2=True)
    self.EX2_nosplit = self.f_E_nosplit(X2=True)
    self.EX2D = self.f_EX2D()
    self.V = self.EX2D.multiply(self.D_probs).sum()-self.EV**2

    self.analysis_present = True
    if computeStrategy:
      self.strategy_present = True

  def compute_hole_probs(self):
    # natural_prob is the probability of getting 21 in two cards
    # aka blackjack.
    # hole_pair_probs is the probability of getting a pair in your first two cards.
    # hole_hand_probs is the remaining probability of other hands. Aka the
    # probability of a certain hand minus the probability that its a natural or a pair
    # the "hole" in blackjack is your first two cards.
    natural_prob = 0
    hole_pair_probs = pd.Series(index=Hand.get_pair_simple_hands_str(),dtype=float).fillna(0)
    hole_state_probs = pd.Series(index=self.str_hands,dtype=float).fillna(0)

    for card1,p1 in self.card_probs.items():
      for card2,p2 in self.card_probs.items():
        if min(card1,card2)==1:
          ace=1
        else:
          ace=0
        state = (card1+card2,ace)
        if state==(11,1):
          natural_prob+=p1*p2
          continue
        if card1==card2:
          hole_pair_probs.loc[self.hand_to_string(state)]+=p1*p2
          continue

        hole_state_probs.loc[self.hand_to_string(state)]+=p1*p2

    return natural_prob, hole_pair_probs, hole_state_probs

  def exportStrategy(self,path="",pretty=False):
    assert self.analysis_present, "Strategy isn't avaiable to export"

    self.hit_matrix.to_csv(os.path.join(path,'hit_matrix'+'.csv'))
    self.dd_matrix.to_csv(os.path.join(path,'dd_matrix'+'.csv'))
    self.split_matrix.to_csv(os.path.join(path,'split_matrix'+'.csv'))

  def importStrategy(self,path=""):
    self.hit_matrix = pd.read_csv(os.path.join(path,'hit_matrix.csv'),
                                  index_col=0)
    self.dd_matrix = pd.read_csv(os.path.join(path,'dd_matrix.csv'),
                                  index_col=0)
    self.split_matrix = pd.read_csv(os.path.join(path,'split_matrix.csv'),
                                  index_col=0)

    self.strategy_present = True

  def exportResults(self,path=""):
    assert self.analysis_present and  self.strategy_present, "Strategy or analysis isn't avaiable to export"
    a = self.analysisResults()
    b = self.strategyMatrices()
    with pd.ExcelWriter(os.path.join(path,'blackjack_analysis_results.xlsx')) as writer:
      for key,x in (a|b).items():
        if not isinstance(x,(pd.DataFrame,pd.Series)):
          x = pd.Series(data = x)
        x.to_excel(writer, sheet_name=key)

  def strategyMatrices(self):
    b ={
      'hit_matrix':self.hit_matrix,
      'dd_matrix':self.dd_matrix,
      'split_matrix':self.split_matrix
    }
    return b

  def exportEV(self,path=""):
    pd.Series(data = [self.EV]).to_csv(os.path.join(path,'EV'+'.csv'))

  def analysisResults(self):
    a = {
          'card_probs':self.card_probs,
          'hit_transition_matrix':self.hit_transition_matrix,
          'dealer_end_tm':self.dealer_end_tm,
          'dealer_ps':self.dealer_ps,
          'dealer_ps2':self.dealer_ps2,
          'dealer_ps_nn':self.dealer_ps_nn,
          'self.dealer_cs_nn':self.dealer_cs_nn,
          'E_hold':self.E_hold,
          'E_hit':self.E_hit,
          'E_M':self.E_M,
          'E_dd':self.E_dd,
          'E_split':self.E_split,
          'E_nosplit':self.E_nosplit,
          'natural_prob':self.natural_prob,
          'hole_pair_probs':self.hole_pair_probs,
          'hole_hand_probs':self.hole_hand_probs,
          'EVD':self.EVD,
          'EV':self.EV,
          'EX2_hold':self.EX2_hold,
          'EX2_hit':self.EX2_hit,
          'EX2_M':self.EX2_M,
          'EX2_dd':self.EX2_dd,
          'EX2_split':self.EX2_split,
          'EX2_nosplit':self.EX2_nosplit,
          'EX2D':self.EX2D,
          'V':self.V
         }
    return a

  def compute_hit_transition_matrix(self):
    tm = pd.DataFrame(index=self.str_hands,columns=self.str_hands,dtype=float).fillna(0)
    #for every hand, compute the probability of the next possible hands
    for str_hand in self.str_hands:
      hand0 = self.string_to_hand(str_hand)
      sum0 = hand0[0]
      ace0 = hand0[1]
      for card,p in self.card_probs.items():
        # useable ace logic
        # if you have an ace and using that ace (adding 10) doesn't make you bust
        # (go over 21), then you have a useable ace
        if (card==1 or ace0==1) and (sum0+card+10<=21):
          ace1=1
        else:
          ace1=0
        sum1 = min(sum0+card,22)
        hand1 = (sum1,ace1)
        tm.loc[str_hand,self.hand_to_string(hand1)]+=p
    return tm

  def f_dealer_end_tm(self):
    tm = pd.DataFrame(index=self.str_hands,columns=self.str_hands,dtype=float).fillna(0)
    # for every hand, compute the probability of terminal hand given how dealers
    # must hit/stand
    # Note that we iterate from over the hands in a certain order to do dynamic
    # programming.
    # I.e recusion over,
    # P(XT = xT|X0=x0) = Sum over x1>x0 and x1 reachable from x0
    # of P(XT=xT|X1=x1)P(X1=x1|X0=x0)
    for str_hand in self.sorted_str_hands:
      hand0 = self.string_to_hand(str_hand)
      sum0 = hand0[0]
      ace0 = hand0[1]
      # Dealers must stand if sum (after adding useable ace) is above or equal to 17
      # Hence if you start above or equal to 17, then you just stand and end there.
      if sum0+ace0*10>=17:
        tm.loc[str_hand,str_hand]=1
        continue

      # Otherwise the dealer hits and can end up in several other new hands.
      # The probability of where you ultimately end up is the sum of
      # the probabilities of where the new hands end up,
      # multiplied by the probability of each new hand.
      hit_row = self.hit_transition_matrix.loc[str_hand,:]
      for str_hand1,p in zip(hit_row.index,hit_row):
        tm.loc[str_hand,:]+=p*tm.loc[str_hand1,:]

    return tm

  def f_dealer_ps(self):
    ps = pd.DataFrame(index=self.str_hands,columns=list(range(17,23)),dtype=float)
    for str_hand in self.str_hands:
      for end_sum in ps.columns:
        if end_sum!=22:
          # There are two ways to end with sum X.
          # Either you have sum X or or end with sum X-10 and a useable ace.
          str_state0 = self.hand_to_string((end_sum,0))
          str_state1 = self.hand_to_string((end_sum-10,1))
          ps.loc[str_hand,end_sum] = (self.dealer_end_tm.loc[str_hand,str_state0]+
                                    self.dealer_end_tm.loc[str_hand,str_state1])
        else:
          ps.loc[str_hand,end_sum] = self.dealer_end_tm.loc[str_hand,'22,0']

    # We're only interested in the probabilities from a dealer's starting hand
    # with a single card, which correspond to the following hands.
    ps = ps.loc[Hand.get_single_card_simple_hands_str(),:]
    return ps

  def f_dealer_ps2(self):
    # Adds a column of probability of Natural 21s from dealer starting cards
    natural21 = pd.Series(index=Hand.get_single_card_simple_hands_str(),dtype=float,name='Natural 21').fillna(0)
    natural21.loc['1,1']=self.card_probs[10]
    natural21.loc['10,0']=self.card_probs[1]
    ps2 = pd.concat([self.dealer_ps.loc[:,self.dealer_ps.columns[self.dealer_ps.columns<21]],
                     self.dealer_ps.loc[:,21]-natural21.values,
                     natural21,
                     self.dealer_ps.loc[:,self.dealer_ps.columns[self.dealer_ps.columns>21]]],axis=1)
    return ps2

  #nn stands for non_natural
  def f_dealer_ps_nn(self):
    # From definition of conditional probability
    # P(A|B)=P(A and B)/P(B). In this case B is "non-natural 21"
    # P(not getting a natural)=1-P(getting a natural)
    ps_nn = self.dealer_ps2.divide(1-self.dealer_ps2.loc[:,'Natural 21'],axis=0)
    ps_nn = ps_nn.drop('Natural 21',axis=1)
    return ps_nn

  #X2 means calculating E(X**2) instead of E(X). Just square all outcomes.
  def f_E_hold(self,X2=False):
    E1 = pd.DataFrame(index=self.str_hands,columns=Hand.get_single_card_simple_hands_str(),dtype=float)
    for str_hand in self.str_hands:
      hand0 = self.string_to_hand(str_hand)
      sum0 = hand0[0]
      ace0 = hand0[1]
      score = sum0+ace0*10

      #if you bust, then you lose right away, -1
      if score>21:
        if not X2:
          E1.loc[str_hand,:]=-1
        else:
          E1.loc[str_hand,:]=1
        continue

      p_dealer_bust = self.dealer_ps_nn.loc[:,22].values

      if score>=18:
        # If you score 18 or more then you might beat the dealer without the dealer busting
        # You score more with probability P(dealer terminal score < score)
        # = P(dealer terminal score <= score - 1)
        # which is just self.dealer_cs_nn.loc[:,score-1].values
        p_player_more = self.dealer_cs_nn.loc[:,score-1].values
      else:
        p_player_more = 0
      # if score>=17:
      #   p_draw=0*self.dealer_ps_nn.loc[:,score]

      if score<=16:
        # if you score less than 17, then a dealer beats you as long as they don't bust
        p_dealer_more = 1-p_dealer_bust
      else:
        # otherwise the dealer wins with P(dealer terminal score > score and dealer doesn't bust)
        # = 1-P(dealer terminal score <= score or dealer busts)
        # = 1-P(dealer terminal score <= score)-P(dealer busts)
        p_dealer_more = 1-p_dealer_bust-self.dealer_cs_nn.loc[:,score].values

      if not X2:
        #Otherwise you win (+1) if the dealer busts or you have more than the dealer.
        #if the dealer has more you lose (-1)
        E1.loc[str_hand,:]=(p_dealer_bust+p_player_more)-(p_dealer_more)
      else:
        E1.loc[str_hand,:]=(p_dealer_bust+p_player_more)+(p_dealer_more)
    return E1

  def f_E_hit(self, X2=False):
    E1 = pd.DataFrame(index=self.str_hands,columns=Hand.get_single_card_simple_hands_str(),dtype=float).fillna(0)
    # the expected value of hitting once and holding is just the expected value
    # of the hands you can reach hitting once multiplied by their probability.
    for str_hand in self.str_hands:
      hit_row = self.hit_transition_matrix.loc[str_hand,:]
      for str_hand1,p in zip(hit_row.index,hit_row):
        if not X2:
          E1.loc[str_hand,:]+=p*self.E_hold.loc[str_hand1,:].values
        else:
          E1.loc[str_hand,:]+=p*self.EX2_hold.loc[str_hand1,:].values
    return E1

  def f_E_M(self,X2=False):
    # for every hand, compute the expected value given how players
    # hit/stand according to the calculated optimal hit/stand  strategy.
    # Note that we iterate from over the hands in a certain order to do dynamic
    # programming.
    # I.e recusion over,
    # E(XT = xT|X0=x0) = Sum over x1>x0 and x1 reachable from x0
    # of E(XT=xT|X1=x1)P(X1=x1|X0=x0)
    E1 = pd.DataFrame(index=self.str_hands,columns=Hand.get_single_card_simple_hands_str(),dtype=float).fillna(0)
    for str_hand in self.sorted_str_hands:
      if str_hand == '22,0':
        if not X2:
          E1.loc[str_hand,:]=-1
        else:
          E1.loc[str_hand,:]=1
        continue

      hit_trow = self.hit_transition_matrix.loc[str_hand,:]
      to_hit_row = self.hit_matrix.loc[str_hand,:]
      if not X2:
        #if you don't hit then your EV is the EV of holding
        E1.loc[str_hand,E1.columns[~to_hit_row]]=self.E_hold.loc[str_hand,self.E_hold.columns[~to_hit_row]].values
      else:
        E1.loc[str_hand,E1.columns[~to_hit_row]]=self.EX2_hold.loc[str_hand,self.EX2_hold.columns[~to_hit_row]].values
      # otherwise you hit, and your EV is the sum of the EV of the new hands multiplied by
      # their probability
      for str_hand1,p in zip(hit_trow.index,hit_trow):
        E1.loc[str_hand,E1.columns[to_hit_row]]+=p*E1.loc[str_hand1,E1.columns[to_hit_row]].values
    return E1

  def f_E_split(self,X2=False):
    E1 = pd.DataFrame(index=Hand.get_pair_simple_hands_str(),columns=Hand.get_single_card_simple_hands_str(),dtype=float).fillna(0)
    for str_hand in E1.index:
      hand = self.string_to_hand(str_hand)
      split_hand = (hand[0]//2,hand[1])

      hit_trow = self.hit_transition_matrix.loc[self.hand_to_string(split_hand),:]
      for str_hand1,p in zip(hit_trow.index,hit_trow):

        if str_hand=='2,1':
          # when splitting aces you can only hit once and hold
          if not X2:
            E1.loc[str_hand,:]+=2*p*self.E_hold.loc[str_hand1,:].values
          else:
            # Not just multiplied by 4 because it's not E((2X)**2) but E((X+Y)**2)
            # Where X and Y are iid. E((X+Y)**2)=E(X**2+2XY+Y**2)
            # = 2E(X**2)+4E(X)
            E1.loc[str_hand,:]+=(2*p*self.EX2_hold.loc[str_hand1,:].values
                                 +4*p*self.E_hold.loc[str_hand1,:].values)
          continue

        # otherwise you'll double down or follow hit/stand strategy depending on
        # dealer hand showing.
        dds = self.dd_matrix.loc[str_hand1,:]
        if not X2:
          E1.loc[str_hand,E1.columns[dds]]+=2*p*self.E_dd.loc[str_hand1,E1.columns[dds]].values
          E1.loc[str_hand,E1.columns[~dds]]+=2*p*self.E_M.loc[str_hand1,E1.columns[~dds]].values
        else:
          # Not just multiplied by 4 because it's not E((2X)**2) but E((X+Y)**2)
          # Where X and Y are iid. E((X+Y)**2)=E(X**2+2XY+Y**2)
          # = 2E(X**2)+4E(X)
          E1.loc[str_hand,E1.columns[dds]]+=(2*p*self.EX2_dd.loc[str_hand1,E1.columns[dds]].values
                                             +4*p*self.E_dd.loc[str_hand1,E1.columns[dds]].values)
          E1.loc[str_hand,E1.columns[~dds]]+=(2*p*self.EX2_M.loc[str_hand1,E1.columns[~dds]].values
                                            +4*p*self.E_M.loc[str_hand1,E1.columns[~dds]].values)
    return E1

  def f_E_nosplit(self,X2=False):
    # if you don't split you'll double down or follow hit/stand strategy depending on
    # dealer hand showing.
    E1 = pd.DataFrame(index=Hand.get_pair_simple_hands_str(),columns=Hand.get_single_card_simple_hands_str(),dtype=float).fillna(0)
    for str_hand in E1.index:
      dds = self.dd_matrix.loc[str_hand,:]
      if not X2:
        E1.loc[str_hand,E1.columns[dds]]=self.E_dd.loc[str_hand,E1.columns[dds]].values
        E1.loc[str_hand,E1.columns[~dds]]=self.E_M.loc[str_hand,E1.columns[~dds]].values
      else:
        E1.loc[str_hand,E1.columns[dds]]=self.EX2_dd.loc[str_hand,E1.columns[dds]].values
        E1.loc[str_hand,E1.columns[~dds]]=self.EX2_M.loc[str_hand,E1.columns[~dds]].values

    return E1

  @staticmethod
  def get_sorted_str_hands(hands,str_hands):
    sorted_hands = list(zip(hands,str_hands))
    sorted_hands.sort(reverse=True)
    sorted_str_hands = [y for _,y in sorted_hands]
    return sorted_str_hands

  @staticmethod
  def generate_hands():
    states = []
    #states (sum, usuable ace)
    for i in range(11):
      states.append((i+1,1))
    for i in range(23):
      states.append((i,0))
    return states

  @staticmethod
  def hand_to_string(hand):
    return ','.join(map(str,hand))

  @staticmethod
  def string_to_hand(str_hand):
    return tuple(map(int,str_hand.split(',')))

  def f_EVD(self):
    EV_natural = 1.5*self.natural_prob

    EV_pair_split = (self.E_split*self.split_matrix).multiply(self.hole_pair_probs,axis='index')
    EV_pair_nsplit = (self.E_nosplit*(~self.split_matrix)).multiply(self.hole_pair_probs,axis='index')

    EV_non_pair_dd = (self.E_dd*self.dd_matrix).multiply(self.hole_hand_probs,axis='index')
    EV_non_pair_ndd = (self.E_M*(~self.dd_matrix)).multiply(self.hole_hand_probs,axis='index')


    EV_dealer_nn = (EV_pair_split.sum(axis='index')+
                    EV_pair_nsplit.sum(axis='index')+
                    EV_non_pair_dd.sum(axis='index')+
                    EV_non_pair_ndd.sum(axis='index')+
                    EV_natural)

    EV_dealer_n = -1*(1-self.natural_prob)

    EVD=(self.dealer_ps2.loc[:,'Natural 21']*EV_dealer_n+
     (1-self.dealer_ps2.loc[:,'Natural 21'])*EV_dealer_nn)

    return EVD

  def f_EX2D(self):
    EX2_natural = (1.5**2)*self.natural_prob

    EX2_pair_split = (self.EX2_split*self.split_matrix).multiply(self.hole_pair_probs,axis='index')
    EX2_pair_nsplit = (self.EX2_nosplit*(~self.split_matrix)).multiply(self.hole_pair_probs,axis='index')

    EX2_non_pair_dd = (self.EX2_dd*self.dd_matrix).multiply(self.hole_hand_probs,axis='index')
    EX2_non_pair_ndd = (self.EX2_M*(~self.dd_matrix)).multiply(self.hole_hand_probs,axis='index')



    EX2_dealer_nn = (EX2_pair_split.sum(axis='index')+
                    EX2_pair_nsplit.sum(axis='index')+
                    EX2_non_pair_dd.sum(axis='index')+
                    EX2_non_pair_ndd.sum(axis='index')+
                    EX2_natural)

    EX2_dealer_n = 1*(1-self.natural_prob)

    VD=(self.dealer_ps2.loc[:,'Natural 21']*EX2_dealer_n+
    (1-self.dealer_ps2.loc[:,'Natural 21'])*EX2_dealer_nn)

    return VD
  
if __name__ == '__main__':
    bl1 = BlackjackAnalysis()
    print("Computing analysis of Blackjack.")
    bl1.compute()
    print("Saving analysis of Blackjack.")
    bl1.exportStrategy()
    bl1.exportEV()
    bl1.exportResults()

