"""Manage font metadata, locale and weight mappings, filename generation, and character subset configuration.

(AI generated docstring)

You can use this module to access locale and weight identifier mappings, generate standardized filename stems, create OpenType
name record metadata, load character subset definitions, and update font file metadata. The module provides the core configuration
and metadata management functions used throughout the Integrated Code 火 build assembly line.

Contents
--------
Functions
	archivistGetsLocales
		Build mapping from locale identifiers to `LocaleIn` instances.
	archivistGetsWeights
		Build mapping from weight identifiers to `WeightIn` instances.
	archivistMakesFilenameStem
		Generate filename stems from font family, locale, style, and weight components.
	archivistMakesNameIDMetadata
		Build OpenType name record mapping for a given weight.
	archivistGetsSubsetCharacters
		Load character subset definitions from metadata files for all locale and style combinations.
	archivistGetsUnicodeFiraCode
		Return the set of Unicode codepoints present in Fira Code fonts.
	archivistUpdatesFontFileMetadata
		Update OpenType metadata in a font file on disk.
	archivistUpdatesMetadata
		Update OpenType metadata in an open `TTFont` instance.
	archivistMakesCharacterSubsets
		Generate glyph ID and Unicode subset files from a UTF-32 character map.
	archivistMakesAllCharacterSubsets
		Generate character subset files for all locale and style combinations.

Variables
	hmtx
		Horizontal metrics table field indices.
	name
		Name table platform and encoding identifiers.
	lookupAFDKOCharacterSet
		Mapping from locale identifiers to AFDKO character set identifiers.

References
----------
[1] fontTools.ttLib.TTFont
	https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html
[2] hunterMakesPy
	https://context7.com/hunterhogan/huntermakespy

"""
from fontTools import subset
from fontTools.ttLib import TTFont
from hunterMakesPy import Ordinals
from hunterMakesPy.filesystemToolkit import writeStringToHere
from Integrated_Code_Fire import LocaleIn, PackageSettings, settingsPackage, WeightIn
from itertools import filterfalse, product as CartesianProduct
from pathlib import Path
from tlz.dicttoolz import keyfilter, keymap  # pyright: ignore[reportMissingModuleSource]
from tlz.functoolz import complement, compose, curry as syntacticCurry  # pyright: ignore[reportMissingModuleSource]
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from collections.abc import Iterable, Iterator
	from hunterMakesPy import identifierDotAttribute
	from pathlib import Path

"""Notes in case I run out of sofunty IDs.

CID subfont names:
Alphabetic
AlphabeticDigits
Bopomofo
Dingbats
DingbatsDigits
Generic
HDingbats
HKana
Hangul
Ideographs
Italic
ItalicCJK
ItalicDigits
Kana
Monospace
MonospaceCJK
MonospaceDigits
VKana

Enclosed CJK Letters and Months
3200-32FE
NOTE Keep 0x32FF

vertical stuff, which _might_ make it possible to use fontTools.Merger.
		, filterfalse(between吗(0x3300, 0x33FF)
		, filterfalse(between吗(0xFB00, 0xFB4F)
		, filterfalse(between吗(0xFE10, 0xFE4F)
"""
#======== Boolean antecedents ================================================

@syntacticCurry
def between吗[小于: Ordinals](floor: 小于, ceiling: 小于, comparand: 小于) -> bool:
	"""Inclusive `floor <= comparand <= ceiling`."""
	return floor <= comparand <= ceiling

#======== Settings that have not yet been obsoleted or found their home, such as a dataclass or function. ========

hmtx: dict[str, int] = {
	'bearingLeft' : 1,
	'increment' : 100,
	'width' : 0,
}

name: dict[str, int] = {
	'langID' : 0x0409,
	'platEncID' : 1,
	'platformID' : 3,
}

# TODO I'd rather get this from an authoritative source.
lookupAFDKOCharacterSet: dict[str, str] = {
	'Hong_Kong': '2',
	'Japan': '1',
	'Korea': '3',
	'Simplified_Chinese': '25',
	'Taiwan': '2',
}
"""Locale identifiers to AFDKO makeotf character set identifiers.

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
	"""Build mapping from locale identifiers to `LocaleIn` instances.

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
		Internal package reference.
	[2] Integrated_Code_Fire.settingsPackage
		Internal package reference.

	"""
	return {
		'Hong_Kong': LocaleIn('Hong_Kong', '香港'),
		'Japan': LocaleIn('Japan', '日本'),
		'Korea': LocaleIn('Korea', '한국인'),
		'Simplified_Chinese': LocaleIn('Simplified_Chinese', '简化字'),
		'Taiwan': LocaleIn('Taiwan', '台灣'),
	}

def archivistGetsWeights() -> dict[str, WeightIn]:
	"""Build mapping from weight identifiers to `WeightIn` instances.

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
		Internal package reference.
	[2] Integrated_Code_Fire.settingsPackage
		Internal package reference.

	"""
	return {
		'Bold': WeightIn(IntegratedCode火='SemiBold', FiraCode='SemiBold', fontFamilyCID='Bold', SourceHanMono='Bold'),
		'Heavy': WeightIn(IntegratedCode火='Bold', FiraCode='Bold', fontFamilyCID='Heavy', SourceHanMono='Heavy'),
		'Light': WeightIn(IntegratedCode火='Light', FiraCode='Light', fontFamilyCID='Light', SourceHanMono='Light'),
		'Medium': WeightIn(IntegratedCode火='Medium', FiraCode='Medium', fontFamilyCID='Medium', SourceHanMono='Medium'),
		'Normal': WeightIn(IntegratedCode火='Retina', FiraCode='Retina', fontFamilyCID='Normal', SourceHanMono='Normal'),
		'Regular': WeightIn(IntegratedCode火='Regular', FiraCode='Regular', fontFamilyCID='Regular', SourceHanMono='Regular'),
	}

def archivistMakesFilenameStem(fontFamily: str | None = None, locale: str | None = None, style: str | None = None, weight: str | None = None, separator: str = '.') -> str:
	"""Generate filename stems by joining `fontFamily`, `locale`, `style`, and `weight` components.

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
	notNone = None # Ironic, no?
	return separator.join(filter(notNone, [fontFamily, locale, style, weight]))

def archivistMakesNameIDMetadata(weight: str, filenameFontFamily: str, fontFamily: str) -> dict[int, str]:
	"""You can build a name record mapping for a given `weight`.

	(AI generated docstring)

	This function returns a `dict[int, str]` that maps a TrueType name record identifier to a name record value. The returned
	mapping is used by `updateFontFile` to update `TTFont['name']`.

	Parameters
	----------
	weight : str
		Font weight suffix derived from the `.ttf` filename stem.
	filenameFontFamilyLocale : str
		Font family locale derived from the `.ttf` filename stem.
	fontFamilyLocale : str
		Font family locale derived from the `.ttf` filename stem.

	Returns
	-------
	dictionaryNameIDToNameRecordValue : dict[int, str]
		Mapping from name record identifier to name record value.

	References
	----------
	[1] fontTools `TTFont` documentation.
		https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html
	[2] Integrated_Code_Fire.writeMetadata.updateFontFile
		Internal package reference.

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

# TODO At the very least, store this data in Python structures.
def archivistGetsSubsetCharacters() -> dict[identifierDotAttribute, dict[str, list[int]]]:
	"""Load character subset definitions from metadata files for all locale and style combinations.

	(AI generated docstring)

	You can load glyph IDs and Unicode codepoints for each Source Han Mono locale and style combination. The
	function reads `.gids` and `.unicodes` files from the metadata directory and returns a nested mapping from filename stem to
	format identifier to character identifier list.

	Returns
	-------
	subsetCharacters : dict[identifierDotAttribute, dict[str, list[int]]]
		Nested mapping from filename stem to format identifier to list of character identifiers. Format identifiers are `'gids'`
		and `'unicodes'`. Character identifiers are integers representing glyph IDs or Unicode codepoints.

	References
	----------
	[1] fontTools.subset.parse_unicodes
		https://fonttools.readthedocs.io/en/latest/subset/index.html
	[2] Integrated_Code_Fire.settingsPackage
		Internal package reference.

	"""
	subsetCharacters: dict[identifierDotAttribute, dict[str, list[int]]] = {}

	fontFamilyCID: str = 'SourceHanMono'
	pathMetadata: Path = settingsPackage.pathRoot / fontFamilyCID / 'metadata'
	dictionaryLocales: dict[str, LocaleIn] = archivistGetsLocales()

	for locale, style in CartesianProduct(settingsPackage.theLocales, settingsPackage.theStyles):
		filenameStem: identifierDotAttribute = archivistMakesFilenameStem(fontFamilyCID, dictionaryLocales[locale].ascii, style)
		subsetCharacters[filenameStem] = {}

		formatCharacterIDs: str = 'gids'
		pathFilename: Path = pathMetadata / f"{filenameStem}.{formatCharacterIDs}"
		subsetCharacters[filenameStem][formatCharacterIDs] = list(map(int, pathFilename.read_text('utf-8').splitlines()))

		formatCharacterIDs: str = 'unicodes'
		pathFilename: Path = pathMetadata / f"{filenameStem}.{formatCharacterIDs}"
		subsetCharacters[filenameStem][formatCharacterIDs] = subset.parse_unicodes(','.join(pathFilename.read_text('utf-8').splitlines()))

	return subsetCharacters

def archivistGetsUnicodeFiraCode() -> frozenset[int]:
	"""Get the Fira Code Unicode codepoints to use in Integrated Code 火.

	Returns
	-------
	unicodeFiraCode : frozenset[int]
		Fira Code Unicode codepoints used in Integrated Code 火.
	"""
	from Integrated_Code_Fire._dataCenter import unicodesLigatures  # noqa: PLC0415
	return frozenset(unicodesLigatures())

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
		Internal package reference.
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
		Internal package reference.

	"""
	ttFont['head'].fontRevision = settingsPackage.fontVersion  # ty:ignore[unresolved-attribute]
	ttFont['OS/2'].achVendID = settingsPackage.achVendID  # ty:ignore[unresolved-attribute]
	for nameID in nameIDmetadata:
		ttFont['name'].setName(nameIDmetadata[nameID], nameID, name['platformID'], name['platEncID'], name['langID'])

#======== Rarely Used Functions ========

def archivistMakesCharacterSubsets(pathFilename: Path) -> list[Path]:
	"""Generate glyph ID and Unicode subset files from a UTF-32 character map.

	(AI generated docstring)

	You can create `.gids` and `.unicodes` subset files from a `.UTF32-map` character map file. The function
	filters out Unicode codepoints present in Fira Code and applies hardcoded range filters to produce glyph ID and Unicode subset
	lists suitable for font subsetting operations.

	Parameters
	----------
	pathFilename : Path
		Path to `.UTF32-map` character map file.

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

	unicodeFiraCode: frozenset[int] = archivistGetsUnicodeFiraCode()

# TODO No one in the entire universe has created a function to load these values from these super-common files?!
	intMAPstr: dict[int, str] = keyfilter(complement(unicodeFiraCode.__contains__)
		, keymap(unicodesToInt, dict(map(compose(tuple[str, str], str.split), pathFilename.read_text('utf-8').splitlines()))))

# TODO I think tlz.keyfilter might have a bug.
	# gids: list[str] = sorted(frozenset(keyfilter((0xFFFF).__gt__, intMAPstr).values()))  # noqa: ERA001
	gids: list[str] = sorted({g for u, g in intMAPstr.items() if 0xFFFF < u}, key=int)  # ty:ignore[invalid-assignment]
	gids.append('')

	pathFilenameGids: Path = pathFilename.with_suffix('.gids')
	writeStringToHere('\n'.join(gids), pathFilenameGids)
	listPathFilenames.append(pathFilenameGids)

# TODO These ranges need to be less hardcoded-ish and/or more semantic (e.g., what is 0x1200?)
# TODO Configuration settings.
	unicodes: Iterator[str] = map(hex
		, filterfalse(between吗(0x1200, 0x2E7F)
		, filterfalse(between吗(0xFF01, 0xFF5E)
			, filter(between吗(0x1100, 0xFFFF), intMAPstr.keys())
	)))

	pathFilenameUnicodes: Path = pathFilename.with_suffix('.unicodes')
	writeStringToHere('\n'.join(unicodes) + '\n', pathFilenameUnicodes)
	listPathFilenames.append(pathFilenameUnicodes)

	return listPathFilenames

def archivistMakesAllCharacterSubsets(fontFamilyCID: str = 'SourceHanMono', theLocales: Iterable[str] | None = None, theStyles: Iterable[str | None] | None = None) -> list[Path]:
	"""Generate character subset files for all locale and style combinations.

	(AI generated docstring)

	You can create `.gids` and `.unicodes` subset files for all combinations of locales and styles. The
	function invokes `archivistMakesCharacterSubsets` [1] for each `.UTF32-map` file found in the metadata directory.

	Parameters
	----------
	fontFamilyCID : str = 'SourceHanMono'
		Font family identifier for CID fonts.
	theLocales : Iterable[str] | None = None
		Locale identifiers to process, or `None` to use `settingsPackage.theLocales`.
	theStyles : Iterable[str | None] | None = None
		Style identifiers to process, or `None` to use `settingsPackage.theStyles`.

	Returns
	-------
	listPathFilenames : list[Path]
		List of paths to all generated `.gids` and `.unicodes` files.

	References
	----------
	[1] Integrated_Code_Fire.archivist.archivistMakesCharacterSubsets
		Internal package reference.
	[2] Integrated_Code_Fire.settingsPackage
		Internal package reference.

	"""
	if theLocales is None or theStyles is None:
		settings = PackageSettings(settingsPackage.identifierPackage)
		theLocales = theLocales or settings.theLocales
		theStyles = theStyles or settings.theStyles

	listPathFilenames: list[Path] = []

	pathMetadata: Path = settingsPackage.pathRoot / fontFamilyCID / 'metadata'
	dictionaryLocales: dict[str, LocaleIn] = archivistGetsLocales()

	for locale, style in CartesianProduct(theLocales, theStyles):
		filenameStem: identifierDotAttribute = archivistMakesFilenameStem(fontFamilyCID, dictionaryLocales[locale].ascii, style)
		suffix: str = 'UTF32-map'
		pathFilename: Path = pathMetadata / f"{filenameStem}.{suffix}"
		listPathFilenames.extend(archivistMakesCharacterSubsets(pathFilename))

	return listPathFilenames

if __name__ == '__main__':
	archivistMakesAllCharacterSubsets()
