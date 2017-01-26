# Trade and Cultivation feature
# From BoggyB

### Imports
from CvPythonExtensions import *
import CvEventInterface
import CvUtil
import random

### Defines
gc = CyGlobalContext()

### Globals
lUntradeable = [] # List of untradeable bonuses
lCorn = [] # Lists of cultivatable bonuses
lLivestock = []
lPlantation = []
lStrategic = []
lCultivatable = [] # = lCorn+lLivestock
lLuxury = [] # List of bonuses which may create trade routes
lRarity = [] # List of bonuses which may create trade routes
lTradeUnits = [] # List of merchant units
lCultivationUnits = [] # List of cultivation units
bInitialised = False # Whether global variables are already initialised
lCitiesSpecialBonus = [] # Cities with Special Trade Bonus

# Reminder: How to use ScriptData: CvUtil.getScriptData(pUnit, ["b"], -1), CvUtil.addScriptData(pUnit, "b", eBonus) (add uses string, get list of strings)
# getScriptData returns string => cast might be necessary

# Used keys for UnitScriptData:
# "x"/"y": coordinates of plots where bonus was picked up (merchants)
# "b": index of bonus stored in merchant (only one at a time)
# "b": indices of bonuses stored in cultivation unit, e.g. "23,21,4"
# "originCiv": original owner of the bonus stored in merchant (owner of the city where it was bought)

# For automated trade routes:
# "automX1"/"automX2"/"automY1"/"automY2": coordinates of cities in trade route
# "automBonus1": bonus bought in city 1/sold in city 2
# "automBonus2": bonus bought in city 2/sold in city 1
# "automActive": if False, automated route is currently inactive
# "automLastTurnChecked": latest turn when "doAutomateMerchant" was called for this unit. Sometimes it is called multiple times per turn, this prevents unnecessary calculations

# Used keys for CityScriptData:
# "b": free bonuses acquired via turns and how long they are available, e.g. "43,4;23,8;12,10" (bonus index + ',' + num turns + ';' + bonus index + ...)

def init():
    global bInitialised
    global lUntradeable
    global lCorn
    global lLivestock
    global lCultivatable
    global lPlantation
    global lStrategic
    global lLuxury
    global lRarity
    global lTradeUnits
    global lCultivationUnits
    global lCitiesSpecialBonus

    if not bInitialised:
        # BonusClass indices
        eGrain = gc.getInfoTypeForString("BONUSCLASS_GRAIN")
        # WHEAT, GERSTE, HAFER, ROGGEN, HIRSE, RICE
        eLivestock = gc.getInfoTypeForString("BONUSCLASS_LIVESTOCK")
        # COW, PIG, SHEEP
        ePlantation = gc.getInfoTypeForString("BONUSCLASS_PLANTATION")
        # GRAPES, OLIVES, DATTELN

        eGeneral = gc.getInfoTypeForString("BONUSCLASS_GENERAL")
        # COAL (Blei), ZINN, ZINK, ZEDERNHOLZ, COPPER, BRONZE, IRON, MESSING, HORSE, CAMEL, HUNDE, PAPYRUS_PAPER
        eLuxury = gc.getInfoTypeForString("BONUSCLASS_LUXURY")
        # GOLD, SILVER, PEARL, LION, SALT, DYE, FUR, INCENSE, MYRRHE, IVORY, SPICES, WINE, MUSIC
        eRarity = gc.getInfoTypeForString("BONUSCLASS_RARITY")
        # MAGNETIT, OBSIDIAN, OREICHALKOS, GLAS, BERNSTEIN, ELEKTRON, WALRUS, GEMS, SILK, SILPHIUM, TERRACOTTA
        eWonder = gc.getInfoTypeForString("BONUSCLASS_WONDER")
        # MARBLE, STONE
        # eMisc =  gc.getInfoTypeForString("BONUSCLASS_MISC")
        # BANANA, CRAB, DEER, FISH, CLAM, PAPYRUS
        # eMerc =  gc.getInfoTypeForString("BONUSCLASS_MERCENARY")
        # BALEAREN, TEUTONEN, BAKTRIEN, KRETA, KILIKIEN, MARS, THRAKIEN

        iNumBonuses = gc.getNumBonusInfos()
        for eBonus in xrange(iNumBonuses):
          pBonusInfo = gc.getBonusInfo(eBonus)
          iClass = pBonusInfo.getBonusClassType()
          if iClass == eGrain: lCorn.append(eBonus)
          elif iClass == eLivestock: lLivestock.append(eBonus)
          elif iClass == ePlantation: lPlantation.append(eBonus)
          elif iClass == eLuxury: lLuxury.append(eBonus)
          elif iClass == eRarity: lRarity.append(eBonus)
          # eg BONUSCLASS_MISC
          elif iClass != eWonder and iClass != eGeneral: lUntradeable.append(eBonus)
          # BonusClasse wonder and general are not stored separately (bc. unnecessary)

        lStrategic.append(gc.getInfoTypeForString("BONUS_HORSE"))

        lCultivatable = lCorn + lLivestock + lPlantation + lStrategic

        lTradeUnits = [
            gc.getInfoTypeForString("UNIT_TRADE_MERCHANT"),
            gc.getInfoTypeForString("UNIT_CARAVAN"),
            gc.getInfoTypeForString("UNIT_TRADE_MERCHANTMAN"),
            gc.getInfoTypeForString("UNIT_GAULOS"),
            gc.getInfoTypeForString("UNIT_CARVEL_TRADE")
        ]
        lCultivationUnits = [
            gc.getInfoTypeForString("UNIT_SUPPLY_FOOD")
        ]

        # Cities mit Special Trade Bonus herausfinden
        iMaxCitiesSpecialBonus = 3
        iRange = gc.getMAX_PLAYERS()
        for i in range(iRange):
          loopPlayer = gc.getPlayer(i)
          if loopPlayer.isAlive():
            (pLoopCity, iter) = loopPlayer.firstCity(false)
            while pLoopCity:
              if int(CvUtil.getScriptData(pLoopCity, ["tsb"], -1)) != -1:
                lCitiesSpecialBonus.append(pLoopCity)
              (pLoopCity,iter) = loopPlayer.nextCity(iter, false)
            if len(lCitiesSpecialBonus) == iMaxCitiesSpecialBonus: break

          if len(lCitiesSpecialBonus) == iMaxCitiesSpecialBonus: break

        bInitialised = True

# --- Bonus cultivation ---

def myRandom (num):
    if num <= 1: return 0
    else: return random.randint(0, num-1)

# Returns chance to cultivate eBonus on pPlot. Currently: either 0 (impossible) or 80 (possible)
def getBonusCultivationChance(iPlayer, pPlot, eBonus):
    global lUntradeable
    global lCorn
    global lLivestock
    global lPlantation
    global lCultivatable

    # Variety of invalid situations
    if eBonus not in lCultivatable: return 0
    if pPlot == None or pPlot.isNone(): return 0
    if pPlot.getOwner() != iPlayer: return 0
    if pPlot.isCity(): return 0
    if pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_DARK_ICE") or pPlot.isPeak() or pPlot.isWater(): return 0

    # Non-cultivatable bonuses cannot be replaced. If there is an invisible (tech reveal) bonus on pPlot, player receives NO information.
    # In particular, the normal cultivation chance will be displayed, but doCultivateBonus() prevents invisible bonus from removal.
    ePlotBonus = pPlot.getBonusType(pPlot.getTeam())
    if ePlotBonus != -1 and ePlotBonus not in lCultivatable: return 0

    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, str(eBonus), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Fertility conditions
    if not pPlot.canHaveBonus(eBonus, True): return 0
    if eBonus in lCorn and not pPlot.isFreshWater(): return 0
    elif eBonus in lPlantation:
      if eBonus == gc.getInfoTypeForString("BONUS_DATTELN") and not pPlot.isFreshWater(): return 0
      elif eBonus == gc.getInfoTypeForString("BONUS_OLIVES") and not pPlot.isCoastalLand(): return 0
      elif eBonus == gc.getInfoTypeForString("BONUS_GRAPES") and not pPlot.isFreshWater(): return 0

    # Regel: Resourcen pro Stadt und dessen Status (Flunky)
    lCities = getCitiesInRange(pPlot)
    if len(lCities) == 0: return 0

    bFood = eBonus in (lCorn + lLivestock)
    for pCity in lCities:
      if not isCityCultivationPossible(pCity, bFood): return 0

    return 80 # everything ok => chance of 80%

def getCitiesInRange(pPlot):
  iX = pPlot.getX()
  iY = pPlot.getY()
  lCities = []
  for x in xrange(-2, 2):
    for y in xrange(-2, 2):
      # Ecken weglassen
      if (x == -2 or x == 2) and (y == -2 or y == 2): continue
      pLoopPlot = plotXY(iX, iY, x, y)
      if pLoopPlot != None and not pLoopPlot.isNone():
        #if pLoopPlot.getOwner() == iPlayer and pLoopPlot.isCity(): lCities.append(pLoopPlot.getPlotCity())
        if pLoopPlot.isCity(): lCities.append(pLoopPlot.getPlotCity())
  return lCities

def isCityCultivationPossible(pCity, bFood):
  iBonusAnzahl = 0
  iFoodMax = 2

  iMax = 1
  if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_STADT")): iMax += 1
  if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_PROVINZ")): iMax += 1
  #if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_METROPOLE")): iMax += 1
  if bFood:
    iMax = min(iMax, iFoodMax)

  for iI in range(gc.getNUM_CITY_PLOTS()):
    pLoopPlot = pCity.getCityIndexPlot(iI)
    if pLoopPlot != None and not pLoopPlot.isNone():
      # Bonusgut checken
      #if pLoopPlot.getOwner() == iPlayer and pLoopPlot.getBonusType(-1) in lCultivatable: iBonusAnzahl += 1
      if pLoopPlot.getBonusType(-1) in lCultivatable: iBonusAnzahl += 1
      if iBonusAnzahl >= iMax: return False
  return True

# Cultivates eBonus on current plot (80% chance). Unit does not need to stand on pPlot (cultivation from city)
def doCultivateBonus(pPlot, pUnit, eBonus):
  iPlayer = pUnit.getOwner()
  pPlayer = gc.getPlayer(iPlayer)
  iChance = getBonusCultivationChance(iPlayer, pPlot, eBonus)

  # If there is an invisible (tech reveal), uncultivatable bonus on pPlot, doCultivateBonus can be called, but the chance is nullified.
  # Player receives NO unique message, just the normal one ("cultivation failed").
  ePlotBonus = pPlot.getBonusType(-1)
  if ePlotBonus != -1 and ePlotBonus not in lCultivatable: iChance = 0

  #CyInterface().addMessage(iPlayer, True, 10, str(eBonus), None, 2, None, ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
  if iChance > myRandom(100):
    pPlot.setBonusType(eBonus)
    if pPlayer.isHuman():
      CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_BONUSVERBREITUNG_DONE",(gc.getBonusInfo(eBonus).getDescription(),)), None, 2, gc.getBonusInfo(eBonus).getButton(), ColorTypes(8), pPlot.getX(), pPlot.getY(), True, True)
    pUnit.kill(1, iPlayer)
  else:
    CvUtil.removeScriptData(pUnit, "b")
    if pPlayer.isHuman():
      if pPlot.isCity(): pCity = pPlot.getPlotCity()
      else: pCity = pPlot.getWorkingCity()
      CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_INFO_BONUSVERBREITUNG_NEG",(gc.getBonusInfo(eBonus).getDescription(),pCity.getName())), None, 2, gc.getBonusInfo(eBonus).getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
  return True

# Cultivates eBonus on random plot within radius of iRange around pUnit (chance of success: 80%).
# Never replaces existing bonus.
def getCityCultivationPlot(pCity, eBonus):
  iPlayer = pCity.getOwner()
  lPlotList = []
  for iI in range(gc.getNUM_CITY_PLOTS()):
    pLoopPlot = pCity.getCityIndexPlot(iI)
    if pLoopPlot != None and not pLoopPlot.isNone():
      ePlotBonus = pLoopPlot.getBonusType(-1)
      if ePlotBonus == -1 and getBonusCultivationChance(iPlayer, pLoopPlot, eBonus) > 0:
        lPlotList.append(pLoopPlot)
  iRand = myRandom(len(lPlotList))
  return lPlotList[iRand]

# Returns list of bonuses which can be cultivated by this particular cultivation unit
# Checks fertility conditions AND unit store
# if iIsCity == 1, 5x5 square is checked. Otherwise: Only current plot.
def getCultivatableBonusesForUnit(pUnit, iIsCity):
  global lCultivationUnits
  if not pUnit.getUnitType() in lCultivationUnits:
    CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("getCultivatableBonusesForUnit mit falscher Unit aufgerufen")), None, 2, None, ColorTypes(10), 0, 0, False, False)
    return -1

  eBonus = int(CvUtil.getScriptData(pUnit, ["b"], -1))
  if eBonus == -1:
    return eBonus
  if iIsCity:
    # Cultivation from city (comfort function), no replacement of existing bonuses
    if bonusIsCultivatableFromCity(pUnit.getOwner(), pUnit.plot().getPlotCity(), eBonus):
      return eBonus
  else:
    # Cultivation on current plot, bonus can be replaced (player knows what he's doing)
    if bonusIsCultivatable(pUnit.getOwner(), pUnit.plot(), eBonus):
      return eBonus

# Returns true if eBonus can be (principally) cultivated by iPlayer in a radius of iRange around pPlot
# Independent from cultivation unit, only checks fertility conditions
# if bRemove == false, only plots without bonus are considered
def bonusIsCultivatable(iPlayer, pPlot, eBonus):
  return getBonusCultivationChance(iPlayer, pPlot, eBonus) > 0

# Returns true if eBonus can be (principally) cultivated by iPlayer from pCity
# Independent from cultivation unit, only checks fertility conditions
def bonusIsCultivatableFromCity(iPlayer, pCity, eBonus):
  for iI in range(gc.getNUM_CITY_PLOTS()):
    pLoopPlot = pCity.getCityIndexPlot(iI)
    if pLoopPlot != None and not pLoopPlot.isNone():
      ePlotBonus = pLoopPlot.getBonusType(-1)
      if ePlotBonus == -1 and getBonusCultivationChance(iPlayer, pLoopPlot, eBonus) > 0:
        if bonusIsCultivatable(iPlayer, pLoopPlot, eBonus):
          return True
  return False

# Returns list of bonuses which can (principally) be cultivated by iPlayer in a radius of iRange around pPlot
# Independent from cultivation unit, only checks fertility conditions
# if bRemove == false, only plots without bonus are considered
def getCultivatableBonusesFromCity(pCity, lCityBonuses):
  lBonuses = [] # List which will be returned
  for eBonus in lCityBonuses:
    if bonusIsCultivatableFromCity(pCity.getOwner(), pCity, eBonus):
      lBonuses.append(eBonus)
  return lBonuses

# Returns list of the cultivatable bonuses which pCity has access to / Liste kultivierbarer Ressis im Handelsnetz von pCity
def getAvailableCultivatableBonuses(pCity):
  global lCultivatable
  lBonuses = []
  for eBonus in lCultivatable:
      if pCity.hasBonus(eBonus): lBonuses.append(eBonus)
  return lBonuses

# Lets pUnit cultivate bonus at nearest city
def doCultivation_AI(pUnit):
  global lCorn
  global lLivestock
  global lCultivationUnits

  if not pUnit.getUnitType() in lCultivationUnits: return False

  lFood = lCorn+lLivestock

  pUnitPlot = pUnit.plot()
  iPlayer = pUnit.getOwner()
  pPlayer = gc.getPlayer(iPlayer)

  lLocalCityBonuses = []
  if pUnitPlot.isCity() and iPlayer == pUnitPlot.getOwner():
    pLocalCity = pUnitPlot.getPlotCity()
    lLocalCityBonuses = getAvailableCultivatableBonuses(pLocalCity)

  lCities = []
  # list of player's cities with distance (2-tuples (distance, city))
  # The nearest city which can still cultivate a bonus is chosen.
  (pLoopCity, iter) = pPlayer.firstCity(False)
  while pLoopCity:
    iValue = 0
    pCityPlot = pLoopCity.plot()
    iDistance = CyMap().calculatePathDistance(pUnitPlot, pCityPlot)
    # exclude unreachable cities
    if iDistance != -1:
      if isCityCultivationPossible(pLoopCity, False):
        if iDistance == 0: iValue = 2
        else: iValue = 1/iDistance
        if isCityCultivationPossible(pLoopCity, True): iValue *= 2
    if iValue != 0: lCities.append((iValue, pLoopCity))
    (pLoopCity, iter) = pPlayer.nextCity(iter, False)


  lSortedCities = sorted(lCities, key = lambda value: lCities[0], reverse=True)
  bDiscard = False
  for tTuple in lCities:
    pLoopCity = tTuple[1]
    lCityBonuses = getAvailableCultivatableBonuses(pLoopCity) # bonuses that city has access to
    lBonuses = getCultivatableBonusesFromCity(pLoopCity, lCityBonuses+lLocalCityBonuses) # bonuses for which fertility conditions are met
    # has this city capacity to cultivate?
    # prefer food if possible
    bFood = False
    if isCityCultivationPossible(pLoopCity, True):
      bFood = True
      lBonuses = getIntersection(lBonuses, lFood)
    eUnitBonus = CvUtil.getScriptData(pUnit, ["b"], -1)

    # wir haben was geladen
    if eUnitBonus != -1:
      # kann man das hier brauchen?
      if eUnitBonus in lBonuses:
        if pLocalCity and pLoopCity.getID() == pLocalCity.getID():
          CyMessageControl().sendModNetMessage(738, iPlayer, iUnit, iIsCity)
          return True
          #~ pPlot = PAE_Trade.getCityCultivationPlot(pLocalCity, eBonus)
          #~ if doCultivateBonus(pPlot, pUnit, eBonus):
            #~ return True
        else:
          # move to destination
          pUnit.getGroup().pushMoveToMission(pLoopCity.getX(), pLoopCity.getY())
          return True
      # vielleicht irgendwo anders, potentiell wegwerfen und neu kaufen
      else:
        bDiscard = True
        continue

    # kauf was, das es hier gibt und dort gebraucht wird und los geht's
    for eBonus in lBonuses:
      iLocalPrice = -1
      iPrice = calculateBonusBuyingPrice4Cultivation(iPlayer,pLoopCity.plot(),eBonus)
      if eBonus in lLocalCityBonuses:
        iLocalPrice = calculateBonusBuyingPrice4Cultivation(iPlayer,pLocalCity.plot(),eBonus)
      if iLocalPrice != -1 and iLocalPrice <= iPrice:
        #buy here. wait if not enough money
        doCollectBonus4Cultivation(pUnit,eBonus)
        pUnit.finishMoves()
        return True
      else:
        # move to destination
        pUnit.getGroup().pushMoveToMission(pLoopCity.getX(), pLoopCity.getY())
        return True

  if bDiscard:
    # TODO: cashback?
    CvUtil.removeScriptData(pUnit, "b")
  # no cities reachable
  if pPlayer.getNumCities() == 1:
    # TODO doGiveFood
    return False
  else:
    # TODO get a ship
    return False

### Buying cultivation resources

# Collect bonus on current plot ('stored' in cultivation unit)
def doCollectBonus(pUnit):
  #~ global lCultivationUnits
  #~ if pUnit == None or pUnit.isNone(): return False
  #~ if not pUnit.getUnitType() in lCultivationUnits: return False

  iTeam = pUnit.getTeam()
  pPlot = pUnit.plot()
  #~ if pPlot == None or pPlot.isNone(): return False
  eBonus = pPlot.getBonusType(iTeam) # If there is an invisible bonus on pPlot, it will not be removed

  if eBonus == -1:
    return False

  eUnitBonus = CvUtil.getScriptData(pUnit, ["b"], -1)
  if eUnitBonus != -1:
    # TODO: Popup Ressource geladen, ueberschreiben?
    CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Die Einheit hatte bereits eine Ressource geladen. Die ist jetzt futsch.")), None, 2, None, ColorTypes(10), 0, 0, False, False)

  CvUtil.addScriptData(pUnit, "b", eBonus)
  pPlot.setBonusType(-1) # remove bonus
  pUnit.finishMoves()
  return True


# Buy bonus on current plot ('stored' in cultivation unit)
def doCollectBonus4Cultivation(pUnit,eBonus):
  #~ global lCultivationUnits
  #~ if pUnit == None or pUnit.isNone(): return False
  #~ if not pUnit.getUnitType() in lCultivationUnits: return False

  iPlayer = pUnit.getOwner()

  if eBonus != -1:
    eUnitBonus = CvUtil.getScriptData(pUnit, ["b"], -1)

    if eBonus == eUnitBonus:
      CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Das haben wir bereits geladen.")), None, 2, None, ColorTypes(10), 0, 0, False, False)
      return False

    if -1 != eUnitBonus:
      # TODO: Popup Ressource geladen, ueberschreiben?
      CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Die Einheit hatte bereits eine Ressource geladen. Die ist jetzt futsch.")), None, 2, None, ColorTypes(10), 0, 0, False, False)

    iPrice = calculateBonusBuyingPrice4Cultivation(iPlayer,pUnit.plot(),eBonus)
    pPlayer = gc.getPlayer(iPlayer)

    if pPlayer.getGold() < iPrice:
      CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_COLLECT_NO_GOODS",("",)), None, 2, "Art/Interface/PlotPicker/Warning.dds", ColorTypes(7), pUnit.getX(), pUnit.getY(), True, True)
      return False

    pPlayer.changeGold(-iPrice)
    CyInterface().addMessage(iPlayer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_COLLECT_GOODS",(gc.getBonusInfo(eBonus).getDescription(),)), "AS2D_COINS", 2, gc.getBonusInfo(eBonus).getButton(), ColorTypes(13), pUnit.getX(), pUnit.getY(), True, True)
    CvUtil.addScriptData(pUnit, "b", eBonus)
    pUnit.finishMoves()
    return True

# Creates popup with all possible cultivation bonuses of the plot or city
def doPopupChooseBonus4Collection(pUnit):
    global lCultivatable
    pPlot = pUnit.plot()
    iPlayer = pUnit.getOwner()

    lGoods = getCollectableGoods4Cultivation(pUnit)

    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
    popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_TRADE_CHOOSE_BONUS",("", )) )
    popupInfo.setOnClickedPythonCallback("popupTradeChooseBonus4Cultivation")
    popupInfo.setData1(iPlayer)
    popupInfo.setData2(pUnit.getID())

    for eBonus in lGoods:
      sBonusDesc = gc.getBonusInfo(eBonus).getDescription()
      iPrice = calculateBonusBuyingPrice4Cultivation(iPlayer,pPlot,eBonus)
      sText = CyTranslator().getText("TXT_KEY_BUY_BONUS", (sBonusDesc, iPrice))
      sBonusButton = gc.getBonusInfo(eBonus).getButton()
      popupInfo.addPythonButton(sText, sBonusButton)

    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
    popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
    popupInfo.addPopup(iPlayer)

# List of selectable cultivation goods
def getCollectableGoods4Cultivation(pUnit):
    global lCultivatable
    pPlot = pUnit.plot()
    lGoods = []

    if pPlot.isCity():
      pCity = pPlot.getPlotCity()
      for eBonus in lCultivatable:
        if pCity.hasBonus(eBonus): lGoods.append(eBonus)
    else:
      ePlotBonus = pPlot.getBonusType(pPlot.getTeam())
      if ePlotBonus != -1: lGoods.append(ePlotBonus)

    return lGoods

# Price of cultivation goods
# regional (on plot): *1
# national: *2
# international: *3
def calculateBonusBuyingPrice4Cultivation(iPlayer,pPlot,eBonus):

  iPrice = getBonusValue(eBonus)

  # Bonus on plot: regional price
  if pPlot.getBonusType(pPlot.getTeam()) == eBonus: return iPrice

  # Bonus in city radius: regional price
  pCity = pPlot.getPlotCity()
  for iI in range(gc.getNUM_CITY_PLOTS()):
    pLoopPlot = pCity.getCityIndexPlot(iI)
    if pLoopPlot != None and not pLoopPlot.isNone():
       if pLoopPlot.getBonusType(pLoopPlot.getTeam()) == eBonus: return iPrice

  # Bonus in realm: national price
  iRange = CyMap().numPlots()
  for iI in range(iRange):
    pLoopPlot = CyMap().plotByIndex(iI)
    if pLoopPlot.getOwner() == iPlayer:
      if pLoopPlot.getBonusType(pLoopPlot.getTeam()) == eBonus: return iPrice * 2

    # Bonus international
  return iPrice * 3
# --- End of bonus cultivation ----


# --- Trade in cities ---

# Unit stores bonus, owner pays, if UnitOwner != CityOwner: city owner gets money
def doBuyBonus(pUnit, eBonus, iCityOwner):
  global lTradeUnits
  if not pUnit.getUnitType() in lTradeUnits: return

  iBuyer = pUnit.getOwner()
  pBuyer = gc.getPlayer(iBuyer)
  pSeller = gc.getPlayer(iCityOwner)
  iPrice = calculateBonusBuyingPrice(eBonus, pUnit.getOwner(), iCityOwner)
  pBuyer.changeGold(-iPrice)
  if iBuyer != iCityOwner:
      pSeller.changeGold(iPrice)
  CvUtil.addScriptData(pUnit, "b", eBonus)
  CvUtil.addScriptData(pUnit, "originCiv", iCityOwner)
  CvUtil.addScriptData(pUnit, "x", pUnit.getX())
  CvUtil.addScriptData(pUnit, "y", pUnit.getY())
  if pSeller.isHuman() and iBuyer != iCityOwner:
      sBonusName = gc.getBonusInfo(eBonus).getDescription()
      CyInterface().addMessage(iCityOwner, True, 10, CyTranslator().getText("TXT_KEY_BONUS_BOUGHT",(sBonusName, pBuyer.getName(), iPrice)), "AS2D_COINS", 2, None, ColorTypes(8), pUnit.getX(), pUnit.getY(), False, False)
  if pBuyer.isHuman():
      CyInterface().addMessage(iBuyer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_COLLECT_GOODS",(gc.getBonusInfo(eBonus).getDescription(),)), "AS2D_COINS", 2, None, ColorTypes(13), 0, 0, False, False)

  pUnit.finishMoves()
  CvEventInterface.getEventManager().doGoToNextUnit(pBuyer, pUnit)

# Unit's store is emptied, unit owner gets money, city gets bonus, research push
def doSellBonus(pUnit, pCity):
  global lTradeUnits
  if not pUnit.getUnitType() in lTradeUnits: return

  eBonus = int(CvUtil.getScriptData(pUnit, ["b"], -1))
  if eBonus == -1: return
  iPrice = calculateBonusSellingPrice(pUnit, pCity)
  iBuyer = pCity.getOwner()
  pBuyer = gc.getPlayer(iBuyer)
  iSeller = pUnit.getOwner()
  pSeller = gc.getPlayer(iSeller)
  pSeller.changeGold(iPrice)
  iOriginCiv = int(CvUtil.getScriptData(pUnit, ["originCiv"], -1)) # where the goods come from
  CvUtil.removeScriptData(pUnit, "b")
  if iOriginCiv != iBuyer:

      # Buyer has bonus or not (fuer Handelsstrasse)
      if pBuyer.hasBonus(eBonus): iChance = 10
      else: iChance = 20

      doResearchPush(iBuyer, iPrice/10)
      doCityProvideBonus(pCity, eBonus, 3)

      # Trade route / Handelsstrasse
      if eBonus in lLuxury + lRarity:

        if not hasBonusIgnoreFreeBonuses(pCity, eBonus) and pUnit.getDomainType != gc.getInfoTypeForString("DOMAIN_SEA"):

          # Rarities doubles chance
          if eBonus in lRarity: iChance *= 2

          if myRandom(100) < iChance:
            iOriginX = CvUtil.getScriptData(pUnit, ["x"], -1)
            iOriginY = CvUtil.getScriptData(pUnit, ["y"], -1)
            pOriginPlot = CyMap().plot(iOriginX, iOriginY)
            if pOriginPlot != None and not pOriginPlot.isNone():
              if pOriginPlot.isCity():
                  iRouteType = gc.getInfoTypeForString("ROUTE_TRADE_ROAD")
                  pOriginCity = pOriginPlot.getPlotCity()
                  #CyInterface().addMessage(iSeller, True, 10, "Vor Traderoute", None, 2, None, ColorTypes(8), pUnit.getX(), pUnit.getY(), False, False)
                  pPlotTradeRoad = getPlotTradingRoad(pOriginPlot, CyMap().plot(pUnit.getX(), pUnit.getY()), 0)
                  #CyInterface().addMessage(iSeller, True, 10, "Nach Traderoute", None, 2, None, ColorTypes(8), pUnit.getX(), pUnit.getY(), False, False)
                  if pPlotTradeRoad != None:
                    pPlotTradeRoad.setRouteType(iRouteType)
                    if pBuyer.isHuman():
                        CyInterface().addMessage(iBuyer, True, 10, CyTranslator().getText("TXT_KEY_TRADE_ROUTE_BUILT",(pSeller.getName(),pSeller.getCivilizationShortDescriptionKey(),pCity.getName(),pOriginCity.getName())), "AS2D_WELOVEKING", 2, "Art/Terrain/Routes/handelsstrasse/button_handelsstrasse.dds", ColorTypes(10), pPlotTradeRoad.getX(), pPlotTradeRoad.getY(), True, True)
                    if pSeller.isHuman() and iBuyer != iSeller:
                        CyInterface().addMessage(iSeller, True, 10, CyTranslator().getText("TXT_KEY_TRADE_ROUTE_BUILT2",(pCity.getName(),pOriginCity.getName())), "AS2D_WELOVEKING", 2, "Art/Terrain/Routes/handelsstrasse/button_handelsstrasse.dds", ColorTypes(10), pPlotTradeRoad.getX(), pPlotTradeRoad.getY(), True, True)
                    if iBuyer != iSeller and iSeller == gc.getGame().getActivePlayer() or iBuyer == gc.getGame().getActivePlayer():
                       CyAudioGame().Play2DSound("AS2D_WELOVEKING")

                  # Sobald von einer Stadt 3 Handelsstrassen (bzw 2 bei einer Kuestenstadt) weggehen,
                  # wird es zum Handelszentrum (Building: 100% auf Trade Routes)
                  iBuilding = gc.getInfoTypeForString("BUILDING_HANDELSZENTRUM")
                  if not pOriginCity.isHasBuilding(iBuilding):
                    iAnz = 0
                    iMax = 3
                    if pOriginCity.isCoastal(4): iMax = 2
                    for x in range(-1, 1):
                      for y in range(-1, 1):
                        if x == 0 and y == 0: continue
                        pLoopPlot = gc.getMap().plot(iOriginX + x, iOriginY + y)
                        if pLoopPlot != None and not pLoopPlot.isNone():
                          if pLoopPlot.getRouteType() == iRouteType: iAnz += 1
                          if iAnz >= iMax: break
                      if iAnz >= iMax: break
                    if iAnz >= iMax:
                      pOriginCity.setNumRealBuilding(iBuilding, 1)
                      if pOriginCity.getOwner() == gc.getGame().getActivePlayer():
                        CyInterface().addMessage(pOriginCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_TRADE_ROUTE_HANDELSZENTRUM",(pOriginCity.getName(),)), "AS2D_WELOVEKING", 2, gc.getBuildingInfo(iBuilding).getButton(), ColorTypes(10), pOriginCity.getX(), pOriginCity.getY(), True, True)



  sBonusName = gc.getBonusInfo(eBonus).getDescription()
  if pBuyer.isHuman() and iBuyer != iSeller:
    CyInterface().addMessage(iBuyer, True, 10, CyTranslator().getText("TXT_KEY_BONUS_SOLD",(sBonusName, pSeller.getName())), None, 2, None, ColorTypes(8), pUnit.getX(), pUnit.getY(), False, False)
  else:
    CyInterface().addMessage(iSeller, True, 10, CyTranslator().getText("TXT_KEY_BONUS_SOLD2",(sBonusName, iPrice)), None, 2, None, ColorTypes(8), pUnit.getX(), pUnit.getY(), False, False)

  if iSeller == gc.getGame().getActivePlayer() or iBuyer == gc.getGame().getActivePlayer():
    CyAudioGame().Play2DSound("AS2D_COINS")

  # Special Order
  if iOriginCiv != iBuyer:
    if eBonus in lLuxury + lRarity:
      doCheckCitySpecialBonus(pUnit,pCity,eBonus)

  pUnit.finishMoves()

# Player gets research points for current project (called when foreign goods are sold to player's cities)
def doResearchPush(iPlayer1, iValue1):
    pPlayer1 = gc.getPlayer(iPlayer1)
#    pPlayer2 = gc.getPlayer(iPlayer2)
    pTeam1 = gc.getTeam(pPlayer1.getTeam())
#    pTeam2 = gc.getTeam(pPlayer2.getTeam())
    eTech1 = pPlayer1.getCurrentResearch()
#    eTech2 = pPlayer2.getCurrentResearch()
    if eTech1 != -1: pTeam1.changeResearchProgress(eTech1, iValue1, iPlayer1)
#    if eTech2 != -1: pTeam2.changeResearchProgress(eTech2, iValue2, iPlayer2)

# City can use bonus for x turns
def doCityProvideBonus(pCity, eBonus, iTurn):
  # ScriptData value is dict, e.g. {43:4; 23:8; 12:10}
  # Key is 'iBonus' and value is 'iTurns'

  bonusDict = CvUtil.getScriptData(pCity, ["b"], {})

  # compatibility
  if type(bonusDict) == str:
    # Konvertiere altes Format "iB,iTurn;..." in dict
    tmp = [paar.split(",") for paar in bonusDict.split(";")]
    bonusDict = {}
    bonusDict.update([ map(int, pair) for pair in tmp])

  # Addiere alten und neuen Rundenwert
  iCurrentTurn = gc.getGameTurn()
  bonusDict[eBonus] = iTurn + bonusDict.setdefault(eBonus, iCurrentTurn)
  CvUtil.addScriptData(pCity, "b", bonusDict)

  pCity.changeFreeBonus(eBonus, 1)

# Called each turn (onCityDoTurn, EventManager), makes sure free bonus disappears after x turns
def doCityCheckFreeBonuses(pCity):
  bonusDict = CvUtil.getScriptData(pCity, ["b"], {})

  # compatibility
  if type(bonusDict) == str:
    # Konvertiere altes Format "iB,iTurn;..." in dict
    tmp = [paar.split(",") for paar in bonusDict.split(";")]
    bonusDict = dict([ map(int, pair) for pair in tmp])
    CvUtil.addScriptData(pCity, "b", bonusDict)

  for eBonus in bonusDict:
    iTurn = bonusDict[eBonus]
    if iTurn <= gc.getGameTurn():
      pCity.changeFreeBonus(eBonus, -1) # Time over: remove bonus from city
      bonusDict.pop(eBonus, None)
      CvUtil.addScriptData(pCity, "b", bonusDict)


# Creates popup with all the affordable bonuses for UnitOwner (bonuses too expensive for UnitOwner are cut)
def doPopupChooseBonus(pUnit, pCity):
    if pCity == None or pCity.isNone() or pUnit == None or pUnit.isNone(): return False
    iBuyer = pUnit.getOwner()
    iSeller = pCity.getOwner()
    lGoods = getCitySaleableGoods(pCity, iBuyer)

    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
    popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_TRADE_CHOOSE_BONUS",("", )) )
    popupInfo.setOnClickedPythonCallback("popupTradeChooseBonus")
    popupInfo.setData1(pUnit.getOwner())
    popupInfo.setData2(pUnit.getID())

    for eBonus in lGoods:
        sBonusDesc = gc.getBonusInfo(eBonus).getDescription()
        iPrice = calculateBonusBuyingPrice(eBonus, iBuyer, iSeller)
        sText = CyTranslator().getText("TXT_KEY_BUY_BONUS", (sBonusDesc, iPrice))
        sBonusButton = gc.getBonusInfo(eBonus).getButton()
        popupInfo.addPythonButton(sText, sBonusButton)

    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
    popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
    popupInfo.addPopup(iBuyer)

# --- End of trade in cities

# --- Price stuff (trade) ---

# Basis value for each bonus
# auch in TXT_KEY_TRADE_ADVISOR_WERT_PANEL
def getBonusValue(eBonus):
    if eBonus == -1 or eBonus in lUntradeable: return -1
    if eBonus in lCultivatable: return 20
    elif eBonus in lLuxury: return 40
    elif eBonus in lRarity: return 50
    else: return 30 # strategic bonus ressource

# Price player pays for buying bonus
def calculateBonusBuyingPrice(eBonus, iBuyer, iSeller):
    if iBuyer == -1 or iSeller == -1: return -1
    iValue = getBonusValue(eBonus)
    pBuyer = gc.getPlayer(iBuyer)
    pSeller = gc.getPlayer(iSeller)
    if pBuyer.getTeam() == pSeller.getTeam(): iAttitudeModifier = 100
    else:
        # Furious = 0, Annoyed = 1, Cautious = 2, Pleased = 3, Friendly = 4
        iAttitudeModifier = 125 - 5*pSeller.AI_getAttitude(iBuyer)
    return (iValue * iAttitudeModifier) / 100

# Money player gets for selling bonus
def calculateBonusSellingPrice(pUnit, pCity):
  global lTradeUnits
  if not pUnit.getUnitType() in lTradeUnits:  return -1
  eBonus = int(CvUtil.getScriptData(pUnit, ["b"], -1))
  if eBonus == -1: return -1
  iValue = getBonusValue(eBonus)
  #iValue += iValue / 2 # besserer Verkaufswert fuer bessere Bonusgueter (Luxusgut)
  iBuyer = pCity.getOwner()
  iSeller = pUnit.getOwner()
  pBuyer = gc.getPlayer(iBuyer)
  pSeller = gc.getPlayer(iSeller)
  if hasBonusIgnoreFreeBonuses(pCity, eBonus): # allows "cancellation" of buying / Bonus direkt nach Einkauf wieder verkaufen (ohne Gewinn)
    return calculateBonusBuyingPrice(eBonus, iSeller, iBuyer) # Switch positions of seller and buyer

  if pBuyer.getTeam() == pSeller.getTeam(): iModifier = 100
  else:
    # Furious = 0, Annoyed = 1, Cautious = 2, Pleased = 3, Friendly = 4
    iModifier = 100 + 5*pSeller.AI_getAttitude(iBuyer)
  return (iValue * iModifier * (100+pCity.getPopulation()*5)) / 10000

# --- End of price stuff (trade) ---

# --- Automated trade routes (popups for HI) ---

# Erzeugt Popup fuer Erstellung einer automatisierten Handelsroute, wird insgesamt sechsmal pro Route aufgerufen:
# Civ waehlen => Stadt waehlen => Bonus waehlen => Civ waehlen => Stadt waehlen => Bonus waehlen
# iType = 1, 2, ...., 6 gibt an, an welcher Stelle im Prozess man gerade ist (1: erste Civ waehlen, ..., 6: zweiten Bonus waehlen)
# iData1/2: Ggf. noetige, zusaetzliche Informationen
def doPopupAutomatedTradeRoute(pUnit, iType, iData1, iData2):
    iUnitOwner = pUnit.getOwner()
    pUnitOwner = gc.getPlayer(iUnitOwner)
    pUnitOwnerTeam = gc.getTeam(pUnitOwner.getTeam())

    if iType == 1 or iType == 4:
        # Choose civilization 1 (iType == 1) or civilization 2 (iType == 4)
        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
        if iType == 1: popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_TRADE_ROUTE_CHOOSE_CIV_1",("", )) )
        else: popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_TRADE_ROUTE_CHOOSE_CIV_2",("", )) )
        popupInfo.setOnClickedPythonCallback("popupTradeRouteChooseCiv")
        popupInfo.setData1(iUnitOwner)
        popupInfo.setData2(pUnit.getID())
        popupInfo.setData3(iType == 1)

        lCivs = getPossibleTradeCivs(iUnitOwner)
        for iPlayer in lCivs:
            pPlayer = gc.getPlayer(iPlayer)
            sText = pPlayer.getCivilizationShortDescription(0) + " (" + pPlayer.getName() + ")"
            sButton = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getButton()
            popupInfo.addPythonButton(sText, sButton)

        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
        popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
        popupInfo.addPopup(iUnitOwner)
    elif iType == 2 or iType == 5:
        # Choose city 1 (iType == 2) or city 2 (iType == 5)
        iCityOwner = iData1
        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
        popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_TRADE_ROUTE_CHOOSE_CITY",("", )) )
        if iType == 2:
            popupInfo.setOnClickedPythonCallback("popupTradeRouteChooseCity1")
        else:
            popupInfo.setOnClickedPythonCallback("popupTradeRouteChooseCity2")
        popupInfo.setData1(iUnitOwner)
        popupInfo.setData2(pUnit.getID())
        popupInfo.setData3(iCityOwner)

        bWater = False
        if pUnit.getDomainType() == DomainTypes.DOMAIN_SEA: bWater = True
        lCities = getPossibleTradeCitiesForCiv(iUnitOwner, iCityOwner, bWater)
        sButton = ",Art/Interface/Buttons/Actions/FoundCity.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,1,4"
        for pCity in lCities:
            sText = pCity.getName()
            popupInfo.addPythonButton(sText, sButton)

        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
        popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
        popupInfo.addPopup(iUnitOwner)
    elif iType == 3 or iType == 6:
        # Choose bonus to buy in selected city.
        pCity = gc.getPlayer(iData1).getCity(iData2)
        sCityName = pCity.getName()
        lGoods = getCitySaleableGoods(pCity, -1)
        lGoods.append(-1)
        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
        popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_TRADE_ROUTE_CHOOSE_BONUS",(sCityName, )) )
        popupInfo.setOnClickedPythonCallback("popupTradeRouteChooseBonus")
        popupInfo.setData1(iUnitOwner)
        popupInfo.setData2(pUnit.getID())
        popupInfo.setData3(iType == 3)

        for eBonus in lGoods:
            if eBonus != -1:
                sText = gc.getBonusInfo(eBonus).getDescription()
                sButton = gc.getBonusInfo(eBonus).getButton()
                popupInfo.addPythonButton(sText, sButton)
            else:
                sText = CyTranslator().getText("TXT_KEY_NO_BONUS",("", ))
                sButton = "Art/Interface/Buttons/Techs/button_x.dds"
                popupInfo.addPythonButton(sText, sButton)

        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
        popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
        popupInfo.addPopup(iUnitOwner)

# --- End of automated trade routes for HI ---

# --- Helper functions ---

"""
# Initialises ScriptData for new merchants
def initMerchant(pUnit):
    CvUtil.addScriptData(pUnit, "x", -1) # coordinates will be saved when bonus is stored
    CvUtil.addScriptData(pUnit, "y", -1)
    CvUtil.addScriptData(pUnit, "bonus", -1)

# Initialises ScriptData for new cultivation Units
def initCultivationUnit(pUnit, pCity):
    #~ global lCultivatable
    #~ iX = pCity.getX()
    #~ iY = pCity.getY()
    #~ iCityOwnerTeam = pCity.getTeam()
    lStored = []
    #~ for x in xrange(5): # check plots
        #~ for y in xrange(5):
            #~ pLoopPlot = gc.getMap().plot(iX + x - 2, iY + y - 2)
            #~ if pLoopPlot != None and not pLoopPlot.isNone():
                #~ if pLoopPlot.getTeam() != iCityOwnerTeam: continue
                #~ # plot needs to have suitable improvement and city needs to have access to bonus (=> connection via trade route (street))
                #~ eBonus = pLoopPlot.getBonusType(iCityOwnerTeam)
                #~ eImprovement = pLoopPlot.getImprovementType()
                #~ if eImprovement != -1 and eBonus != -1 and eBonus not in lStored and eBonus in lCultivatable:
                  #~ if gc.getImprovementInfo(eImprovement).isImprovementBonusMakesValid(eBonus) and hasBonusIgnoreFreeBonuses(pCity, eBonus):
                    #~ lStored.append(eBonus)

    #~ if gc.getPlayer(pUnit.getOwner()).isHuman():
       #~ if len(lStored) > 0:
         #~ CyInterface().addMessage(pUnit.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_COLLECT_GOODS",(gc.getBonusInfo(eBonus).getDescription(),)), "AS2D_BUILD_GRANARY", 2, None, ColorTypes(4), 0, 0, False, False)
       #~ else:
         #~ CyInterface().addMessage(pUnit.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_COLLECT_NO_GOODS",("",)), "AS2D_ERROR", 2, None, ColorTypes(4), 0, 0, False, False)

    sScriptDataString = convertIntListToString(lStored)
##    sScriptDataString = "" # String which will be stored in pUnit, represents bonuses stored in unit
##    for eBonus in lStored:
##        sScriptDataString += ","
##        sScriptDataString += str(eBonus)
##    sScriptDataString = sScriptDataString[1:] # Remove comma at the beginning
    CvUtil.addScriptData(pUnit, "cultivationBonuses", sScriptDataString) # string looks like e.g. "23,45,12,34"
"""

def initAutomatedTradeRoute(pUnit, iX1, iY1, iX2, iY2, eBonus1, eBonus2):
    CvUtil.addScriptData(pUnit, "automX1", iX1)
    CvUtil.addScriptData(pUnit, "automY1", iY1)
    CvUtil.addScriptData(pUnit, "automX2", iX2)
    CvUtil.addScriptData(pUnit, "automY2", iY2)
    CvUtil.addScriptData(pUnit, "automBonus1", eBonus1) # bonus bought in city 1
    CvUtil.addScriptData(pUnit, "automBonus2", eBonus2) # bonus bought in city 2
    CvUtil.addScriptData(pUnit, "automActive", 1)

# Returns whether pCity has access to eBonus, ignoring free bonuses (from trade). Gets an own function bc. it used several times.
def hasBonusIgnoreFreeBonuses(pCity, eBonus):
    return ((pCity.getNumBonuses(eBonus) - pCity.getFreeBonus(eBonus)) > 0)

# Returns a list of the tradeable bonuses within pCity's range (radius of 2) + bonuses from buildings (bronze etc.). Only goods within the team's culture are considered.
# if iBuyer != -1: Bonuses the buying player cannot afford (not enough money) are excluded
def getCitySaleableGoods(pCity, iBuyer):
    if pCity == None or pCity.isNone(): return []
    iCityOwnerTeam = pCity.getTeam()
    iCityOwner = pCity.getOwner()
    pCityOwner = gc.getPlayer(iCityOwner)
    if iBuyer != -1: iMaxPrice = gc.getPlayer(iBuyer).getGold()
    lGoods = []
    iX = pCity.getX()
    iY = pCity.getY()
    for x in xrange(5): # check plots
        for y in xrange(5):
            pLoopPlot = gc.getMap().plot(iX + x - 2, iY + y - 2)
            if pLoopPlot != None and not pLoopPlot.isNone():
                if pLoopPlot.getTeam() != iCityOwnerTeam: continue
                # plot needs to have suitable improvement and city needs to have access to bonus (=> connection via trade route (street))
                eBonus = pLoopPlot.getBonusType(iCityOwnerTeam)
                eImprovement = pLoopPlot.getImprovementType()
                if eImprovement != -1 and eBonus != -1 and eBonus not in lGoods and eBonus not in lUntradeable:
                  if gc.getImprovementInfo(eImprovement).isImprovementBonusMakesValid(eBonus) and hasBonusIgnoreFreeBonuses(pCity, eBonus):
                    if iBuyer == -1 or calculateBonusBuyingPrice(eBonus, iBuyer, iCityOwner) <= iMaxPrice: # Max price
                        lGoods.append(eBonus)
    iMaxNumBuildings = gc.getNumBuildingInfos()
    for iBuilding in xrange(iMaxNumBuildings): # check buildings
        if pCity.isHasBuilding(iBuilding):
            eBonus = gc.getBuildingInfo(iBuilding).getFreeBonus()
            if eBonus != -1 and eBonus not in lUntradeable and eBonus not in lGoods and hasBonusIgnoreFreeBonuses(pCity, eBonus):
                if iBuyer == -1 or calculateBonusBuyingPrice(eBonus, iBuyer, iCityOwner) <= iMaxPrice: # Max price
                    lGoods.append(eBonus)
    return lGoods

# Returns list of civs iPlayer can trade with (has met and peace with). List always includes iPlayer himself.
def getPossibleTradeCivs(iPlayer):
    pPlayer = gc.getPlayer(iPlayer)
    pTeam = gc.getTeam(pPlayer.getTeam())
    lCivList = []
    for iCiv in xrange(gc.getMAX_PLAYERS()):
        iCivTeam = gc.getPlayer(iCiv).getTeam()
        if pTeam.isHasMet(iCivTeam) and not pTeam.isAtWar(iCivTeam):
            lCivList.append(iCiv)
    return lCivList

# Returns list of cities which 1. belong to iPlayer2 and 2. are visible to iPlayer1
def getPossibleTradeCitiesForCiv(iPlayer1, iPlayer2, bWater):
    iTeam1 = gc.getPlayer(iPlayer1).getTeam()
    pPlayer2 = gc.getPlayer(iPlayer2)
    lCityList = []
    (pLoopCity, iter) = pPlayer2.firstCity(False)
    while pLoopCity:
        if pLoopCity.isRevealed(iTeam1, 0):
          if bWater:
             if pLoopCity.isCoastal(4): lCityList.append(pLoopCity)
          else: lCityList.append(pLoopCity)
        (pLoopCity, iter) = pPlayer2.nextCity(iter, False)
    return lCityList

# Converts e.g. "34,56,23" to [ 34, 56, 23 ] (list entries are ints, not strings!). Used for cultivation unit ScriptData.
def convertStringToIntList(sString):
    if sString == "": return []
    lStoredBonusesString = sString.split(",") # e.g. = [ "32", "21", 43" ], contains bonuses as strings
    lStoredBonusesInt = []
    for sBonus in lStoredBonusesString:
        lStoredBonusesInt.append(int(sBonus))
    return lStoredBonusesInt

# Like convertStringToIntList, but the other way around
def convertIntListToString(lList):
    if len(lList) == 0: return ""
    sString = ""
    for l in lList:
        sString += "," + str(l)
    sString = sString[1:] # remove comma at the beginning
    return sString

# Returns intersection of two lists (Schnitt beider Listen).
def getIntersection(lList1, lList2):
    lIntersection = []
    for a in lList1:
        if a in lList2: lIntersection.append(a)
    return lIntersection

# Gibt Plot zurueck, auf dem das naechste Handelsstrassen-Stueck entstehen soll bzw. ob die Strasse schon fertig ist. Von Pie.
def getPlotTradingRoad(pSource, pDest, iTyp):

    # iTyp=0: Handelsstrasse bauen (Returns: pPlot/None),
    # iTyp=1: Handelsstrasse checken ob zw. pSource und pDest fertig (Returns: True/False)

    # Nur auf gleichem Kontinent
    if pSource.getArea() != pDest.getArea(): return None

    iTradeRoad = gc.getInfoTypeForString("ROUTE_TRADE_ROAD")
    iSourceX = pSource.getX()
    iSourceY = pSource.getY()
    iDestX = pDest.getX()
    iDestY = pDest.getY()
    bSourceGerade = False

    # wenn pSource = pTarget (Haendler ueber Schiff im Hafen)
    if iSourceX == iDestX and iSourceY == iDestY: return None

    # Herausfinden, ob bei pSource eine GERADE Strasse gebaut wurde
    # um zu verhindern, dass 2 Routen erstellt werden:
    #-------#
    #   --X #
    #  / /  #
    # X--   #
    #-------#
    # wenn es noch keine Strasse in der Stadt gibt => egal
    # wenn es eine Strasse gibt, dann den Umkreis checken
    if pSource.getRouteType() == iTradeRoad:
     iBest = 0
     for i in range(3):
      for j in range(3):
        loopPlot = gc.getMap().plot(iSourceX + i - 1, iSourceY + j - 1)
        if not loopPlot.isNone():
          if loopPlot.getRouteType() == iTradeRoad:
            iTmp = gc.getMap().calculatePathDistance(loopPlot,pDest)
            if iBest == 0: iBest = iTmp
            elif iTmp == iBest and (i==1 or j==1): bSourceGerade = True
            elif iTmp < iBest:
              if i==1 or j==1: bSourceGerade = True
              else: bSourceGerade = False


    # Den naechsten Plot fuer die Handelsstrasse herausfinden
    if pDest.getRouteType() != iTradeRoad:
        if iTyp == 0: return pDest # Wenn die Stadt noch keine Handelsstrasse hat
        else: return False

    iBestX = iDestX
    iBestY = iDestY
    pBest = pDest
    while (iBestX != iSourceX or iBestY != iSourceY):
      i=0
      j=0
      iBest=0
      for i in range(3):
       for j in range(3):
        loopPlot = gc.getMap().plot(iBestX + i - 1, iBestY + j - 1)
        if not loopPlot.isNone():
          if not loopPlot.isPeak() and not loopPlot.isWater():
            iTmp = gc.getMap().calculatePathDistance(loopPlot,pSource)

            # Beenden, wenn kein Weg moeglich
            if iTmp == -1:
              if iTyp == 0: return None
              else: return True
            # wenn Distanz null ist, wurde der letzte Plot gefunden
            elif iTmp == 0:
              if iTyp == 0:
                if loopPlot.getRouteType() == iTradeRoad: return None
                else: return loopPlot
              else:
                  if loopPlot.getRouteType() == iTradeRoad: return True
                  else: return False
            # ---------

            if iBest == 0 or iTmp < iBest:
              iBest = iTmp
              pBest = loopPlot
            elif iTmp == iBest:
              # Bei gleichen Entfernungen (max. 3 Moeglichkeiten: schraeg - gerade (- schraeg))
              # Wenn bei der Quelle eine GERADE Strasse verlaeuft, dann schraeg bauen. Sonst umgekehrt.
              if i==1 or j==1 and not bSourceGerade: pBest = loopPlot

      iBestX = pBest.getX()
      iBestY = pBest.getY()

      if pBest.getRouteType() != iTradeRoad:
        if iTyp == 0: return pBest
        else: return False

    # Wenn iTyp=0 und kein Plot gefunden wurde
    if iTyp == 0: return None
    else: return True

# --- End of helper functions ---

# --- AI and automated trade routes ---

# Lets pUnit shuttle between two cities (defined by UnitScriptData). Used by AI and by HI (automated trade routes).
def doAutomateMerchant(pUnit, bAI):
##    for i in range(gc.getMAX_PLAYERS()):
##        if gc.getPlayer(i).isHuman():
##            iHumanPlayer = i (needed for test messages, otherwise unnecessary)
##            break
    iPlayer = pUnit.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    s = pPlayer.getName()
    pUnitPlot = pUnit.plot()
    iUnitX = pUnitPlot.getX()
    iUnitY = pUnitPlot.getY()
    bActive = int(CvUtil.getScriptData(pUnit, ["automActive"], 0)) # set to False if automated route is deactivated
    if not bActive: return False
    iTurn = gc.getGame().getGameTurn()
    # Verhindern, dass mehrmals pro Runden geprueft wird, um Rundenzeit zu sparen
    # Z.B. bei bedrohten Einheiten ruft Civ die Funktion sonst 100 Mal auf, weiss nicht wieso...
    iLastTurnChecked = int(CvUtil.getScriptData(pUnit, ["automLastTurnChecked"], -1))
    if iLastTurnChecked >= iTurn: return False
    else: CvUtil.addScriptData(pUnit, "automLastTurnChecked", iTurn)
    pUnit.getGroup().clearMissionQueue()
    eStoredBonus = int(CvUtil.getScriptData(pUnit, ["b"], -1))
    iX1 = int(CvUtil.getScriptData(pUnit, ["automX1"], -1))
    iY1 = int(CvUtil.getScriptData(pUnit, ["automY1"], -1))
    iX2 = int(CvUtil.getScriptData(pUnit, ["automX2"], -1))
    iY2 = int(CvUtil.getScriptData(pUnit, ["automY2"], -1))
    eBonus1 = int(CvUtil.getScriptData(pUnit, ["automBonus1"], -1)) # bonus bought in city 1
    eBonus2 = int(CvUtil.getScriptData(pUnit, ["automBonus2"], -1)) # bonus bought in city 2
    pCityPlot1 = CyMap().plot(iX1, iY1)
    pCityPlot2 = CyMap().plot(iX2, iY2)
    pCity1 = pCityPlot1.getPlotCity()
    pCity2 = pCityPlot2.getPlotCity()
    if pCity1 == None or pCity1.isNone() or pCity2 == None or pCity2.isNone(): return False
    if pUnit.atPlot(pCityPlot1) or pUnit.atPlot(pCityPlot2):
        if pUnit.atPlot(pCityPlot1):
            pCurrentCity = pCity1
            pNewCity = pCity2
            eBonusBuy = eBonus1
            eBonusSell = eBonus2
        elif pUnit.atPlot(pCityPlot2):
            pCurrentCity = pCity2
            pNewCity = pCity1
            eBonusBuy = eBonus2
            eBonusSell = eBonus1
        if eBonusSell != -1 and eStoredBonus == eBonusSell: doSellBonus(pUnit, pCurrentCity)
        # HI: if player does not have enough money, trade route is cancelled
        # AI: if AI does not have enough money, AI buys bonus nonetheless (causes no known errors)
        if bAI: iBuyer = -1
        else: iBuyer = iPlayer
        lCitySaleableGoods = getCitySaleableGoods(pCurrentCity, iBuyer)
        if eBonusBuy == -1:
            #pUnit.getGroup().clearMissionQueue()
            pUnit.getGroup().pushMoveToMission(pNewCity.getX(), pNewCity.getY())
            # CyInterface().addMessage(iHumanPlayer, True, 10, "Mission eBonusBuy == -1 " + s, None, 2, None, ColorTypes(7), pUnit.getX(), pUnit.getY(), False, False)
        elif eBonusBuy in lCitySaleableGoods:
            if eStoredBonus != eBonusBuy:
                # if not already acquired / Wenn Bonus nicht bereits gekauft wurde
                doBuyBonus(pUnit, eBonusBuy, pCurrentCity.getOwner())
            #pUnit.getGroup().clearMissionQueue()
            pUnit.getGroup().pushMoveToMission(pNewCity.getX(), pNewCity.getY())
            # CyInterface().addMessage(iHumanPlayer, True, 10, "Mission eBonusBuy in lCitySaleable " + s, None, 2, None, ColorTypes(7), pUnit.getX(), pUnit.getY(), False, False)
        elif eStoredBonus == eBonusBuy:
            #pUnit.getGroup().clearMissionQueue()
            pUnit.getGroup().pushMoveToMission(pNewCity.getX(), pNewCity.getY())
            # CyInterface().addMessage(iHumanPlayer, True, 10, "Mission eBonusBuy == eStoredBonus " + s, None, 2, None, ColorTypes(7), pUnit.getX(), pUnit.getY(), False, False)
        else:
            # bonus is no longer available (or player does not have enough money) => cancel automated trade route
            CvUtil.addScriptData(pUnit, "automActive", 0) # deactivate route
            # CyInterface().addMessage(iHumanPlayer, True, 10, "doAutomateMerchant returns False " + s, None, 2, None, ColorTypes(7), pUnit.getX(), pUnit.getY(), False, False)
            return False
    else:
        # unit is anywhere => send to city 1
        iDistance1 = CyMap().calculatePathDistance(pUnitPlot, pCityPlot1)
        iDistance2 = CyMap().calculatePathDistance(pUnitPlot, pCityPlot1)
        if iDistance1 == -1 and iDistance2 == -1:
            # CyInterface().addMessage(iHumanPlayer, True, 10, "doAutomateMerchant returns False " + s, None, 2, None, ColorTypes(7), pUnit.getX(), pUnit.getY(), False, False)
            return False # plot unreachable
        elif iDistance1 == -1: pUnit.getGroup().pushMoveToMission(pCityPlot2.getX(), pCityPlot2.getY())
        elif iDistance2 == -1 or iDistance1 <= iDistance2: pUnit.getGroup().pushMoveToMission(pCityPlot1.getX(), pCityPlot1.getY())
        else: pUnit.getGroup().pushMoveToMission(pCityPlot2.getX(), pCityPlot2.getY())
##        if iDistance != -1: pUnit.getGroup().pushMoveToMission(pCityPlot1.getX(), pCityPlot1.getY())
##        else:
##            CyInterface().addMessage(iHumanPlayer, True, 10, "doAutomateMerchant returns False " + s, None, 2, None, ColorTypes(7), pUnit.getX(), pUnit.getY(), False, False)
##            return False # plot unreachable
    # CyInterface().addMessage(iHumanPlayer, True, 10, "doAutomateMerchant returns True " + s, None, 2, None, ColorTypes(7), pUnit.getX(), pUnit.getY(), False, False)
    # Am Ende eine Runde warten, da die Einheit sonst, wenn sie bei Erreichen einer Stadt noch Bewegungspunkte hat, einen neuen Befehl verlangt
    pUnit.getGroup().pushMission(MissionTypes.MISSION_SKIP, 0, 0, 0, True, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
    return True

# Weist der Einheit eine moeglichst kurze Handelsroute zu, die moeglichst so verlaeuft, dass an beiden Stationen ein Luxusgut eingeladen wird
def doAssignTradeRoute_AI(pUnit):
    # iHumanPlayer = -1 (Needed for test messages, otherwise unnecessary)
    iPlayer = pUnit.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    pTeam = gc.getTeam(pPlayer.getTeam())
    pUnitPlot = pUnit.plot()
    # friedliche Nachbarn raussuchen
    lNeighbors = []
    iRange = gc.getMAX_PLAYERS()
    for iLoopPlayer in range(iRange):
     pLoopPlayer = gc.getPlayer(iLoopPlayer)
     # if pLoopPlayer.isHuman(): iHumanPlayer = iLoopPlayer
     if pLoopPlayer.isAlive() and iLoopPlayer != iPlayer:
       if pTeam.isHasMet(pLoopPlayer.getTeam()):
         if pTeam.isOpenBorders (pLoopPlayer.getTeam()):
           if not pTeam.isAtWar(pLoopPlayer.getTeam()):
            # Distanz mittels Abstand zur Hauptstadt herausfinden
            if not pLoopPlayer.getCity(0).isNone():
              iDistance = CyMap().calculatePathDistance(pUnitPlot, pLoopPlayer.getCity(0).plot())
              if iDistance != -1: lNeighbors.append([iDistance,iLoopPlayer])
    lNeighbors.sort() # sort by distance
    lNeighbors = lNeighbors[:5] # only check max. 5 neighbors
    # Liste aller Staedte des Spielers mit verfuegbaren Luxusguetern. Staedte ohne Luxusgut ausgelassen.
    lPlayerLuxuryCities = getPlayerLuxuryCities(iPlayer)
    iMaxDistance = 20 # Wie weit die KI einen Haendler max. schickt
    iMinDistance = -1
    bBothDirections = False
    pBestPlayerCity = None
    pBestNeighborCity = None
    for [iDistance, iNeighbor] in lNeighbors:
        #iNeighbor = lList[1]
        pNeighbor = gc.getPlayer(iNeighbor)
        lNeighborLuxuryCities = getPlayerLuxuryCities(iNeighbor)
        # Sucht nach Paar von Staedten, zwischen denen Luxushandel moeglich ist, mit min. Distanz.
        # Routen, bei denen in beiden Staedten Luxus eingekauft werden kann, der in der anderen Stadt wieder verkauft
        # werden kann (=> Bonus NICHT in beiden Staedten), werden bevorzugt (dann ist bBothDirections = True).
        # Sonst wird eine Route gewaehlt, bei der der Haendler nur in eine Richtung handelt (andere Richtung Leertransport)
        for [pNeighborCity, lNeighborCityLuxury] in lNeighborLuxuryCities:
            for [pPlayerCity, lPlayerCityLuxury] in lPlayerLuxuryCities:
                pCityPlotPlayer = CyMap().plot(pPlayerCity.getX(), pPlayerCity.getY())
                pCityPlotNeighbor = CyMap().plot(pNeighborCity.getX(), pNeighborCity.getY())
                #CyInterface().addMessage(iHumanPlayer, True, 10, "Innere for-Schleife", None, 2, None, ColorTypes(8), pUnit.getX(), pUnit.getY(), False, False)
                # Handelsstrasse existiert schon => andere Route waehlen
                if getPlotTradingRoad(pCityPlotPlayer, pCityPlotNeighbor, 1): continue
                #CyInterface().addMessage(iHumanPlayer, True, 10, "Keine Handelsstrasse", None, 2, None, ColorTypes(8), pUnit.getX(), pUnit.getY(), False, False)
                bDirection1 = False
                bDirection2 = False
                for eBonus in lNeighborCityLuxury:
                    #if eBonus not in lPlayerCityLuxury:
                    if not pPlayerCity.hasBonus(eBonus):
                        bDirection1 = True
                        break
                for eBonus in lPlayerCityLuxury:
                    #if eBonus not in lNeighborCityLuxury:
                    if not pNeighborCity.hasBonus(eBonus):
                        bDirection2 = True
                        break
                iDistance = CyMap().calculatePathDistance(pCityPlotPlayer, pCityPlotNeighbor)
                if iDistance != -1 and iDistance < iMaxDistance:
                    #CyInterface().addMessage(iHumanPlayer, True, 10, "iDistance != -1", None, 2, None, ColorTypes(8), pUnit.getX(), pUnit.getY(), False, False)
                    if bDirection1 and bDirection2:
                        if iMinDistance == -1 or iDistance < iMinDistance or bBothDirections == False:
                            bBothDirections = True
                            iMinDistance = iDistance
                            pBestPlayerCity = pPlayerCity
                            pBestNeighborCity = pNeighborCity
                    elif (bDirection1 or bDirection2) and bBothDirections == False:
                        if iMinDistance == -1 or iDistance < iMinDistance:
                            iMinDistance = iDistance
                            pBestPlayerCity = pPlayerCity
                            pBestNeighborCity = pNeighborCity
        # Wenn Route, die in beide Richtungen funktioniert, gefunden wurde, abbrechen (spart Rechenzeit)
        # Route ist zwar ggf. nicht optimal, aber gut genug (beide Richtungen, Abstand <= iMaxDistance)
        if bBothDirections: break

    if pBestPlayerCity != None and pBestNeighborCity != None:
        s = pPlayer.getName()
        # CyInterface().addMessage(iHumanPlayer, True, 10, "Stadt gefunden " + s, None, 2, None, ColorTypes(7), pUnit.getX(), pUnit.getY(), False, False)
        lPlayerLuxuries = getCityLuxuries(pBestPlayerCity)
        lNeighborLuxuries = getCityLuxuries(pBestNeighborCity)
        eBonus1 = -1
        eBonus2 = -1
        for eBonus in lPlayerLuxuries:
            #if eBonus not in lNeighborLuxuries:
            if not pBestNeighborCity.hasBonus(eBonus):
                eBonus1 = eBonus
                break
        for eBonus in lNeighborLuxuries:
            #if eBonus not in lPlayerLuxuries:
            if not pBestPlayerCity.hasBonus(eBonus):
                eBonus2 = eBonus
                break
        initAutomatedTradeRoute(pUnit, pBestPlayerCity.getX(),pBestPlayerCity.getY(), pBestNeighborCity.getX(), pBestNeighborCity.getY(), eBonus1, eBonus2)
        return True
    else:
        return False

# Returns list of iPlayer's cities and the luxuries in their reach (saleable). Cities without luxuries are skipped.
# e.g. returns [ [pCity1, [3, 34, 7]], [pCity2, [3, 7, 13] ]
def getPlayerLuxuryCities(iPlayer):
    pPlayer = gc.getPlayer(iPlayer)
    lCityList = []
    (pLoopCity, iter) = pPlayer.firstCity(False)
    while pLoopCity:
        lLuxuryGoods = getCityLuxuries(pLoopCity)
        if len(lLuxuryGoods) > 0: lCityList.append([pLoopCity, lLuxuryGoods])
        (pLoopCity, iter) = pPlayer.nextCity(iter, False)
    return lCityList

# Returns list of the luxuries in reach of pCity (saleable). Used by AI trade route determination.
def getCityLuxuries(pCity):
    global lLuxury
    global lRarity
    lBonuses = getCitySaleableGoods(pCity, -1)
    lBonuses2 = getIntersection(lRarity, lBonuses)
    if len(lBonuses2) > 0: return lBonuses2
    lBonuses2 = getIntersection(lLuxury, lBonuses)
    if len(lBonuses2) > 0: return lBonuses2
    return lBonuses


############# Cities with special bonus order #################

# lCitiesSpecialBonus:
# tsb: TradeSpecialBonus
# tst: TradeSpecialTurns
def doUpdateCitiesWithSpecialBonus():
    global lCitiesSpecialBonus
    # Max 3 cities
    for pCity in lCitiesSpecialBonus:
      if pCity and not pCity.isNone():
        iTurn = int(CvUtil.getScriptData(pCity, ["tst"],-1))
        iTurn -= 1
        if iTurn <= 0:
          eBonus = int(CvUtil.getScriptData(pCity, ["tsb"],-1))
          CvUtil.removeScriptData(pCity, "tsb")
          CvUtil.removeScriptData(pCity, "tst")
          lCitiesSpecialBonus.remove(pCity)
          if pCity != None and not pCity.isNone():
           if eBonus != -1:
            if gc.getTeam(gc.getPlayer(gc.getGame().getActivePlayer()).getTeam()).isHasMet(gc.getPlayer(pCity.getOwner()).getTeam()):
             CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_SPECIAL_1",(pCity.getName(),gc.getBonusInfo(eBonus).getDescription())), None, 2, None, ColorTypes(13), 0, 0, False, False)
        else:
          CvUtil.addScriptData(pCity, "tst", iTurn)
    return

def addCityWithSpecialBonus():
    global lCitiesSpecialBonus
    global lLuxury
    global lRarity

    # Test
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("lCitiesSpecialBonus",len(lCitiesSpecialBonus))), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Max 3 cities
    # Neue Stadt mit Sonderauftrag hinzufuegen
    if len(lCitiesSpecialBonus) < 3:
      lNewCities = []
      iRange = gc.getMAX_PLAYERS()
      for i in range(iRange):
        loopPlayer = gc.getPlayer(i)
        if loopPlayer.isAlive() and not loopPlayer.isHuman():
          (pLoopCity, iter) = loopPlayer.firstCity(false)
          while pLoopCity:
            if pLoopCity not in lCitiesSpecialBonus: lNewCities.append(pLoopCity)
            (pLoopCity,iter) = loopPlayer.nextCity(iter, false)

      if len(lNewCities):
        # Stadt auswaehlen
        iRand = myRandom(len(lNewCities))
        pCity = lNewCities[iRand]

        # Globale Variable setzen
        lCitiesSpecialBonus.append(pCity)
        # Runden setzen
        lTurns = [21,26,31,36,41]
        iRand = myRandom(len(lTurns))
        CvUtil.addScriptData(pCity, "tst", lTurns[iRand])
        # Bonusgut herausfinden
        lNewBonus = []
        for iBonus in lLuxury + lRarity:
          if not pCity.hasBonus(iBonus): lNewBonus.append(iBonus)
        # Bonus setzen
        iRand = myRandom(len(lNewBonus))
        CvUtil.addScriptData(pCity, "tsb", lNewBonus[iRand])
        # Message
        if gc.getTeam(gc.getPlayer(gc.getGame().getActivePlayer()).getTeam()).isHasMet(gc.getPlayer(pCity.getOwner()).getTeam()):
           CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_SPECIAL_2",(pCity.getName(),gc.getBonusInfo(lNewBonus[iRand]).getDescription())), None, 2, None, ColorTypes(13), 0, 0, False, False)
    return

# In doSellBonus
def doCheckCitySpecialBonus(pUnit,pCity,eBonus):
    global lCitiesSpecialBonus

    eCityBonus =  int(CvUtil.getScriptData(pCity, ["tsb"],-1))
    if eCityBonus != -1 and eCityBonus == eBonus:
        iPlayer = pUnit.getOwner()
        pPlayer = gc.getPlayer(iPlayer)
        if iPlayer != gc.getGame().getActivePlayer():
              CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_SPECIAL_3",(pPlayer.getName(),)), None, 2, None, ColorTypes(13), 0, 0, False, False)
        else:
              CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_SPECIAL_4",("",)), "AS2D_WELOVEKING", 2, None, ColorTypes(13), 0, 0, False, False)

        # Belohnungen
        # Standard gift
        lGift = []
        lGift.append(gc.getInfoTypeForString("UNIT_GOLDKARREN"))
        lGift.append(gc.getInfoTypeForString("UNIT_SUPPLY_FOOD"))
        iNewUnitAIType = UnitAITypes.NO_UNITAI

        # Unit as gift:
        if myRandom(5) == 1:
            lGift = []
            # Auxiliar
            iUnit = gc.getCivilizationInfo(gc.getPlayer(pCity.getOwner()).getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_AUXILIAR"))
            if pCity.canTrain(iUnit,0,0): lGift.append(iUnit)
            iUnit = gc.getInfoTypeForString("UNIT_AUXILIAR_HORSE")
            if pCity.canTrain(iUnit,0,0): lGift.append(iUnit)
            # Slave
            if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_SKLAVENMARKT")): lGift.append(gc.getInfoTypeForString("UNIT_SLAVE"))
            # Mounted
            if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_STABLE")):
                lGift.append(gc.getInfoTypeForString("UNIT_HORSE"))
                if pCity.canTrain(gc.getInfoTypeForString("UNIT_CHARIOT"),0,0): lGift.append(gc.getCivilizationInfo(gc.getPlayer(pCity.getOriginalOwner()).getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_CHARIOT")))
                if pCity.canTrain(gc.getInfoTypeForString("UNIT_HORSE_ARCHER"),0,0): lGift.append(gc.getCivilizationInfo(gc.getPlayer(pCity.getOriginalOwner()).getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_HORSE_ARCHER")))
                if pCity.canTrain(gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"),0,0): lGift.append(gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"))
            # Elefant
            if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_ELEPHANT_STABLE")):
                lGift.append(gc.getInfoTypeForString("UNIT_ELEFANT"))
                if pCity.canTrain(gc.getInfoTypeForString("UNIT_WAR_ELEPHANT"),0,0): lGift.append(gc.getInfoTypeForString("UNIT_WAR_ELEPHANT"))
            # Kamel
            if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_CAMEL_STABLE")):
                lGift.append(gc.getInfoTypeForString("UNIT_CAMEL"))
                if pCity.canTrain(gc.getInfoTypeForString("UNIT_ARABIA_CAMELARCHER"),0,0): lGift.append(gc.getInfoTypeForString("UNIT_ARABIA_CAMELARCHER"))
                if pCity.canTrain(gc.getInfoTypeForString("UNIT_CAMEL_CATAPHRACT"),0,0): lGift.append(gc.getInfoTypeForString("UNIT_CAMEL_CATAPHRACT"))
            # Special units
            iUnit = gc.getCivilizationInfo(gc.getPlayer(pCity.getOwner()).getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SPECIAL4"))
            if pCity.canTrain(iUnit,0,0): lGift.append(iUnit)
            iUnit = gc.getCivilizationInfo(gc.getPlayer(pCity.getOwner()).getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SPECIAL5"))
            if pCity.canTrain(iUnit,0,0): lGift.append(iUnit)

                    # Set AI Type
            if len(lGift):
                iNewUnitAIType = UnitAITypes.UNITAI_ATTACK

                    # Message : Stadt schenkt Truppen
            if pPlayer.isHuman():
                CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_SPECIAL_5",("",)), "AS2D_WELOVEKING", 2, None, ColorTypes(13), 0, 0, False, False)

        else:
            # Message : Stadt schenkt Kostbarkeiten
            if pPlayer.isHuman():
                CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_SPECIAL_6",("",)), "AS2D_WELOVEKING", 2, None, ColorTypes(13), 0, 0, False, False)


        # Choose unit
        iRand = myRandom(len(lGift))
        iNewUnit = lGift[iRand]

        # Create unit (2x)
        pUnit1 = pPlayer.initUnit(iNewUnit, pCity.getX(), pCity.getY(), iNewUnitAIType, DirectionTypes.DIRECTION_SOUTH)
        pUnit2 = pPlayer.initUnit(iNewUnit, pCity.getX(), pCity.getY(), iNewUnitAIType, DirectionTypes.DIRECTION_SOUTH)

        # Load supply unit
        if iNewUnit == gc.getInfoTypeForString("UNIT_SUPPLY_FOOD"):
            lGoods = getAvailableCultivatableBonuses(pCity)

            lBonusList = [lGoods[myRandom(len(lGoods))]]
            CvUtil.addScriptData(pUnit1, "b", convertIntListToString(lBonusList))
            lBonusList = [lGoods[myRandom(len(lGoods))]]
            CvUtil.addScriptData(pUnit2, "b", convertIntListToString(lBonusList))


        CvUtil.removeScriptData(pCity, "tsb")
        CvUtil.removeScriptData(pCity, "tst")

        if pCity in lCitiesSpecialBonus:
            lCitiesSpecialBonus.remove(pCity)
    return
