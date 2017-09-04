#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Durchsucht WB-Saves und Pythondateien nach nicht mehr vorhandenen XML-Tags.
    Es wird nicht nach allen Schlüsselwörten gesucht, aber nach den
    wichtigsten, wie beispielsweise TECH_XYZ, UNIT_XYZ, TXT_KEY_XYZ.

    Notes:
    • Bei TXT_KEY wird auch in den Nicht-Mod-XML-Dateien gesucht.
    • Angenommen wird, dass diese Datei in Mods/PieAncientEuropeV/Extras liegt.
      und per relativer Pfadangabe auf die Dateien des Grundspiels zugegriffen
      werden kann.
"""

import sys
import re
import os.path

Supported_Types = [
    # (Key, Type, (Regex-XML, File-XML),
    #  (Regex-WB-Keyword, RegexMatch-WB))
    ("Unit", "UNIT_", ("<Type>UNIT_", "CIV4UnitInfos.xml"),
     (r"(UnitType|ProductionUnit)", 2)),
    ("Tech", "TECH_", ("<Type>TECH_", "CIV4TechInfos.xml"),
     ("Tech", 1)),
    ("Promotion", "PROMOTION_", ("<Type>PROMOTION_", "CIV4PromotionInfos.xml"),
     ("PromotionType", 1)),
    ("Terrain", "TERRAIN_", ("<Type>TERRAIN_", "CIV4TerrainInfos.xml"),
     ("TerrainType", 1)),
    ("Feature", "FEATURE_", ("<Type>FEATURE_", "CIV4FeatureInfos.xml"),
     ("FeatureType", 1)),
    ("Building", "BUILDING_", ("<Type>BUILDING_", "CIV4BuildingInfos.xml"),
     (r"(BuildingType|ProductionBuilding)", 2)),
    ("Improvement", "IMPROVEMENT_", ("<Type>IMPROVEMENT_", "CIV4ImprovementInfos.xml"),
     ("ImprovementType", 1)),
    ("Route", "ROUTE_", ("<Type>ROUTE_", "CIV4RouteInfos.xml"),
     ("RouteType", 1)),
]

# For (separated) TXT_KEY search
Supported_Txt_Types = [
    # (Key, Type, (Regex-XML, File-XML),
    #  (Regex-WB-Keyword, RegexMatch-WB))
    ("txt", "TXT_KEY_", ("<Tag>TXT_KEY_", None),
     (r"", -1)),
]

Supported_Paths = {
    "maps" : [],
    "python": [],
}

Mod_Name = "PieAncientEuropeV"
Rel_Path = ".."  # PieAncientEuropeV/Extras/..

# Relative from PieAncientEuropeV/Extras
Civ4_Path = os.path.join("..", "..", "..", "..")

# Absolute path / Debug
Civ4_Path = r"/opt/spiele/Civ4/"

def show_help():
    t = [st[0] for st in Supported_Types]
    txt = """Search undefined keywords in Civ4 Szenario maps and Python files.
    
    Usage:
      python {prog_name} {{all|txt|{types}}} [all|{paths}]

    - The first argument decides which type (UNIT_, PROMOTION_, etc) should be
      searched for. Use 'all' to seach for all.
      Moreover, the 'txt' argument could be used to search for TXT_KEY token.

    - The optional second argument restricts the searches on maps/python files
      only.
    """.format(prog_name=sys.argv[0],
               types="|".join(t),
               paths="|".join(Supported_Paths.keys()))
    print(txt)

def get_civ4_files(sSearchType):
    sMod = os.path.join(Rel_Path)
    sBts = os.path.join(Civ4_Path, "Beyond the Sword")
    sWls = os.path.join(Civ4_Path, "Warlords")
    sVan = os.path.join(Civ4_Path)
    sRoots = [sMod, sBts, sWls, sVan]

    if sSearchType == "python":
        lDirs = [os.path.join(sMod, "Assets", "Python")]
        sExt = ".py"
    elif sSearchType == "xml":
        lDirs = [os.path.join(sMod, "Assets", "XML")]
        # lDirs = [os.path.join(x, "Assets", "XML") for x in sRoots]
        sExt = ".xml"
    elif sSearchType == "txt":
        lDirs = [os.path.join(x, "Assets", "XML", "Text") for x in sRoots]
        sExt = ".xml"
    elif sSearchType == "maps":
        lDirs = [os.path.join(sMod, "PrivateMaps"),
                os.path.join(sMod, "PublicMaps")]
        sExt = ".CivBeyondSwordWBSave"

    o = {}
    def extension_filter(o, sPath, lFiles):
        for f in lFiles:
            if not f.endswith(sExt):
                continue

            # Skip 'non top-level version' of a file
            if f in o:
                continue

            o[f] = os.path.join(sPath, f)

    for d in lDirs:
        # print("d: "+str(d))
        os.path.walk(d, extension_filter, o)

    return o


def print_keywords_not_found(dInfoTypesNotFound):
    lSortedKeys = dInfoTypesNotFound.keys()
    lSortedKeys.sort()
    for k1 in lSortedKeys:
        # Print affected files for each keyword.
        dFiles = dInfoTypesNotFound[k1]
        l = ["%s: %d" % (k2, dFiles[k2]) for k2 in dFiles]
        print("%s:\n\t%s" % (k1, "\n\t".join(l)))


def search_in_maps(lKeys=None):
    lXmlFiles = get_civ4_files("xml")
    lInfoTypes = load_xml(lXmlFiles, lKeys)
    lMapFiles = get_civ4_files("maps")
    # print("Files:\n" + "\n".join(lMapFiles.values()))

    dInfoTypesNotFound = compare_matches_maps(lMapFiles, lInfoTypes, lKeys)
    if len(dInfoTypesNotFound) == 0:
        print("(WBSaves) No missing info types strings found.")
    else:
        print("(WBSaves) %d info types missing" % len(dInfoTypesNotFound))
        print_keywords_not_found(dInfoTypesNotFound)


def search_in_python(lKeys=None):
    lXmlFiles = get_civ4_files("xml")
    lInfoTypes = load_xml(lXmlFiles, lKeys)
    lPythonFiles = get_civ4_files("python")

    dInfoTypesNotFound = compare_matches_python(lPythonFiles, lInfoTypes, lKeys)
    if len(dInfoTypesNotFound) == 0:
        print("(Python) No missing info types strings found.")
    else:
        print("(Python) %d info types missing" % len(dInfoTypesNotFound))
        print_keywords_not_found(dInfoTypesNotFound)


def search_txt_in_maps():
    lTxtFiles = get_civ4_files("txt")
    lInfoTypes = load_txt(lTxtFiles)
    lMapFiles = get_civ4_files("maps")

    dInfoTypesNotFound = compare_txt_matches_maps(
        lMapFiles, lInfoTypes, True)

    if len(dInfoTypesNotFound) == 0:
        print("(WBSaves) No missing info types strings found.")
    else:
        print("(WBSaves) %d info types missing" % len(dInfoTypesNotFound))
        print_keywords_not_found(dInfoTypesNotFound)


def search_txt_in_python():
    lTxtFiles = get_civ4_files("txt")
    lInfoTypes = load_txt(lTxtFiles)
    lPythonFiles = get_civ4_files("python")

    # (Ugly hack) Replace global Supported_Types dict...
    global Supported_Types
    Supported_Types = Supported_Txt_Types

    dInfoTypesNotFound = compare_matches_python(
        lPythonFiles, lInfoTypes, None, True)
    if len(dInfoTypesNotFound) == 0:
        print("(Python) No missing info types strings found.")
    else:
        print("(Python) %d info types missing" % len(dInfoTypesNotFound))
        print_keywords_not_found(dInfoTypesNotFound)


def load_xml_infotypes(sKeyword, sFilename):
    reg = re.compile(r'^.*>([^<]*)<.*\r*\n*$')
    lInfoTypes = []
    with open(sFilename, "r") as f:
        sLine = f.readline()
        while sLine:
            if sKeyword in sLine:
                sInfoType = reg.sub(r"\1", sLine)
                lInfoTypes.append(sInfoType)
            sLine = f.readline()

    return lInfoTypes


def load_xml(lFilepaths, lKeys=None):
    #  EXISTING_NAMES=$(grep "$1" "$2" | sed -n -e 's/^.*>\([^<]*\)<.*$/\1/p' \
    #     | sort | uniq)
    """ Read for each supported type one XML file,
    extract the keywords like UNIT_XYZ and return them.
    """

    lResults = []
    for st in Supported_Types:
        if lKeys is not None and st[0] not in lKeys:
            # Supress loading of xml files of no interest
            continue

        # print("Handle %s" % st[0])
        if st[2][1] not in lFilepaths:
            # No path for this xml file available.
            continue

        lResults.extend(
            load_xml_infotypes(st[2][0], lFilepaths[st[2][1]])
        )

    # Filter out duplicates
    lResults = dict.fromkeys(lResults).keys()

    print("(XML) Num loaded infotypes: %i" % (len(lResults), ))

    if False:
        write_list("/dev/shm/info_types.txt", lResults)

    return lResults


def load_txt(lFilepaths):
    """ Read files in Assets/XML/Text/ and save <Tag>-entries.
    """

    lResults = []
    for st in Supported_Txt_Types:
        for sFilename in lFilepaths:
            lResults.extend(
                load_xml_infotypes(st[2][0], lFilepaths[sFilename])
            )

    # Filter out duplicates
    lResults = dict.fromkeys(lResults).keys()

    print("(XML) Num loaded infotypes: %i" % (len(lResults), ))

    if False:
        write_list("/dev/shm/info_types.txt", lResults)

    return lResults


def write_list(sFilepath, lInfoTypes):
    """ For Debugging only"""
    lInfoTypes.sort()
    with open(sFilepath, "w") as f:
        for r in lInfoTypes:
            f.write(r+",\n")


def prefix_check(sInfoType, lInfoTypes):
    # Let TXT_KEY_BLA match also with TXT_KEY_BLA1,
    # etc...
    bFound = False
    for sLongInfoType in lInfoTypes:
        if sLongInfoType.startswith(sInfoType):
            bFound = True
            break

    return bFound


def compare_matches_maps(lFilepaths, lInfoTypes, lKeys=None, bPrefix=False):
    #  USED_NAMES=$(grep "$3" ../PrivateMaps/*.CivBeyondSwordWBSave \
    #    | sed -n -e "s/^.*$4=\([^, ]\+\).*\$/\\$5/p" \
    #    | sed -e "s/\r//p" \
    #    | sort | uniq )
    """
    Return dict with missing info types. Structure:
        {
        "INFO_TYPE" : {"FILENAME": NUMBER_OF_HITS"},
        ...
        }
    """

    dInfoTypesNotFound = {}
    lKeywords = [st[1] for st in Supported_Types
                 if lKeys is None or st[0] in lKeys]
    tRegs = [(re.compile(r"^.*{key}=([^, \r]+).*\n*$".format(key=st[3][0])),
             st[3][1])
             for st in Supported_Types
             if lKeys is None or st[0] in lKeys]

    for sFilename in lFilepaths:
        with open(lFilepaths[sFilename], "r") as f:
            sLine = f.readline()
            while sLine:
                for i in range(len(lKeywords)):
                    if lKeywords[i] in sLine:
                        sInfoType = tRegs[i][0].sub(r"\%i" % (tRegs[i][1]), sLine)
                        if sInfoType == sLine:
                            # Substitution failed (by several reasons, i.e.
                            # keyword found in substring)
                            # print("Failed: "+sLine)
                            continue

                        if bPrefix and prefix_check(sInfoType, lInfoTypes):
                            continue

                        if sInfoType not in lInfoTypes:
                            dnf = dInfoTypesNotFound.setdefault(sInfoType, {})
                            dnf[sFilename] = dnf.setdefault(sFilename, 0) + 1
                sLine = f.readline()

    return dInfoTypesNotFound


def compare_txt_matches_maps(lFilepaths, lInfoTypes, bPrefix=False):
    """
    Like compare_matches_python but search for '=TXT_KEY_*' instead of
    "TXT_KEY_*'.
    """

    dInfoTypesNotFound = {}
    lKeywords = [st[1] for st in Supported_Txt_Types]
    lRegs = [re.compile(r"""^.*=({key}[^, \r]+).*\n*$""".format(key=st[1]))
             for st in Supported_Txt_Types]

    for sFilename in lFilepaths:
        with open(lFilepaths[sFilename], "r") as f:
            sLine = f.readline()
            while sLine:
                for i in range(len(lKeywords)):
                    if lKeywords[i] in sLine:
                        sInfoType = lRegs[i].sub(r"\1", sLine)
                        if sInfoType == sLine:
                            # Substitution failed (by several reasons, i.e.
                            # keyword found in substring)
                            # print("Failed: "+sLine)
                            continue

                        if bPrefix and prefix_check(sInfoType, lInfoTypes):
                            continue

                        if sInfoType not in lInfoTypes:
                            dnf = dInfoTypesNotFound.setdefault(sInfoType, {})
                            dnf[sFilename] = dnf.setdefault(sFilename, 0) + 1
                sLine = f.readline()

    return dInfoTypesNotFound


def compare_matches_python(lFilepaths, lInfoTypes, lKeys=None, bPrefix=False):
    """
    Like compare_matches_maps but for python files. The info types will be
    searched as quoted strings.
    """

    dInfoTypesNotFound = {}
    lKeywords = [st[1] for st in Supported_Types
                 if lKeys is None or st[0] in lKeys]
    lRegs = [re.compile(r"""^.*["']({key}[^"']+)["'].*\n*$""".format(key=st[1]))
             for st in Supported_Types
             if lKeys is None or st[0] in lKeys]

    for sFilename in lFilepaths:
        with open(lFilepaths[sFilename], "r") as f:
            sLine = f.readline()
            while sLine:
                for i in range(len(lKeywords)):
                    if lKeywords[i] in sLine:
                        sInfoType = lRegs[i].sub(r"\1", sLine)
                        if sInfoType == sLine:
                            # Substitution failed (by several reasons, i.e.
                            # keyword found in substring)
                            # print("Failed: "+sLine)
                            continue

                        if bPrefix and prefix_check(sInfoType, lInfoTypes):
                            continue

                        if sInfoType not in lInfoTypes:
                            dnf = dInfoTypesNotFound.setdefault(sInfoType, {})
                            dnf[sFilename] = dnf.setdefault(sFilename, 0) + 1
                sLine = f.readline()

    return dInfoTypesNotFound


if __name__ == '__main__':
    lArgs = sys.argv[1:]
    if len(lArgs) == 0 or lArgs[0] in ["-h", "--help"]:
        show_help()

    else:
        lArgs.append("all")  # Opt. second arg

        if lArgs[1] in ["all", "maps"]:
            if lArgs[0] == "txt":
                search_txt_in_maps()
            elif lArgs[0] == "all":
                search_in_maps()
            else:
                search_in_maps([lArgs[0]])

        if lArgs[1] in ["all", "python"]:
            if lArgs[0] == "txt":
                search_txt_in_python()
            elif lArgs[0] == "all":
                search_in_python()
            else:
                search_in_python([lArgs[0]])

