### Imports
from CvPythonExtensions import *
import random

import PAE_Sklaven

### Defines
gc = CyGlobalContext()
    
# PAE Stadtstatus
iPopDorf = 3
iPopStadt = 6
iPopProvinz = 12
iPopMetropole = 20



def myRandom (num):
      if num <= 1: return 0
      else: return random.randint(0, num-1)
      

def doMessageCityGrowing(pCity):
    if pCity.isNone(): return

    if pCity.getFoodTurnsLeft() == 1 and pCity.foodDifference(True) > 0 and not pCity.isFoodProduction() and not pCity.AI_isEmphasize(5):

      # Inits
      iBuildingDorf = gc.getInfoTypeForString("BUILDING_KOLONIE")
      iBuildingStadt = gc.getInfoTypeForString("BUILDING_STADT")
      iBuildingProvinz = gc.getInfoTypeForString("BUILDING_PROVINZ")
      iBuildingMetropole = gc.getInfoTypeForString("BUILDING_METROPOLE")

      kBuildingDorf = gc.getBuildingInfo(iBuildingDorf)
      kBuildingStadt = gc.getBuildingInfo(iBuildingStadt)
      kBuildingProvinz = gc.getBuildingInfo(iBuildingProvinz)
      kBuildingMetropole = gc.getBuildingInfo(iBuildingMetropole)

      iPlayer = pCity.getOwner()
      # ---

      # MESSAGE: city will grow / Stadt wird wachsen
      iPop = pCity.getPopulation() + 1
      CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_WILL_GROW",(pCity.getName(),iPop)), None, 2, None, ColorTypes(13), 0, 0, False, False)

      # MESSAGE: city gets/is unhappy / Stadt wird/ist unzufrieden
      iBonusHealth = 0
      iBonusHappy = 0
      if iPop == iPopDorf:
        iBonusHealth = kBuildingDorf.getHealth()
        iBonusHappy = kBuildingDorf.getHappiness()
        # for iBonus in gc.getNumBonuses():
            # iAddHealth = kBuildingDorf.getBonusHealthChanges(iBonus)
            # if iAddHealth != -1:
              # iBonusHealth += iAddHealth
            # iAddHappy = kBuildingDorf.getBonusHappinessChanges(iBonus)
            # if iAddHappy != -1:
              # iBonusHappy += iAddHappy
      elif iPop == iPopStadt:
        iBonusHealth = kBuildingStadt.getHealth()
        iBonusHappy = kBuildingStadt.getHappiness()
      elif iPop == iPopProvinz:
        iBonusHealth = kBuildingProvinz.getHealth()
        iBonusHappy = kBuildingProvinz.getHappiness()
      elif iPop == iPopMetropole:
        iBonusHealth = kBuildingMetropole.getHealth()
        iBonusHappy = kBuildingMetropole.getHappiness()

      if pCity.happyLevel() - pCity.unhappyLevel(0) + iBonusHappy <= 0:
        if pCity.happyLevel() - pCity.unhappyLevel(0) == 0:
          CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GETS_UNHAPPY",(pCity.getName(),)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
        else:
          CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_IS_UNHAPPY",(pCity.getName(),)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)

      # MESSAGE: city gets/is unhealthy / Stadt wird/ist ungesund
      if pCity.goodHealth() - pCity.badHealth(False) + iBonusHealth <= 0:
        if pCity.goodHealth() - pCity.badHealth(False) == 0:
          CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GETS_UNHEALTY",(pCity.getName(),)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
        else:
          CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_IS_UNHEALTY",(pCity.getName(),)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)

  # -----------------

  
# PAE City status --------------------------
# Check City colony or province after events
# once getting a province: keep being a province
# Methode auch in CvWorldBuilderScreen.py - immer beide aendern
def doCheckCityState(pCity):
    global iPopDorf
    global iPopStadt
    global iPopProvinz
    global iPopMetropole
    
    if pCity.isNone(): return

    iBuildingSiedlung = gc.getInfoTypeForString("BUILDING_SIEDLUNG")
    iBuildingKolonie = gc.getInfoTypeForString("BUILDING_KOLONIE")
    iBuildingCity = gc.getInfoTypeForString("BUILDING_STADT")
    iBuildingProvinz = gc.getInfoTypeForString("BUILDING_PROVINZ")
    iBuildingMetropole = gc.getInfoTypeForString("BUILDING_METROPOLE")

    if pCity.getNumRealBuilding(iBuildingSiedlung) == 0:
      pCity.setNumRealBuilding(iBuildingSiedlung,1)

    if pCity.getPopulation() >= iPopDorf and pCity.getNumRealBuilding(iBuildingKolonie) == 0:
      pCity.setNumRealBuilding(iBuildingKolonie,1)
      if gc.getPlayer(pCity.getOwner()).isHuman():
        CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_1",(pCity.getName(),0)), "AS2D_WELOVEKING", 2, gc.getBuildingInfo(iBuildingKolonie).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

    if pCity.getPopulation() >= iPopStadt and pCity.getNumRealBuilding(iBuildingCity) == 0:
      pCity.setNumRealBuilding(iBuildingCity,1)
      if gc.getPlayer(pCity.getOwner()).isHuman():
        CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_2",(pCity.getName(),0)), "AS2D_WELOVEKING", 2, gc.getBuildingInfo(iBuildingCity).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

    # Falls extremer Wachstum: Meldungen von kleinerem Status beginnend
    if pCity.getPopulation() >= iPopProvinz and pCity.getNumRealBuilding(iBuildingProvinz) == 0:
      pCity.setNumRealBuilding(iBuildingProvinz,1)
      if gc.getPlayer(pCity.getOwner()).isHuman():
        CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_3",(pCity.getName(),0)), "AS2D_WELOVEKING", 2, gc.getBuildingInfo(iBuildingProvinz).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)
    if pCity.getPopulation() >= iPopMetropole and pCity.getNumRealBuilding(iBuildingMetropole) == 0:
      pCity.setNumRealBuilding(iBuildingMetropole,1)
      if gc.getPlayer(pCity.getOwner()).isHuman():
        CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_5",(pCity.getName(),0)), "AS2D_WELOVEKING", 2, gc.getBuildingInfo(iBuildingMetropole).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

    # Falls extremer Bev.rueckgang: Meldungen von hoeheren Status beginnend
    if pCity.getPopulation() < iPopMetropole and pCity.getNumRealBuilding(iBuildingMetropole) == 1:
      pCity.setNumRealBuilding(iBuildingMetropole,0)
      if gc.getPlayer(pCity.getOwner()).isHuman():
        CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_6",(pCity.getName(),0)), "AS2D_PLAGUE", 2, gc.getBuildingInfo(iBuildingProvinz).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)
    if pCity.getPopulation() < iPopProvinz and pCity.getNumRealBuilding(iBuildingProvinz) == 1:
      pCity.setNumRealBuilding(iBuildingProvinz,0)
      if gc.getPlayer(pCity.getOwner()).isHuman():
        CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_4",(pCity.getName(),0)), "AS2D_PLAGUE", 2, gc.getBuildingInfo(iBuildingCity).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

    # AI and its slaves
    if not gc.getPlayer(pCity.getOwner()).isHuman():
       PAE_Sklaven.doAIReleaseSlaves(pCity)
       
 

# --------------------------------
# Methode auch in CvWorldBuilderScreen.py - immer beide aendern
def doCheckTraitBuildings (pCity, iOwner):
      pOwner = gc.getPlayer(iOwner)
      # Trait-Gebaeude
      lTraitBuildings = []
      lTraitBuildings.append(gc.getInfoTypeForString("BUILDING_TRAIT_MARITIME_LOCAL"))
      lTraitBuildings.append(gc.getInfoTypeForString("BUILDING_TRAIT_CREATIVE_LOCAL"))
      lTraitBuildings.append(gc.getInfoTypeForString("BUILDING_TRAIT_CREATIVE_GLOBAL"))
      lTraitBuildings.append(gc.getInfoTypeForString("BUILDING_TRAIT_PHILOSOPHICAL_GLOBAL"))
      # Tech, ab der Creative_Local gesetzt wird
      iTechCreativeLocal = gc.getInfoTypeForString("TECH_ALPHABET")
      # Alle nicht passenden Gebaeude entfernen
      # Nur lokale hinzufuegen, globale nicht
      if pOwner.hasTrait(gc.getInfoTypeForString("TRAIT_MARITIME")): pCity.setNumRealBuilding(lTraitBuildings[0], 1)
      else: pCity.setNumRealBuilding(lTraitBuildings[0], 0)
      if not pOwner.hasTrait(gc.getInfoTypeForString("TRAIT_CREATIVE")):
          pCity.setNumRealBuilding(lTraitBuildings[1], 0)
          pCity.setNumRealBuilding(lTraitBuildings[2], 0)
      else:
          if gc.getTeam(pOwner.getTeam()).isHasTech(iTechCreativeLocal): pCity.setNumRealBuilding(lTraitBuildings[1], 1)
          else: pCity.setNumRealBuilding(lTraitBuildings[1], 0)
      if not pOwner.hasTrait(gc.getInfoTypeForString("TRAIT_PHILOSOPHICAL")): pCity.setNumRealBuilding(lTraitBuildings[3], 0)

# Methode auch in CvWorldBuilderScreen.py - immer beide aendern
def doCheckGlobalTraitBuildings (iPlayer):
      pPlayer = gc.getPlayer(iPlayer)

      lTraitBuildings = []
      lTraitBuildings.append(gc.getInfoTypeForString("BUILDING_TRAIT_CREATIVE_GLOBAL"))
      lTraitBuildings.append(gc.getInfoTypeForString("BUILDING_TRAIT_PHILOSOPHICAL_GLOBAL"))
      lTraits = []
      lTraits.append(gc.getInfoTypeForString("TRAIT_CREATIVE"))
      lTraits.append(gc.getInfoTypeForString("TRAIT_PHILOSOPHICAL"))
      iRangeTraitBuildings = len(lTraitBuildings)

      lCities = PyPlayer(iPlayer).getCityList()
      iRangeCities = len(lCities)

      for i in range(iRangeTraitBuildings):
          if not pPlayer.hasTrait(lTraits [i]): continue
          iTraitBuilding = lTraitBuildings [i]
          iCount = 0
          for iCity in range(iRangeCities):
             pCity = pPlayer.getCity(lCities[iCity].getID())
             if pCity.getNumRealBuilding(iTraitBuilding) > 0:
                 iCount += 1
                 if iCount > 1: pCity.setNumRealBuilding(iTraitBuilding, 0)
          if iCount == 0 and iRangeCities > 0: pPlayer.getCity(lCities[0].getID()).setNumRealBuilding(iTraitBuilding, 1)


# Begin Inquisition -------------------------------

def doInquisitorPersecution(pCity, pUnit):
    pPlayer = gc.getPlayer( pCity.getOwner( ) )
    iPlayer = pPlayer.getID( )

    iNumReligions = gc.getNumReligionInfos()
    # HI soll PopUp bekommen
    if pPlayer.isHuman():
       popupInfo = CyPopupInfo()
       popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
       popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_INQUISITION",(pCity.getName(), )) )
       popupInfo.setData1(iPlayer)
       popupInfo.setData2(pCity.getID())
       popupInfo.setData3(pUnit.getID())
       popupInfo.setOnClickedPythonCallback("popupReliaustreibung") # EntryPoints/CvScreenInterface und CvGameUtils / 704
       for iReligion in range(iNumReligions):
         if iReligion != pPlayer.getStateReligion() and pCity.isHasReligion(iReligion) and pCity.isHolyCityByType(iReligion) == 0:
           popupInfo.addPythonButton(gc.getReligionInfo(iReligion).getText(), gc.getReligionInfo(iReligion).getButton())
       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_INQUISITION_CANCEL",("", )), "Art/Interface/Buttons/General/button_alert_new.dds")
       popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
       popupInfo.addPopup(iPlayer)

    ## AI
    #else:
       #ReligionArray = []
       #for iReligion in range(iRange):
         #if iReligion != pPlayer.getStateReligion() and pCity.isHasReligion(iReligion) and pCity.isHolyCityByType(iReligion) == 0:
           #ReligionArray.append(iReligion)

       #if len(ReligionArray) > 0:
         #iRand = myRandom(len(ReligionArray))
         #doInquisitorPersecution2(iPlayer, pCity.getID(), -1, ReligionArray[iRand], pUnit.getID())

    pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
    #pUnit.kill(1,pUnit.getOwner())
  # -------------

def doInquisitorPersecution2(iPlayer, iCity, iButton, iReligion, iUnit):
    pPlayer = gc.getPlayer(iPlayer)
    pCity = pPlayer.getCity(iCity)
    szButton = gc.getUnitInfo(gc.getInfoTypeForString("UNIT_INQUISITOR")).getButton()
    iStateReligion = pPlayer.getStateReligion()
    iNumReligions = gc.getNumReligionInfos()
    # gets a list of all religions in the city except state religion
    lCityReligions = []
    for iReligionLoop in range(iNumReligions):
      if pCity.isHasReligion( iReligionLoop ):
        if pCity.isHolyCityByType(iReligionLoop) == 0 and iReligionLoop != iStateReligion:
          lCityReligions.append( iReligionLoop )

    # Wenn die Religion ueber PopUp kommt, muss sie mittels Buttonreihenfolge gefunden werden
    if iReligion == -1:
       iReligion = lCityReligions[iButton]

    if iReligion != -1:
       if iReligion != iStateReligion: iHC = -25
       else: iHC = 15

       # Does Persecution succeed
       iRandom = myRandom(100)
       if (iRandom < 95 - (len(lCityReligions) * 5) + iHC):

            pCity.setHasReligion(iReligion, 0, 0, 0)

            if pPlayer.isHuman():
              CyInterface().addMessage(iPlayer,True,15,CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION",(pCity.getName(),)),"AS2D_PLAGUE",2,szButton,ColorTypes(8),pCity.getX(),pCity.getY(),True,True)

            # remove its buildings
            iRange = gc.getNumBuildingInfos()
            for iBuildingLoop in range(iRange):
              if (pCity.isHasBuilding( iBuildingLoop )):
                pBuilding = gc.getBuildingInfo( iBuildingLoop )
                iRequiredReligion = pBuilding.getPrereqReligion( )
                # Wunder sollen nicht betroffen werden
                iBuildingClass = pBuilding.getBuildingClassType()
                thisBuildingClass = gc.getBuildingClassInfo(iBuildingClass)
                if iRequiredReligion == iReligion and thisBuildingClass.getMaxGlobalInstances() != 1:
                  pCity.setNumRealBuilding (iBuildingLoop,0)
                  #if pPlayer.isHuman():
                                        ##Meldung dass das Gebaeude zerstoert wurde
                                        #CyInterface().addMessage(iPlayer,True,15,CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION_Bildersturm",(pCity.getName(),)),"AS2D_PLAGUE",2,szButton,ColorTypes(8),pCity.getX(),pCity.getY(),True,True)

            # increasing Anger or Sympathy for an AI
            iRange = gc.getMAX_PLAYERS()
            for iPlayer2 in range(iRange):
              pSecondPlayer = gc.getPlayer(iPlayer2)
              iSecondPlayer = pSecondPlayer.getID()
              pReligion = gc.getReligionInfo( iReligion )

              # increases Anger for all AIs which have this religion as State Religion
              if (iReligion == pSecondPlayer.getStateReligion() and pSecondPlayer.isAlive()):
                pSecondPlayer.AI_changeAttitudeExtra(iPlayer,-2)
              # increases Sympathy for all AIs which have the same State Religion as the inquisitor
              elif (pPlayer.getStateReligion() == pSecondPlayer.getStateReligion() and pSecondPlayer.isAlive()):
                pSecondPlayer.AI_changeAttitudeExtra(iPlayer,+1)

              # info for all
              if (pSecondPlayer.isHuman()):
                iSecTeam = pSecondPlayer.getTeam()
                if gc.getTeam(iSecTeam).isHasMet(pPlayer.getTeam()):
                  CyInterface().addMessage(iSecondPlayer,True,15,CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION_GLOBAL",(pCity.getName(),pReligion.getText())),None,2,szButton,ColorTypes(10),pCity.getX(),pCity.getY(),True,True)

            # info for the player
            CyInterface().addMessage(iPlayer,True,20,CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION_GLOBAL_NEG",(pCity.getName(),pReligion.getText())),None,2,szButton,ColorTypes(7),pCity.getX(),pCity.getY(),True,True)
            CyInterface().addMessage(iPlayer,True,20,CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION_GLOBAL_POS",(pCity.getName(),pReligion.getText())),None,2,szButton,ColorTypes(8),pCity.getX(),pCity.getY(),True,True)

            # decrease population by 1, even if mission fails
            if pCity.getPopulation() > 1:
              pCity.changePopulation(-1)
              doCheckCityState(pCity)

       # Persecution fails
       elif pPlayer.isHuman():
         CyInterface().addMessage(iPlayer,True,15,CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION_FAIL",(pCity.getName(),)),"AS2D_SABOTAGE",2,szButton,ColorTypes(7),pCity.getX(),pCity.getY(),True,True)


    # City Revolt
    pCity.changeOccupationTimer(1)
  # ------

# end Inquisition / Religionsaustreibung


  # City Revolt
  # iTurns = deaktiv
def doCityRevolt(pCity, iTurns):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    pPlot = pCity.plot()

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("City Revolt (Zeile 6485)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Strafe verschaerfen
    #iTurns = iTurns * 2

    # Einheiten stilllegen
    iRange = pPlot.getNumUnits()
    for iUnit in range (iRange):
      pPlot.getUnit(iUnit).setDamage(60, -1)
      if 1 == myRandom(2):
        pPlot.getUnit(iUnit).setImmobileTimer(iTurns)

    #Stadtaufruhr
    pCity.changeHurryAngerTimer (iTurns)

    iTurns = int (iTurns / 2)
    if iTurns < 2: iTurns = 2
    #pCity.changeOccupationTimer (iTurns)
    pCity.setOccupationTimer(iTurns)

#    if gc.getNumEventTriggerInfos() > 0: # prevents mods that don't have events from getting an error
#       iEvent = CvUtil.findInfoTypeNum(gc.getEventTriggerInfo, gc.getNumEventTriggerInfos(),'EVENTTRIGGER_DESPOT_REVOLT')
#       if iEvent != -1 and gc.getGame().isEventActive(iEvent):
#          triggerData = pPlayer.initTriggeredData(iEvent, True, -1, pCity.getX(), pCity.getY(), iPlayer, pCity.getID(), -1, -1, -1, -1)
#       else: pCity.setOccupationTimer(2)
#    else: pCity.setOccupationTimer(2)


# --- renegading city
# A nearby city of pCity will revolt
def doNextCityRevolt(iX, iY, iOwner, iAttacker):
    if iOwner != -1 and iOwner != gc.getBARBARIAN_PLAYER():
      pOwner = gc.getPlayer(iOwner)
      if pOwner.getNumCities() > 1:
        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Next City Revolt (Zeile 4766)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        # Stadtentfernung messen und naeheste Stadt definieren / die Stadt soll innerhalb 10 Plots entfernt sein.
        iRevoltCity = -1
        iCityCheck  = -1
        # City with forbidden palace shall not revolt
        if gc.getTeam(pOwner.getTeam()).isHasTech(gc.getInfoTypeForString('TECH_POLYARCHY')): iBuilding = gc.getInfoTypeForString('BUILDING_PRAEFECTUR')
        else: iBuilding = gc.getInfoTypeForString('BUILDING_PROVINZPALAST')
        iRange = pOwner.getNumCities()
        for i in range (iRange):
          pLoopCity = pOwner.getCity(i) 
          if not pLoopCity.isNone():
            if not pLoopCity.isCapital() and pLoopCity.getOccupationTimer() < 1 and not pLoopCity.isHasBuilding(iBuilding) and pLoopCity.getOwner() != iAttacker:
              tmpX = pLoopCity.getX()
              tmpY = pLoopCity.getY()

              iBetrag = plotDistance(iX, iY, tmpX, tmpY)

              if iBetrag > 0 and iBetrag < 11 and (iCityCheck == -1 or iCityCheck > iBetrag):
                iCityCheck = iBetrag
                iRevoltCity = i

#            CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("City",i)), None, 2, None, ColorTypes(10), 0, 0, False, False)
#            CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Betrag",iBetrag)), None, 2, None, ColorTypes(10), 0, 0, False, False)

#        CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Revolt",iRevoltCity)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        # Stadt soll revoltieren: 3 Runden
        if iRevoltCity != -1:
          pCity = pOwner.getCity(iRevoltCity)
          #pCity.setOccupationTimer(3)
          doCityRevolt (pCity,4)

          # Message for the other city revolt
          if (gc.getPlayer(iAttacker).isHuman()):
            iRand = 1 + myRandom(6)
            CyInterface().addMessage(iAttacker, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_REVOLTS_1_"+str(iRand),(pCity.getName(),0)), "AS2D_REVOLTSTART", 2, "Art/Interface/Buttons/Techs/button_brandschatzen.dds", ColorTypes(8), pCity.getX(), pCity.getY(), True, True)
          elif (gc.getPlayer(iOwner).isHuman()):
            iRand = 1 + myRandom(6)
            CyInterface().addMessage(iOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_REVOLTS_2_"+str(iRand),(pCity.getName(),0)), "AS2D_REVOLTSTART", 2, "Art/Interface/Buttons/Techs/button_brandschatzen.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)

  # --- next city revolt

def doDesertification(pCity, pUnit):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    iCurrentEra = pPlayer.getCurrentEra()
    iUnitCombatType = pUnit.getUnitCombatType()
    if iCurrentEra > 0 and iUnitCombatType > 0:
        if iUnitCombatType in [gc.getInfoTypeForString("UNITCOMBAT_ARCHER"),gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER")]:
            return
            
        lNoForgeUnit = [
        gc.getInfoTypeForString("UNIT_WARRIOR"),
        gc.getInfoTypeForString("UNIT_AXEWARRIOR"),
        gc.getInfoTypeForString("UNIT_LIGHT_SPEARMAN"),
        gc.getInfoTypeForString("UNIT_HUNTER"),
        gc.getInfoTypeForString("UNIT_SCOUT"),
        gc.getInfoTypeForString("UNIT_MOUNTED_SCOUT"),
        gc.getInfoTypeForString("UNIT_BEGLEITHUND"),
        gc.getInfoTypeForString("UNIT_KAMPFHUND"),
        gc.getInfoTypeForString("UNIT_KAMPFHUND_TIBET"),
        gc.getInfoTypeForString("UNIT_KAMPFHUND_MACEDON"),
        gc.getInfoTypeForString("UNIT_KAMPFHUND_BRITEN"),
        gc.getInfoTypeForString("UNIT_BURNING_PIGS"),
        gc.getInfoTypeForString("UNIT_WORKBOAT"),
        gc.getInfoTypeForString("UNIT_DRUIDE"),
        gc.getInfoTypeForString("UNIT_BRAHMANE"),
        gc.getInfoTypeForString("UNIT_HORSE"),
        gc.getInfoTypeForString("UNIT_CAMEL"),
        gc.getInfoTypeForString("UNIT_ELEFANT")
        ]
        
        if pUnit.getUnitType() not in lNoForgeUnit:
            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Waldrodung",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

            iHolzLager = gc.getInfoTypeForString("IMPROVEMENT_LUMBER_CAMP")
            iMine = gc.getInfoTypeForString("IMPROVEMENT_MINE")
            iFeatForest = gc.getInfoTypeForString("FEATURE_FOREST")
            iFeatSavanna = gc.getInfoTypeForString("FEATURE_SAVANNA")
            iFeatJungle = gc.getInfoTypeForString("FEATURE_JUNGLE")
            iFeatDichterWald = gc.getInfoTypeForString("FEATURE_DICHTERWALD")
            [iFeatForest, iFeatSavanna, iFeatJungle, iFeatDichterWald]
            # nicht bei Zedernholz
            iBonusZedern = gc.getInfoTypeForString("BONUS_ZEDERNHOLZ")

            # Einen guenstigen Plot auswaehlen
            # Priority:
            # 1. Leerer Wald oder Mine
            # 2. Leere Savanne
            # 3. Leerer Dschungel
            # 4. Bewirtschaftetes Feld mit Wald aber ohne Holzlager
            # 5. Dichter Wald
            # 6. Wald im feindlichen Terrain (-1 Beziehung zum Nachbarn), aber nur wenn kein Holzlager drauf is
            PlotArray1 = []
            PlotArray2 = []
            PlotArray3 = []
            PlotArray4 = []
            PlotArray5 = []
            PlotArray6 = []
            PlotArrayX = []
            
            for iI in range(gc.getNUM_CITY_PLOTS()):
                pLoopPlot = pCity.getCityIndexPlot(iI)
                if pLoopPlot != None and not pLoopPlot.isNone():
                    iPlotFeature = pLoopPlot.getFeatureType()
                    if iPlotFeature in lFeatures:
                        iPlotImprovement = pLoopPlot.getImprovementType()
                        iLoopPlayer = pLoopPlot.getOwner()
                        if pLoopPlot.getBonusType(iLoopPlayer) != iBonusZedern:
                            if iLoopPlayer == iPlayer:
                                if iPlotImprovement == iMine: PlotArray1.append(pLoopPlot)
                                if iPlotImprovement == -1:
                                    if iPlotFeature == iFeatForest: PlotArray1.append(pLoopPlot)
                                    elif iPlotFeature == iFeatSavanna: PlotArray2.append(pLoopPlot)
                                    elif iPlotFeature == iFeatJungle: PlotArray3.append(pLoopPlot)
                                    elif iPlotFeature == iFeatDichterWald: PlotArray5.append(pLoopPlot)
                                elif iPlotImprovement != iHolzLager: PlotArray4.append(pLoopPlot)

                            elif iPlotImprovement != iHolzLager:
                                if iPlotFeature != iFeatDichterWald:
                                    # PAE V: no unit on the plot (Holzraub)
                                    if pLoopPlot.getNumUnits() == 0:
                                        PlotArray6.append(pLoopPlot)

            # Plot wird ausgewaehlt, nach Prioritaet zuerst immer nur Wald checken, wenn keine mehr da, dann Savanne, etc...
            # Wald: Chance: Bronzezeit: 4%, Eisenzeit: 5%, Klassik: 6%
            if len(PlotArray1) > 0:
               iChance = 30 - iCurrentEra * 5
               if myRandom(iChance) == 0: PlotArrayX = PlotArray1
            # Savanne: Bronze: 5%, Eisen: 10%, Klassik: 20%
            elif len(PlotArray2) > 0:
               iChance = 20 - iCurrentEra * 5
               if myRandom(iChance) == 0: PlotArrayX = PlotArray2
            # Dschungel: wie Wald
            elif len(PlotArray3) > 0:
               iChance = 30 - iCurrentEra * 5
               if myRandom(iChance) == 0: PlotArrayX = PlotArray3
            # Bewirt. Feld ohne Holzlager: wie Savanne
            elif len(PlotArray4) > 0:
               iChance = 20 - iCurrentEra * 5
               if myRandom(iChance) == 0: PlotArrayX = PlotArray4
            # Dichter Wald: Bronze: 2%, Eisen: 2.5%, Klassik: 3%
            elif len(PlotArray5) > 0:
               iChance = 60 - iCurrentEra * 10
               if myRandom(iChance) == 0: PlotArrayX = PlotArray5

            # Ausl. Feld 10%, erst wenn es nur mehr 1 Waldfeld gibt (das soll auch bleiben)
            if len(PlotArray1) + len(PlotArray2) + len(PlotArray3) + len(PlotArray4) + len(PlotArray5) < 2:
                PlotArrayX = [] # Feld leeren
                if len(PlotArray6) > 0 and myRandom(10) == 0: PlotArrayX = PlotArray6
                 
            # Gibts einen Waldplot
            if len(PlotArrayX) > 0:
                iPlot = myRandom(len(PlotArrayX))
                pPlot = PlotArrayX[iPlot]
                iPlotPlayer = pPlot.getOwner()
                # Auswirkungen Feature (Wald) entfernen, Holzlager entfernen, Nachbar checken
                # Feature (Wald) entfernen
                # Dichten Wald zu normalen Wald machen
                if pPlot.getFeatureType() == iFeatDichterWald: 
                    pPlot.setFeatureType(iFeatForest,0)
                else:
                    pPlot.setFeatureType(-1,0)
                    # Lumber camp entfernen
                    # Flunky: Holzlager-Felder werden garnicht erst ausgewaehlt
                    #if PlotArrayX[iPlot].getImprovementType() == iHolzLager: PlotArrayX[iPlot].setImprovementType(-1)

                # Meldung
                # Attention: AS2D_CHOP_WOOD is additional defined in XML/Audio/Audio2DScripts.xml   (not used, AS2D_BUILD_FORGE instead)
                if iPlotPlayer == iPlayer:
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_RODUNG_1",(pCity.getName(),0)), 'AS2D_BUILD_FORGE', 2, ',Art/Interface/Buttons/Builds/BuildChopDown.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,7,8', ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)

                elif iPlotPlayer > -1 and iPlotPlayer != gc.getBARBARIAN_PLAYER():
                    pPlotPlayer = gc.getPlayer(iPlotPlayer)
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_RODUNG_2",(pPlotPlayer.getCivilizationShortDescription(0),pPlotPlayer.getCivilizationAdjective(1))), 'AS2D_BUILD_FORGE', 2, ',Art/Interface/Buttons/Builds/BuildChopDown.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,7,8', ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
                    CyInterface().addMessage(iPlotPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_RODUNG_3",(pPlayer.getCivilizationShortDescription(0),0)), 'AS2D_BUILD_FORGE', 2, ',Art/Interface/Buttons/Builds/BuildChopDown.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,7,8', ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
                    pPlotPlayer.AI_changeAttitudeExtra(iPlayer,-1)

    # Feature Waldrodung Ende