==== Szenario Starting Points ====

The XML files in this folder contain several information for PAE szenario's.

If the first plot of a szenario file (search for BeginPlot) contains the line
'ScriptData=[Name]'
the program search for XML/Szenarios/[Name].xml


Example XML-Code:

<Szenario>
	<!-- Program use very simple parser. Do not use multiple tags in one line. 
	• Optional properties: Image, Title, Description, StartingPoints
	• Required properties for starting points: Civilization, StartX, StartY
	• Optional properties for starting points: StartName, LeaderType, LeaderName,
	     Description, ShortDescription, Adjective, DefaultPlayerColor, Cities
	• Without the LeaderType tag, the current leader will be kept.
       Insert the value RANDOM>  to force a new leader
	-->
	<Image>Art/Interface/Screens/WorldPicker/pae_map.dds</Image>
	<Title>TXT_KEY_MY_SZENARIO_TITLE/Title>
	<Description>TXT_KEY_MY_SZENARIO_DESCRIPTION</Description>
	<StartingPoints>
		<StartingPoint>
			<Civilization>CIVILIZATION_ASSYRIA</Civilization>
			<StartX>40</StartX>
			<StartY>40</StartY>
			<StartName>My start spot</StartName>
			<LeaderName>My leader name</LeaderName>
			<LeaderType>LEADER_TIGLATPILESER1</LeaderType>
      <Description>TXT_KEY_CIV_ASSYRIA_DESC</Description>
      <ShortDescription>TXT_KEY_CIV_ASSYRIA_DESC</ShortDescription>
      <Adjective>TXT_KEY_CIV_ASSYRIA_ADJECTIVE</Adjective>
      <DefaultPlayerColor>PLAYERCOLOR_ASSUR</DefaultPlayerColor>
      <Cities>
        <City>My capital</City>
        <City>My second city</City>
			</Cities>
		</StartingPoint>
	</StartingPoints>
</Szenario>
