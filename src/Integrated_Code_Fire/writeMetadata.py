# ruff: noqa: D100, D103
from fontTools.ttLib import TTFont
from Integrated_Code_Fire import achVendID, filenameFontFamilyLocale, fontFamilyLocale, pathWorkbenchFonts
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pathlib import Path

fontVersionHARDCODED: float = 0.002
fontVersion: float = fontVersionHARDCODED

def getMetadataByFontWeight(weight: str) -> dict[int, str]:
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
	set(map(updateFontFile, pathWorkbenchFonts.glob(f'{filenameFontFamilyLocale}*.ttf')))

if __name__ == '__main__':
	writeMetadata()
