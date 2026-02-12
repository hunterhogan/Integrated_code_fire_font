from fontTools import subset
from hunterMakesPy import PackageSettings
from Integrated_Code_Fire import WeightIn
from pathlib import Path

settingsPackage = PackageSettings('Integrated_Code_Fire')

#======== Eliminate hardcoding, which sometimes means adding the value to `settingsPackage`. ========
pathWorkbenchHARDCODED: Path = Path(settingsPackage.pathPackage.parent.parent, 'workbench').resolve()
pathAssetsHARDCODED: Path = Path(settingsPackage.pathPackage.parent.parent, 'assets').resolve()

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
unicodeSC: tuple[str, ...] = ('3000-303F', '3400-4DBF', '4E00-9FFF', 'F900-FAFF')

dictionaryWeights: dict[str, WeightIn] = {
	'Light': WeightIn('Light', 'Light'),
	'Regular': WeightIn('Regular', 'Regular'),
	'Retina': WeightIn('Retina', 'Normal'),
	'Medium': WeightIn('Medium', 'Medium'),
	'SemiBold': WeightIn('SemiBold', 'Bold'),
	'Bold': WeightIn('Bold', 'Heavy'),
}

fontFamily: str = fontFamilyHARDCODED
fontLocale한국인: str = fontLocale한국인HARDCODED
fontLocale台湾: str = fontLocale台湾HARDCODED
fontLocale日本: str = fontLocale日本HARDCODED
fontLocale简化字: str = fontLocale简化字HARDCODED
fontLocale香港: str = fontLocale香港HARDCODED
fontFamilyLocale: str = ' '.join((fontFamily, fontLocale简化字))  # noqa: FLY002
filenameFontFamilyLocale: str = fontFamilyLocale.replace(' ', '')

pathAssets: Path = pathAssetsHARDCODED
pathWorkbench: Path = pathWorkbenchHARDCODED
pathWorkbenchFonts: Path = pathWorkbench / 'fonts'

achVendID: str = '1INT'
fontUnitsPerEm: int = fontUnitsPerEmHARDCODED
subsetOptions: subset.Options = subsetOptionsHARDCODED

pathRootCompiled: Path = Path(settingsPackage.pathPackage.parent.parent, 'compiled').resolve()
pathFilenameFiraCodeGlyphs: Path = Path(settingsPackage.pathPackage.parent.parent, 'FiraCode', 'FiraCode.glyphs').resolve()
pathWorkbenchSourceHanMono: Path = pathWorkbench / 'SourceHanMono'
