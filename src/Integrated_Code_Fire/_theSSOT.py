from fontTools import subset
from hunterMakesPy import errorL33T, PackageSettings as humpy_PackageSettings
from pathlib import Path
from typing import Final
import dataclasses
import socket

#======== Eliminate hardcoding, typically with a dynamic process or adding the value to `settingsPackage`. ========
fontVersionHARDCODED: float = 0.014
# TODO version update? ^^^^^^^^^^^^

widthHalfSourceHanMonoHARDCODED: int = 667

subsetOptionsHARDCODED: subset.Options = subset.Options(
	drop_tables = ['vhea', 'vmtx', 'VORG', 'vert', 'vrt2'],
	glyph_names = False,
	layout_features = '*',
	name_IDs = '',
	passthrough_tables = True,
	symbol_cmap = True,
)

#======== Subclass `hunterMakesPy.PackageSettings` to add package-specific settings. ========

@dataclasses.dataclass
class PackageSettings(humpy_PackageSettings):
	"""Store package-specific settings for Integrated Code 火 font generation.

	You can use this class to define font metadata, locale coverage, layout dimensions, and derived workspace paths shared across
	the Integrated Code 火 assembly line. The class extends `hunterMakesPy.PackageSettings` [1] and computes derived path
	attributes in `__post_init__`.

	Parameters
	----------
	achVendID : str = '1INT'
		OS/2 vendor identifier written into compiled fonts.
	fontFamily : str = 'Integrated Code 火'
		Display name for the font family.
	fontVersion : float = errorL33T
		Version number written into compiled font metadata.
	theLocales : frozenset[str] = frozenset(['Hong_Kong', 'Japan', 'Korea', 'Simplified_Chinese', 'Taiwan'])
		Locale identifiers to build.
	theStyles : frozenset[str | None] = frozenset(['Italic', None])
		Style identifiers to build. The value `None` represents upright style.
	theWeights : frozenset[str] = frozenset(['Bold', 'ExtraLight', 'SemiBold', 'Light', 'Medium', 'Retina', 'Regular'])
		Weight identifiers to build.
	unitsPerEm : int = 2000
		Target units-per-em value for merged fonts.
	width : int = 2400
		Target glyph advance width used for merged fonts.

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
	unitsPerEm : int = 2000
		Units per em square for the font coordinate system.
	width : int = 2400
		Target glyph advance width for merged fonts.
	fontFamilyASCII : str
		ASCII-safe font family name used for filenames and asset names.
	pathRoot : Path
		Root directory of the workspace, computed in `__post_init__`.
	pathAssets : Path
		Directory for output assets, computed in `__post_init__`.
	pathWarehouse : Path
		Directory for persistent intermediate fonts, computed in `__post_init__`.
	pathWorkbench : Path
		Directory for intermediate assembly line artifacts, computed in `__post_init__`.
	pathWorkbenchFonts : Path
		Directory for intermediate font files, computed in `__post_init__`.

	References
	----------
	[1] hunterMakesPy.PackageSettings
		https://context7.com/hunterhogan/huntermakespy
	[2] Register a font vendor ID
		https://learn.microsoft.com/en-us/typography/vendors/register
	[3] Email
		"Registering Vendor ID 1INT.pdf"
	"""
	achVendID: Final[str] = '1INT'
	fontFamily: Final[str] = 'Integrated Code 火'
	fontVersion: float = errorL33T
	theLocales: frozenset[str] = frozenset(['Hong_Kong', 'Japan', 'Korea', 'Simplified_Chinese', 'Taiwan'])
	theStyles: frozenset[str | None] = frozenset(['Italic', None])
	theWeights: frozenset[str] = frozenset(['Bold', 'ExtraLight', 'SemiBold', 'Light', 'Medium', 'Retina', 'Regular'])
	unitsPerEm: int = 2000
	width: int = 2400

	fontFamilyASCII: str = dataclasses.field(init=False)

	pathRoot: Path = dataclasses.field(init=False)
	pathAssets: Path = dataclasses.field(init=False)
	pathWarehouse: Path = dataclasses.field(init=False)
	pathWorkbench: Path = dataclasses.field(init=False)
	pathWorkbenchFonts: Path = dataclasses.field(init=False)

	def __post_init__(self, identifierPackageFALLBACK: str) -> None:
		super().__post_init__(identifierPackageFALLBACK)

		self.pathRoot = self.pathPackage.parent.parent
		self.pathAssets = self.pathRoot / 'assets'
		self.pathWarehouse = self.pathRoot / 'warehouse'
		self.pathWorkbench = self.pathRoot / 'workbench'
		self.pathWorkbenchFonts = self.pathWorkbench / 'fonts'

		self.fontFamilyASCII = self.fontFamily.replace('火', 'Fire')

#-------- Package settings. ---------------------------------------------

fontVersion: float = fontVersionHARDCODED
settingsPackage = PackageSettings('Integrated_Code_Fire'
	, fontVersion = fontVersion
	, theLocales = frozenset(['Hong_Kong', 'Japan', 'Korea', 'Simplified_Chinese', 'Taiwan'])
	, theStyles = frozenset([None])
	, theWeights = frozenset(['Bold', 'SemiBold', 'Light', 'Medium', 'Retina', 'Regular'])
)

if socket.gethostname() == 'duda':
	pathRootRepositoriesDEFAULT: Path = Path('/clones')
else:
	# NOTE I assume you cloned this repository to the same parent directory as other repositories.
	pathRootRepositoriesDEFAULT = settingsPackage.pathRoot.parent

pathRootRepositories: Path = pathRootRepositoriesDEFAULT

pathFilenameFiraCodeGlyphsDEFAULT: Path = pathRootRepositories / 'FiraCode' / 'FiraCode.glyphs'
pathRootSourceHanMonoDEFAULT: Path = pathRootRepositories / "source-han-mono"

subsetOptionsDEFAULT: subset.Options = subsetOptionsHARDCODED

incrementHARDCODED: int = (settingsPackage.width - settingsPackage.unitsPerEm) // 2
"""Provide the per-side width increment used when widening Source Han Mono glyphs.

The `incrementHARDCODED` value equals half of `settingsPackage.width - settingsPackage.unitsPerEm`. The assembly line uses
`incrementHARDCODED` when `machinistModifiesSideBearings` [1] widens retained CJK glyphs after subsetting.

References
----------
[1] Integrated_Code_Fire.machineShop.machinistModifiesSideBearings
	Internal package reference.
"""
