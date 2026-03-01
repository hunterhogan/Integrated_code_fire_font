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
# ruff: noqa: D103
from Integrated_Code_Fire import LocaleIn, settingsPackage, WeightIn
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
	from fontTools.ttLib import TTFont

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

name: dict[str, int] = {
	'platformID' : 3,
	'platEncID' : 1,
	'langID' : 0x0409,
}

def updateFontFile(ttFont: TTFont, nameIDmetadata: dict[int, str]) -> None:
	ttFont['head'].fontRevision = settingsPackage.fontVersion  # ty:ignore[unresolved-attribute]
	ttFont['OS/2'].achVendID = settingsPackage.achVendID  # ty:ignore[unresolved-attribute]
	for nameID in nameIDmetadata:
		ttFont['name'].removeNames(nameID, name['platformID'], name['platEncID'], name['langID'])
		ttFont['name'].setName(nameIDmetadata[nameID], nameID, name['platformID'], name['platEncID'], name['langID'])

"""filenameSuffix
cidfont.ps
cidfontinfo
features
gids
map
otf
sequences
ttf
UTF16-H
UTF32-H
"""

def getFilenameStem(fontFamily: str, locale: str | None = None, style: Literal['Italic'] | None = None, weight: str | None = None, separator: str = '.') -> str:
	notNone = None # Ironic, no?
	return separator.join(filter(notNone, [fontFamily, locale, style, weight]))

dictionaryLocales: dict[str, LocaleIn] = {
	'Hong_Kong': LocaleIn('Hong_Kong', '香港'),
	'Japan': LocaleIn('Japan', '日本'),
	'Korea': LocaleIn('Korea', '한국인'),
	'Simplified_Chinese': LocaleIn('Simplified_Chinese', '简化字'),
	'Taiwan': LocaleIn('Taiwan', '台灣'),
}

dictionaryWeights: dict[str, WeightIn] = {
	'Light': WeightIn('Light', 'Light', 'Light'),
	'Regular': WeightIn('Regular', 'Regular', 'Regular'),
	'Normal': WeightIn('Retina', 'Retina', 'Normal'),
	'Medium': WeightIn('Medium', 'Medium', 'Medium'),
	'Bold': WeightIn('SemiBold', 'SemiBold', 'Bold'),
	'Heavy': WeightIn('Bold', 'Bold', 'Heavy'),
}
unicodeFiraCodeAbove0x3000: tuple[int, ...] = (12300, 12301, 57344, 57345, 57346, 57347, 57504, 57505, 57506, 57520, 57521, 57522, 57523, 60928, 60929, 60930, 60931, 60932, 60933, 60934, 60935, 60936, 60937, 60938, 60939, 65279, 65378, 65379, 65533, 120121, 127245, 127246, 127247, 127341, 127342, 127343, 127405, 127760, 129904, 129905, 129906, 129907, 129908, 129909, 129910, 129911, 129912, 129913, 129914, 129915, 129916, 129917, 129918, 129919, 129920, 129921, 129922, 129923, 129924, 129925, 129926, 129927, 129928, 129929, 129930, 129931)

hmtx: dict[str, int] = {
	'width' : 0,
	'bearingLeft' : 1,
	'increment' : 100,
}
"""Horizontal increment in font units added to left bearings and advance
widths when integrating Source Han glyphs.

(AI generated docstring)

The `bearingIncrement` value is used by `applyBearingIncrementToFont` to
translate glyph coordinates and to increase left side bearings and advance
widths so that merged CJK glyphs have an appropriate visual offset when
combined with Latin monospace glyphs.

References
----------
[1] fontTools - Read the Docs
	https://fonttools.readthedocs.io/en/latest/
"""

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

