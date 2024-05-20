from BlackjackAnalysis import BlackjackAnalysis
import os
import pandas as pd


def compute_EORs():
  EORs = pd.Series(dtype=float)
  EORs.index.name = 'card_value'
  EV = pd.read_csv('EV.csv',index_col=0).values[0][0]
  for i in range(10):
    print(i+1)
    card_probs = {k:v for k,v in zip([1+x for x in range(10)],[4/51]*9+[16/51])}
    card_probs[i+1]-=1/51
    bl = BlackjackAnalysis(card_probs)
    bl.importStrategy()
    bl.compute(computeStrategy=False)
    EORs[i+1]=bl.EV-EV
  print(EORs)
  return EORs

def export_EORs():
  EORs = compute_EORs()
  EORs.to_csv('effect_of_removals.csv')





if __name__=='__main__':
  print("Computing effect of removals.")
  if (os.path.exists('EV.csv') and 
    os.path.exists('hit_matrix.csv') and
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

  export_EORs()






