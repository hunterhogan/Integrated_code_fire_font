from fontTools import subset
from hunterMakesPy import PackageSettings
from Integrated_Code_Fire import WeightIn
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pathlib import Path

settingsPackage = PackageSettings('Integrated_Code_Fire')

#======== Eliminate hardcoding, which sometimes means adding the value to `settingsPackage`. ========
pythonDesignedAnIdioticFileStructureWithoutCreatingProperTools: Path = settingsPackage.pathPackage.parent.parent.resolve()

fontFamilyHARDCODED: str = 'Integrated Code 火'
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
fontUnitsPerEmHARDCODED: int = 2000

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

pathRoot: Path = pythonDesignedAnIdioticFileStructureWithoutCreatingProperTools

fontFamily: str = fontFamilyHARDCODED
fontLocale한국인: str = fontLocale한국인HARDCODED
fontLocale台湾: str = fontLocale台湾HARDCODED
fontLocale日本: str = fontLocale日本HARDCODED
fontLocale简化字: str = fontLocale简化字HARDCODED
fontLocale香港: str = fontLocale香港HARDCODED
fontFamilyLocale: str = ' '.join((fontFamily, fontLocale简化字))  # noqa: FLY002
filenameFontFamilyLocale: str = fontFamilyLocale.replace(' ', '')

pathAssets: Path = pathRoot / 'assets'
pathWorkbench: Path = pathRoot / 'workbench'
pathWorkbenchFonts: Path = pathWorkbench / 'fonts'

achVendID: str = '1INT' # See "Registering Vendor ID 1INT.pdf".
fontUnitsPerEm: int = fontUnitsPerEmHARDCODED
subsetOptions: subset.Options = subsetOptionsHARDCODED

pathRootCompiled: Path = pathRoot / 'compiled'
pathFilenameFiraCodeGlyphs: Path = pathRoot / 'FiraCode' / 'FiraCode.glyphs'
pathWorkbenchSourceHanMono: Path = pathWorkbench / 'SourceHanMono'
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
