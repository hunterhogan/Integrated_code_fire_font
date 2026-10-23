"""I use this module to share font settings, source locations, and subsetting options.

(AI generated docstring)

The active `settingsPackage` selects five locales, upright style, and six matching western and
CJK weights. A separately constructed `PackageSettings` includes italic style and the CJK-only
`"ExtraLight"` weight as well. Build operations can therefore have broader selection defaults
than the active release configuration.

Contents
--------
Classes
	PackageSettings
		Store font settings and derive workspace locations.
Settings
	fontVersion
		Provide the font version used by the active configuration.
	fontVersionHARDCODED
		Supply the initial font version.
	languagesHARDCODED
		Map locale labels to language tags for font metadata.
	pathFilenameFiraCodeGlyphsDEFAULT
		Locate `FiraCode/FiraCode.glyphs` under the repository parent.
	pathRootRepositories
		Select the parent directory used to locate font source checkouts.
	pathRootRepositoriesDEFAULT
		Use `/clones` on host `"duda"` and the project parent elsewhere.
	pathRootSourceHanMonoDEFAULT
		Locate the `source-han-mono` source checkout.
	rangeIncludeHARDCODED
		Supply inclusive Unicode bounds for CJK character selections.
	rangesExcludeHARDCODED
		Supply inclusive Unicode intervals omitted from CJK character selections.
	settingsPackage
		Provide the active font configuration, including the one-cell `⋯` mapping.
	subsetOptionsDEFAULT
		Provide the shared subsetting options used by the build entry point.
	subsetOptionsHARDCODED
		Configure retained layout features and discarded font tables and names.
	widthHalfSourceHanMonoHARDCODED
		Supply the advance width used to recognize half-width CJK source glyphs.
"""
from __future__ import annotations

from fontTools import subset
from hunterMakesPy import errorL33T, PackageSettings as humpy_PackageSettings
from pathlib import Path
from typing import Final
import dataclasses
import socket

#======== Eliminate hardcoding, typically with a dynamic process or adding the value to `settingsPackage`. ========
fontVersionHARDCODED: float = 0.015
# TODO version update? ^^^^^^^^^^^^

# TODO These ranges need to be less hardcoded-ish and/or more semantic (e.g., what is 0x1200?)
rangeIncludeHARDCODED: tuple[int, int] = (0x1100, 0xFFFF)
rangesExcludeHARDCODED: tuple[tuple[int, int], ...] = ((0x1200, 0x21FF), (0x2300, 0x2E7F), (0xFF01, 0xFF5E))

languagesHARDCODED: dict[str, str] = {
	'Hong_Kong': 'zh-Hant',
	'Japan': 'ja',
	'Korea': 'ko',
	'Simplified_Chinese': 'zh',
	'Taiwan': 'zh-Hant',
}

subsetOptionsHARDCODED: subset.Options = subset.Options(
	drop_tables=['vhea', 'vmtx', 'VORG', 'vert', 'vrt2'],
	glyph_names=False,
	layout_features='*',
	name_IDs='',
	passthrough_tables=True,
	symbol_cmap=True,
)

widthHalfSourceHanMonoHARDCODED: int = 667

#======== Subclass `hunterMakesPy.PackageSettings` to add package-specific settings. ========

@dataclasses.dataclass
class PackageSettings(humpy_PackageSettings):
	"""Configure font metadata, character coverage, dimensions, and build directories.

	(AI generated docstring)

	You can construct a configuration with the dataclass fields below and the inherited package
	location settings. The generated constructor accepts fields with defaults; the workspace paths
	and ASCII family name are derived after construction. Build operations share `settingsPackage`;
	constructing another configuration does not replace `settingsPackage`.

	Attributes
	----------
	achVendID : str = '1INT'
		Font vendor identifier written to the `OS/2` table.
	cmapUpdates : dict[int, str] = {}
		Unicode code points mapped to existing western glyph names during preparation. Each new
		configuration receives its own dictionary. The active configuration maps U+22EF to
		`"ellipsis"`.
	fontFamily : str = 'Integrated Code 火'
		Family name used to construct installed font names.
	fontVersion : float = errorL33T
		Font revision and version text. The active configuration supplies the module's
		`fontVersion` instead of the error sentinel.
	languages : dict[str, str]
		Independent copy of `languagesHARDCODED`, mapping each locale to a language tag.
	rangeInclude : tuple[int, int] = (0x1100, 0xFFFF)
		Inclusive Unicode interval eligible for the CJK `.unicodes` selections.
	rangesExclude : tuple[tuple[int, int], ...]
		Inclusive intervals removed from the CJK `.unicodes` selections. The defaults are
		`(0x1200, 0x21FF)`, `(0x2300, 0x2E7F)`, and `(0xFF01, 0xFF5E)`.
	theLocales : frozenset[str]
		Locale labels. Defaults to `"Hong_Kong"`, `"Japan"`, `"Korea"`, `"Simplified_Chinese"`,
		and `"Taiwan"`.
	theStyles : frozenset[str | None] = frozenset(['Italic', None])
		Styles to build. An element of `None` selects upright style. The active configuration
		selects only upright style.
	theWeights : frozenset[str]
		Weight labels. Defaults to `"Bold"`, `"ExtraLight"`, `"SemiBold"`, `"Light"`, `"Medium"`,
		`"Retina"`, and `"Regular"`. The active configuration excludes `"ExtraLight"`.
	unitsPerEm : int = 2000
		Target coordinate units per em for prepared fonts.
	width : int = 2400
		Width used to derive the CJK side bearing adjustment. Full-width CJK glyphs use two
		1200-unit Latin cells in the supplied configuration.
	widthHalfSourceHanMono : int = 667
		Advance width identifying glyphs that receive half the usual side bearing adjustment.
	fontFamilyASCII : str
		Family name with `"火"` replaced by `"Fire"`, derived after construction.
	pathRoot : Path
		Project directory containing the installed package directory.
	pathAssets : Path
		Release archive directory, `pathRoot / 'assets'`.
	pathWarehouse : Path
		Persistent prepared-font directory, `pathRoot / 'warehouse'`.
	pathWorkbench : Path
		Temporary build directory, `pathRoot / 'workbench'`.
	pathWorkbenchFonts : Path
		Staged-font directory, `pathWorkbench / 'fonts'`.
	"""
	achVendID: Final[str] = '1INT'
	cmapUpdates: dict[int, str] = dataclasses.field(default_factory=dict[int, str])
	fontFamily: Final[str] = 'Integrated Code 火'
	fontVersion: float = errorL33T
	languages: dict[str, str] = dataclasses.field(default_factory=languagesHARDCODED.copy)
	rangeInclude: tuple[int, int] = rangeIncludeHARDCODED
	rangesExclude: tuple[tuple[int, int], ...] = rangesExcludeHARDCODED
	theLocales: frozenset[str] = frozenset(['Hong_Kong', 'Japan', 'Korea', 'Simplified_Chinese', 'Taiwan'])
	theStyles: frozenset[str | None] = frozenset(['Italic', None])
	theWeights: frozenset[str] = frozenset(['Bold', 'ExtraLight', 'SemiBold', 'Light', 'Medium', 'Retina', 'Regular'])
	unitsPerEm: int = 2000
	width: int = 2400
	widthHalfSourceHanMono: int = widthHalfSourceHanMonoHARDCODED

	fontFamilyASCII: str = dataclasses.field(init=False)

	pathRoot: Path = dataclasses.field(init=False)
	pathAssets: Path = dataclasses.field(init=False)
	pathWarehouse: Path = dataclasses.field(init=False)
	pathWorkbench: Path = dataclasses.field(init=False)
	pathWorkbenchFonts: Path = dataclasses.field(init=False)

	def __post_init__(self, identifierPackageFALLBACK: str) -> None:
		"""I use this initialization step to derive font names and build directories.

		(AI generated docstring)

		Parameters
		----------
		identifierPackageFALLBACK : str
			Package identifier used when the inherited configuration has no package identifier.

		Input Mutation
		--------------
		The configuration receives its package location, ASCII font family name, and workspace paths.
		The workspace directories are not created.
		"""
		super().__post_init__(identifierPackageFALLBACK)

		self.pathRoot = self.pathPackage.parent
		self.pathAssets = self.pathRoot / 'assets'
		self.pathWarehouse = self.pathRoot / 'warehouse'
		self.pathWorkbench = self.pathRoot / 'workbench'
		self.pathWorkbenchFonts = self.pathWorkbench / 'fonts'

		self.fontFamilyASCII = self.fontFamily.replace('火', 'Fire')

	@property
	def incrementSourceHanMono(self) -> int:
		"""Obtain the horizontal adjustment for each side of a full-width CJK glyph.

		(AI generated docstring)

		Returns
		-------
		incrementSourceHanMono : int
			Half of `width - unitsPerEm`, rounded down to a whole font unit. The default dimensions
			produce `200` font units per side.

		See Also
		--------
		`Integrated_Code_Fire.machineShop.machinistModifiesSideBearings`
			Apply the adjustment to horizontal advance and side bearing values.
		"""
		return (self.width - self.unitsPerEm) // 2

#-------- Package settings. ---------------------------------------------

fontVersion: float = fontVersionHARDCODED
settingsPackage = PackageSettings('Integrated_Code_Fire'
	, fontVersion=fontVersion
	, cmapUpdates={0x22EF: 'ellipsis'}
	, theLocales=frozenset(['Hong_Kong', 'Japan', 'Korea', 'Simplified_Chinese', 'Taiwan'])
	, theStyles=frozenset([None])
	, theWeights=frozenset(['Bold', 'SemiBold', 'Light', 'Medium', 'Retina', 'Regular'])
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
