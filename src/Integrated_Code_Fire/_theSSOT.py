from fontTools import subset
from hunterMakesPy import PackageSettings
from Integrated_Code_Fire import WeightIn
from pathlib import Path

settingsPackage = PackageSettings('Integrated_Code_Fire')

pathWorkbenchHARDCODED: Path = Path(settingsPackage.pathPackage.parent.parent, 'workbench').resolve()
pathWorkbenchFontsHARDCODED: Path = Path(pathWorkbenchHARDCODED, 'fonts').resolve()
pathWorkbench: Path = pathWorkbenchHARDCODED
pathWorkbenchFonts: Path = pathWorkbenchFontsHARDCODED

fontFamilyHARDCODED: str = 'Integrated Code 火'
fontLocale简化字HARDCODED: str = '简化字'

fontFamily: str = fontFamilyHARDCODED
fontLocale简化字: str = fontLocale简化字HARDCODED

fontFamilyLocale: str = ' '.join((fontFamily, fontLocale简化字))  # noqa: FLY002
filenameFontFamilyLocale: str = fontFamilyLocale.replace(' ', '')
achVendID: str = '    '

dictionaryWeights: dict[str, WeightIn] = {
	'Light': WeightIn('Light', 'Light'),
	'Regular': WeightIn('Regular', 'Regular'),
	'Retina': WeightIn('Retina', 'Normal'),
	'Medium': WeightIn('Medium', 'Medium'),
	'SemiBold': WeightIn('SemiBold', 'Bold'),
	'Bold': WeightIn('Bold', 'Heavy'),
}

unicodeSC: tuple[str, ...] = ('3000-303F', '3400-4DBF', '4E00-9FFF', 'F900-FAFF')

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
subsetOptions: subset.Options = subsetOptionsHARDCODED

fontUnitsPerEmTargetHARDCODED: int = 2000
fontUnitsPerEmTarget: int = fontUnitsPerEmTargetHARDCODED
