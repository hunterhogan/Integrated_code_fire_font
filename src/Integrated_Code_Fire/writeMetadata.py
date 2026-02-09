"""You can use this module to write OpenType name metadata into built `.ttf` files.

(AI generated docstring)

This module updates each built `.ttf` font file in `pathWorkbenchFonts` by
setting `TTFont['head'].fontRevision`, `TTFont['OS/2'].achVendID`, and selected
name records in `TTFont['name']`. The name record values are produced by
`getMetadataByFontWeight`.

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

References
----------
[1] fontTools `TTFont` documentation.
	https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html
[2] Integrated_Code_Fire.go.go
	Internal package reference.

"""

from fontTools.ttLib import TTFont
from Integrated_Code_Fire import achVendID, filenameFontFamilyLocale, fontFamilyLocale, pathWorkbenchFonts
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pathlib import Path

fontVersionHARDCODED: float = 0.002
fontVersion: float = fontVersionHARDCODED

def getMetadataByFontWeight(weight: str) -> dict[int, str]:
	"""You can build a name record mapping for a given `weight`.

	(AI generated docstring)

	This function returns a `dict[int, str]` that maps a TrueType name record
	identifier to a name record value. The returned mapping is used by
	`updateFontFile` to update `TTFont['name']`.

	Parameters
	----------
	weight : str
		Font weight suffix derived from the `.ttf` filename stem.

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
		0: 'Copyright 2026 Hunter Hogan (https://www.patreon.com/integrated), with Reserved Font Name "Integrated."',
		1: fontFamilyLocale,
		2: weight,
		3: f"{fontVersion};{achVendID};{filenameFontFamilyLocale}{weight}",
		4: f"{fontFamilyLocale}{weight}",
		5: f"Version {fontVersion}",
		6: f"{filenameFontFamilyLocale}{weight}",
		7: 'Fira Mono is a trademark of The Mozilla Corporation. Source is a trademark of Adobe in the United States and/or other countries.',
		8: 'Carrois Corporate; Edenspiekermann AG; Nikita Prokopov; Adobe',
		9: 'Carrois Corporate; Edenspiekermann AG; Nikita Prokopov; Ryoko NISHIZUKA 西塚涼子 (kana, bopomofo & ideographs); Paul D. Hunt (Latin, Italic, Greek & Cyrillic); Sandoll Communications 산돌커뮤니케이션, Soo-young JANG 장수영 & Joo-yeon KANG 강주연 (hangul elements, letters & syllables)',
		10: 'For Adobe: Dr. Ken Lunde (project architect, glyph set definition & overall production); Masataka HATTORI 服部正貴 (production & ideograph elements)',
		11: 'https://www.patreon.com/integrated',
		12: 'https://tonsky.me http://www.adobe.com/type/',
		13: 'This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: http://scripts.sil.org/OFL',
		14: 'http://scripts.sil.org/OFL',
		16: fontFamilyLocale,
		17: weight,
	}

platformID: int = 3
platEncID: int = 1
langID: int = 0x0409

def updateFontFile(pathFilenameFont: Path) -> None:
	"""You can update a `.ttf` font file in place.

	(AI generated docstring)

	This function derives `weight` from `pathFilenameFont.stem` by removing the
	prefix `filenameFontFamilyLocale`. This function uses
	`getMetadataByFontWeight(weight)` to populate a name record mapping.

	This function opens `pathFilenameFont` with `TTFont` and writes these values.

	* `TTFont['head'].fontRevision` is set to `fontVersion`.
	* `TTFont['OS/2'].achVendID` is set to `achVendID`.
	* Each name record in the mapping is applied by removing and setting a name
		record using `platformID`, `platEncID`, and `langID`.

	Parameters
	----------
	pathFilenameFont : Path
		Path to the `.ttf` font file to update.

	Returns
	-------
	resultNone : None
		This function returns `None`.

	Raises
	------
	OSError
		Raised if `TTFont.save` fails to write `pathFilenameFont`.
	Exception
		Raised if `fontTools` fails to parse or update `pathFilenameFont`.

	Examples
	--------
	This function is invoked by `writeMetadata`.

	>>> from Integrated_Code_Fire.writeMetadata import writeMetadata
	>>> writeMetadata()

	References
	----------
	[1] fontTools `TTFont` documentation.
		https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html
	[2] Integrated_Code_Fire.writeMetadata.getMetadataByFontWeight
		Internal package reference.
	[3] Integrated_Code_Fire.writeMetadata.writeMetadata
		Internal package reference.

	"""
	weight: str = pathFilenameFont.stem.removeprefix(filenameFontFamilyLocale)
	dictionaryNameIDToNameRecordValue: dict[int, str] = getMetadataByFontWeight(weight)
	with TTFont(pathFilenameFont) as fontBase:
		fontBase['head'].fontRevision = fontVersion  # ty:ignore[unresolved-attribute]
		fontBase['OS/2'].achVendID = achVendID  # ty:ignore[unresolved-attribute]
		for nameID in sorted(dictionaryNameIDToNameRecordValue):
			fontBase['name'].removeNames(nameID, platformID, platEncID, langID)
			fontBase['name'].setName(dictionaryNameIDToNameRecordValue[nameID], nameID, platformID, platEncID, langID)
		fontBase.save(pathFilenameFont)

def writeMetadata() -> None:
	"""You can update metadata for each built `.ttf` file in `pathWorkbenchFonts`.

	(AI generated docstring)

	This function calls `updateFontFile` for each `.ttf` file matched by
	`pathWorkbenchFonts.glob(f'{filenameFontFamilyLocale}*.ttf')`.

	Returns
	-------
	resultNone : None
		This function returns `None`.

	Raises
	------
	Exception
		Raised if `updateFontFile` fails for any matched `.ttf` file.

	Examples
	--------
	This function is invoked by `Integrated_Code_Fire.go.go`.

	>>> from Integrated_Code_Fire.go import go
	>>> go()

	References
	----------
	[1] Integrated_Code_Fire.go.go
		Internal package reference.
	[2] Integrated_Code_Fire.writeMetadata.updateFontFile
		Internal package reference.

	"""
	set(map(updateFontFile, pathWorkbenchFonts.glob(f'{filenameFontFamilyLocale}*.ttf')))
