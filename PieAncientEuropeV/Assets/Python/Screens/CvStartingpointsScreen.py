## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import string
from time import time
from copy import deepcopy
import CvUtil
from CvWBDesc import CvPlayerDesc
import ScreenInput
import CvScreenEnums
import CvPediaScreen                # base class
import CvWBInterface

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

def clamp(a,x,b):
  return min( max(a,x), b)

class CvStartingPointsScreen( CvPediaScreen.CvPediaScreen ):

  def __init__(self):
    self.bInit = False
    # List of Displayed Scenarios
    self.szenarioFilenames = [
        "Eurasia",
        "Orient",
        "EasternMed",
        "RiseOfEgypt",
        "",
        "EuropeMini",
        "EuropeSmall",
        "EuropeStandard",
        "EuropeLarge",
        "EuropeXL",
        "",
        "LimesGermanicus",
        "WarOfDiadochi",
        "FirstPunicWar", #
        "480BC", # GrecoPersianWars
        "PeloponnesianWarKeinpferd",
        "",
        "XPAE L4000BC 18 CIVs+Barbs",
        "XPAE L4000BC 18 CIVs Hellenic",
        "XM4000BC 18 CIVs+Barbs",
        "XS4000BC 17 CIVs+Barbs",
        "",
        "SchmelzEuro", # Ice Age
        "SchmelzWelt", # Ice Age 2
        ]
    self.szenarioData = None

    self.PEDIA_MAIN_SCREEN_NAME = "StartingPointsScreen"
    self.INTERFACE_ART_INFO = "SCREEN_BG_OPAQUE"

    self.WIDGET_ID = "StartingPointsWidget"
    self.MAP_BACKGROUND_ID = "MapBG"

    self.Y_TITLE = 8
    self.DY_TEXT = 45

    self.X_EXIT = 994
    self.Y_EXIT = 730

    self.X_ITEMS_PANE = 10
    self.Y_ITEMS_PANE = 57
    self.H_ITEMS_PANE = 650
    self.W_ITEMS_PANE = 780

    self.nWidgetCount = 0
    self.nLineCount = 0

    self.subscreens = {
        "rightMenu" : False,
        "leftMenu" : False,
        "map" : False,
        }
    self.ID_OFFSET = 11111
    self.events = {
        "exit": 0,
        "showFirstStart": 1,
        "showInfo": 2,
        "show40DLL": 3,
        "showScenarioPage": 4,
        "showStartingPoints": 5,
        "minimize": 6,
        "selectPlayer": 8,
        "selectSpot": 9,
        "randomSpots": 10,
        "showScenarioList": 11,
        }
    # Pages on right side
    self.pages = {
        "pageFirstStart": 1,
        "pageInfo": 2,
        "page40DLL": 3,
        "pageScenarioDesc": 4,
        "pageStartingPoints": 5,
        "pageScenarioList": 6,
        }
    self.currentPage = 1
    self.szenario = None
    self.wbDesc = None
    self.mapCache = None
    self.iCurrentPlayer = 0

    self.szDropdownPlayer = "PlayerSlot"
    self.szEditBoxKeyName = "EditKeyName"
    self.szEditBoxKeyCivDesc = "EditKeyCivDesc"
    self.szDropdownCiv = "CivType"
    self.szDropdownLeader = "LeaderType"
    self.szDropdownSpot = "StartingPoint"
    self.szEditBoxStartX = "EditStartX"
    self.szEditBoxStartY = "EditStartY"

    self.dice = gc.getGame().getMapRand()
    self.dice.init(int(time()))

  def getScreen(self):
    return CyGInterfaceScreen(self.PEDIA_MAIN_SCREEN_NAME, CvScreenEnums.STARTINGPOINTS_SCREEN)

  def initScreen(self):
    if self.bInit:
        return

    self.bInit = True
    screen = self.getScreen()
    #screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )
    # Bildschirm Auflösung
    self.SCREEN_RES = [screen.getXResolution(), screen.getYResolution()]
    # Abmaße des nicht verdeckbaren Hauptmenüs
    self.MAIN_MENU_RES = [700, 400]
    self.BORDER = 60
    self.HEADLINE_HEIGHT = 55

    # Rechteck für rechtes Menu in der Form [X,Y,W,H]
    self.RIGHT_DIM  = [
      (self.SCREEN_RES[0] + self.MAIN_MENU_RES[0])/2 + 20,
      100,
      (self.SCREEN_RES[0] - self.MAIN_MENU_RES[0])/2 - 40,
      self.SCREEN_RES[1] - 200
      ]

    # Rechteck für linkes Menu in der Form [X,Y,W,H]
    self.LEFT_DIM  = [
        20,
        50,
        (self.SCREEN_RES[0] - self.MAIN_MENU_RES[0])/2 - 140,
        self.SCREEN_RES[1]/2 - 100
        ]

    # Rechteck für Karte [X,Y,W,H]
    self.MAP_DIM  = [
        20,
        self.SCREEN_RES[1]/2,
        (self.SCREEN_RES[0] - self.MAIN_MENU_RES[0])/2 - 40,
        self.SCREEN_RES[1]/2 - 50
        ]

    for x in [
        (self.RIGHT_DIM,450,True),
        (self.LEFT_DIM,250, False),
        (self.MAP_DIM,300, False),
        ]:
      d = x[1] - x[0][2]
      if d > 0:
        x[0][2] += d
        if x[2]:
          x[0][0] -= d

    self.X_EXIT = self.RIGHT_DIM[0] + self.RIGHT_DIM[2] - 30
    self.Y_EXIT = self.RIGHT_DIM[1] + self.RIGHT_DIM[3] - 38

  def setCommonWidgets(self):
    self.EXIT_TEXT = u"<font=4>" + localText.getText("TXT_KEY_PAE_MENU_MINIMIZE", ()).upper() + "</font>"
    self.MENU_TEXT = u"<font=4>" + localText.getText("TXT_KEY_PAE_MENU_HEADLINE", ()).upper() + "</font>"

    # Create a new screen
    screen = self.getScreen()
    screen.setRenderInterfaceOnly(False);
    screen.setScreenGroup(0) # ?
    screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)

    # LEFT MENU
    if self.subscreens["leftMenu"]:
      screen.addDDSGFC(self.getNextWidgetName(), ArtFileMgr.getInterfaceArtInfo("SCREEN_BG_OPAQUE").getPath(),
      self.LEFT_DIM[0], self.LEFT_DIM[1], self.LEFT_DIM[2], self.LEFT_DIM[3],
      WidgetTypes.WIDGET_GENERAL, -1, -1 )
      screen.addPanel(self.getNextWidgetName(), u"", u"", True, False,
      self.LEFT_DIM[0], self.LEFT_DIM[1]+self.LEFT_DIM[3] - self.HEADLINE_HEIGHT, self.LEFT_DIM[2], 55,
      PanelStyles.PANEL_STYLE_BOTTOMBAR )

    if True:
      minimizeFlag = 1
      if self.subscreens["leftMenu"]:
        minimizeFlag = -1
      screen.addPanel(self.getNextWidgetName(), u"", u"", True, False,
      self.LEFT_DIM[0], self.LEFT_DIM[1], self.LEFT_DIM[2], self.HEADLINE_HEIGHT,
      PanelStyles.PANEL_STYLE_TOPBAR )
      screen.setText(self.getNextWidgetName(), "Background", self.MENU_TEXT, CvUtil.FONT_CENTER_JUSTIFY,
          self.LEFT_DIM[0]+ self.LEFT_DIM[2]/2, self.LEFT_DIM[1] + self.Y_TITLE, 0, FontTypes.TITLE_FONT,
          WidgetTypes.WIDGET_PEDIA_DESCRIPTION_NO_HELP, self.ID_OFFSET+self.events["minimize"], minimizeFlag)

    if self.subscreens["leftMenu"]:
      self.fillLeftMenu()


    # RIGHT MENU
    if self.subscreens["rightMenu"]:
      # Set background
      screen.addDDSGFC(self.getNextWidgetName(), ArtFileMgr.getInterfaceArtInfo("SCREEN_BG_OPAQUE").getPath(),
      self.RIGHT_DIM[0], self.RIGHT_DIM[1], self.RIGHT_DIM[2], self.RIGHT_DIM[3],
      WidgetTypes.WIDGET_GENERAL, -1, -1 )
      screen.addPanel(self.getNextWidgetName(), u"", u"", True, False,
      self.RIGHT_DIM[0], self.RIGHT_DIM[1], self.RIGHT_DIM[2], self.HEADLINE_HEIGHT,
      PanelStyles.PANEL_STYLE_TOPBAR )
      screen.addPanel(self.getNextWidgetName(), u"", u"", True, False,
      self.RIGHT_DIM[0], self.RIGHT_DIM[1]+self.RIGHT_DIM[3] - self.HEADLINE_HEIGHT, self.RIGHT_DIM[2], 55,
      PanelStyles.PANEL_STYLE_BOTTOMBAR )
      #screen.setDimensions(screen.centerX(0), screen.centerY(0), self.RIGHT_DIM[2], self.RIGHT_DIM[3])

      # Exit button
      #screen.setText(self.getNextWidgetName(), "Background", self.EXIT_TEXT, CvUtil.FONT_RIGHT_JUSTIFY, self.X_EXIT, self.Y_EXIT, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1)
      # General-Widgets werden nicht ausgeführt, da Event nicht an Handler weiter gereicht wird.
      #screen.setText(self.getNextWidgetName(), "Background", self.EXIT_TEXT, CvUtil.FONT_RIGHT_JUSTIFY, self.X_EXIT, self.Y_EXIT, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, self.ID_OFFSET, -1)

      # Hier habe ich ein Widget mit zwei Argumenten, Funktionen, die ich exploiten kann.
      # Durch den Umweg ueber die DLL klappt das auch im Startbildschirm.
      screen.setText(self.getNextWidgetName(), "Background", self.EXIT_TEXT, CvUtil.FONT_RIGHT_JUSTIFY,
          self.X_EXIT, self.Y_EXIT, 0, FontTypes.TITLE_FONT,
          WidgetTypes.WIDGET_PEDIA_DESCRIPTION_NO_HELP, self.ID_OFFSET+self.events["minimize"], 1)

      if self.currentPage == self.pages["pageScenarioDesc"]:
        backText = u"<font=4>" + localText.getText("TXT_KEY_PEDIA_SCREEN_BACK", ()).upper() + "</font>"
        screen.setText(self.getNextWidgetName(), "Background", backText, CvUtil.FONT_LEFT_JUSTIFY,
            self.RIGHT_DIM[0]+20, self.Y_EXIT, 0, FontTypes.TITLE_FONT,
            WidgetTypes.WIDGET_PEDIA_DESCRIPTION_NO_HELP, self.ID_OFFSET+self.events["showScenarioList"], -1)

      self.fillRightMenu()

    # MAP MENU
    if self.subscreens["map"]:
      """
      screen.addDDSGFC(self.getNextWidgetName(), ArtFileMgr.getInterfaceArtInfo("SCREEN_BG_OPAQUE").getPath(),
      self.MAP_DIM[0], self.MAP_DIM[1], self.MAP_DIM[2], self.MAP_DIM[3],
      WidgetTypes.WIDGET_GENERAL, -1, -1 )
      """

      self.fillMap()

    # Header...
    """
    szHeader = u"<font=4b>" +localText.getText("TXT_KEY_WIDGET_FOO1", ()).upper() + u"</font>"
    szHeaderId = self.getNextWidgetName()
    screen.setLabel(szHeaderId, "Background", szHeader, CvUtil.FONT_CENTER_JUSTIFY, self.RIGHT_DIM[0], self.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_PEDIA_DESCRIPTION, -1, -1)
    self.panelName = self.getNextWidgetName()
    screen.addPanel(self.panelName, "", "", false, false,
    self.X_ITEMS_PANE, self.Y_ITEMS_PANE, self.W_ITEMS_PANE, self.H_ITEMS_PANE, PanelStyles.PANEL_STYLE_BLUE50)

    """

  def fillLeftMenu(self):
    screen = self.getScreen()
    textPos = [self.LEFT_DIM[0] + 20, self.LEFT_DIM[1] + self.HEADLINE_HEIGHT + 20]
    textFirstStart = u"<font=3>" +localText.getText("TXT_KEY_PAE_MENU_FIRST_START", ()) + u"</font>"
    textInfo = u"<font=3>" +localText.getText("TXT_KEY_PAE_MENU_INFO", ()) + u"</font>"
    text40DLL = u"<font=3>" +localText.getText("TXT_KEY_PAE_MENU_40DLL", ()) + u"</font>"
    textScenarioList = u"<font=3>" +localText.getText("TXT_KEY_PAE_MENU_SCENARIO_LIST", ()) + u"</font>"
    textScenario = u"<font=3>" +localText.getText("TXT_KEY_PAE_MENU_SCENARIO", ()) + u"</font>"
    textStartingPoints = u"<font=3>" +localText.getText("TXT_KEY_PAE_MENU_STARTING_POINTS", ()) + u"</font>"
    screen.setText(self.getNextWidgetName(), "", textFirstStart, CvUtil.FONT_LEFT_JUSTIFY,
        textPos[0], textPos[1], 0, FontTypes.TITLE_FONT,
        WidgetTypes.WIDGET_PEDIA_DESCRIPTION_NO_HELP, self.ID_OFFSET+self.events["showFirstStart"], -1)

    textPos[1] += 30
    screen.setText(self.getNextWidgetName(), "", textInfo, CvUtil.FONT_LEFT_JUSTIFY,
        textPos[0], textPos[1], 0, FontTypes.TITLE_FONT,
        WidgetTypes.WIDGET_PEDIA_DESCRIPTION_NO_HELP, self.ID_OFFSET+self.events["showInfo"], -1)

    textPos[1] += 30
    screen.setText(self.getNextWidgetName(), "", text40DLL, CvUtil.FONT_LEFT_JUSTIFY,
        textPos[0], textPos[1], 0, FontTypes.TITLE_FONT,
        WidgetTypes.WIDGET_PEDIA_DESCRIPTION_NO_HELP, self.ID_OFFSET+self.events["show40DLL"], -1)

    textPos[1] += 30
    screen.setText(self.getNextWidgetName(), "", textScenarioList, CvUtil.FONT_LEFT_JUSTIFY,
        textPos[0], textPos[1], 0, FontTypes.TITLE_FONT,
        WidgetTypes.WIDGET_PEDIA_DESCRIPTION_NO_HELP, self.ID_OFFSET+self.events["showScenarioList"], -1)

    if self.szenario != None:
      textPos[1] += 30
      screen.setText(self.getNextWidgetName(), "", textScenario, CvUtil.FONT_LEFT_JUSTIFY,
          textPos[0], textPos[1], 0, FontTypes.TITLE_FONT,
          WidgetTypes.WIDGET_PEDIA_DESCRIPTION_NO_HELP, self.ID_OFFSET+self.events["showScenarioPage"], -1)

      if self.bScenarioEdit:
        textPos[1] += 30
        screen.setText(self.getNextWidgetName(), "", textStartingPoints, CvUtil.FONT_LEFT_JUSTIFY,
            textPos[0], textPos[1], 0, FontTypes.TITLE_FONT,
            WidgetTypes.WIDGET_PEDIA_DESCRIPTION_NO_HELP, self.ID_OFFSET+self.events["showStartingPoints"], -1)



  def fillRightMenu(self):
    screen = self.getScreen()
    textPos = [self.RIGHT_DIM[0] + 20, self.RIGHT_DIM[1] + self.HEADLINE_HEIGHT + 20]
    if self.currentPage == self.pages["pageFirstStart"]:
      szTitle = localText.getText("TXT_KEY_PAE_MENU_FIRST_START", ())
      screen.setLabel(self.getNextWidgetName(), "Background", szTitle, CvUtil.FONT_CENTER_JUSTIFY,
          self.RIGHT_DIM[0]+ self.RIGHT_DIM[2]/2, self.RIGHT_DIM[1] + self.Y_TITLE, 0, FontTypes.TITLE_FONT,
          WidgetTypes.WIDGET_GENERAL, -1, -1)

      szSpecialText =  "TXT_KEY_PAE_INFO_FIRST_START"
      szSpecialText = localText.getText(szSpecialText,())
      skippedHeight = (textPos[1] - self.RIGHT_DIM[1]) + self.HEADLINE_HEIGHT
      screen.addMultilineText(self.getNextWidgetName(), szSpecialText,
          textPos[0], textPos[1], self.RIGHT_DIM[2] - 20, self.RIGHT_DIM[3] - skippedHeight - 20,
          WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

    elif self.currentPage == self.pages["pageInfo"]:
      szTitle = localText.getText("TXT_KEY_PAE_MENU_INFO", ())
      screen.setLabel(self.getNextWidgetName(), "Background", szTitle, CvUtil.FONT_CENTER_JUSTIFY,
          self.RIGHT_DIM[0]+ self.RIGHT_DIM[2]/2, self.RIGHT_DIM[1] + self.Y_TITLE, 0, FontTypes.TITLE_FONT,
          WidgetTypes.WIDGET_GENERAL, -1, -1)

      szSpecialText =  "TXT_KEY_PAE_INFO_GENERAL"
      szSpecialText = localText.getText(szSpecialText,())
      skippedHeight = (textPos[1] - self.RIGHT_DIM[1]) + self.HEADLINE_HEIGHT
      screen.addMultilineText(self.getNextWidgetName(), szSpecialText,
          textPos[0], textPos[1], self.RIGHT_DIM[2] - 20, self.RIGHT_DIM[3] - skippedHeight - 20,
          WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

    elif self.currentPage == self.pages["page40DLL"]:
      szTitle = localText.getText("TXT_KEY_PAE_MENU_40DLL", ())
      screen.setLabel(self.getNextWidgetName(), "Background", szTitle, CvUtil.FONT_CENTER_JUSTIFY,
          self.RIGHT_DIM[0]+ self.RIGHT_DIM[2]/2, self.RIGHT_DIM[1] + self.Y_TITLE, 0, FontTypes.TITLE_FONT,
          WidgetTypes.WIDGET_GENERAL, -1, -1)

      szSpecialText =  "TXT_KEY_PAE_INFO_40DLL"
      szSpecialText = localText.getText(szSpecialText,())
      skippedHeight = (textPos[1] - self.RIGHT_DIM[1]) + self.HEADLINE_HEIGHT
      screen.addMultilineText(self.getNextWidgetName(), szSpecialText,
          textPos[0], textPos[1], self.RIGHT_DIM[2] - 20, self.RIGHT_DIM[3] - skippedHeight - 20,
          WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

    elif self.currentPage == self.pages["pageScenarioDesc"]:
      if self.szenario == None:
        screen.setLabel(self.getNextWidgetName(), "", "TXT_KEY_PAE_MENU_NO_SCENARIO_DATA", CvUtil.FONT_LEFT_JUSTIFY,
            textPos[0], textPos[1], 0, FontTypes.TITLE_FONT,
            WidgetTypes.WIDGET_GENERAL, -1, -1)
      else:
        self.drawScenarioDesc(self.szenario)
    elif self.currentPage == self.pages["pageScenarioList"]:
     self.drawScenarioList()

    elif self.currentPage == self.pages["pageStartingPoints"] and self.szenario != None:
      if self.szenario.get("Title") != None:
        szenarioTitle = localText.getText(self.szenario["Title"], ())
        screen.setLabel(self.getNextWidgetName(), "Background", szenarioTitle, CvUtil.FONT_CENTER_JUSTIFY,
            self.RIGHT_DIM[0]+ self.RIGHT_DIM[2]/2, self.RIGHT_DIM[1] + self.Y_TITLE, 0, FontTypes.TITLE_FONT,
            WidgetTypes.WIDGET_GENERAL, -1, -1)
      iPanelWidth = 35*6

      # Dropdownmenu von allen Civ Slots
      screen.setLabel(self.getNextWidgetName(), "",
          "<font=3b>" + localText.getText("TXT_KEY_MAIN_MENU_PLAYERS", ()) + "</font>",
          CvUtil.FONT_LEFT_JUSTIFY,
          textPos[0], textPos[1], 0, FontTypes.TITLE_FONT,
          WidgetTypes.WIDGET_GENERAL, -1, -1)
      textPos[1] += 30

      currentPlayer = None
      screen.addDropDownBoxGFC(self.szDropdownPlayer, textPos[0], textPos[1], iPanelWidth,
          WidgetTypes.WIDGET_PEDIA_DESCRIPTION_NO_HELP, self.ID_OFFSET+self.events["selectPlayer"], 1,
          FontTypes.GAME_FONT)
      for i in range( len(CvWBInterface.WBDesc.playersDesc) ):
        pl = CvWBInterface.WBDesc.playersDesc[i]
        if pl.civType == "CIVILIZATION_BARBARIAN":
          continue

        plName = ("%2d %s" % (i, localText.getText( self.getPlayerName(pl) ,()) ))

        if (i == self.iCurrentPlayer):
          screen.addPullDownString(self.szDropdownPlayer, plName, i, i, True )
          currentPl = pl
        else:
          screen.addPullDownString(self.szDropdownPlayer, plName, i, i, False )

      screen.setButtonGFC( self.getNextWidgetName(), localText.getText("TXT_KEY_PAE_MENU_SELECT",()), "",
          textPos[0] + iPanelWidth + 10, textPos[1], iPanelWidth, 30,
          WidgetTypes.WIDGET_PEDIA_DESCRIPTION_NO_HELP, self.ID_OFFSET+self.events["selectPlayer"], -1,
          ButtonStyles.BUTTON_STYLE_STANDARD )
      textPos[1] += 60

      if currentPl is not None:
        iCurrentLeader = gc.getInfoTypeForString( currentPl.leaderType )
        iCurrentCiv = gc.getInfoTypeForString( currentPl.civType )
      else:
        iCurrentLeader = -1
        iCurrentCiv = -1
      # leader = localText.getTextKey( gc.getLeaderHeadInfo(plLeader).getTextKey(), ())

      screen.setLabel(self.getNextWidgetName(), "",
          "<font=3b>" + localText.getText("TXT_KEY_PAE_MENU_SELECTED_PLAYER", ()) + "</font>",
          CvUtil.FONT_LEFT_JUSTIFY,
          textPos[0], textPos[1], 0, FontTypes.TITLE_FONT,
          WidgetTypes.WIDGET_GENERAL, -1, -1)
      textPos[1] += 30

      # Information about current Player
      if currentPl is not None:
        playerName = localText.getText( self.getPlayerName(currentPl) ,())
        screen.setLabel(self.getNextWidgetName(), "", localText.getText("TXT_KEY_MAIN_MENU_PLAYER", ())+":", CvUtil.FONT_RIGHT_JUSTIFY,
            textPos[0] + iPanelWidth/2, textPos[1], 0, FontTypes.TITLE_FONT,
            WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.setLabel(self.getNextWidgetName(), "", playerName, CvUtil.FONT_LEFT_JUSTIFY,
            textPos[0] + iPanelWidth/2 + 10, textPos[1], 0, FontTypes.TITLE_FONT,
            WidgetTypes.WIDGET_GENERAL, -1, -1)
        textPos[1] += 30

        screen.setLabel(self.getNextWidgetName(), "", localText.getText("TXT_KEY_PAE_NATION", ())+":", CvUtil.FONT_RIGHT_JUSTIFY,
            textPos[0] + iPanelWidth/2, textPos[1], 0, FontTypes.TITLE_FONT,
            WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.setLabel(self.getNextWidgetName(), "", localText.getText( self.getPlayerCiv(currentPl) ,()), CvUtil.FONT_LEFT_JUSTIFY,
            textPos[0] + iPanelWidth/2 + 10, textPos[1], 0, FontTypes.TITLE_FONT,
            WidgetTypes.WIDGET_GENERAL, -1, -1)
        textPos[1] += 30


        """
        screen.setLabel(self.getNextWidgetName(), "", "Player Key", CvUtil.FONT_LEFT_JUSTIFY,
            textPos[0], textPos[1], 0, FontTypes.TITLE_FONT,
            WidgetTypes.WIDGET_GENERAL, -1, -1)
        textPos[1] += 20

        #addEditBoxGFC (STRING szName, INT iX, INT iY, INT iWidth, INT iHeight, WidgetType eWidgetType, INT iData1, INT iData2, FontType eFont)
        #setEditBoxMaxCharCount (STRING szName, INT maxCharCount, INT preferredCharCount)
        #setEditBoxString (STRING szName, STRING szString)
        #setEditBoxTextColor (STRING szName, NiColorA kColor)
        screen.addEditBoxGFC( self.szEditBoxKeyName,
            textPos[0], textPos[1], iPanelWidth, 30,
            WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
        screen.setEditBoxMaxCharCount( self.szEditBoxKeyName, 100, 20 )
        screen.setEditBoxString ( self.szEditBoxKeyName, str(currentPl.szLeaderName) )
        textPos[1] += 40

        screen.setLabel(self.getNextWidgetName(), "", "Civ Description Key", CvUtil.FONT_LEFT_JUSTIFY,
            textPos[0], textPos[1], 0, FontTypes.TITLE_FONT,
            WidgetTypes.WIDGET_GENERAL, -1, -1)
        textPos[1] += 20

        screen.addEditBoxGFC( self.szEditBoxKeyCivDesc,
            textPos[0], textPos[1], iPanelWidth, 30,
            WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
        screen.setEditBoxMaxCharCount( self.szEditBoxKeyCivDesc, 100, 20 )
        screen.setEditBoxString ( self.szEditBoxKeyCivDesc, str(currentPl.szCivDesc) )
        textPos[1] += 40
        """

        """
        # Dropdownmenu für Zivilisation für gewählten Slot
        screen.setLabel(self.getNextWidgetName(), "", "Civilization", CvUtil.FONT_LEFT_JUSTIFY,
            textPos[0], textPos[1], 0, FontTypes.TITLE_FONT,
            WidgetTypes.WIDGET_GENERAL, -1, -1)
        textPos[1] += 20

        screen.addDropDownBoxGFC(self.szDropdownCiv, textPos[0], textPos[1], iPanelWidth,
            WidgetTypes.WIDGET_GENERAL, -1, -1,
            FontTypes.GAME_FONT)
        for i in range( gc.getNumCivilizationInfos() ):
          civ = localText.getText( str(gc.getCivilizationInfo(i).getTextKey()), ())
          if (i == iCurrentCiv):
            screen.addPullDownString(self.szDropdownCiv, civ, i, i, True )
          else:
            screen.addPullDownString(self.szDropdownCiv, civ, i, i, False )
        textPos[1] += 40

        # Dropdownmenu für Anführer für gewählten Slot
        screen.setLabel(self.getNextWidgetName(), "", "Leader", CvUtil.FONT_LEFT_JUSTIFY,
            textPos[0], textPos[1], 0, FontTypes.TITLE_FONT,
            WidgetTypes.WIDGET_GENERAL, -1, -1)
        textPos[1] += 20

        screen.addDropDownBoxGFC(self.szDropdownLeader, textPos[0], textPos[1], iPanelWidth,
            WidgetTypes.WIDGET_GENERAL, -1, -1,
            FontTypes.GAME_FONT)
        for i in range( gc.getNumLeaderHeadInfos() ):
          leader = localText.getText( str(gc.getLeaderHeadInfo(i).getTextKey()), ())
          if (i == iCurrentLeader):
            screen.addPullDownString(self.szDropdownLeader, leader, i, i, True )
          else:
            screen.addPullDownString(self.szDropdownLeader, leader, i, i, False )
        textPos[1] += 40
        """

        # Start Plot
        screen.setLabel(self.getNextWidgetName(), "", "Start Plot", CvUtil.FONT_RIGHT_JUSTIFY,
            textPos[0] + iPanelWidth/2, textPos[1], 0, FontTypes.TITLE_FONT,
            WidgetTypes.WIDGET_GENERAL, -1, -1)

        screen.addEditBoxGFC( self.szEditBoxStartX,
            textPos[0] + iPanelWidth/2 + 10, textPos[1], iPanelWidth/2, 30,
            WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
        screen.setEditBoxMaxCharCount( self.szEditBoxStartX, 10, 10 )
        screen.setEditBoxString ( self.szEditBoxStartX, str(currentPl.iStartingX) )

        screen.addEditBoxGFC( self.szEditBoxStartY,
            textPos[0] + iPanelWidth + 20, textPos[1], iPanelWidth/2, 30,
            WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
        screen.setEditBoxMaxCharCount( self.szEditBoxStartY, 10, 10 )
        screen.setEditBoxString ( self.szEditBoxStartY, str(currentPl.iStartingY) )
        textPos[1] += 60


      screen.setLabel(self.getNextWidgetName(), "",
          "<font=3b>" + localText.getText("TXT_KEY_PAE_MENU_ASSIGN_SPOT", (playerName,)) + "</font>",
          CvUtil.FONT_LEFT_JUSTIFY,
          textPos[0], textPos[1], 0, FontTypes.TITLE_FONT,
          WidgetTypes.WIDGET_GENERAL, -1, -1)
      textPos[1] += 30

      # List of unused starting slots
      screen.deleteWidget(self.szDropdownSpot)
      screen.addDropDownBoxGFC(self.szDropdownSpot, textPos[0], textPos[1], iPanelWidth * 2,
          WidgetTypes.WIDGET_PEDIA_DESCRIPTION_NO_HELP, self.ID_OFFSET+self.events["selectSpot"], 1,
          FontTypes.GAME_FONT)

      # Check if Player already owns a City. This nations can not be changed anymore.
      # The evaluation was sourced out into analyseLoadedScenario()
      bAlreadySettled = False
      if currentPl is not None and currentPl.bLocked:
        bAlreadySettled = True

      if bAlreadySettled:
        screen.addPullDownString( self.szDropdownSpot, localText.getText("TXT_KEY_PAE_ALREADY_SETTLED",()), -1, -1, True )
      else:
        bEmpty = True
        iGroup = 0
        for civ in self.szenario.get("StartingPoints",{}).values():
          iSpot = 0
          for spot in civ:
            if spot.get("PlayerID") in [-1, self.iCurrentPlayer]:
              spotName = localText.getText(str(spot.get("StartName", spot.get("LeaderName", ""))), ())
              if spotName == "":
                iCiv = gc.getInfoTypeForString( spot.get("Civilization","NONE") )
                if iCiv > -1:
                  civInfo = gc.getCivilizationInfo(iCiv)
                  #spotName = localText.getText(str(civInfo.getTextKey()), ())
                  spotName = civInfo.getAdjective(3) + u" " + localText.getText("TXT_KEY_PAE_SPOT", ())
                else:
                  spotName = localText.getText("TXT_KEY_PAE_UNNAMED_SPOT", ())
                # Append number for generic name.
                spotName = "%s %d" %(spotName, (iSpot+1))
                spotName[0].upper()

              if spot.get("PlayerID") == -1:
                screen.addPullDownString( self.szDropdownSpot, spotName, iGroup, iSpot, False )
                bEmpty = False
              elif spot.get("PlayerID") == self.iCurrentPlayer:
                screen.addPullDownString( self.szDropdownSpot, spotName, iGroup, iSpot, True )
                bEmpty = False
            iSpot += 1
          iGroup += 1

        if bEmpty:
          screen.addPullDownString( self.szDropdownSpot, localText.getText("TXT_KEY_PAE_NO_FREE_SP",()), -1, -1, True )
        screen.addPullDownString( self.szDropdownSpot, localText.getText("TXT_KEY_PAE_CLEAR_SPOT",()), -2, -2, False )

      textPos[1] += 30

      screen.setButtonGFC( self.getNextWidgetName(), localText.getText("TXT_KEY_PAE_MENU_APPLY",()) , "",
          textPos[0], textPos[1], iPanelWidth, 30,
          WidgetTypes.WIDGET_PEDIA_DESCRIPTION_NO_HELP, self.ID_OFFSET+self.events["selectSpot"], -1,
          ButtonStyles.BUTTON_STYLE_STANDARD )
      """
      screen.setText(self.getNextWidgetName(), "", "Apply", CvUtil.FONT_LEFT_JUSTIFY,
          textPos[0], textPos[1], 0, FontTypes.TITLE_FONT,
          WidgetTypes.WIDGET_PEDIA_DESCRIPTION_NO_HELP, self.ID_OFFSET+self.events["selectSpot"], -1)
      """
      textPos[1] += 60

      screen.setButtonGFC( self.getNextWidgetName(), localText.getText("TXT_KEY_PAE_MENU_RANDOM1",()), "",
          textPos[0], textPos[1], iPanelWidth, 30,
          WidgetTypes.WIDGET_PEDIA_DESCRIPTION_NO_HELP, self.ID_OFFSET+self.events["randomSpots"], 0,
          ButtonStyles.BUTTON_STYLE_STANDARD )
      screen.setButtonGFC( self.getNextWidgetName(), localText.getText("TXT_KEY_PAE_MENU_RANDOM2",()), "",
          textPos[0] + iPanelWidth, textPos[1] , iPanelWidth, 30,
          WidgetTypes.WIDGET_PEDIA_DESCRIPTION_NO_HELP, self.ID_OFFSET+self.events["randomSpots"], 1,
          ButtonStyles.BUTTON_STYLE_STANDARD )
      textPos[1] += 60

      skippedHeight = (textPos[1] - self.RIGHT_DIM[1]) + self.HEADLINE_HEIGHT
      screen.addMultilineText(self.getNextWidgetName(), localText.getText("TXT_KEY_PAE_INFO_STARTINGPOINTS",()),
          textPos[0], textPos[1], self.RIGHT_DIM[2] - 20, self.RIGHT_DIM[3] - skippedHeight - 20,
          WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

  def drawScenarioDesc(self, szenario):
    screen = self.getScreen()
    textPos = [self.RIGHT_DIM[0] + 20, self.RIGHT_DIM[1] + self.HEADLINE_HEIGHT + 20]
    if szenario.get("Title") != None:
      szenarioTitle = localText.getText(szenario["Title"], ())
      screen.setLabel(self.getNextWidgetName(), "Background", szenarioTitle, CvUtil.FONT_CENTER_JUSTIFY,
          self.RIGHT_DIM[0]+ self.RIGHT_DIM[2]/2, self.RIGHT_DIM[1] + self.Y_TITLE, 0, FontTypes.TITLE_FONT,
          WidgetTypes.WIDGET_GENERAL, -1, -1)
    if szenario.get("Image","") != "":
      screen.addDDSGFC(self.getNextWidgetName(), szenario["Image"],
          textPos[0], textPos[1] - 40 , self.RIGHT_DIM[2] - 40, 300,
          WidgetTypes.WIDGET_GENERAL, -1, -1 )
      textPos[1] += 300
    skippedHeight = (textPos[1] - self.RIGHT_DIM[1]) + self.HEADLINE_HEIGHT
    szenarioText = localText.getText(szenario["Description"], ())
    screen.addMultilineText(self.getNextWidgetName(), szenarioText,
        textPos[0], textPos[1], self.RIGHT_DIM[2] - 20, self.RIGHT_DIM[3] - skippedHeight - 20,
        WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

  def drawScenarioList(self):
    screen = self.getScreen()

    if self.szenarioData == None:
      self.szenarioData = []
      for szenarioFilename in self.szenarioFilenames:
        bSkipStartingPoints = True
        bMatchingWBFile = False # ( CvWBInterface.WBDesc != None and CvWBInterface.WBDesc.plotDesc[0].szScriptData == szenarioFilename)
        szenario = CvUtil.ReadScenarioDescription(szenarioFilename+".xml",
            bSkipStartingPoints or bMatchingWBFile )
        if( len(str(szenario.get("description","")).strip()) == 0 ):
          szenario["description"] = "TXT_KEY_PAE_MENU_NO_SCENARIO_DATA"
        self.szenarioData.append(szenario)

    szTitle = localText.getText("TXT_KEY_PAE_MENU_SCENARIO_LIST", ())
    screen.setLabel(self.getNextWidgetName(), "Background", szTitle, CvUtil.FONT_CENTER_JUSTIFY,
        self.RIGHT_DIM[0]+ self.RIGHT_DIM[2]/2, self.RIGHT_DIM[1] + self.Y_TITLE, 0, FontTypes.TITLE_FONT,
        WidgetTypes.WIDGET_GENERAL, -1, -1)

    # Use container panel to get scrollbars if required.
    szContainer = self.getNextWidgetName()
    """
    # Hm, nicht anklickbar...
    screen.addTableControlGFC(szContainer, 1,
        self.RIGHT_DIM[0], self.RIGHT_DIM[1] + self.HEADLINE_HEIGHT,
        self.RIGHT_DIM[2], self.RIGHT_DIM[3] - 2 * self.HEADLINE_HEIGHT,
        False, False, 24, 24, TableStyles.TABLE_STYLE_EMPTY)
    """
    screen.addScrollPanel (szContainer, u"",
        self.RIGHT_DIM[0], self.RIGHT_DIM[1] + self.HEADLINE_HEIGHT,
        self.RIGHT_DIM[2], self.RIGHT_DIM[3] - 2 * self.HEADLINE_HEIGHT,
        PanelStyles.PANEL_STYLE_EXTERNAL )
    textPos = [self.RIGHT_DIM[0] + 20, self.RIGHT_DIM[1] + self.HEADLINE_HEIGHT + 20]
    textHeight = 30

    # Ich würde die Szenariotitel gerne in eine Scrollbox packen,
    # aber das gelingt mir nicht so, dass die Titel noch anklickbar sind.
    # Daher reduziere ich die benutzte Höhe per Hand…
    bSmallResolution = ( self.SCREEN_RES[1] < 1080 )
    if bSmallResolution:
      textHeight = 20

    for i in xrange(len(self.szenarioData)):
      iRow = screen.appendTableRow(szContainer)
      szenarioTitle = localText.getText(self.szenarioData[i].get("Title",""), ())
      if len(szenarioTitle) == 0:
        if bSmallResolution and False:
          continue
        else:
          szenarioTitle = str(self.szenarioFilenames[i])
      screen.setText(self.getNextWidgetName(), szContainer, szenarioTitle, CvUtil.FONT_LEFT_JUSTIFY,
          textPos[0], textPos[1], 0, FontTypes.TITLE_FONT,
          WidgetTypes.WIDGET_PEDIA_DESCRIPTION_NO_HELP, self.ID_OFFSET+self.events["showScenarioPage"], i)
      textPos[1] += textHeight
      """
      szenarioTitle = "[LINK=CONCEPT_MOVEMENT]"+szenarioTitle+"[\LINK]"
      screen.setTableText(szContainer, 0, iRow, szenarioTitle, None,
          WidgetTypes.WIDGET_PEDIA_DESCRIPTION_NO_HELP, self.ID_OFFSET+self.events["showScenarioPage"], i,
          CvUtil.FONT_LEFT_JUSTIFY)
      """

  def fillMap(self):
    if self.mapCache == None:
      return

    self.clearAllLines()

    screen = self.getScreen()
    iGridW = len(self.mapCache)
    iGridH = len(self.mapCache[0])

    # Verbrauchte Pixel pro Plot hängen von den Kartendimensionen ab.
    plotWidth = min(8, int(self.MAP_DIM[2]/iGridW))
    plotWidth = min(plotWidth, int(self.MAP_DIM[3]/iGridH))
    plotWidth = max(plotWidth,1)

    MAP_MARGIN = 20
    X_MAP = self.MAP_DIM[0] + MAP_MARGIN
    Y_MAP = self.MAP_DIM[1] + MAP_MARGIN
    W_MAP = plotWidth * iGridW
    H_MAP = plotWidth * iGridH
    self.MAP_DIM.append( W_MAP + 2 * MAP_MARGIN ) # 4
    self.MAP_DIM.append( H_MAP + 2 * MAP_MARGIN ) # 5

    screen.addDrawControl(self.MAP_BACKGROUND_ID, ArtFileMgr.getInterfaceArtInfo("SCREEN_BG_OPAQUE").getPath(),
        self.MAP_DIM[0], self.MAP_DIM[1], self.MAP_DIM[4], self.MAP_DIM[5],
        WidgetTypes.WIDGET_GENERAL, -1, -1 )

    # Overlay with starting positions
    for iPl in xrange(len(CvWBInterface.WBDesc.playersDesc)):
      pl = CvWBInterface.WBDesc.playersDesc[iPl]
      iPlayerColor = gc.getInfoTypeForString(pl.color)
      if iPlayerColor > -1 :
        color = gc.getPlayerColorInfo(iPlayerColor).getColorTypePrimary()
        color2 = gc.getPlayerColorInfo(iPlayerColor).getColorTypeSecondary()
      else:
        color = gc.getInfoTypeForString("COLOR_BLACK")
        color2 = gc.getInfoTypeForString("COLOR_BLACK")

      if pl.iStartingX != -1 and pl.iStartingY != -1:
        # Karte ist gespiegelt, daher muss PosY geflippt werden.
        posX = plotWidth * pl.iStartingX + MAP_MARGIN
        posY = plotWidth * (iGridH-1 - pl.iStartingY) + MAP_MARGIN
        x = clamp( 0, pl.iStartingX, iGridW)
        y = clamp( 0, iGridH-1-pl.iStartingY, iGridH)
        if iPl == self.iCurrentPlayer:
          b = 2
        else:
          b = 1
        for i in range( max(0,x-b), min(x+b+1,iGridW)):
          for j in range(max(0,y-b),min(y+b+1,iGridH)):
            self.mapCache[i][j][1] = color
        self.mapCache[x][y][1] = color2


    # Draw color information
    for iX in xrange(iGridW):
      posX = plotWidth * iX + MAP_MARGIN
      prevColor = -1
      sameColor = 1
      for iY in xrange(iGridH):
        posY = plotWidth * iY + MAP_MARGIN
        currColor = self.mapCache[iX][iY][1] #overlay color
        if currColor == -1:
          currColor = self.mapCache[iX][iY][0] #base color

        if prevColor == currColor:
          sameColor += 1
        else:
          # Flush previous color
          if prevColor != -1:
            for l in xrange(plotWidth):
              screen.addLineGFC(self.MAP_BACKGROUND_ID, self.getNextLineName(),
                  posX + l, posY - sameColor*plotWidth,
                  posX + l, posY - 1, prevColor)

          prevColor = currColor
          sameColor = 1

      # Flush last color (at image bottom )
      for l in xrange(plotWidth):
        screen.addLineGFC(self.MAP_BACKGROUND_ID, self.getNextLineName(),
            posX + l, posY - (sameColor-1)*plotWidth ,
            posX + l, posY - 1 + plotWidth, prevColor)

    # Draw river information
    colorRiver = gc.getInfoTypeForString("COLOR_PLAYER_LIGHT_BLUE")
    for iX in xrange(iGridW):
      posX = plotWidth * iX + MAP_MARGIN + plotWidth - 1
      for iY in xrange(iGridH):
        posY = plotWidth * iY + MAP_MARGIN + plotWidth - 1
        mapIndex = iX * iGridH + (iGridH-1-iY)
        pl = CvWBInterface.WBDesc.plotDesc[mapIndex]
        if pl.isNOfRiver:
          screen.addLineGFC(self.MAP_BACKGROUND_ID, self.getNextLineName(),
              posX - plotWidth, posY,
              posX , posY, colorRiver)
        if pl.isWOfRiver:
          screen.addLineGFC(self.MAP_BACKGROUND_ID, self.getNextLineName(),
              posX, posY - plotWidth,
              posX, posY, colorRiver)


  # Screen construction function
  def showScreen(self, bForce=False):
    self.initScreen()

    self.deleteAllWidgets()
    screen = self.getScreen()

    bNotActive = (not screen.isActive())
    if bNotActive or bForce:
      self.setCommonWidgets()

  # returns a unique ID for a widget in this screen
  def getNextWidgetName(self):
    szName = self.WIDGET_ID + str(self.nWidgetCount)
    self.nWidgetCount += 1
    return szName

  def deleteAllWidgets(self):
    screen = self.getScreen()
    iNumWidgets = self.nWidgetCount
    self.nWidgetCount = 0
    for i in range(iNumWidgets):
      screen.deleteWidget(self.getNextWidgetName())
    self.nWidgetCount = 0
    screen.deleteWidget(self.MAP_BACKGROUND_ID)
    screen.deleteWidget(self.szDropdownPlayer)
    screen.deleteWidget(self.szEditBoxKeyName)
    screen.deleteWidget(self.szEditBoxKeyCivDesc)
    screen.deleteWidget(self.szDropdownCiv)
    screen.deleteWidget(self.szDropdownLeader)
    screen.deleteWidget(self.szEditBoxStartX)
    screen.deleteWidget(self.szEditBoxStartY)


  def hideAllWidgets(self):
    screen = self.getScreen()
    iNumWidgets = self.nWidgetCount
    self.nWidgetCount = 0
    for i in range(iNumWidgets):
      screen.hide(self.getNextWidgetName())
    self.nWidgetCount = 0
    screen.hide(self.MAP_BACKGROUND_ID)
    screen.hide(self.szDropdownPlayer)
    screen.hide(self.szEditBoxKeyName)
    screen.hide(self.szEditBoxKeyCivDesc)
    screen.hide(self.szDropdownCiv)
    screen.hide(self.szDropdownLeader)
    screen.hide(self.szEditBoxStartX)
    screen.hide(self.szEditBoxStartY)
    screen.hide(self.szDropdownSpot)

  def getNextLineName(self):
    szName = self.MAP_BACKGROUND_ID + "L" + str(self.nLineCount)
    self.nLineCount += 1
    return szName

  def clearAllLines(self):
    screen = self.getScreen()
    nLines = self.nLineCount
    self.nLineCount = 0
    for i in range(nLines):
      screen.removeLineGFC(self.MAP_BACKGROUND_ID, self.getNextLineName())
    self.nLineCount = 0

  def redraw( self ):
    self.initScreen()
    self.hideAllWidgets()
    self.setCommonWidgets()

  def initScenarioPage(self, szenario, bAllowScenarioEdit = False):
    self.initScreen()
    self.hideAllWidgets()
    self.bScenarioEdit = bAllowScenarioEdit
    self.szenario = szenario
    self.iCurrentPlayer = 0
    if self.szenario == None:
      self.currentPage = -1
      self.subscreens["map"] = False
      self.mapCache = None
      self.clearAllLines()
    else:
      self.subscreens["leftMenu"] = True
      self.subscreens["rightMenu"] = True
      self.currentPage = self.pages["pageScenarioDesc"]
    self.redraw()

  def handleClick (self, val1, val2):
    screen = self.getScreen()
    if val1 == self.events["exit"]:
      screen.hideScreen()
      return
    elif val1 == self.events["minimize"]:
      # Alles ausblenden
      for k in self.subscreens.keys():
        self.subscreens[k] = False
      # Linkes Menü wieder einblenden, falls val2 gesetzt
      if val2 != -1:
        self.subscreens["leftMenu"] = True
    elif val1 == self.events["showStartingPoints"]:
      self.analyseLoadedScenario()
      self.subscreens["leftMenu"] = True
      self.subscreens["rightMenu"] = True
      self.subscreens["map"] = True
      self.currentPage = self.pages["pageStartingPoints"]
      self.setupMinimapMap()
    elif val1 == self.events["selectPlayer"]:
      self.iCurrentPlayer = screen.getPullDownData(self.szDropdownPlayer, screen.getSelectedPullDownID(self.szDropdownPlayer))
    elif val1 == self.events["selectSpot"]:
      #self.iCurrentPlayer = screen.getPullDownData(self.szDropdownPlayer, screen.getSelectedPullDownID(self.szDropdownPlayer))
      iGroup = screen.getPullDownType(self.szDropdownSpot, screen.getSelectedPullDownID(self.szDropdownSpot))
      iSpot = screen.getPullDownData(self.szDropdownSpot, screen.getSelectedPullDownID(self.szDropdownSpot))
      if( self.szenario != None and self.bScenarioEdit and iGroup < len(self.szenario.get("StartingPoints",{}))
          and iGroup > -1 and iSpot > -1 ):
        spot = self.szenario["StartingPoints"].values()[iGroup][iSpot]
        self.applySpot( self.iCurrentPlayer, spot)
        self.resetMinimap()
      elif( iGroup == -2):
        self.applySpot( self.iCurrentPlayer, None)
        self.resetMinimap()

    elif val1 == self.events["randomSpots"]:
      """ Random placement of available civilizations
          Mode 0: Just randomize the position of each selected civilization. Thus, a
             player will just replaced by a player with the same civType.
          Mode 1: Select 'numPlayers' starting spots randomly.
      """

      if val2 == 0:
        tmp = deepcopy(self.szenario.get("StartingPoints"))
        for i in range(len(CvWBInterface.WBDesc.playersDesc)):
          pl = CvWBInterface.WBDesc.playersDesc[i]
          if pl.civType in ["NONE", "CIVILIZATION_BARBARIAN", ""]:
            continue

          iNumSpots = len(tmp.get(pl.civType,[]))
          if iNumSpots > 0:
            iR = self.dice.get(iNumSpots, "OracleSayMeTheSpot" )
            spot = tmp.get(pl.civType).pop(iR)
            self.applySpot( i, spot)

      else:
        tmp = []
        for civ in self.szenario.get("StartingPoints").values():
          tmp.extend(civ)

        # Find latest used slot. Change all slots up to this index
        latestUsedSlot = 0
        for i in range(len(CvWBInterface.WBDesc.playersDesc)):
          if CvWBInterface.WBDesc.playersDesc[i].civType not in ["NONE", "CIVILIZATION_BARBARIAN"]:
            latestUsedSlot = i
        latestUsedSlot = max(latestUsedSlot, self.iCurrentPlayer)

        for i in range(latestUsedSlot+1):
          pl = CvWBInterface.WBDesc.playersDesc[i]
          iNumSpots = len(tmp)
          if iNumSpots > 0:
            iR = self.dice.get(iNumSpots, "OracleSayMeTheSpot" )
            spot = tmp.pop(iR)
            self.applySpot( i, spot)

            # Some spots does not contain a leader tag.
            # Use random leader in this case.
            if spot.get("LeaderType","NONE") in ["", "NONE", "RANDOM"]:
              iCiv = gc.getInfoTypeForString( pl.civType )
              civInfo = gc.getCivilizationInfo(iCiv)
              pl.leaderType = self.getRandomLeader(civInfo)
          else:
            # All starting points was already consumed. Set player to NONE
            self.applySpot( i, None)


      self.resetMinimap()
    elif val1 == self.events["showScenarioPage"]:
      if val2 > -1:
        try:
          bMatchingWBFile = ( CvWBInterface.WBDesc != None and
              CvWBInterface.WBDesc.plotDesc[0].szScriptData == self.szenarioFilenames[val2])
        except:
          bMatchingWBFile = False
        if bMatchingWBFile:
          self.szenarioData[val2]["StartingPoints"] = self.szenario.get("StartingPoints",{})
        self.szenario = self.szenarioData[val2]
        self.bScenarioEdit = bMatchingWBFile
      self.subscreens["rightMenu"] = True
      self.currentPage = self.pages["pageScenarioDesc"]

    elif val1 == self.events["showScenarioList"]:
      self.subscreens["rightMenu"] = True
      self.currentPage = self.pages["pageScenarioList"]
    else:
      self.currentPage = int(val1)
      self.subscreens["rightMenu"] = True
      #self.subscreens["map"] = not self.subscreens["map"]

    # Karte immer ausblenden, falls Scenario nicht bearbeitet wird
    if self.currentPage != self.pages["pageStartingPoints"]:
      self.subscreens["map"] = False

    if not self.subscreens["map"]:
      self.clearAllLines()

    self.redraw()

  # Will handle the input for this screen...
  # Achtung, das funktioniert nicht vor dem Laden eines Spiels.
  # Nutze handleClick und den Umweg über WIDGET_PEDIA_DESCRIPTION_NO_HELP
  def handleInput (self, inputClass):
    iNotifyCode = inputClass.getNotifyCode()
    if( inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED ):
      if( inputClass.getData1() == self.ID_OFFSET ):
        i = 0/0

    return 0

  """ Nutze DrawLine um Feld zu zeichnen.
  """
  def setupMinimapMap(self):
    if CvWBInterface.WBDesc == None:
      return

    iGridW = CvWBInterface.WBDesc.mapDesc.iGridW
    iGridH = CvWBInterface.WBDesc.mapDesc.iGridH
    colorLand = gc.getInfoTypeForString("COLOR_PLAYER_DARK_YELLOW")
    colorOcean  = gc.getInfoTypeForString("COLOR_BLUE")
    colorCoast = gc.getInfoTypeForString("COLOR_PLAYER_LIGHT_BLUE")
    colorHills = gc.getInfoTypeForString("COLOR_BROWN_TEXT")
    colorPeak = gc.getInfoTypeForString("COLOR_LIGHT_GREY")
    colorBlack = gc.getInfoTypeForString("COLOR_BLACK")

    mapCache = []

    # Collect color information
    for iX in xrange(iGridW):
      mapCache.append([])
      for iY in xrange(iGridH):
        color = colorOcean
        mapIndex = iX * iGridH + (iGridH-1-iY)
        pl = CvWBInterface.WBDesc.plotDesc[mapIndex]
        if pl.plotType == PlotTypes.PLOT_LAND:
          color = colorLand
        elif pl.plotType == PlotTypes.PLOT_HILLS:
          color = colorLand
        elif pl.plotType == PlotTypes.PLOT_PEAK:
          color = colorPeak
        elif pl.featureType == "FEATURE_DARK_ICE":
          color = colorBlack
        #elif not CvWBInterface.WBDesc.plotDesc[mapIndex].terrainType == "TERRAIN_OCEAN":
        #  color = colorCoast
        mapCache[iX].append( [color,-1] )

    self.mapCache = mapCache

  def resetMinimap(self):
    # Reset Minimap
    if self.mapCache != None:
      for row in self.mapCache:
        for x in row:
          x[1] = -1
    self.clearAllLines()

  def applySpot(self, iPlayer, spot):
    if spot == None:
      # Set Player to none
      CvWBInterface.WBDesc.playersDesc[iPlayer] = CvPlayerDesc()
      CvWBInterface.WBDesc.playersDesc[iPlayer].bLocked = False
      # Remove player index from slots
      for civ in self.szenario.get("StartingPoints",{}).values():
        for spot2 in civ:
          if spot2.get("PlayerID") == iPlayer:
            spot2["PlayerID"] = -1
      return

    pl = CvWBInterface.WBDesc.playersDesc[iPlayer]
    oldCivType = pl.civType

    if spot.get("Civilization","NONE") != "NONE":
      pl.civType = spot.get("Civilization", pl.civType)
    pl.leaderType = spot.get("LeaderType", pl.leaderType)
    pl.iStartingX = spot.get("StartX", pl.iStartingX)
    pl.iStartingY = spot.get("StartY", pl.iStartingY)

    if pl.iStartingX == -1 and pl.iStartingY == -1:
      pl.bRandomStartLocation = True
    else:
      pl.bRandomStartLocation = False

    iCiv = gc.getInfoTypeForString( pl.civType )
    civInfo = gc.getCivilizationInfo(iCiv)
    iColor = civInfo.getDefaultPlayerColor()
    colorInfo = gc.getPlayerColorInfo(iColor)

    # Use random leader if leaderType is NONE
    """
    if pl.leaderType == "NONE" and False:
      pl.leaderType = self.getRandomLeader(civInfo)
    """
    # Es ist nicht immer erwünscht einen zufälligen
    # Anführer zu verwenden, falls der Spot keinen
    # LeaderType enthält. Daher wird statt NONE
    # hier auf das Schlüsselwort RANDOM getestet.
    if pl.leaderType == "RANDOM":
      pl.leaderType = self.getRandomLeader(civInfo)

    iLeader = gc.getInfoTypeForString( pl.leaderType )
    leaderInfo = gc.getLeaderHeadInfo(iLeader)

    if leaderInfo != None:
      #pl.szLeaderName = spot.get("LeaderName", leaderInfo.getTextKey() )
      pl.szLeaderName = spot.get("LeaderName", "")
    else:
      pl.szLeaderName = spot.get("LeaderName", "" )

    if oldCivType == pl.civType:
      pl.color = spot.get("DefaultPlayerColor", pl.color)
      pl.szCivDesc = spot.get("Description", pl.szCivDesc)
      pl.szCivShortDesc = spot.get("ShortDescription", pl.szCivShortDesc)
      pl.szCivAdjective = spot.get("Adjective", pl.szCivAdjective)
      pl.aszCityList = spot.get("Cities", pl.aszCityList)
    else:
      pl.color = spot.get("DefaultPlayerColor", colorInfo.getType())
      pl.szCivDesc = spot.get("Description", civInfo.getTextKey() )
      pl.szCivShortDesc = spot.get("ShortDescription", civInfo.getShortDescriptionKey() )
      pl.szCivAdjective = spot.get("Adjective", civInfo.getAdjective(0) ) # No key variant of function available
      pl.aszCityList = spot.get("Cities", [])

    # Shift id to new slot
    for civ in self.szenario.get("StartingPoints",{}).values():
      for spot2 in civ:
        if spot2.get("PlayerID") == iPlayer:
          spot2["PlayerID"] = -1

    # das könnte das falsche Objekt beeinflussen, da spot teilweise die Kopie eines Startpunktes ist
    # spot["PlayerID"] =  iPlayer
    # Daher...
    for spot2 in self.szenario.get("StartingPoints",{}).get(pl.civType,[]):
      if spot == spot2:
        spot2["PlayerID"] = iPlayer

    UpdatePlayerTechs(iPlayer)
    OmitCppCrash()

  def analyseLoadedScenario(self):
    if CvWBInterface.WBDesc == None:
      return

    for pl in CvWBInterface.WBDesc.playersDesc:
      pl.bLocked = False

    # Check if a player already owns a City. This nations can not be changed anymore.
    iGridH = CvWBInterface.WBDesc.mapDesc.iGridH
    for plot in CvWBInterface.WBDesc.plotDesc:
      if plot.cityDesc != None and plot.cityDesc.owner != None:
        # Fix wrong starting spot values for minimap display
        # Use city with biggest population als starting point
        pl = CvWBInterface.WBDesc.playersDesc[plot.cityDesc.owner]
        if( pl.iStartingX > -1 and pl.iStartingY > -1):
          plot2 = CvWBInterface.WBDesc.plotDesc[
              pl.iStartingX * iGridH + pl.iStartingY ]
          if( plot2.cityDesc != None and
              plot2.cityDesc.owner == plot.cityDesc.owner and
              plot2.cityDesc.population >= plot.cityDesc.population ):
            continue
        pl.iStartingX = plot.iX
        pl.iStartingY = plot.iY
        pl.bLocked = True

  def getPlayerName( self, plDesc):
    if plDesc.szLeaderName != "":
      return str(plDesc.szLeaderName)
    return str("TXT_KEY_"+plDesc.leaderType)

  def getPlayerCiv( self, plDesc):
    if plDesc.szCivDesc != "":
      return str(plDesc.szCivDesc)
    return str("TXT_KEY_"+plDesc.civType)

  def getRandomLeader(self, civInfo):
    """ This returns always 0!
    The DLL code never increases the number. Thus, the function
    is totally useless.
    """
    # iL = civInfo.getNumLeaders()
    leaderIds = []
    iCounter = 0
    for iLeader in xrange(gc.getNumLeaderHeadInfos()):
      if civInfo.isLeaders(iLeader):
        leaderIds.append(iLeader)

    iR = self.dice.get(len(leaderIds) , "OracleSayMeTheLeader" )
    newLeaderId = leaderIds[iR]

    return str(gc.getLeaderHeadInfo(newLeaderId).getType())


# Nachbau der Techanpassung an die Zivilisation
# (Siehe CvEventManager.onGameStart )
# Man kann es von dort nich auslagern, um Redundanzen zu vermeiden,
# da hier das WB-Objekt manipuliert wird.
lTechs = []
lTechs.append("TECH_NONE")
lTechs.append("TECH_TECH_INFO_1")
lTechs.append("TECH_TECH_INFO_2")
lTechs.append("TECH_TECH_INFO_3")
lTechs.append("TECH_TECH_INFO_4")
lTechs.append("TECH_TECH_INFO_5")
lTechs.append("TECH_TECH_INFO_6")
lTechs.append("TECH_TECH_INFO_7")
lTechs.append("TECH_TECH_INFO_8")
lTechsReli = []
lTechsReli.append("TECH_RELIGION_NORDIC")
lTechsReli.append("TECH_RELIGION_CELTIC")
lTechsReli.append("TECH_RELIGION_HINDU")
lTechsReli.append("TECH_RELIGION_EGYPT")
lTechsReli.append("TECH_RELIGION_SUMER")
lTechsReli.append("TECH_RELIGION_GREEK")
lTechsReli.append("TECH_RELIGION_PHOEN")
lTechsReli.append("TECH_RELIGION_ROME")
lTechsReli.append("TECH_DUALISMUS")
lTechsReli.append("TECH_MONOTHEISM")
lTechsReli.append("TECH_ASKESE")
lTechsReli.append("TECH_MEDITATION")
techRome = "TECH_ROMAN"
techGreek = "TECH_GREEK"
lCivsRome = []
lCivsRome.append("CIVILIZATION_ROME")
lCivsRome.append("CIVILIZATION_ETRUSCANS")
lCivsGreek = []
lCivsGreek.append("CIVILIZATION_GREECE")
lCivsGreek.append("CIVILIZATION_ATHENS")
lCivsGreek.append("CIVILIZATION_SPARTA")
lCivsGreek.append("CIVILIZATION_THEBAI")
lCivsGreek.append("CIVILIZATION_MACEDONIA")

# Troublesome are teams with more than one player.
def UpdatePlayerTechs(iPlayer):
  iEra= gc.getInfoTypeForString(CvWBInterface.WBDesc.gameDesc.eraType)
  pl = CvWBInterface.WBDesc.playersDesc[iPlayer]
  team = CvWBInterface.WBDesc.teamsDesc[pl.team]
  techs = team.techTypes
  if iEra > 0:
    techs =  filter( lambda x: x not in lTechsReli, techs)
  if (pl.civType in lCivsRome) and not (techRome in techs):
    techs.append(techRome)
  elif not (pl.civType in lCivsRome) and (techRome in techs):
    techs.remove(techRome)
  if (pl.civType in lCivsGreek) and not (techGreek in techs):
    techs.append(techGreek)
  elif not (pl.civType in lCivsGreek) and (techGreek in techs):
    techs.remove(techGreek)

  team.techTypes = techs

# Workaround für bisher unbekannten Fehler in
# pPlayer.findStartingPlot(True). Tritt nur auf, wenn
# die Startpunkte verändert werden.
def OmitCppCrash():
  for pl in CvWBInterface.WBDesc.playersDesc:
    pl.bRandomStartLocation = False
