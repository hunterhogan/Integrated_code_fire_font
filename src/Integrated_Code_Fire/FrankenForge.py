"""The functions in this module are to renovate other fonts and should be run infrequently. Put oft-run updating-functions in other modules."""
# ruff: noqa: D103
from fontTools.misc.encodingTools import getEncoding
from fontTools.misc.textTools import byteord, tobytes
from Integrated_Code_Fire import settingsPackage
from Integrated_Code_Fire.writeMetadata import getMetadataByFontWeight
from multiprocessing import Pool
from typing import TYPE_CHECKING
import re as regex
import shutil

if TYPE_CHECKING:
	from pathlib import Path

def scientistCreatesFrankenFont(fontFamilyDonor: str = 'SourceHanMono', fontFamilyMonster: str = 'FrankenFont', workersMaximum: int = 1) -> None:  # noqa: ARG001
	pathDonor: Path = settingsPackage.pathRoot / fontFamilyDonor
	pathMonster: Path = settingsPackage.pathRoot / fontFamilyMonster

	shutil.copytree(pathDonor, pathMonster, dirs_exist_ok=True)

	scribeUpdatesFontFamily(workersMaximum=14)
	scribeUpdatesMetadata(workersMaximum=14)

#======== Font family name transformations ========

def scribeUpdatesFontFamily(fontFamilyDonor: str = 'SourceHanMono', fontFamilyMonster: str = 'FrankenFont', fontDisplayNameDonor: str = 'Source Han Mono', fontDisplayNameMonster: str = 'Franken Font', workersMaximum: int = 1) -> None:
	pathMonster: Path = settingsPackage.pathRoot / fontFamilyMonster

	pathFilename: Path = pathMonster / 'metadata' / 'FontMenuNameDB'
	pathFilename.write_text(pathFilename.read_text(encoding='utf-8').replace(f'[{fontFamilyDonor}', f'[{fontFamilyMonster}').replace(fontDisplayNameDonor, fontDisplayNameMonster), encoding='utf-8')

	with Pool(processes=workersMaximum) as concurrencyManager:
		set(concurrencyManager.starmap(_updateCIDFontInfo, [(pathFilename, fontFamilyDonor, fontFamilyMonster, fontDisplayNameDonor, fontDisplayNameMonster) for pathFilename in pathMonster.glob('glyphs/*.cidfontinfo')]))
		set(concurrencyManager.starmap(_updateCIDFont, [(pathFilename, fontFamilyDonor, fontFamilyMonster, fontDisplayNameDonor, fontDisplayNameMonster) for pathFilename in pathMonster.glob('glyphs/*.cidfont.ps')]))
		set(concurrencyManager.starmap(_updateUTF32H, [(pathFilename, fontFamilyDonor, fontFamilyMonster) for pathFilename in pathMonster.glob('metadata/*.H')]))

def _updateCIDFontInfo(pathFilename: Path, fontFamilyDonor: str, fontFamilyMonster: str, fontDisplayNameDonor: str, fontDisplayNameMonster: str) -> None:
	string: str = pathFilename.read_text(encoding='utf-8')

	regexFontName: regex.Pattern[str] = regex.compile(r'^(FontName\s+\()([^)]+)(\).*)$', flags=regex.MULTILINE)
	regexFullName: regex.Pattern[str] = regex.compile(r'^(FullName\s+\()([^)]+)(\).*)$', flags=regex.MULTILINE)
	regexFamilyName: regex.Pattern[str] = regex.compile(r'^(FamilyName\s+\()([^)]+)(\).*)$', flags=regex.MULTILINE)

	string = regexFontName.sub(lambda matchFontName: matchFontName.group(1) + matchFontName.group(2).replace(fontFamilyDonor, fontFamilyMonster) + matchFontName.group(3), string)
	string = regexFullName.sub(lambda matchFullName: matchFullName.group(1) + matchFullName.group(2).replace(fontDisplayNameDonor, fontDisplayNameMonster) + matchFullName.group(3), string)
	string = regexFamilyName.sub(lambda matchFamilyName: matchFamilyName.group(1) + matchFamilyName.group(2).replace(fontDisplayNameDonor, fontDisplayNameMonster) + matchFamilyName.group(3), string)

	pathFilename.write_text(string, encoding='utf-8')

def _updateCIDFont(pathFilename: Path, fontFamilyDonor: str, fontFamilyMonster: str, fontDisplayNameDonor: str, fontDisplayNameMonster: str) -> None:
	string: str = pathFilename.read_bytes().decode('latin-1')

	matchStartData: regex.Match[str] | None = regex.search(r'\(Binary\)\s+\d+\s+StartData', string)
	if matchStartData is None:
		return

	cutHere: int = matchStartData.end()

	pathFilename.write_bytes((string[:cutHere].replace(fontFamilyDonor, fontFamilyMonster).replace(fontDisplayNameDonor, fontDisplayNameMonster) + string[cutHere:]).encode('latin-1'))

def _updateUTF32H(pathFilename: Path, fontFamilyDonor: str, fontFamilyMonster: str) -> None:
	pathFilename.write_text(pathFilename.read_text(encoding='utf-8').replace(fontFamilyDonor, fontFamilyMonster), encoding='utf-8')

#======== Metadata transformations ========

def scribeUpdatesMetadata(fontFamily: str = 'FrankenFont', workersMaximum: int = 1) -> None:
	pathMetadata: Path = settingsPackage.pathRoot / fontFamily

	dictionaryMetadata: dict[int, str] = getMetadataByFontWeight('', settingsPackage.filenameFontFamilyLocale简化字, settingsPackage.fontFamilyLocale简化字)
	stringCopyright: str = dictionaryMetadata[0]
	stringTrademark: str = dictionaryMetadata[7]

	with Pool(processes=workersMaximum) as concurrencyManager:
		set(concurrencyManager.starmap(_updateCIDFontInfoMetadata, [(pathFilename, stringCopyright, stringTrademark) for pathFilename in pathMetadata.glob('glyphs/*.cidfontinfo')]))
		set(concurrencyManager.starmap(_updateCIDFontMetadata, [(pathFilename, stringCopyright) for pathFilename in pathMetadata.glob('glyphs/*.cidfont.ps')]))
		set(concurrencyManager.starmap(_updateFeatureMetadata, [(pathFilename, dictionaryMetadata) for pathFilename in pathMetadata.glob('glyphs/*.features')]))

def _updateCIDFontInfoMetadata(pathFilename: Path, stringCopyright: str, trademark: str) -> None:
	dictionaryMetadataUpdates: dict[str, str] = {
		'version': f'({settingsPackage.fontVersion})',
		'AdobeCopyright': f'({stringCopyright})',
		'Trademark': f'({trademark})',
	}

	listStringLineTransformed: list[str] = []
	for stringLine in pathFilename.read_text(encoding='utf-8').splitlines(keepends=True):
		for stringKey, stringValue in dictionaryMetadataUpdates.items():
			if stringLine.startswith(stringKey):
				listStringLineTransformed.append(f'{stringKey:<26} {stringValue}\n')
				break
		else:
			listStringLineTransformed.append(stringLine)

	pathFilename.write_text(''.join(listStringLineTransformed), encoding='utf-8')

def _updateCIDFontMetadata(pathFilename: Path, stringCopyright: str) -> None:
	stringPostScriptSource: str = pathFilename.read_bytes().decode('latin-1')
	matchStartData: regex.Match[str] | None = regex.search(r'\(Binary\)\s+\d+\s+StartData', stringPostScriptSource)
	if matchStartData is None:
		return

	stringASCIIHeader: str = stringPostScriptSource[:matchStartData.end()]

	regexVersion: regex.Pattern[str] = regex.compile(r'^(%%Version:\s+)[\d.]+', flags=regex.MULTILINE)
	regexCIDFontVersion: regex.Pattern[str] = regex.compile(r'^(/CIDFontVersion\s+)[\d.]+(.+def)', flags=regex.MULTILINE)
	regexNotice: regex.Pattern[str] = regex.compile(r'^(\s*/Notice\s+\()[^)]+', flags=regex.MULTILINE)

	stringCopyrightASCII: str = stringCopyright.removesuffix(', with Reserved Font Name "Integrated."').replace('\u2018', '"').replace('\u2019', '"')

	stringASCIIHeaderTransformed: str = regexVersion.sub(f'\\g<1>{settingsPackage.fontVersion}', stringASCIIHeader)
	stringASCIIHeaderTransformed = regexCIDFontVersion.sub(f'\\g<1>{settingsPackage.fontVersion}\\g<2>', stringASCIIHeaderTransformed)
	stringASCIIHeaderTransformed = regexNotice.sub(f'\\g<1>{stringCopyrightASCII})', stringASCIIHeaderTransformed)

	pathFilename.write_bytes((stringASCIIHeaderTransformed + stringPostScriptSource[matchStartData.end():]).encode('latin-1'))

def _updateFeatureMetadata(pathFilename: Path, dictionaryMetadata: dict[int, str]) -> None:
	stringFeatureSource: str = pathFilename.read_text(encoding='utf-8')

	regexHeadRevision: regex.Pattern[str] = regex.compile(r'(table head \{[^}]*FontRevision)[\d.]+', flags=regex.DOTALL)
	stringFeatureTransformed: str = regexHeadRevision.sub(f'\\g<1>{settingsPackage.fontVersion}', stringFeatureSource)

	regexNameTable: regex.Pattern[str] = regex.compile(r'(table name \{)(.*?)(\} name;)', flags=regex.DOTALL)
	matchNameTable: regex.Match[str] | None = regexNameTable.search(stringFeatureTransformed)
	if matchNameTable is not None:
		listNameIDToUpdate: list[int] = [0, 7, 8, 9, 10, 11, 12, 13, 14]
		listStringNameEntry: list[str] = [
			f'  nameid {nameID} "{escapesStringForOpenTypeFeature(dictionaryMetadata[nameID])}";'
			for nameID in listNameIDToUpdate if nameID in dictionaryMetadata
		]

		stringNameTableTransformed: str = f"{matchNameTable.group(1)}\n{'\n'.join(listStringNameEntry)}\n{matchNameTable.group(3)}"
		stringFeatureTransformed = regexNameTable.sub(lambda _: stringNameTableTransformed, stringFeatureTransformed, count=1)

	pathFilename.write_text(stringFeatureTransformed, encoding='utf-8')

def escapesStringForOpenTypeFeature(stringValue: str, platformID: int = 3, platformEncodingID: int = 1, languageID: int = 0x0409) -> str:
	encoding = getEncoding(platformID, platformEncodingID, languageID)
	if encoding is None:
		messageError: str = f'Unsupported encoding for platform {platformID}, encoding {platformEncodingID}, language {languageID}'
		raise ValueError(messageError)

	bytesEncoded: bytes = tobytes(stringValue, encoding=encoding)

	if encoding == 'utf_16_be':
		return ''.join(
			_escapesCharacterForOpenTypeFeature(byteord(bytesEncoded[index]) * 256 + byteord(bytesEncoded[index + 1]))
			for index in range(0, len(bytesEncoded), 2)
		)

	return ''.join(_escapesCharacterForOpenTypeFeature(byteord(byte)) for byte in bytesEncoded)

def _escapesCharacterForOpenTypeFeature(integerCodepoint: int) -> str:
	if integerCodepoint == 0x22:
		return '\\"'
	if integerCodepoint == 0x5C:
		return '\\\\\\\\'

	if 0x20 <= integerCodepoint <= 0x7E:
		return chr(integerCodepoint)

	if integerCodepoint <= 0xFF:
		return f'\\{integerCodepoint:02X}'

	if integerCodepoint <= 0xFFFF:
		return f'\\{integerCodepoint:04X}'

	return f'\\{integerCodepoint:06X}'

if __name__ == '__main__':
	scientistCreatesFrankenFont(workersMaximum=14)
