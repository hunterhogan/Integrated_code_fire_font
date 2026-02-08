# ruff: noqa: D100, D103
from fontTools.ttLib import TTFont
from Integrated_Code_Fire import fontNameFamily, fontNameLocale简化字, pathWorkbenchFonts
from operator import attrgetter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e
	from pathlib import Path

fontVersionHARDCODED: float = 0.002
fontVersion: float = fontVersionHARDCODED
fontNameFamilyLocale: str = ' '.join((fontNameFamily, fontNameLocale简化字))  # noqa: FLY002

fontNameFamilyLocaleWithoutSpaces: str = fontNameFamilyLocale.replace(' ', '')
achVendID: str = '    '

platformID: int = 3
platEncID: int = 1
langID: int = 0x0409

dictionaryNameIDToNameRecordValueStatic: dict[int, str] = {
	0: 'Copyright 2026 Hunter Hogan (https://www.patreon.com/integrated), with Reserved Font Name "Integrated."',
	7: 'Fira Mono is a trademark of The Mozilla Corporation. Source is a trademark of Adobe in the United States and/or other countries.',
	8: 'Carrois Corporate; Edenspiekermann AG; Nikita Prokopov; Adobe',
	9: 'Carrois Corporate; Edenspiekermann AG; Nikita Prokopov; Ryoko NISHIZUKA 西塚涼子 (kana, bopomofo & ideographs); Paul D. Hunt (Latin, Italic, Greek & Cyrillic); Sandoll Communications 산돌커뮤니케이션, Soo-young JANG 장수영 & Joo-yeon KANG 강주연 (hangul elements, letters & syllables)',
	10: 'For Adobe: Dr. Ken Lunde (project architect, glyph set definition & overall production); Masataka HATTORI 服部正貴 (production & ideograph elements)',
	11: 'https://www.patreon.com/integrated',
	12: 'https://tonsky.me http://www.adobe.com/type/',
	13: 'This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: http://scripts.sil.org/OFL',
	14: 'http://scripts.sil.org/OFL',
}

def buildNameIDToNameRecordValue(weightName: str) -> dict[int, str]:
	return {
		**dictionaryNameIDToNameRecordValueStatic,
		1: fontNameFamilyLocale,
		2: weightName,
		3: f"{fontVersion};{fontNameFamilyLocaleWithoutSpaces}{weightName}",
		4: f"{fontNameFamilyLocale}{weightName}",
		5: f"Version {fontVersion}",
		6: f"{fontNameFamilyLocaleWithoutSpaces}{weightName}",
		16: fontNameFamilyLocale,
		17: weightName,
	}

def updateFontFile(pathFilenameFont: Path) -> None:
	weightName: str = pathFilenameFont.stem.removeprefix(fontNameFamilyLocaleWithoutSpaces)
	dictionaryNameIDToNameRecordValue: dict[int, str] = buildNameIDToNameRecordValue(weightName)
	with TTFont(pathFilenameFont) as fontBase:
		fontBase['head'].fontRevision = fontVersion
		fontBase['OS/2'].achVendID = achVendID
		table_name: table__n_a_m_e = fontBase['name']
		nameID: int
		for nameID in sorted(dictionaryNameIDToNameRecordValue):
			nameRecordValue: str = dictionaryNameIDToNameRecordValue[nameID]
			table_name.removeNames(
				nameID = nameID
				, platformID = platformID
				, platEncID = platEncID
				, langID = langID
			)
			table_name.setName(
				nameRecordValue
				, nameID
				, platformID
				, platEncID
				, langID
			)
		fontBase.save(pathFilenameFont)

def writeMetadata() -> None:
	pathFilenameFont: Path
	for pathFilenameFont in sorted(
		pathWorkbenchFonts.glob(f'{fontNameFamilyLocaleWithoutSpaces}*.ttf')
		, key = attrgetter('name')
	):
		updateFontFile(pathFilenameFont)

if __name__ == '__main__':
	writeMetadata()
