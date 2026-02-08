"""Potential settings and constants for the project, not in use."""
from fontTools import subset
from pathlib import Path

pathRootFiraCodeHARDCODED = Path('/clones/FiraCode')
URLSourceHanMonoHARDCODED: str = 'https://github.com/adobe-fonts/source-han-mono/releases/download/1.002/SourceHanMono.ttc'
filenameSourceHanMonoHARDCODED: str = 'SourceHanMono.ttc'

pathRootFiraCode: Path = pathRootFiraCodeHARDCODED
URLSourceHanMono: str = URLSourceHanMonoHARDCODED
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

fontUnitsPerEmTargetHARDCODED: int = 2000
fontUnitsPerEmTarget: int = fontUnitsPerEmTargetHARDCODED

