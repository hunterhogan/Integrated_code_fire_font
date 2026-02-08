from hunterMakesPy import PackageSettings
from Integrated_Code_Fire._theSSOTSketchBook import (
	filenameSourceHanMono as filenameSourceHanMono, fontUnitsPerEmTarget as fontUnitsPerEmTarget,
	subsetOptions as subsetOptions, unicodeSC as unicodeSC, URLSourceHanMono as URLSourceHanMono)
from pathlib import Path

settingsPackage = PackageSettings('Integrated_Code_Fire')

pathWorkbenchHARDCODED: Path = Path(settingsPackage.pathPackage.parent.parent, 'workbench').resolve()
pathWorkbenchFontsHARDCODED: Path = Path(pathWorkbenchHARDCODED, 'fonts').resolve()
pathWorkbench: Path = pathWorkbenchHARDCODED
pathWorkbenchFonts: Path = pathWorkbenchFontsHARDCODED

fontNameFamilyHARDCODED: str = 'Integrated Code 火'
fontNameLocale简化字HARDCODED: str = '简化字'

fontNameFamily: str = fontNameFamilyHARDCODED
fontNameLocale简化字: str = fontNameLocale简化字HARDCODED
