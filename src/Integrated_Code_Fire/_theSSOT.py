from fontTools import subset
from hunterMakesPy import PackageSettings as humpy_PackageSettings
from Integrated_Code_Fire import WeightIn
from pathlib import Path
from socket import gethostname
from sys import modules as sysModules
from typing import Final
import dataclasses
import platformdirs

#======== Eliminate hardcoding, which sometimes means adding the value to `settingsPackage`. ========
fontVersionHARDCODED: float = 0.002
# NOTE Update this? ^^^^^^^^^^^^^^^

fontLocale한국인HARDCODED: str = '한국인'
fontLocale台湾HARDCODED: str = '台灣'
fontLocale日本HARDCODED: str = '日本'
fontLocale简化字HARDCODED: str = '简化字'
fontLocale香港HARDCODED: str = '香港'

subsetOptionsHARDCODED = subset.Options(
	glyph_names = True,
	legacy_cmap = True,
	name_IDs='*',
	name_languages='*',
	name_legacy = True,
	passthrough_tables = True,
	drop_tables = [],
	symbol_cmap = True,
	layout_features='*',
)

if 'google.colab' in sysModules:
	pathRootHARDCODED: Path = Path("/content/drive/MyDrive")
else:
	pathRootHARDCODED = Path(platformdirs.user_data_dir(appauthor=False))

if gethostname() == 'duda':
	pathRootHARDCODED = Path('/apps/Integrated_Code_Fire')

#======== Subclass `PackageSettings` to add package-specific settings. ========

@dataclasses.dataclass
class PackageSettings(humpy_PackageSettings):
	achVendID: str = '1INT' # See "Registering Vendor ID 1INT.pdf".
	fontFamily: Final[str] = 'Integrated Code 火'
	unitsPerEm: int = 1000
	fontVersion: float = fontVersionHARDCODED
	pathRoot: Path = pathRootHARDCODED

	fontLocale한국인: dataclasses.InitVar[str] = fontLocale한국인HARDCODED
	fontLocale台湾: dataclasses.InitVar[str] = fontLocale台湾HARDCODED
	fontLocale日本: dataclasses.InitVar[str] = fontLocale日本HARDCODED
	fontLocale简化字: dataclasses.InitVar[str] = fontLocale简化字HARDCODED
	fontLocale香港: dataclasses.InitVar[str] = fontLocale香港HARDCODED

	pathAssets: Path = dataclasses.field(init=False)
	pathWorkbench: Path = dataclasses.field(init=False)
	pathWorkbenchFonts: Path = dataclasses.field(init=False)

	fontFamilyLocale한국인: str = dataclasses.field(init=False)
	fontFamilyLocale台湾: str = dataclasses.field(init=False)
	fontFamilyLocale日本: str = dataclasses.field(init=False)
	fontFamilyLocale简化字: str = dataclasses.field(init=False)
	fontFamilyLocale香港: str = dataclasses.field(init=False)

	filenameFontFamilyLocale한국인: str = dataclasses.field(init=False)
	filenameFontFamilyLocale台湾: str = dataclasses.field(init=False)
	filenameFontFamilyLocale日本: str = dataclasses.field(init=False)
	filenameFontFamilyLocale简化字: str = dataclasses.field(init=False)
	filenameFontFamilyLocale香港: str = dataclasses.field(init=False)
	filenameFontFamily: str = dataclasses.field(init=False)

	def __post_init__( self, identifierPackageFALLBACK: str, fontLocale한국인: str, fontLocale台湾: str, fontLocale日本: str, fontLocale简化字: str, fontLocale香港: str ) -> None:
		super().__post_init__(identifierPackageFALLBACK)

		self.pathRoot = self.pathRoot / self.identifierPackage
		if gethostname() == 'duda':
			self.pathRoot = pathRootHARDCODED

		self.pathAssets = self.pathRoot / 'assets'
		self.pathWorkbench = self.pathRoot / 'workbench'
		self.pathWorkbenchFonts = self.pathWorkbench / 'fonts'

		self.fontFamilyLocale한국인 = ' '.join((self.fontFamily, fontLocale한국인))
		self.fontFamilyLocale台湾 = ' '.join((self.fontFamily, fontLocale台湾))
		self.fontFamilyLocale日本 = ' '.join((self.fontFamily, fontLocale日本))
		self.fontFamilyLocale简化字 = ' '.join((self.fontFamily, fontLocale简化字))
		self.fontFamilyLocale香港 = ' '.join((self.fontFamily, fontLocale香港))

		self.filenameFontFamilyLocale한국인 = self.fontFamilyLocale한국인.replace(' ', '')
		self.filenameFontFamilyLocale台湾 = self.fontFamilyLocale台湾.replace(' ', '')
		self.filenameFontFamilyLocale日本 = self.fontFamilyLocale日本.replace(' ', '')
		self.filenameFontFamilyLocale简化字 = self.fontFamilyLocale简化字.replace(' ', '')
		self.filenameFontFamilyLocale香港 = self.fontFamilyLocale香港.replace(' ', '')
		self.filenameFontFamily = self.fontFamily.replace(' ', '')


#-------- Package settings. ---------------------------------------------

settingsPackage = PackageSettings('Integrated_Code_Fire')

#======== Centralized settings that have not yet found their home, such as in `settingsPackage`. ========

# TODO These ranges are wrong. Figure out the correct way to subset Source Han Mono.
unicodeSC: tuple[str, ...] = ('FFFE-FFFF', 'FF64-FFFC', 'FF00-FF61', 'EE0C-FEFE', 'E0B4-EDFF', '300E-DFFF', '3000-300B')

dictionaryWeights: dict[str, WeightIn] = {
	'Light': WeightIn('Light', 'Light'),
	'Regular': WeightIn('Regular', 'Regular'),
	'Retina': WeightIn('Retina', 'Normal'),
	'Medium': WeightIn('Medium', 'Medium'),
	'SemiBold': WeightIn('SemiBold', 'Bold'),
	'Bold': WeightIn('Bold', 'Heavy'),
}

subsetOptions: subset.Options = subsetOptionsHARDCODED

pathFilenameFiraCodeGlyphs: Path = settingsPackage.pathRoot / 'FiraCode' / 'FiraCode.glyphs'
fontFamily: str = 'FrankenFont'
pathFilenameGlyphs: Path = Path(pathFilenameFiraCodeGlyphs.parent.parent, fontFamily, fontFamily + pathFilenameFiraCodeGlyphs.suffix)
pathWorkbenchSourceHanMono: Path = settingsPackage.pathWorkbench / 'SourceHanMono'
advanceWidth: int = 0
leftSideBearing: int = 1
bearingIncrement: int = 200
"""Horizontal increment in font units added to left bearings and advance
widths when integrating Source Han glyphs.

(AI generated docstring)

The `bearingIncrement` value is used by `applyBearingIncrementToFont` to
translate glyph coordinates and to increase left side bearings and advance
widths so that merged CJK glyphs have an appropriate visual offset when
combined with Latin monospace glyphs.

References
----------
[1] fontTools - Read the Docs
	https://fonttools.readthedocs.io/en/latest/
"""
maximumErrorUnitsPerEm: float = 1.0
postTableFormat: float = 2.0
reverseContourDirection: bool = True

lookupAFDKOCharacterSet: dict[str, str] = {
	'Hong_Kong': '2',
	'Japan': '1',
	'Korea': '3',
	'Simplified_Chinese': '25',
	'Taiwan': '2',
}
"""Locale identifiers to AFDKO makeotf character set identifiers.

Maps font locale identifiers to Adobe CID character collection ROS
(Registry-Ordering-Supplement) identifiers for use with AFDKO makeotf -cs
argument [1].

The character set identifiers correspond to:
- '1': Adobe-Japan1 (Japanese)
- '2': Adobe-CNS1 (Traditional Chinese: Hong Kong, Taiwan)
- '3': Adobe-Korea1 (Korean)
- '25': Adobe-GB1 (Simplified Chinese)

References
----------
[1] AFDKO makeotf - Read the Docs
	https://adobe-type-tools.github.io/afdko/AFDKO-Overview.html#makeotf
[2] Adobe CMap Resources - GitHub
	https://github.com/adobe-type-tools/cmap-resources
"""
