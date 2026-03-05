from fontTools import subset
from hunterMakesPy import PackageSettings as humpy_PackageSettings
from typing import Final, TYPE_CHECKING
import dataclasses

if TYPE_CHECKING:
	from pathlib import Path

#======== Eliminate hardcoding, typically with a dynamic process or adding the value to `settingsPackage`. ========
fontVersionHARDCODED: float = 0.008
# TODO version update? ^^^^^^^^^^^^

subsetOptionsHARDCODED: subset.Options = subset.Options(
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

#======== Subclass `hunterMakesPy.PackageSettings` to add package-specific settings. ========

@dataclasses.dataclass
class PackageSettings(humpy_PackageSettings):
	"""Configure package-wide settings specific to Integrated Code 火 font generation.

	You can use this class to define font metadata, directory paths, locale and weight sets, and other package-wide configuration
	values. The class extends `hunterMakesPy.PackageSettings` [1] with font-specific fields and computes derived paths in
	`__post_init__`.

	Attributes
	----------
	achVendID : str = '1INT'
		OS/2 vendor identifier registered for Integrated Code fonts.
	fontFamily : str
		Display name for the font family.
	fontVersion : float
		Current version number written into compiled font metadata.
	theLocales : frozenset[str]
		Set of supported locale identifiers.
	theStyles : frozenset[str | None]
		Set of supported style identifiers, where `None` represents upright.
	theWeights : frozenset[str]
		Set of supported weight identifiers.
	unitsPerEm : int = 1000
		Units per em square for the font coordinate system.
	pathRoot : Path
		Root directory of the workspace, computed in `__post_init__`.
	pathAssets : Path
		Directory for output assets, computed in `__post_init__`.
	pathWorkbench : Path
		Directory for intermediate build artifacts, computed in `__post_init__`.
	pathWorkbenchFonts : Path
		Directory for intermediate font files, computed in `__post_init__`.
	filenameFontFamily : str
		Font family name without spaces, computed in `__post_init__`.

	References
	----------
	[1] hunterMakesPy.PackageSettings
		https://context7.com/hunterhogan/huntermakespy
	[2] Register a font vendor ID
		https://learn.microsoft.com/en-us/typography/vendors/register
	[3] Email
		"Registering Vendor ID 1INT.pdf"
	"""
	achVendID: str = '1INT'
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
