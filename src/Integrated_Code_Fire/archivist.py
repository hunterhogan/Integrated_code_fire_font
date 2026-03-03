"""You can use this module to write OpenType name metadata into built `.ttf` files.

(AI generated docstring)

This module updates each built `.ttf` font file in `pathWorkbenchFonts` by
setting `TTFont['head'].fontRevision`, `TTFont['OS/2'].achVendID`, and selected
name records in `TTFont['name']`. The name record values are produced by
`getMetadataByFontWeight`.

This module also provides `updateCIDFontInfoVersion` to update version numbers
in CIDFont info files before compilation.

Contents
--------
Variables
	fontVersion
		Font revision value written into the `head` table.
	fontVersionHARDCODED
		Hard-coded value used to initialize `fontVersion`.
	langID
		Name record language identifier used by `updateFontFile`.
	platEncID
		Name record platform encoding identifier used by `updateFontFile`.
	platformID
		Name record platform identifier used by `updateFontFile`.

Functions
	getMetadataByFontWeight
		Build the name record value mapping for a specific `weight`.
	updateFontFile
		Update one `.ttf` font file in place.
	writeMetadata
		Update all built `.ttf` font files in `pathWorkbenchFonts`.
	updateCIDFontInfoVersion
		Update version number in CIDFont info files before compilation.

References
----------
[1] fontTools `TTFont` documentation.
	https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html
[2] Integrated_Code_Fire.go.go
	Internal package reference.

"""
from fontTools import subset
from hunterMakesPy import Ordinals
from hunterMakesPy.filesystemToolkit import writeStringToHere
from Integrated_Code_Fire import LocaleIn, settingsPackage, WeightIn
from itertools import filterfalse, product as CartesianProduct
from pathlib import Path
from tlz.dicttoolz import keyfilter, keymap  # pyright: ignore[reportMissingModuleSource]
from tlz.functoolz import complement, compose, curry as syntacticCurry  # pyright: ignore[reportMissingModuleSource]
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from collections.abc import Iterable, Iterator
	from fontTools.ttLib import TTFont
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

Based ONLY on looking at SourceHanMono.Simplified_Chinese.Regular.otf:
Ranges I can exclude.
Small Form Variants (punctuation, so I'd like to push users towards the ligatures (to avoid "Issues"), but users might want these forms for inline documentation, so idk.)
FE50-FE6F

"""
#======== Boolean antecedents ================================================

@syntacticCurry
def between吗[小于: Ordinals](floor: 小于, ceiling: 小于, comparand: 小于) -> bool:
	"""Inclusive `floor <= comparand <= ceiling`."""
	return floor <= comparand <= ceiling

#======== Settings that have not yet found their home, such as a dataclass or function. ========

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

unicodeFiraCode_jamoOrAbove0x2e80: frozenset[int] = frozenset([12300, 12301, 57344, 57345, 57346, 57347, 57504, 57505, 57506, 57520, 57521, 57522, 57523, 60928, 60929, 60930, 60931, 60932, 60933, 60934, 60935, 60936, 60937, 60938, 60939, 65279, 65378, 65379, 65533, 120121, 127245, 127246, 127247, 127341, 127342, 127343, 127405, 127760, 129904, 129905, 129906, 129907, 129908, 129909, 129910, 129911, 129912, 129913, 129914, 129915, 129916, 129917, 129918, 129919, 129920, 129921, 129922, 129923, 129924, 129925, 129926, 129927, 129928, 129929, 129930, 129931])

def getFilenameStem(fontFamily: str, locale: str | None = None, style: str | None = None, weight: str | None = None, separator: str = '.') -> str:
	"""Get stem.

	Common filename suffixes:
	- cidfont.ps  # NOTE that this is now the only "faux suffix" because it has a '.', so I might want to change it.
	- cidfontinfo
	- features
	- gids
	- otf
	- sequences
	- ttf
	- unicodes
	- UTF32-map
	- UTF32-H
	"""
	notNone = None # Ironic, no?
	return separator.join(filter(notNone, [fontFamily, locale, style, weight]))

def getDictionaryLocales() -> dict[str, LocaleIn]:
	"""Keyed to `settingsPackage.theLocales`."""
	return {
		'Hong_Kong': LocaleIn('Hong_Kong', '香港'),
		'Japan': LocaleIn('Japan', '日本'),
		'Korea': LocaleIn('Korea', '한국인'),
		'Simplified_Chinese': LocaleIn('Simplified_Chinese', '简化字'),
		'Taiwan': LocaleIn('Taiwan', '台灣'),
	}

def getDictionaryWeights() -> dict[str, WeightIn]:
	"""Keyed to SourceHanMono weight names."""
	return {
		'Bold': WeightIn(IntegratedCode火='SemiBold', FiraCode='SemiBold', fontFamilyCID='Bold', SourceHanMono='Bold'),
		'Heavy': WeightIn(IntegratedCode火='Bold', FiraCode='Bold', fontFamilyCID='Heavy', SourceHanMono='Heavy'),
		'Light': WeightIn(IntegratedCode火='Light', FiraCode='Light', fontFamilyCID='Light', SourceHanMono='Light'),
		'Medium': WeightIn(IntegratedCode火='Medium', FiraCode='Medium', fontFamilyCID='Medium', SourceHanMono='Medium'),
		'Normal': WeightIn(IntegratedCode火='Retina', FiraCode='Retina', fontFamilyCID='Normal', SourceHanMono='Normal'),
		'Regular': WeightIn(IntegratedCode火='Regular', FiraCode='Regular', fontFamilyCID='Regular', SourceHanMono='Regular'),
	}

def getNameIDMetadata(weight: str, filenameFontFamily: str, fontFamily: str) -> dict[int, str]:
	"""You can build a name record mapping for a given `weight`.

	(AI generated docstring)

	This function returns a `dict[int, str]` that maps a TrueType name record
	identifier to a name record value. The returned mapping is used by
	`updateFontFile` to update `TTFont['name']`.

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
		3: f"{settingsPackage.fontVersion};{settingsPackage.achVendID};{filenameFontFamily}{weight}",
		4: f"{fontFamily} {weight}",
		5: f"Version {settingsPackage.fontVersion}",
		6: f"{filenameFontFamily}{weight}",
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

def getSubsetCharacters() -> dict[identifierDotAttribute, dict[str, list[int]]]:
	subsetCharacters: dict[identifierDotAttribute, dict[str, list[int]]] = {}

	fontFamilyCID: str = 'SourceHanMono'
	pathMetadata: Path = settingsPackage.pathRoot / fontFamilyCID / 'metadata'
	dictionaryLocales: dict[str, LocaleIn] = getDictionaryLocales()

	for locale, style in CartesianProduct(settingsPackage.theLocales, settingsPackage.theStyles):
		filenameStem: identifierDotAttribute = getFilenameStem(fontFamilyCID, dictionaryLocales[locale].ascii, style)
		subsetCharacters[filenameStem] = {}

		formatCharacterIDs: str = 'gids'
		pathFilename: Path = pathMetadata / f"{filenameStem}.{formatCharacterIDs}"
		subsetCharacters[filenameStem][formatCharacterIDs] = list(map(int, pathFilename.read_text('utf-8').splitlines()))

		formatCharacterIDs: str = 'unicodes'
		pathFilename: Path = pathMetadata / f"{filenameStem}.{formatCharacterIDs}"
		subsetCharacters[filenameStem][formatCharacterIDs] = subset.parse_unicodes(','.join(pathFilename.read_text('utf-8').splitlines()))

	return subsetCharacters

def updateMetadata(ttFont: TTFont, nameIDmetadata: dict[int, str]) -> None:
	ttFont['head'].fontRevision = settingsPackage.fontVersion  # ty:ignore[unresolved-attribute]
	ttFont['OS/2'].achVendID = settingsPackage.achVendID  # ty:ignore[unresolved-attribute]
	for nameID in nameIDmetadata:
		ttFont['name'].removeNames(nameID, name['platformID'], name['platEncID'], name['langID'])
		ttFont['name'].setName(nameIDmetadata[nameID], nameID, name['platformID'], name['platEncID'], name['langID'])

def archivistWritesCharacterSubsets(pathFilename: Path) -> list[Path]:
	def unicodesToInt(unicodeHexadecimalAsStr: str, /) -> int:
		return int(unicodeHexadecimalAsStr.strip('<>'), 16)

	listPathFilenames: list[Path] = []

	intMAPstr: dict[int, str] = keyfilter(complement(unicodeFiraCode_jamoOrAbove0x2e80.__contains__)
		, keymap(unicodesToInt, dict(map(compose(tuple[str, str], str.split), pathFilename.read_text('utf-8').splitlines()))))

	# gids: list[str] = sorted(frozenset(keyfilter((0xFFFF).__gt__, intMAPstr).values()))  # noqa: ERA001
	gids: list[str] = sorted({g for u, g in intMAPstr.items() if 0xFFFF < u}, key=int)  # ty:ignore[invalid-assignment]
	gids.append('')

	pathFilenameGids: Path = pathFilename.with_suffix('.gids')
	writeStringToHere('\n'.join(gids), pathFilenameGids)
	listPathFilenames.append(pathFilenameGids)

	unicodes: Iterator[str] = map(hex
		, filterfalse(between吗(0x1200, 0x2E7F)
		, filterfalse(between吗(0xFF01, 0xFF5E)
			, filter(between吗(0x1100, 0xFFFF), intMAPstr.keys())
	)))

	pathFilenameUnicodes: Path = pathFilename.with_suffix('.unicodes')
	writeStringToHere('\n'.join(unicodes) + '\n', pathFilenameUnicodes)
	listPathFilenames.append(pathFilenameUnicodes)

	return listPathFilenames

def Z0Z_doTheNeedful(fontFamilyCID: str = 'SourceHanMono'
		, theLocales: Iterable[str] = frozenset(['Hong_Kong', 'Japan', 'Korea', 'Simplified_Chinese', 'Taiwan'])
		, theStyles: Iterable[str | None] = frozenset(['Italic', None])
	) -> list[Path]:
	listPathFilenames: list[Path] = []

	pathMetadata: Path = settingsPackage.pathRoot / fontFamilyCID / 'metadata'
	dictionaryLocales: dict[str, LocaleIn] = getDictionaryLocales()

	for locale, style in CartesianProduct(theLocales, theStyles):
		filenameStem: identifierDotAttribute = getFilenameStem(fontFamilyCID, dictionaryLocales[locale].ascii, style)
		suffix: str = 'UTF32-map'
		pathFilename: Path = pathMetadata / f"{filenameStem}.{suffix}"
		listPathFilenames.extend(archivistWritesCharacterSubsets(pathFilename))

	return listPathFilenames

if __name__ == '__main__':
	Z0Z_doTheNeedful()
