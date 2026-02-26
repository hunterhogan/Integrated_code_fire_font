"""The functions in this module are to renovate other fonts and should be run infrequently. Put oft-run updating-functions in other modules."""
# ruff: noqa: D103
from concurrent.futures import as_completed, Future, ProcessPoolExecutor
from fontTools.misc.psCharStrings import T1CharString
from hunterMakesPy import raiseIfNone
from Integrated_Code_Fire import bearingIncrement, settingsPackage
from Integrated_Code_Fire.writeMetadata import escapesStringForOpenTypeFeature, getMetadataByFontWeight
from itertools import repeat
from more_itertools import loops
from multiprocessing import Pool
from tqdm import tqdm
from typing import TYPE_CHECKING
import fontTools.misc.eexec
import re as regex
import shutil

if TYPE_CHECKING:
	from pathlib import Path

regexBeginData: regex.Pattern[bytes] = regex.compile(rb'%%BeginData:\s*\d+\s+Binary Bytes')
regexFontMatrix: regex.Pattern[bytes] = regex.compile(rb'/FontMatrix\s+\[([^\]]+)\]\s+def')
regexLenIV: regex.Pattern[bytes] = regex.compile(rb'/lenIV\s+(-?\d+)', flags=regex.IGNORECASE)
regexOpenTypeMetricLine: regex.Pattern[str] = regex.compile(r'^(\s*)([A-Za-z][A-Za-z0-9/]*)\s+(-?\d+)(\s*;.*)$')
regexStartData: regex.Pattern[bytes] = regex.compile(rb'\(Binary\)\s+(\d+)\s+StartData')

set_hhea: set[str] = {'Ascender', 'Descender', 'LineGap'}
setOS2: set[str] = {'TypoAscender', 'TypoDescender', 'TypoLineGap', 'XHeight', 'CapHeight', 'winAscent', 'winDescent'}

def scientistCreatesFrankenFont(fontFamilyDonor: str = 'SourceHanMono', fontFamilyMonster: str = 'FrankenFont', workersMaximum: int = 1) -> None:
	pathDonor: Path = settingsPackage.pathRoot / fontFamilyDonor
	pathMonster: Path = settingsPackage.pathRoot / fontFamilyMonster

	shutil.copytree(pathDonor, pathMonster, dirs_exist_ok=True)

	for pathFilename in (*pathMonster.rglob('*.txt'), *pathMonster.rglob('*.H')):
		pathFilename.rename(pathFilename.with_stem(pathFilename.stem.replace(fontFamilyDonor, fontFamilyMonster)))

	with ProcessPoolExecutor(workersMaximum) as concurrencyManager:
		listClaimTickets: list[Future[None]] =list(map(concurrencyManager.submit, repeat(artisanChangesFeatures), pathMonster.glob('glyphs/*.features')))  # pyright: ignore[reportArgumentType] # ty:ignore[invalid-argument-type]
		listClaimTickets.extend(map(concurrencyManager.submit, repeat(artisanChangesPostScript), pathMonster.glob('glyphs/*.cidfont.ps')))  # pyright: ignore[reportArgumentType] # ty:ignore[invalid-argument-type]

		for claimTicket in tqdm(as_completed(listClaimTickets), total=len(listClaimTickets), desc='Applying artisan changes'):
			claimTicket.result()

	scribeUpdatesFontFamily(workersMaximum=14)
	scribeUpdatesMetadata(workersMaximum=14)

#======== CID font PostScript transformations ========

def artisanChangesPostScript(pathFilename: Path) -> None:
	PostScript: bytes = pathFilename.read_bytes()
	matchStartData: regex.Match[bytes] = raiseIfNone(regexStartData.search(PostScript))

	offsetStart: int = matchStartData.end() + 1
	offsetEnd: int = offsetStart + int(matchStartData.group(1))

	prefix: bytes = PostScript[:offsetStart]

	bytesPostScriptTransformed: bytes = _rebuildCIDFont(_updateFontMatrix(prefix, settingsPackage.unitsPerEm), PostScript[offsetEnd:]
			, _updateCIDStart(prefix, PostScript[offsetStart:offsetEnd]
				, _getInt(prefix, b'CIDMapOffset')
				, _getInt(prefix, b'FDBytes')
				, _getInt(prefix, b'GDBytes')
				, _getInt(prefix, b'CIDCount')
				, bearingIncrement))

	pathFilename.write_bytes(bytesPostScriptTransformed)

def _getInt(prefix: bytes, key: bytes) -> int:
	return int(raiseIfNone(regex.search(rb'/' + regex.escape(key) + rb'\s+(-?\d+)', prefix)).group(1))

def _updateFontMatrix(prefix: bytes, unitsPerEm: int) -> bytes:
	def replaceFontMatrix(matchFontMatrix: regex.Match[bytes]) -> bytes:
		bytesFontMatrixTransformed: bytes = matchFontMatrix.group(0)
		listNumberAsString: list[bytes] = matchFontMatrix.group(1).split()
		if len(listNumberAsString) == 6:
			listNumber: list[float] = [float(numberAsString) for numberAsString in listNumberAsString]
			MaximumAbsoluteScale: float = max(abs(listNumber[0]), abs(listNumber[1]), abs(listNumber[2]), abs(listNumber[3]))
			if MaximumAbsoluteScale != 0.0 and MaximumAbsoluteScale <= 0.01:
				FontUnitsPerEmSource: int = round(1.0 / MaximumAbsoluteScale)
				if FontUnitsPerEmSource > 0:
					listNumberScaled: list[float] = [number * (FontUnitsPerEmSource / unitsPerEm) for number in listNumber]
					bytesNumberScaled: bytes = ' '.join(_formatFloat(number) for number in listNumberScaled).encode('ascii')
					bytesFontMatrixTransformed = b'/FontMatrix [' + bytesNumberScaled + b'] def'

		return bytesFontMatrixTransformed

	return regexFontMatrix.sub(replaceFontMatrix, prefix)

def _formatFloat(number: float) -> str:
	string: str = format(number, '.10f').rstrip('0').rstrip('.')
	if string in {'', '-0'}:
		string = '0'
	return string

def _updateCIDStart(prefix: bytes, startData: bytes, CIDMapOffset: int, FDBytes: int, GDBytes: int, CIDCount: int, bearingIncrement: int) -> bytes:
	EntryCount: int = CIDCount + 1
	MapStart: int = CIDMapOffset
	MapEnd: int = MapStart + EntryCount * (FDBytes + GDBytes)

	listFDByEntry: list[int] = []
	listOffsetByEntry: list[int] = []
	offsetMapRead: int = MapStart
	for _indexEntry in loops(EntryCount):
		FD: int = 0
		if FDBytes > 0:
			FD = int.from_bytes(startData[offsetMapRead:offsetMapRead + FDBytes], 'big')
			offsetMapRead += FDBytes
		offsetMapRead += GDBytes
		listFDByEntry.append(FD)
		listOffsetByEntry.append(int.from_bytes(startData[offsetMapRead:offsetMapRead + GDBytes], 'big'))

	GlyphDataStart: int = listOffsetByEntry[0]

	listLenIVByFD: list[int] = _getLenIV(prefix, max(listFDByEntry))

	bytearrayGlyphDataTransformed: bytearray = bytearray()
	listOffsetByEntryTransformed: list[int] = []
	OffsetCurrent: int = GlyphDataStart
	for CID in range(CIDCount):
		listOffsetByEntryTransformed.append(OffsetCurrent)
		if listOffsetByEntry[CID] != listOffsetByEntry[CID + 1]:
			FDCurrent: int = listFDByEntry[CID]
			LenIV: int = listLenIVByFD[FDCurrent] if FDCurrent < len(listLenIVByFD) else 4
			bytesCharstringTransformed: bytes = _updateT1CharString(startData[listOffsetByEntry[CID]:listOffsetByEntry[CID + 1]], bearingIncrement, LenIV)
			bytearrayGlyphDataTransformed.extend(bytesCharstringTransformed)
			OffsetCurrent += len(bytesCharstringTransformed)
	listOffsetByEntryTransformed.append(OffsetCurrent)

	bytearrayMapTransformed: bytearray = bytearray()
	for indexEntry in range(EntryCount):
		FD = listFDByEntry[indexEntry]
		if FDBytes > 0:
			bytearrayMapTransformed.extend(FD.to_bytes(FDBytes, 'big'))
		bytearrayMapTransformed.extend(listOffsetByEntryTransformed[indexEntry].to_bytes(GDBytes, 'big'))

	return b''.join((startData[:MapStart], bytes(bytearrayMapTransformed), startData[MapEnd:GlyphDataStart], bytes(bytearrayGlyphDataTransformed), startData[listOffsetByEntry[-1]:]))

def _getLenIV(prefix: bytes, maximumFDIndex: int) -> list[int]:
	listLenIVFromPrefix: list[int] = [int(matchLenIV.group(1)) for matchLenIV in regexLenIV.finditer(prefix)]
	listLenIVByFD: list[int] = []
	if not listLenIVFromPrefix:
		listLenIVByFD = [4] * (maximumFDIndex + 1)
	elif len(listLenIVFromPrefix) == 1:
		listLenIVByFD = [listLenIVFromPrefix[0]] * (maximumFDIndex + 1)
	else:
		for indexFD in range(maximumFDIndex + 1):
			if indexFD < len(listLenIVFromPrefix):
				listLenIVByFD.append(listLenIVFromPrefix[indexFD])
			else:
				listLenIVByFD.append(listLenIVFromPrefix[-1])
	return listLenIVByFD

def _updateT1CharString(CharString: bytes, bearingIncrement: int, LenIV: int) -> bytes:
	prefixDecrypted: bytes = b''
	bytesProgramSource: bytes = CharString
	if LenIV != -1:
		tupleDecrypted: tuple[bytes, int] = fontTools.misc.eexec.decrypt(CharString, 4330)
		bytesDecrypted: bytes = tupleDecrypted[0]
		prefixDecrypted = bytesDecrypted[:LenIV]
		bytesProgramSource = bytesDecrypted[LenIV:]

	charstring: T1CharString = T1CharString(bytecode=bytesProgramSource)
	charstring.decompile()
	listProgram: list[int | float | str | bytes] = raiseIfNone(charstring.program)
	_updateBearings(listProgram, bearingIncrement)
	charstring.program = listProgram
	charstring.compile()
	bytesProgramTransformed: bytes = bytes(raiseIfNone(charstring.bytecode))

	bytesCharstringTransformed: bytes = bytesProgramTransformed
	if LenIV != -1:
		bytesDecryptedTransformed: bytes = prefixDecrypted + bytesProgramTransformed
		tupleEncrypted: tuple[bytes, int] = fontTools.misc.eexec.encrypt(bytesDecryptedTransformed, 4330)
		bytesEncryptedTransformed: bytes = tupleEncrypted[0]
		bytesCharstringTransformed = bytesEncryptedTransformed

	return bytesCharstringTransformed

def _updateBearings(listProgram: list[int | float | str | bytes], bearingIncrement: int) -> None:
	if 'hsbw' in listProgram:
		index: int = listProgram.index('hsbw')
		listProgram[index - 2] += bearingIncrement  # pyright: ignore[reportOperatorIssue] # ty:ignore[unsupported-operator]
		listProgram[index - 1] += bearingIncrement * 2  # pyright: ignore[reportOperatorIssue] # ty:ignore[unsupported-operator]

	elif 'sbw' in listProgram:
		index = listProgram.index('sbw')
		listProgram[index - 4] += bearingIncrement  # pyright: ignore[reportOperatorIssue] # ty:ignore[unsupported-operator]
		listProgram[index - 2] += bearingIncrement * 2  # pyright: ignore[reportOperatorIssue] # ty:ignore[unsupported-operator]

def _rebuildCIDFont(prefix: bytes, suffix: bytes, startData: bytes) -> bytes:
	StartDataLength: int = len(startData)
	bytesStartDataToken: bytes = f'(Binary) {StartDataLength} StartData'.encode('ascii')
	prefixUpdated: bytes = regexStartData.sub(bytesStartDataToken, prefix, count=1)

	LineEndingLength: int = 0
	if suffix.startswith(b'\r\n'):
		LineEndingLength = 2
	elif suffix.startswith((b'\r', b'\n')):
		LineEndingLength = 1

	bytesBeginDataToken: bytes = f'%%BeginData: {len(bytesStartDataToken) + 1 + StartDataLength + LineEndingLength} Binary Bytes'.encode('ascii')
	prefixUpdated = regexBeginData.sub(bytesBeginDataToken, prefixUpdated, count=1)

	return b''.join((prefixUpdated, startData, suffix))

#======== OpenType feature file transformations ========

def artisanChangesFeatures(pathFilename: Path) -> None:
	stringFeatureSource: str = pathFilename.read_bytes().decode('utf-8')
	stringFeatureTransformed: str = _updateOverrides(stringFeatureSource, settingsPackage.unitsPerEm)
	pathFilename.write_bytes(stringFeatureTransformed.encode('utf-8'))

def _updateOverrides(feature: str, unitsPerEm: int) -> str:
	SourceUnitsPerEm: int = _getSourceUnitsPerEm(feature)
	scaleBy: float = 1.0
	if SourceUnitsPerEm > 0:
		scaleBy = unitsPerEm / SourceUnitsPerEm

	stringFeatureTransformed: str = feature
	if scaleBy != 1.0:
		stringFeatureTransformed = _scaleMetrics(stringFeatureTransformed, 'hhea', set_hhea, scaleBy)
		stringFeatureTransformed = _scaleMetrics(stringFeatureTransformed, 'OS/2', setOS2, scaleBy)

	return stringFeatureTransformed

def _getSourceUnitsPerEm(feature: str) -> int:
	UnitsPerEm: int = 0

	if ((TypoAscender := _useRegexForEverythingBecauseNoOneInTheUniverseHasEverDoneThisBefore(feature, 'OS/2', 'TypoAscender')) is not None
		and (TypoDescender := _useRegexForEverythingBecauseNoOneInTheUniverseHasEverDoneThisBefore(feature, 'OS/2', 'TypoDescender')) is not None
		and (TypoLineGap := _useRegexForEverythingBecauseNoOneInTheUniverseHasEverDoneThisBefore(feature, 'OS/2', 'TypoLineGap')) is not None):
		UnitsPerEm = TypoAscender - TypoDescender + TypoLineGap

	if (UnitsPerEm <= 0
		and (hheaAscender := _useRegexForEverythingBecauseNoOneInTheUniverseHasEverDoneThisBefore(feature, 'hhea', 'Ascender')) is not None
		and (hheaDescender := _useRegexForEverythingBecauseNoOneInTheUniverseHasEverDoneThisBefore(feature, 'hhea', 'Descender')) is not None
		and (hheaLineGap := _useRegexForEverythingBecauseNoOneInTheUniverseHasEverDoneThisBefore(feature, 'hhea', 'LineGap')) is not None):
		UnitsPerEm = hheaAscender - hheaDescender + hheaLineGap

	return UnitsPerEm

def _useRegexForEverythingBecauseNoOneInTheUniverseHasEverDoneThisBefore(feature: str, table: str, metric: str) -> int | None:
	matchTable: regex.Match[str] | None = regex.compile(
		rf'(?ms)table\s+{regex.escape(table)}\s*\{{(.*?)\}}\s*{regex.escape(table)};'
	).search(feature)

	MetricValue: int |   None = None
	if matchTable is not None:
		stringTableContent: str = matchTable.group(1)
		matchMetric: regex.Match[str] | None = regex.compile(
			rf'(?m)^\s*{regex.escape(metric)}\s+(-?\d+)\s*;'
		).search(stringTableContent)
		if matchMetric is not None:
			MetricValue = int(matchMetric.group(1))

	return MetricValue

def _scaleMetrics(feature: str, table: str, metric: set[str], scaleBy: float) -> str:

	listStringSection: list[str] = []
	OffsetCurrent: int = 0
	for matchTable in regex.compile(
		rf'(?ms)(table\s+{regex.escape(table)}\s*\{{)(.*?)(\}}\s*{regex.escape(table)};)'
	).finditer(feature):
		stringTableContentSource: str = matchTable.group(2)
		stringTableContentTransformed: str = _scaleLines(stringTableContentSource, metric, scaleBy)
		listStringSection.append(feature[OffsetCurrent:matchTable.start()])
		listStringSection.append(matchTable.group(1))
		listStringSection.append(stringTableContentTransformed)
		listStringSection.append(matchTable.group(3))
		OffsetCurrent = matchTable.end()

	listStringSection.append(feature[OffsetCurrent:])
	return ''.join(listStringSection)

def _scaleLines(tableContent: str, setMetricNames: set[str], scaleBy: float) -> str:
	listStringLineSource: list[str] = tableContent.splitlines(keepends=True)
	listStringLineTransformed: list[str] = []

	for stringLineSource in listStringLineSource:
		stringLineTransformed: str = stringLineSource
		matchMetricLine: regex.Match[str] | None = regexOpenTypeMetricLine.match(stringLineSource)
		if matchMetricLine is not None:
			stringMetricName: str = matchMetricLine.group(2)
			if stringMetricName in setMetricNames:
				MetricValueSource: int = int(matchMetricLine.group(3))
				MetricValueTransformed: int = round(MetricValueSource * scaleBy)
				stringLineTransformed = (
					f'{matchMetricLine.group(1)}{stringMetricName} {MetricValueTransformed}{matchMetricLine.group(4)}'
				)
		listStringLineTransformed.append(stringLineTransformed)

	stringTableContentTransformed: str = ''.join(listStringLineTransformed)
	return stringTableContentTransformed

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

if __name__ == '__main__':
	scientistCreatesFrankenFont(workersMaximum=14)
