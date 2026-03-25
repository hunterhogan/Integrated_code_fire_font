"""Manage font metadata, locale and weight mappings, filename generation, and character subset configuration.

(AI generated docstring)

You can use this module to access locale and weight identifier mappings, generate standardized filename stems, create
OpenType `TTFont` [1] name record metadata, load character subset definitions, and update font file metadata. The module
provides the core configuration and metadata management functions used throughout the Integrated Code 火 assembly line,
using utilities from `hunterMakesPy` [2] and `glyphsLib` [3].

Contents
--------
Functions
	archivistGetsGlyphsUnicode
		Get Unicode codepoints present in a Glyphs source file.
	archivistGetsLocales
		Get mapping from locale identifiers to `LocaleIn` instances.
	archivistGetsSubsetCharacters
		Load character subset definitions from metadata files for all locale and style combinations.
	archivistGetsWeights
		Get mapping from weight identifiers to `WeightIn` instances.
	archivistMakesAllCharacterSubsets
		Generate character subset files for all locale and style combinations.
	archivistMakesCharacterSubsets
		Generate glyph ID and Unicode subset files from a UTF-32 character map.
	archivistMakesFilenameStem
		Generate filename stems from font family, locale, style, and weight components.
	archivistMakesNameIDMetadata
		Make OpenType name record mapping for a given weight.
	archivistUpdatesFontFileMetadata
		Update OpenType metadata in a font file on disk.
	archivistUpdatesMetadata
		Update OpenType metadata in an open `TTFont` instance.
	between吗
		Return `True` when `comparand` satisfies `floor <= comparand <= ceiling`.

Variables
	lookupAFDKOCharacterSet
		Mapping from locale identifiers to AFDKO character set identifiers.
	name
		Name table platform and encoding identifiers.

References
----------
[1] fontTools.ttLib.TTFont
	https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html
[2] hunterMakesPy
	https://context7.com/hunterhogan/huntermakespy
[3] glyphsLib
	https://github.com/googlefonts/glyphsLib

"""
from fontTools import subset
from fontTools.ttLib import TTFont
from humpy_cytoolz.dicttoolz import keyfilter, keymap, valfilter
from humpy_cytoolz.functoolz import complement, compose, curry as syntacticCurry
from hunterMakesPy import Ordinals
from hunterMakesPy.filesystemToolkit import writeStringToHere
from hunterMakesPy.semiotics import ansiColorReset, AnsiColors
from Integrated_Code_Fire import (
	LocaleIn, PackageSettings, pathFilenameFiraCodeGlyphsDEFAULT, pathRootSourceHanMonoDEFAULT, settingsPackage, WeightIn)
from itertools import filterfalse, product as CartesianProduct
from pathlib import Path
from typing import Literal, TYPE_CHECKING
import glyphsLib
import sys

if TYPE_CHECKING:
	from collections.abc import Container, Iterable, Iterator
	from hunterMakesPy import identifierDotAttribute
	from pathlib import Path

ansiColors = AnsiColors()

#======== Boolean antecedents ================================================

@syntacticCurry
def between吗[小于: Ordinals](floor: 小于, ceiling: 小于, comparand: 小于) -> bool:
	"""Return `True` when `comparand` satisfies `floor <= comparand <= ceiling`.

	Parameters
	----------
	floor : Ordinals
		Lower bound of the range, inclusive.
	ceiling : Ordinals
		Upper bound of the range, inclusive.
	comparand : Ordinals
		Value to test against `floor` and `ceiling`.

	Returns
	-------
	isBetween : bool
		`True` when `floor <= comparand <= ceiling`, `False` otherwise.

	"""
	return floor <= comparand <= ceiling

#======== Settings that have not yet been obsoleted or found their home, such as a dataclass or function. ========

name: dict[str, int] = {
	'langID' : 0x0409,
	'platEncID' : 1,
	'platformID' : 3,
}
"""Provide name table platform and encoding identifiers for Windows Unicode BMP name records.

(AI generated docstring)

The `name` mapping provides the `platformID`, `platEncID`, and `langID` values used when writing
OpenType name records via `archivistUpdatesMetadata` [1].

References
----------
[1] Integrated_Code_Fire.archivist.archivistUpdatesMetadata

"""

# TODO I'd rather get this from an authoritative source.
lookupAFDKOCharacterSet: dict[str, str] = {'HK': '2', 'JP': '1', 'KR': '3', 'CN': '25', 'TW': '2'}
"""Map locale identifiers to AFDKO makeotf character set identifiers.

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

#======== Font-construction functions ===============================================

def archivistGetsLocales() -> dict[str, LocaleIn]:
	"""Get mapping from locale identifiers to `LocaleIn` instances.

	(AI generated docstring)

	You can obtain the complete mapping of supported locale identifiers to `LocaleIn` [1] instances
	containing both ASCII and Unicode representations. The returned mapping keys correspond to the locale identifiers in
	`settingsPackage.theLocales` [2].

	Returns
	-------
	dictionaryLocales : dict[str, LocaleIn]
		Mapping from locale identifier to `LocaleIn` instance.

	References
	----------
	[1] Integrated_Code_Fire.LocaleIn
	[2] Integrated_Code_Fire.settingsPackage

	"""
	return {
		'Hong_Kong': LocaleIn('Hong_Kong', '香港', SourceHanMono='HK', SourceHanMonoOTC='HC'),
		'Japan': LocaleIn('Japan', '日本', SourceHanMono='JP', SourceHanMonoOTC='J'),
		'Korea': LocaleIn('Korea', '한국인', SourceHanMono='KR', SourceHanMonoOTC='K'),
		'Simplified_Chinese': LocaleIn('Simplified_Chinese', '简化字', SourceHanMono='CN', SourceHanMonoOTC='SC'),
		'Taiwan': LocaleIn('Taiwan', '台灣', SourceHanMono='TW', SourceHanMonoOTC='TC'),
	}

def archivistGetsWeights() -> dict[str, WeightIn]:
	"""Get mapping from weight identifiers to `WeightIn` instances.

	(AI generated docstring)

	You can obtain the complete mapping of supported weight identifiers to `WeightIn` [1] instances
	containing weight names for all font families. The returned mapping keys are Source Han Mono weight names and correspond to
	the weight identifiers in `settingsPackage.theWeights` [2].

	Returns
	-------
	dictionaryWeights : dict[str, WeightIn]
		Mapping from weight identifier to `WeightIn` instance.

	References
	----------
	[1] Integrated_Code_Fire.WeightIn
	[2] Integrated_Code_Fire.settingsPackage

	"""
	return {
		'SemiBold': WeightIn(IntegratedCode火='SemiBold', FiraCode='SemiBold', fontFamilyScaled='SemiBold', fontFamilyCID='Bold', SourceHanMono='Bold'),
		'ExtraLight': WeightIn(IntegratedCode火='', FiraCode='', fontFamilyScaled='', fontFamilyCID='ExtraLight', SourceHanMono='ExtraLight'),
		'Bold': WeightIn(IntegratedCode火='Bold', FiraCode='Bold', fontFamilyScaled='Bold', fontFamilyCID='Heavy', SourceHanMono='Heavy'),
		'Light': WeightIn(IntegratedCode火='Light', FiraCode='Light', fontFamilyScaled='Light', fontFamilyCID='Light', SourceHanMono='Light'),
		'Medium': WeightIn(IntegratedCode火='Medium', FiraCode='Medium', fontFamilyScaled='Medium', fontFamilyCID='Medium', SourceHanMono='Medium'),
		'Retina': WeightIn(IntegratedCode火='Retina', FiraCode='Retina', fontFamilyScaled='Retina', fontFamilyCID='Normal', SourceHanMono='Normal'),
		'Regular': WeightIn(IntegratedCode火='Regular', FiraCode='Regular', fontFamilyScaled='Regular', fontFamilyCID='Regular', SourceHanMono='Regular'),
	}

def archivistMakesFilenameStem(fontFamily: str | None = None, locale: str | None = None, style: str | None = None, weight: str | None = None, separator: str = '.') -> str:
	"""Make filename stems by joining `fontFamily`, `locale`, `style`, and `weight` components.

	(AI generated docstring)

	You can create standardized filename stems from font components. The function filters out `None` values
	and joins the remaining components with `separator`. Common suffixes appended to the returned stems include `cidfont.ps`,
	`cidfontinfo`, `features`, `gids`, `otf`, `sequences`, `ttf`, `unicodes`, `UTF32-map`, and `UTF32-H`.

	Parameters
	----------
	fontFamily : str | None = None
		Font family identifier such as `'SourceHanMono'` or `'IntegratedCode火'`.
	locale : str | None = None
		Locale identifier such as `'Hong_Kong'`, `'Japan'`, or `'简化字'`.
	style : str | None = None
		Style identifier such as `'Italic'`, or `None` for upright.
	weight : str | None = None
		Weight identifier such as `'Bold'`, `'Regular'`, or `'SemiBold'`.
	separator : str = '.'
		String used to join components.

	Returns
	-------
	filenameStem : str
		Filename stem created by joining non-`None` components with `separator`.

	Examples
	--------
	Generate CID font glyphs filename stem:

	>>> archivistMakesFilenameStem('SourceHanMono', 'Japan', None, 'Bold')
	'SourceHanMono.Japan.Bold'

	Generate metadata filename stem without weight:

	>>> archivistMakesFilenameStem('SourceHanMono', 'Simplified_Chinese', 'Italic')
	'SourceHanMono.Simplified_Chinese.Italic'

	Generate Integrated Code 火 filename stem with no separator:

	>>> archivistMakesFilenameStem('IntegratedCode火', '日本', None, 'SemiBold', '')
	'IntegratedCode火日本SemiBold'

	Generate font family name with space separator:

	>>> archivistMakesFilenameStem('Integrated Code 火', '台灣', separator=' ')
	'Integrated Code 火 台灣'

	"""
	notNone: None = None # Ironic, no?
	return separator.join(filter(notNone, [fontFamily, locale, style, weight]))

def archivistMakesNameIDMetadata(weight: str, filenameFontFamily: str, fontFamily: str) -> dict[int, str]:
	"""Make a name record mapping for a given `weight`.

	(AI generated docstring)

	This function returns a `dict[int, str]` that maps a TrueType name record identifier to a name record
	value. The returned mapping is used by `archivistUpdatesFontFileMetadata` [2] to update `TTFont['name']` [1].

	Parameters
	----------
	weight : str
		Weight identifier used to populate name records 2 and 17.
	filenameFontFamily : str
		Font family identifier used in filename-compatible name records (name IDs 3 and 6).
	fontFamily : str
		Human-readable font family name used in user-facing name records (name IDs 1, 4, and 16).

	Returns
	-------
	dictionaryNameIDToNameRecordValue : dict[int, str]
		Mapping from name record identifier to name record value.

	References
	----------
	[1] fontTools.ttLib.TTFont
		https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html
	[2] Integrated_Code_Fire.archivist.archivistUpdatesFontFileMetadata

	"""
	return {
		0: 'Copyright 2026 Hunter Hogan (https://www.patreon.com/integrated), with Reserved Font Name \u2018Integrated.\u2019',
		1: fontFamily,
		2: weight,
		3: f"{settingsPackage.fontVersion};{settingsPackage.achVendID};{filenameFontFamily}{weight.replace(' ', '')}",
		4: f"{fontFamily} {weight}",
		5: f"Version {settingsPackage.fontVersion}",
		6: f"{filenameFontFamily}{weight.replace(' ', '')}",
		7: 'Fira Mono is a trademark of The Mozilla Corporation. Source is a trademark of Adobe in the United States and/or other countries.',
		8: 'Carrois Corporate; Edenspiekermann AG; Nikita Prokopov; Adobe',
		9: 'Carrois Corporate; Edenspiekermann AG; Nikita Prokopov; Ryoko NISHIZUKA 西塚涼子 (kana, bopomofo & ideographs); Paul D. Hunt (Latin, Italic, Greek & Cyrillic); Sandoll Communications 산돌커뮤니케이션, Soo-young JANG 장수영 & Joo-yeon KANG 강주연 (hangul elements, letters & syllables)',
		10: 'For Adobe: Dr. Ken Lunde (project architect, glyph set definition & overall production); Masataka HATTORI 服部正貴 (production & ideograph elements)',
		11: 'https://www.patreon.com/integrated',
		12: 'https://tonsky.me http://www.adobe.com/type/',
		13: 'This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: http://scripts.sil.org/OFL',
		14: 'http://scripts.sil.org/OFL',
		16: fontFamily,
		17: weight,
	}

def archivistUpdatesFontFileMetadata(pathFilename: Path, nameIDmetadata: dict[int, str]) -> Path:
	"""Update OpenType metadata in a font file on disk.

	(AI generated docstring)

	You can update OpenType name records and other metadata in a font file. The function opens the font file,
	calls `archivistUpdatesMetadata` [1], saves the updated font, and returns the original path.

	Parameters
	----------
	pathFilename : Path
		Path to font file to update.
	nameIDmetadata : dict[int, str]
		Mapping from OpenType name record identifier to name record value.

	Returns
	-------
	pathFilename : Path
		Path to the updated font file, identical to the input `pathFilename`.

	References
	----------
	[1] Integrated_Code_Fire.archivist.archivistUpdatesMetadata
	[2] fontTools.ttLib.TTFont
		https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html

	"""
	with TTFont(pathFilename) as ttFont:
		archivistUpdatesMetadata(ttFont, nameIDmetadata)
		ttFont.save(pathFilename)
	return pathFilename

def archivistUpdatesMetadata(ttFont: TTFont, nameIDmetadata: dict[int, str]) -> None:
	"""Update OpenType metadata in an open `TTFont` instance.

	(AI generated docstring)

	You can update font version, vendor ID, and name records in an open `TTFont` [1] instance. The function
	sets `fontRevision` in the `head` table, `achVendID` in the `OS/2` table, and all name records provided in `nameIDmetadata`.

	Parameters
	----------
	ttFont : fontTools.ttLib.TTFont
		Open `TTFont` instance to update.
	nameIDmetadata : dict[int, str]
		Mapping from OpenType name record identifier to name record value.

	References
	----------
	[1] fontTools.ttLib.TTFont
		https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html
	[2] Integrated_Code_Fire.settingsPackage

	"""
	ttFont['head'].fontRevision = settingsPackage.fontVersion  # ty:ignore[unresolved-attribute]
	ttFont['OS/2'].achVendID = settingsPackage.achVendID  # ty:ignore[unresolved-attribute]
	for nameID in nameIDmetadata:
		ttFont['name'].setName(nameIDmetadata[nameID], nameID, name['platformID'], name['platEncID'], name['langID'])

def Z0Z_make_afdkoOptions(pathRoot: Path, fontFamilyCID: str = 'SourceHanMono', locale: str = 'Simplified_Chinese', style: Literal['Italic'] | None = None, weight: str = 'Regular') -> tuple[str, ...]:
	"""Prototype."""
	styleA: Literal['.It', ''] = ''
	styleB: Literal['It', ''] = ''
	styleC: Literal['_italic', ''] = ''
	if style == 'Italic':
		styleA = '.It'
		styleB = 'It'
		styleC = '_italic'

	dictionaryLocales: dict[str, LocaleIn] = archivistGetsLocales()
	dictionaryWeights: dict[str, WeightIn] = archivistGetsWeights()
	if fontFamilyCID == 'SourceHanMono':
		aLocaleOTC: str = dictionaryLocales[locale].SourceHanMonoOTC
		aLocale: str = dictionaryLocales[locale].SourceHanMono
		aWeight: str = dictionaryWeights[weight].SourceHanMono
	else:
		aLocaleOTC = dictionaryLocales[locale].ascii
		aLocale = dictionaryLocales[locale].ascii
		aWeight = dictionaryWeights[weight].fontFamilyCID
		message: str = f"I received {fontFamilyCID = }. This is a reminder to check the flow from start to finish."
		sys.stdout.write(f"{ansiColors.CyanOnMagenta}{message}{ansiColorReset}\n")

	options: list[str] =[
		'-f',	str(pathRoot / aWeight / 'OTC' / f"cidfont.ps.OTC{styleA}.{aLocaleOTC}"),
		'-ff',	str(pathRoot / aWeight / 'OTC' / f"features.OTC{styleA}.{aLocaleOTC}"),

		'-ch',	str(pathRoot / f"Uni{fontFamilyCID}{styleB}{aLocale}-UTF32-H"),
		'-ci',	str(pathRoot / f"{fontFamilyCID}_{aLocale}_sequences{styleC}.txt"),
		'-mf',	str(pathRoot / 'FontMenuNameDB'),

		'-cs',	lookupAFDKOCharacterSet[aLocale],
	]

	if style == 'Italic':
		options.append('-i')

	return tuple(options)

#======== Rarely Used Functions ========

def archivistGetsSubsetCharacters(fontFamilyCID: str = 'SourceHanMono', theLocales: Iterable[str] | None = None, theStyles: Iterable[str | None] | None = None) -> dict[identifierDotAttribute, dict[str, list[int]]]:
	# TODO At the very least, store this data in Python structures.
	"""Load character subset definitions from metadata files for all locale and style combinations.

	(AI generated docstring)

	You can load glyph IDs and Unicode codepoints for each `fontFamilyCID` locale and style combination. The
	function reads `.gids` and `.unicodes` files from the metadata directory and returns a nested mapping from filename stem to
	format identifier to character identifier list.

	Parameters
	----------
	fontFamilyCID : str = 'SourceHanMono'
		Font family identifier used to locate metadata files.
	theLocales : Iterable[str] | None = None
		Locale identifiers to process, or `None` to use `settingsPackage.theLocales` [2].
	theStyles : Iterable[str | None] | None = None
		Style identifiers to process, or `None` to use `settingsPackage.theStyles` [2].

	Returns
	-------
	subsetCharacters : dict[identifierDotAttribute, dict[str, list[int]]]
		Nested mapping from filename stem to format identifier to list of character identifiers. Format identifiers are `'gids'`
		and `'unicodes'`. Character identifiers are integers representing glyph IDs or Unicode codepoints.

	References
	----------
	[1] fontTools.subset
		https://fonttools.readthedocs.io/en/latest/subset/index.html
	[2] Integrated_Code_Fire.settingsPackage

	"""
	subsetCharacters: dict[identifierDotAttribute, dict[str, list[int]]] = {}

	pathDatacenter: Path = settingsPackage.pathPackage / 'dataCenter'
	dictionaryLocales: dict[str, LocaleIn] = archivistGetsLocales()

	for locale, style in CartesianProduct(theLocales or settingsPackage.theLocales, theStyles or settingsPackage.theStyles):
		filenameStem: identifierDotAttribute = archivistMakesFilenameStem(fontFamilyCID, dictionaryLocales[locale].ascii, style)
		subsetCharacters[filenameStem] = {}

		formatCharacterIDs: str = 'gids'
		pathFilename: Path = pathDatacenter / f"{filenameStem}.{formatCharacterIDs}"
		subsetCharacters[filenameStem][formatCharacterIDs] = subset.parse_gids(','.join(pathFilename.read_text('utf-8').splitlines()))

		formatCharacterIDs: str = 'unicodes'
		pathFilename: Path = pathDatacenter / f"{filenameStem}.{formatCharacterIDs}"
		subsetCharacters[filenameStem][formatCharacterIDs] = subset.parse_unicodes(','.join(pathFilename.read_text('utf-8').splitlines()))

	return subsetCharacters

def archivistGetsGlyphsUnicode(pathFilename: Path) -> frozenset[int]:
	"""Get Unicode codepoints present in a Glyphs source file.

	Load a Glyphs source file [1] from `pathFilename` and return a `frozenset` of all Unicode
	codepoints referenced by glyphs in the file.

	Parameters
	----------
	pathFilename : Path
		Path to the Glyphs source file.

	Returns
	-------
	unicodeGlyphs : frozenset[int]
		Unicode codepoints present in the Glyphs source file at `pathFilename`.

	References
	----------
	[1] glyphsLib
		https://github.com/googlefonts/glyphsLib

	"""
	return frozenset([int(unicode, 16) for glyph in glyphsLib.load(pathFilename).glyphs for unicode in glyph.unicodes])

def archivistMakesCharacterSubsets(pathFilename: Path, pathWrite: Path, filenameStemWrite: str, unicodeExclude: Container[int] = frozenset(), gidsExclude: Container[str] = frozenset()) -> list[Path]:
	"""Generate glyph ID and Unicode subset files from a UTF-32 character map.

	(AI generated docstring)

	You can create `.gids` and `.unicodes` subset files from a `.UTF32-map` character map file. The function
	filters out codepoints in `unicodeExclude` and glyph IDs in `gidsExclude`, then applies hardcoded range
	filters to produce glyph ID and Unicode subset lists suitable for font subsetting operations.

	Parameters
	----------
	pathFilename : Path
		Path to `.UTF32-map` character map file.
	pathWrite : Path
		Directory path where the generated subset files are written.
	filenameStemWrite : str
		Filename stem for the output `.gids` and `.unicodes` files.
	unicodeExclude : Container[int] = frozenset()
		Unicode codepoints to exclude from all subsets.
	gidsExclude : Container[str] = frozenset()
		Glyph IDs to exclude from all subsets.

	Returns
	-------
	listPathFilenames : list[Path]
		List containing paths to generated `.gids` and `.unicodes` files.

	References
	----------
	[1] hunterMakesPy.filesystemToolkit.writeStringToHere
		https://context7.com/hunterhogan/huntermakespy

	"""
	def unicodesToInt(unicodeHexadecimalAsStr: str, /) -> int:
		return int(unicodeHexadecimalAsStr.strip('<>'), 16)

	listPathFilenames: list[Path] = []

	# TODO No one in the entire universe has created a function to load these values from these super-common files?!
	unicodeTOgid: dict[int, str] = keyfilter(complement(unicodeExclude.__contains__)
		, keymap(unicodesToInt
			, valfilter(complement(gidsExclude.__contains__)
				, dict(map(compose(tuple[str, str], str.split), pathFilename.read_text('utf-8').splitlines())))))

	# TODO I think tlz.keyfilter might have a bug.
	# qq = keyfilter(lambda u: 65535 < u, unicodeTOgid)  # noqa: ERA001
	# qq = itemfilter(lambda ug: 65535 < ug[0], unicodeTOgid)  # noqa: ERA001
	# ww = qq.values()  # noqa: ERA001
	# gids: list[str] = sorted(ww, key=int)  # noqa: ERA001
	# gids: list[str] = sorted(keyfilter((65535).__ge__, unicodeTOgid).values(), key=int)  # noqa: ERA001
	gids: list[str] = sorted({gid for unicode, gid in unicodeTOgid.items() if 0xFFFF < unicode}, key=int)  # ty:ignore[invalid-assignment]
	gids.append('')

	suffix: str = 'gids'
	listPathFilenames.append(writeStringToHere('\n'.join(gids), pathWrite / f"{filenameStemWrite}.{suffix}"))

	# TODO These ranges need to be less hardcoded-ish and/or more semantic (e.g., what is 0x1200?)  # noqa: ERA001
	# TODO Configuration settings.
	unicodes: Iterator[str] = map(hex
		, filterfalse(between吗(0x1200, 0x2E7F)
		, filterfalse(between吗(0xFF01, 0xFF5E)
			, filter(between吗(0x1100, 0xFFFF), unicodeTOgid.keys())
	)))

	suffix: str = 'unicodes'
	listPathFilenames.append(writeStringToHere('\n'.join(unicodes) + '\n', pathWrite / f"{filenameStemWrite}.{suffix}"))

	return listPathFilenames

def archivistMakesAllCharacterSubsets(pathMetadata: Path, fontFamilyCID: str = 'SourceHanMono', theLocales: Iterable[str] | None = None, theStyles: Iterable[str | None] | None = None, unicodeExclude: frozenset[int] = frozenset()) -> list[Path]:
	"""Generate character subset files for all locale and style combinations.

	(AI generated docstring)

	You can create `.gids` and `.unicodes` subset files for all combinations of locales and styles. The
	function invokes `archivistMakesCharacterSubsets` [1] for each `.UTF32-map` file found in the metadata directory.

	Parameters
	----------
	pathMetadata : Path
		Directory path containing the `.map` source files for each locale and style.
	fontFamilyCID : str = 'SourceHanMono'
		Font family identifier for CID fonts.
	theLocales : Iterable[str] | None = None
		Locale identifiers to process, or `None` to use `settingsPackage.theLocales` [2].
	theStyles : Iterable[str | None] | None = None
		Style identifiers to process, or `None` to use `settingsPackage.theStyles` [2].
	unicodeExclude : frozenset[int] = frozenset()
		Unicode codepoints to exclude from all generated subsets.

	Returns
	-------
	listPathFilenames : list[Path]
		List of paths to all generated `.gids` and `.unicodes` files.

	References
	----------
	[1] Integrated_Code_Fire.archivist.archivistMakesCharacterSubsets
	[2] Integrated_Code_Fire.settingsPackage

	"""
	if theLocales is None or theStyles is None:
		settings: PackageSettings = PackageSettings(settingsPackage.identifierPackage)
		theLocales = theLocales or settings.theLocales
		theStyles = theStyles or settings.theStyles

	listPathFilenames: list[Path] = []

	pathWrite: Path = settingsPackage.pathPackage / 'dataCenter'

	dictionaryLocales: dict[str, LocaleIn] = archivistGetsLocales()
	# TODO Remove the hardcoding.
	from Integrated_Code_Fire.dataCenter.SourceHanMono import cidsVerticalOnly  # pyright: ignore[reportUnusedImport] # noqa: PLC0415
	for locale, style in CartesianProduct(theLocales, theStyles):
		if style:
			pathFilename: Path = pathMetadata / f"utf32-{dictionaryLocales[locale].SourceHanMono.lower()}-ital.map"
		else:
			pathFilename: Path = pathMetadata / f"utf32-{dictionaryLocales[locale].SourceHanMono.lower()}.map"
		filenameStem: identifierDotAttribute = archivistMakesFilenameStem(fontFamilyCID, dictionaryLocales[locale].ascii, style)
		listPathFilenames.extend(archivistMakesCharacterSubsets(pathFilename, pathWrite, filenameStem, unicodeExclude, cidsVerticalOnly))

	return listPathFilenames

if __name__ == '__main__':
	pathMetadata: Path = pathRootSourceHanMonoDEFAULT / 'Resources'
	unicodeExclude: frozenset[int] = archivistGetsGlyphsUnicode(pathFilenameFiraCodeGlyphsDEFAULT)
	archivistMakesAllCharacterSubsets(pathMetadata, unicodeExclude=unicodeExclude)
