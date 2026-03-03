from fontTools import subset
from hunterMakesPy import PackageSettings as humpy_PackageSettings
from typing import Final, TYPE_CHECKING
import dataclasses

if TYPE_CHECKING:
	from pathlib import Path

#======== Eliminate hardcoding, which sometimes means adding the value to `settingsPackage`. ========
fontVersionHARDCODED: float = 0.007
# TODO version update? ^^^^^^^^^^^^

subsetOptionsHARDCODED = subset.Options(
	drop_tables = [],
	glyph_names = False,
	layout_features = '*',
	legacy_cmap = True,
	name_IDs = '*',
	name_languages = '*',
	name_legacy = True,
	passthrough_tables = True,
	symbol_cmap = True,
)

#======== Subclass `PackageSettings` to add package-specific settings. ========

@dataclasses.dataclass
class PackageSettings(humpy_PackageSettings):
	achVendID: str = '1INT' # See "Registering Vendor ID 1INT.pdf".
	fontFamily: Final[str] = 'Integrated Code 火'
	fontVersion: float = fontVersionHARDCODED
	theLocales: frozenset[str] = frozenset(['Hong_Kong', 'Japan', 'Korea', 'Simplified_Chinese', 'Taiwan'])
	theStyles: frozenset[str | None] = frozenset(['Italic', None])
	theWeights: frozenset[str] = frozenset(['Bold', 'ExtraLight', 'Heavy', 'Light', 'Medium', 'Normal', 'Regular'])
	unitsPerEm: int = 1000

	pathRoot: Path = dataclasses.field(init=False)
	pathAssets: Path = dataclasses.field(init=False)
	pathWorkbench: Path = dataclasses.field(init=False)
	pathWorkbenchFonts: Path = dataclasses.field(init=False)

	filenameFontFamily: str = dataclasses.field(init=False)

	def __post_init__(self, identifierPackageFALLBACK: str) -> None:
		super().__post_init__(identifierPackageFALLBACK)

		self.pathRoot = self.pathPackage.parent.parent
		self.pathAssets = self.pathRoot / 'assets'
		self.pathWorkbench = self.pathRoot / 'workbench'
		self.pathWorkbenchFonts = self.pathWorkbench / 'fonts'

		self.filenameFontFamily = self.fontFamily.replace(' ', '')

#-------- Package settings. ---------------------------------------------

settingsPackage = PackageSettings('Integrated_Code_Fire'
	, theLocales = frozenset(['Hong_Kong', 'Japan', 'Korea', 'Simplified_Chinese', 'Taiwan'])
	, theStyles = frozenset([None])
	, theWeights = frozenset(['Bold', 'Heavy', 'Light', 'Medium', 'Normal', 'Regular'])
)

#======== Centralized settings that have not yet found their home, such as in `settingsPackage`. ========

pathFilenameFiraCodeGlyphs: Path = settingsPackage.pathRoot / 'FiraCode' / 'FiraCode.glyphs'
