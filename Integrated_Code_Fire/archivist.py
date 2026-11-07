"""Select CJK characters and manage font names, weight mappings, and metadata.

(AI generated docstring)

You can match locale and weight labels across source fonts, construct build filenames, and write
Integrated Code 火 metadata. Character selection operations choose the characters that each CJK
font contributes alongside the western font.

Contents
--------
Font-construction functions
	archivistGetsLocales
		Match locale labels across display names and source files.
	archivistGetsWeights
		Match western and CJK weight labels.
	archivistMakesFilenameStem
		Join the nonempty parts of a font filename.
	archivistMakesNameIDMetadata
		Prepare family, weight, credit, license, and version name records.
	archivistUpdatesFontFileMetadata
		Replace metadata in a font file.
	archivistUpdatesMetadata
		Change metadata in an open font.
	make_afdkoOptions
		Select source files and locale options for CID font compilation.
Character selection functions
	archivistGetsUnicodes
		Obtain the code points that a font maps.
	archivistMakesRangeBlocks
		Obtain the code points of a span of consecutive Unicode blocks.
	archivistMakesUnicodesHan
		Select the code points that a CJK font contributes to a merged font.
"""
from __future__ import annotations

from fontTools.ttLib import newTable, TTFont
from fontTools.unicodedata import Blocks
from humpy_cytoolz import complement, keyfilter
from hunterMakesPy.semiotics import ansiColor, ansiColorReset
from Integrated_Code_Fire import LocaleIn, settingsPackage, WeightIn
from Integrated_Code_Fire.dataCenter.SourceHanMono import cidsVerticalOnly
from itertools import chain, starmap
from typing import Literal, TYPE_CHECKING
import sys

if TYPE_CHECKING:
	from collections.abc import Iterable, Mapping
	from fontTools.ttLib.tables._n_a_m_e import NameRecord, table__n_a_m_e
	from pathlib import Path

#======== Font-construction functions ===============================================

def archivistGetsLocales() -> dict[str, LocaleIn]:
	"""Obtain locale labels for font names, filenames, and Source Han Mono source files.

	(AI generated docstring)

	Returns
	-------
	dictionaryLocales : dict[str, LocaleIn]
		New mapping for `"Hong_Kong"`, `"Japan"`, `"Korea"`, `"Simplified_Chinese"`, and
		`"Taiwan"`. Each value contains the display label and both Source Han Mono locale codes.
	"""
	return {
		'Hong_Kong': LocaleIn('Hong_Kong', '香港', SourceHanMono='HK', SourceHanMonoOTC='HC'),
		'Japan': LocaleIn('Japan', '日本', SourceHanMono='JP', SourceHanMonoOTC='J'),
		'Korea': LocaleIn('Korea', '한국인', SourceHanMono='KR', SourceHanMonoOTC='K'),
		'Simplified_Chinese': LocaleIn('Simplified_Chinese', '简化字', SourceHanMono='CN', SourceHanMonoOTC='SC'),
		'Taiwan': LocaleIn('Taiwan', '台灣', SourceHanMono='TW', SourceHanMonoOTC='TC'),
	}

def archivistGetsWeights() -> dict[str, WeightIn]:
	"""Obtain matching western, CJK, and Integrated Code 火 weight labels.

	(AI generated docstring)

	Returns
	-------
	dictionaryWeights : dict[str, WeightIn]
		New mapping for `"Bold"`, `"ExtraLight"`, `"SemiBold"`, `"Light"`, `"Medium"`,
		`"Retina"`, and `"Regular"`. Integrated Code 火 `"SemiBold"`, `"Bold"`, and `"Retina"`
		match Source Han Mono `"Bold"`, `"Heavy"`, and `"Normal"`, respectively. The CJK-only
		`"ExtraLight"` entry has empty western and Integrated Code 火 labels.
	"""
	return {
		'SemiBold': WeightIn(IntegratedCode火='SemiBold', FiraCode='SemiBold', fontFamilyWestern='SemiBold', fontFamilyCID='Bold', SourceHanMono='Bold'),
		'ExtraLight': WeightIn(IntegratedCode火='', FiraCode='', fontFamilyWestern='', fontFamilyCID='ExtraLight', SourceHanMono='ExtraLight'),
		'Bold': WeightIn(IntegratedCode火='Bold', FiraCode='Bold', fontFamilyWestern='Bold', fontFamilyCID='Heavy', SourceHanMono='Heavy'),
		'Light': WeightIn(IntegratedCode火='Light', FiraCode='Light', fontFamilyWestern='Light', fontFamilyCID='Light', SourceHanMono='Light'),
		'Medium': WeightIn(IntegratedCode火='Medium', FiraCode='Medium', fontFamilyWestern='Medium', fontFamilyCID='Medium', SourceHanMono='Medium'),
		'Retina': WeightIn(IntegratedCode火='Retina', FiraCode='Retina', fontFamilyWestern='Retina', fontFamilyCID='Normal', SourceHanMono='Normal'),
		'Regular': WeightIn(IntegratedCode火='Regular', FiraCode='Regular', fontFamilyWestern='Regular', fontFamilyCID='Regular', SourceHanMono='Regular'),
	}

def archivistMakesFilenameStem(fontFamily: str | None = None, locale: str | None = None, style: str | None = None, weight: str | None = None, separator: str = '.') -> str:
	"""Join the nonempty family, locale, style, and weight parts of a font filename.

	(AI generated docstring)

	Parameters
	----------
	fontFamily : str | None = None
		Family label, or `None` or empty text to omit the family label.
	locale : str | None = None
		Locale label, or `None` or empty text to omit the locale label.
	style : str | None = None
		Style label, or `None` or empty text to omit the style label.
	weight : str | None = None
		Weight label, or `None` or empty text to omit the weight label.
	separator : str = '.'
		Text placed between retained parts. Empty text joins parts without separators.

	Returns
	-------
	filenameStem : str
		Retained parts in family, locale, style, and weight order, without a file extension.
	"""
	notNone: None = None  # Ironic, no?
	return separator.join(filter(notNone, [fontFamily, locale, style, weight]))

def archivistMakesNameIDMetadata(weight: str, filenameFontFamily: str, fontFamily: str) -> dict[int, str]:
	"""Prepare font name records for an Integrated Code 火 family and weight.

	(AI generated docstring)

	Parameters
	----------
	weight : str
		Weight label displayed in the font subfamily and full name.
	filenameFontFamily : str
		Family identifier used in the unique identifier and PostScript name. Supply only ASCII
		letters and digits, because the PostScript name permits no other characters in practice;
		only spaces in `weight` are removed here.
	fontFamily : str
		Installed family name, including the locale label.

	Returns
	-------
	nameIDmetadata : dict[int, str]
		OpenType name identifiers mapped to family, weight, version, credit, trademark, and license
		text. Version and vendor fields use `settingsPackage`.

	See Also
	--------
	`archivistUpdatesMetadata`
		Apply the records to an open font.
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
	"""Replace font metadata in an existing font file.

	(AI generated docstring)

	Parameters
	----------
	pathFilename : Path
		Font file to open and replace.
	nameIDmetadata : dict[int, str]
		OpenType name identifiers mapped to their replacement text.

	Returns
	-------
	pathFilename : Path
		Path of the updated font file.

	See Also
	--------
	`archivistUpdatesMetadata`
		Change metadata in an open font without saving a file.

	File Replacement
	----------------
	The font file is saved at the supplied path with the requested name records and the version
	and vendor identifier from `settingsPackage`.
	"""
	with TTFont(pathFilename) as ttFont:
		archivistUpdatesMetadata(ttFont, nameIDmetadata)
		ttFont.save(pathFilename)
	return pathFilename

def archivistUpdatesMetadata(ttFont: TTFont, nameIDmetadata: dict[int, str]) -> None:
	"""Set name records, font revision, and vendor identifier in an open font.

	(AI generated docstring)

	Parameters
	----------
	ttFont : TTFont
		Open font containing the `head`, `OS/2`, and `name` tables.
	nameIDmetadata : dict[int, str]
		OpenType name identifiers mapped to their replacement text.

	See Also
	--------
	`archivistUpdatesFontFileMetadata`
		Apply the metadata and save an existing font file.

	Input Mutation
	--------------
	The supplied font receives English Windows name records for the supplied identifiers. The
	font revision and vendor identifier use `settingsPackage.fontVersion` and
	`settingsPackage.achVendID`. The font remains open and is not saved.
	"""
	ttFont['head'].fontRevision = settingsPackage.fontVersion
	ttFont['OS/2'].achVendID = settingsPackage.achVendID
	for nameID in nameIDmetadata:
		ttFont['name'].addMultilingualName({'en': nameIDmetadata[nameID]}, nameID=nameID, windows=True, mac=False)
		name: NameRecord = ttFont['name'].names.pop()
		ttFont['name'].setName(nameIDmetadata[nameID], nameID, name.platformID, name.platEncID, name.langID)

def make_afdkoOptions(pathRoot: Path, fontFamilyCID: str = 'SourceHanMono', locale: str = 'Simplified_Chinese', style: Literal['Italic'] | None = None, weight: str = 'Regular') -> tuple[str, ...]:
	"""Select source files and locale settings for compiling a CJK font with AFDKO.

	(AI generated docstring)

	Parameters
	----------
	pathRoot : Path
		Source checkout containing weight directories, character maps, variation sequences, and
		`FontMenuNameDB`.
	fontFamilyCID : str = 'SourceHanMono'
		Family label used in source filenames. Source Han Mono receives its specific locale and
		weight labels; other families use ASCII locale labels and CID weight labels.
	locale : str = 'Simplified_Chinese'
		Locale key from `archivistGetsLocales`.
	style : {None, 'Italic'} = None
		Upright style or italic style. Italic style selects the italic source files.
	weight : str = 'Regular'
		Weight key from `archivistGetsWeights`.

	Returns
	-------
	options : tuple[str, ...]
		AFDKO options selecting the PostScript source, feature definitions, character maps,
		variation sequences, menu names, and Macintosh script identifier. Output location is
		supplied separately during compilation.

	See Also
	--------
	`Integrated_Code_Fire.foundry.smithy_makeotf`
		Compile the selected sources to an output font file.
	"""
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
		sys.stdout.write(f"{ansiColor.CyanOnMagenta}{message}{ansiColorReset}\n")

	nameTable: table__n_a_m_e = newTable('name')  # pyright: ignore[reportAssignmentType] # ty: ignore[invalid-assignment]
	nameTable.addMultilingualName({settingsPackage.languages[locale]: fontFamilyCID}, nameID=1, windows=False, mac=True)

	options: list[str] = [
		'-f', str(pathRoot / aWeight / 'OTC' / f"cidfont.ps.OTC{styleA}.{aLocaleOTC}"),
		'-ff', str(pathRoot / aWeight / 'OTC' / f"features.OTC{styleA}.{aLocaleOTC}"),

		'-ch', str(pathRoot / f"Uni{fontFamilyCID}{styleB}{aLocale}-UTF32-H"),
		'-ci', str(pathRoot / f"{fontFamilyCID}_{aLocale}_sequences{styleC}.txt"),
		'-mf', str(pathRoot / 'FontMenuNameDB'),

		'-cs', str(nameTable.names[0].platEncID),
	]

	if style == 'Italic':
		options.append('-i')

	return tuple(options)

#======== Character selection functions ========

def archivistGetsUnicodes(pathFilename: Path) -> frozenset[int]:
	"""Obtain the code points that a font maps.

	(AI generated docstring)

	Parameters
	----------
	pathFilename : Path
		Font to read.

	Returns
	-------
	unicodes : frozenset[int]
		Every code point in the Unicode subtables of the font's character map.
	"""
	with TTFont(pathFilename, lazy=True) as ttFont:
		return frozenset(chain.from_iterable(ttFont['cmap'].buildReversed().values()))

def archivistMakesRangeBlocks(blockFirst: str, blockLast: str) -> range:
	"""Obtain the code points of a span of consecutive Unicode blocks.

	(AI generated docstring)

	Parameters
	----------
	blockFirst : str
		Name of the first Unicode block of the span, such as `"Basic Latin"`.
	blockLast : str
		Name of the last Unicode block of the span, such as `"Georgian"`.

	Returns
	-------
	rangeBlocks : range
		Every code point from the start of `blockFirst` through the end of `blockLast`.

	See Also
	--------
	`fontTools.unicodedata.Blocks`
		The Unicode block names and their starting code points.
	"""
	return range(Blocks.RANGES[Blocks.VALUES.index(blockFirst)], Blocks.RANGES[Blocks.VALUES.index(blockLast) + 1])

def archivistMakesUnicodesHan(cmapReversed: Mapping[str, Iterable[int]], unicodesWestern: Iterable[int]) -> frozenset[int]:
	"""Select the code points that a CJK font contributes to a merged font.

	(AI generated docstring)

	Parameters
	----------
	cmapReversed : Mapping[str, Iterable[int]]
		Glyph names of the CJK font mapped to the code points of each glyph, as from
		`TTFont['cmap'].buildReversed()`.
	unicodesWestern : Iterable[int]
		Code points of the western fonts. The western font supplies these characters.

	Returns
	-------
	unicodesHan : frozenset[int]
		Code points of the CJK font, except code points that the western fonts map, code points in
		`settingsPackage.rangesExclude` and `settingsPackage.unicodesExclude`, and code points of
		glyphs in `cidsVerticalOnly`.
	"""
	unicodesExclude: frozenset[int] = frozenset(chain(unicodesWestern
		, settingsPackage.unicodesExclude
		, chain.from_iterable(starmap(archivistMakesRangeBlocks, settingsPackage.rangesExclude))))
	glyphNamesVerticalOnly: frozenset[str] = frozenset(map('cid{:05d}'.format, cidsVerticalOnly))
	return frozenset(chain.from_iterable(keyfilter(complement(glyphNamesVerticalOnly.__contains__), cmapReversed).values())) - unicodesExclude
