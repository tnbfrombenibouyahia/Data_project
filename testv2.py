SP500 = 200
CAC = 199

def biggestvalue(SP500, CAC):
  if SP500 < CAC:
    return CAC
  else: 
    return SP500

resultat = biggestvalue(SP500, CAC)
print(f" la plus grosse valeur est : {resultat}")