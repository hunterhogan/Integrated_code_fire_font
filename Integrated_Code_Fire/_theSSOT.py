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
	autohintOptionsDEFAULT
		Provide the `ttfautohint` options applied to prepared western fonts.
	autohintOptionsHARDCODED
		Supply the `ttfautohint` options that Fira Code uses.
	boxOfCheckIDsHinting
		Select the FontBakery checks for hinted western fonts.
	boxOfCheckIDsHintingHARDCODED
		Supply the FontBakery checks of TrueType hinting.
	boxOfCheckIDsMerged
		Select the FontBakery checks for merged fonts.
	boxOfCheckIDsMergedHARDCODED
		Supply the FontBakery checks of merging, metadata, hinting, and font validity.
	fontVersion
		Provide the font version used by the active configuration.
	fontVersionHARDCODED
		Supply the initial font version.
	headFlagsHinting
		Select the `head.flags` bits that describe TrueType instructions.
	headFlagsHintingHARDCODED
		Supply bits 2, 3, and 4 of `head.flags`.
	headFlagsIntegerPPEM
		Select the `head.flags` bit that forces integer ppem for hinted fonts.
	headFlagsIntegerPPEMHARDCODED
		Supply bit 3 of `head.flags`.
	languagesHARDCODED
		Map locale labels to language tags for font metadata.
	pathFilenameFiraCodeGlyphsDEFAULT
		Locate `FiraCode/FiraCode.glyphs` under the repository parent.
	pathFilenameFiraCode_build_ttfDEFAULT
		Locate `FiraCode/script/build_ttf.sh` under the repository parent.
	pathRootRepositories
		Select the parent directory used to locate font source checkouts.
	pathRootRepositoriesDEFAULT
		Use `/clones` on host `"duda"` and the project parent elsewhere.
	pathRootSourceHanMonoDEFAULT
		Locate the `source-han-mono` source checkout.
	rangesExcludeHARDCODED
		Supply spans of Unicode blocks omitted from CJK character selections.
	settingsPackage
		Provide the active font configuration, including the one-cell `⋯` mapping.
	subsetOptionsDEFAULT
		Provide the shared subsetting options used by the build entry point.
	subsetOptionsHARDCODED
		Configure retained layout features and discarded font tables and names.
	textShaping
		Provide programming text whose shaping in merged fonts must equal its shaping in Fira Code.
	textShapingHARDCODED
		Supply ligature and contextual-alternate sequences from Fira Code.
	unicodesExcludeHARDCODED
		Supply individual code points omitted from CJK character selections.
"""
from __future__ import annotations

from fontTools import subset
from hunterMakesPy import errorL33T, PackageSettings as humpy_PackageSettings
from hunterMakesPy.semiotics import inclusive
from pathlib import Path
from typing import Final, TYPE_CHECKING
import dataclasses
import socket

if TYPE_CHECKING:
	from ttfautohint.options import UserOptions

#======== Eliminate hardcoding, typically with a dynamic process or adding the value to `settingsPackage`. ========
# NOTE Fira Code `script/build_ttf.sh` runs `ttfautohint --no-info --ignore-restrictions`; `qualityControl` compares.
autohintOptionsHARDCODED: UserOptions = {
	'ignore_restrictions': True,
	'no_info': True,
}

# NOTE OpenType `head.flags` bits 2, 3, and 4 describe TrueType instructions; bit 3 forces integer ppem.
headFlagsHintingHARDCODED: int = 0b0001_1100
headFlagsIntegerPPEMHARDCODED: int = 0b0000_1000

fontVersionHARDCODED: float = 0.016
# TODO version update? ^^^^^^^^^^^^

# NOTE Each pair names the first and the last Unicode block of a span of consecutive blocks.
rangesExcludeHARDCODED: tuple[tuple[str, str], ...] = (
	('Basic Latin', 'Georgian'),
	('Ethiopic', 'Arrows'),
	('Miscellaneous Technical', 'Supplemental Punctuation'),
	('Alphabetic Presentation Forms', 'Alphabetic Presentation Forms'),
)
# NOTE The fullwidth forms of the ASCII characters `!` through `~`.
unicodesExcludeHARDCODED: frozenset[int] = frozenset(range(ord('\N{FULLWIDTH EXCLAMATION MARK}'), ord('\N{FULLWIDTH TILDE}') + inclusive))

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

boxOfCheckIDsHintingHARDCODED: tuple[str, ...] = ('integer_ppem_if_hinted', 'smart_dropout')
boxOfCheckIDsMergedHARDCODED: tuple[str, ...] = (
	'integer_ppem_if_hinted',
	'mandatory_glyphs',
	'name/char_restrictions',
	'name/family_and_style_max_length',
	'name/trailing_spaces',
	'opentype/font_version',
	'opentype/glyf_unused_data',
	'opentype/loca/maxp_num_glyphs',
	'opentype/maxadvancewidth',
	'opentype/name/empty_records',
	'opentype/name/match_familyname_fullfont',
	'opentype/postscript_name',
	'ots',
	'required_tables',
	'smart_dropout',
	'unique_glyphnames',
	'whitespace_widths',
)

# NOTE Sequences from the Fira Code README ligature showcase.
textShapingHARDCODED: str = (
	'-> => == === != !== <= >= <=> <!-- --> |> <| ||> www ** *** /* */ // /// :: ::: := =:= ..= .. ... ?. ?? ;; '
	'0xFF 1:2 a*b #{ #[ #( #? #_ ]# {| |} [| |] </ /> </> <> ~~> ~> ~- -~ ~@ <~> <~~ <<- <<= >>= >>- ++ +++ '
	'|||> <||| ||= |= ^= $> <$> <*> <+> <|> && ||'
)

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
	rangesExclude : tuple[tuple[str, str], ...]
		Spans of consecutive Unicode blocks that the CJK font does not contribute. Each pair names
		the first and the last block of a span. The defaults span Basic Latin through Georgian,
		Ethiopic through Arrows, Miscellaneous Technical through Supplemental Punctuation, and
		Alphabetic Presentation Forms.
	theLocales : frozenset[str]
		Locale labels. Defaults to `"Hong_Kong"`, `"Japan"`, `"Korea"`, `"Simplified_Chinese"`,
		and `"Taiwan"`.
	theStyles : frozenset[str | None] = frozenset(['Italic', None])
		Styles to build. An element of `None` selects upright style. The active configuration
		selects only upright style.
	theWeights : frozenset[str]
		Weight labels. Defaults to `"Bold"`, `"ExtraLight"`, `"SemiBold"`, `"Light"`, `"Medium"`,
		`"Retina"`, and `"Regular"`. The active configuration excludes `"ExtraLight"`.
	unicodesExclude : frozenset[int]
		Individual code points that the CJK font does not contribute. The defaults are the
		fullwidth forms of the ASCII characters `!` through `~`.
	unitsPerEm : int = 2000
		Target coordinate units per em for prepared fonts.
	width : int = 2400
		Advance width of full-width CJK glyphs, which occupy two 1200-unit Latin cells in the
		supplied configuration. Half-width CJK glyphs occupy one cell, `width // 2`.
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
	rangesExclude: tuple[tuple[str, str], ...] = rangesExcludeHARDCODED
	theLocales: frozenset[str] = frozenset(['Hong_Kong', 'Japan', 'Korea', 'Simplified_Chinese', 'Taiwan'])
	theStyles: frozenset[str | None] = frozenset(['Italic', None])
	theWeights: frozenset[str] = frozenset(['Bold', 'ExtraLight', 'SemiBold', 'Light', 'Medium', 'Retina', 'Regular'])
	unicodesExclude: frozenset[int] = unicodesExcludeHARDCODED
	unitsPerEm: int = 2000
	width: int = 2400

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
	# NOTE I assume you, the user, cloned this repository to the same parent directory as other repositories.
	pathRootRepositoriesDEFAULT = settingsPackage.pathRoot.parent

pathRootRepositories: Path = pathRootRepositoriesDEFAULT

pathFilenameFiraCodeGlyphsDEFAULT: Path = pathRootRepositories / 'FiraCode' / 'FiraCode.glyphs'
pathFilenameFiraCode_build_ttfDEFAULT: Path = pathRootRepositories / 'FiraCode' / 'script' / 'build_ttf.sh'
pathRootSourceHanMonoDEFAULT: Path = pathRootRepositories / "source-han-mono"

autohintOptionsDEFAULT: UserOptions = autohintOptionsHARDCODED
boxOfCheckIDsHinting: tuple[str, ...] = boxOfCheckIDsHintingHARDCODED
boxOfCheckIDsMerged: tuple[str, ...] = boxOfCheckIDsMergedHARDCODED
textShaping: str = textShapingHARDCODED
headFlagsHinting: int = headFlagsHintingHARDCODED
headFlagsIntegerPPEM: int = headFlagsIntegerPPEMHARDCODED
subsetOptionsDEFAULT: subset.Options = subsetOptionsHARDCODED
