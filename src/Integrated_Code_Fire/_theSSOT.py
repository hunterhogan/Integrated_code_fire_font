from fontTools import subset
from hunterMakesPy import PackageSettings
from pathlib import Path

settingsPackage = PackageSettings('Integrated_Code_Fire')

pathRootFiraCodeHARDCODED = Path('/clones/FiraCode')
URLSourceHanMonoHARDCODED: str = 'https://github.com/adobe-fonts/source-han-mono/releases/download/1.002/SourceHanMono.ttc'
filenameSourceHanMonoHARDCODED: str = 'SourceHanMono.ttc'
pathRootWorkbenchHARDCODED: Path = settingsPackage.pathPackage / 'workbench'

pathRootFiraCode: Path = pathRootFiraCodeHARDCODED
URLSourceHanMono: str = URLSourceHanMonoHARDCODED
pathRootWorkbench: Path = pathRootWorkbenchHARDCODED
filenameSourceHanMono: str = filenameSourceHanMonoHARDCODED

unicodeSC: tuple[str, ...] = ('3000-303F', '3400-4DBF', '4E00-9FFF', 'F900-FAFF')

subsetOptionsHARDCODED = subset.Options(
	glyph_names = True,
	legacy_cmap = True,
	name_IDs='*',
	name_languages='*',
	name_legacy = True,
	passthrough_tables = True,
	symbol_cmap = True,
	layout_features='*',
)
subsetOptions: subset.Options = subsetOptionsHARDCODED

fontFamilyNameHARDCODED: str = 'Integrated Code 火 简化字'
fontPostScriptNamePrefixHARDCODED: str = 'IntegratedCode火简化字'
fontVersionStringHARDCODED: str = 'Version 0.001'
fontOutputFilenamePrefixHARDCODED: str = 'IntegratedCode火简化字'
fontUnitsPerEmTargetHARDCODED: int = 2000
fontBearingIncrementHARDCODED: int = 200

fontFamilyName: str = fontFamilyNameHARDCODED
fontPostScriptNamePrefix: str = fontPostScriptNamePrefixHARDCODED
fontVersionString: str = fontVersionStringHARDCODED
fontOutputFilenamePrefix: str = fontOutputFilenamePrefixHARDCODED
fontUnitsPerEmTarget: int = fontUnitsPerEmTargetHARDCODED
fontBearingIncrement: int = fontBearingIncrementHARDCODED

fontPairsHARDCODED: list[tuple[str, str, str]] = [
	('Bold', 'FiraCode-Bold.otf', 'SourceHanMonoSC-Heavy.otf'),
	('Light', 'FiraCode-Light.otf', 'SourceHanMonoSC-Light.otf'),
	('Medium', 'FiraCode-Medium.otf', 'SourceHanMonoSC-Medium.otf'),
	('Retina', 'FiraCode-Retina.otf', 'SourceHanMonoSC-Normal.otf'),
	('SemiBold', 'FiraCode-SemiBold.otf', 'SourceHanMonoSC-Bold.otf'),
	('Regular', 'FiraCode-Regular.otf', 'SourceHanMonoSC-Regular.otf'),
]
fontPairs: list[tuple[str, str, str]] = fontPairsHARDCODED
