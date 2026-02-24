"""The functions in this module should be run infrequently. Put oft-run updating functions in other modules."""
# ruff: noqa: D103
from fontTools.misc.psCharStrings import T1CharString
from hunterMakesPy import raiseIfNone
from Integrated_Code_Fire import (
	bearingIncrement, filenameFontFamilyLocale, fontFamilyLocale, fontUnitsPerEm, pathRoot, settingsPackage)
from Integrated_Code_Fire.writeMetadata import escapesStringForOpenTypeFeature, getMetadataByFontWeight
from more_itertools import loops
from multiprocessing import Pool
from pathlib import Path
import fontTools.misc.eexec
import re as regex
import shutil

regexBeginData: regex.Pattern[bytes] = regex.compile(rb'%%BeginData:\s*\d+\s+Binary Bytes')
regexFontMatrix: regex.Pattern[bytes] = regex.compile(rb'/FontMatrix\s+\[([^\]]+)\]\s+def')
regexLenIV: regex.Pattern[bytes] = regex.compile(rb'/lenIV\s+(-?\d+)', flags=regex.IGNORECASE)
regexOpenTypeMetricLine: regex.Pattern[str] = regex.compile(r'^(\s*)([A-Za-z][A-Za-z0-9/]*)\s+(-?\d+)(\s*;.*)$')
regexStartData: regex.Pattern[bytes] = regex.compile(rb'\(Binary\)\s+(\d+)\s+StartData')

setOpenTypeMetricNameHhea: set[str] = {'Ascender', 'Descender', 'LineGap'}
setOpenTypeMetricNameOS2: set[str] = {'TypoAscender', 'TypoDescender', 'TypoLineGap', 'XHeight', 'CapHeight', 'winAscent', 'winDescent'}

def scientistCreatesFrankenFont(fontFamilyDonor: str = 'SourceHanMono', fontFamilyMonster: str = 'FrankenFont', workersMaximum: int = 1) -> None:
	pathDonor: Path = pathRoot / fontFamilyDonor
	pathMonster: Path = pathRoot / fontFamilyMonster

	shutil.copytree(pathDonor, pathMonster, dirs_exist_ok=True)

	for pathFilename in (*Path(pathMonster, 'metadata').glob('*.txt'), *Path(pathMonster, 'metadata').glob('*.H')):
		pathFilename: Path = pathFilename.with_stem(pathFilename.stem.replace(fontFamilyDonor, fontFamilyMonster))

	listPathFilenamesCIDFontPostScript: list[Path] = sorted(pathMonster.glob('glyphs/*.cidfont.ps'))
	listPathFilenamesOpenTypeFeature: list[Path] = sorted(pathMonster.glob('glyphs/*.features'))

	with Pool(processes=workersMaximum) as concurrencyManager:
		set(concurrencyManager.map(artisanTransformsOpenTypeFeature, listPathFilenamesOpenTypeFeature))
		set(concurrencyManager.map(artisanTransformsCIDFontPostScript, listPathFilenamesCIDFontPostScript))

#======== CID font PostScript transformations ========

def artisanTransformsCIDFontPostScript(pathFilename: Path) -> None:
	bytesPostScriptSource: bytes = pathFilename.read_bytes()
	matchStartData: regex.Match[bytes] = raiseIfNone(regexStartData.search(bytesPostScriptSource))

	lengthStartData: int = int(matchStartData.group(1))
	offsetStartData: int = matchStartData.end() + 1
	offsetEndData: int = offsetStartData + lengthStartData
	if offsetEndData > len(bytesPostScriptSource):
		message: str = f'I received {offsetEndData = }, but I need a value less than or equal to {len(bytesPostScriptSource) = }.'
		raise ValueError(message)

	bytesPrefix: bytes = bytesPostScriptSource[:offsetStartData]
	bytesStartData: bytes = bytesPostScriptSource[offsetStartData:offsetEndData]
	bytesSuffix: bytes = bytesPostScriptSource[offsetEndData:]

	integerCIDMapOffset: int = _readsIntegerKeyFromPrefix(bytesPrefix, b'CIDMapOffset')
	integerFDBytes: int = _readsIntegerKeyFromPrefix(bytesPrefix, b'FDBytes')
	integerGDBytes: int = _readsIntegerKeyFromPrefix(bytesPrefix, b'GDBytes')
	integerCIDCount: int = _readsIntegerKeyFromPrefix(bytesPrefix, b'CIDCount')

	bytesPrefixTransformed: bytes = _updatesFontMatrixEntries(bytesPrefix, fontUnitsPerEm)
	bytesStartDataTransformed: bytes = _updatesCIDStartDataBytes( bytesPrefix , bytesStartData , integerCIDMapOffset , integerFDBytes , integerGDBytes , integerCIDCount , bearingIncrement )
	bytesPostScriptTransformed: bytes = _rebuildsCIDFontPostScriptBytes( bytesPrefixTransformed , bytesSuffix , bytesStartDataTransformed )

	pathFilename.write_bytes(bytesPostScriptTransformed)

def _readsIntegerKeyFromPrefix(bytesPrefix: bytes, keyName: bytes) -> int:
	matchKey: regex.Match[bytes] = raiseIfNone(regex.search(rb'/' + regex.escape(keyName) + rb'\s+(-?\d+)', bytesPrefix))
	return int(matchKey.group(1))

def _updatesFontMatrixEntries(bytesPrefix: bytes, fontUnitsPerEmTarget: int) -> bytes:
	def replaceFontMatrix(matchFontMatrix: regex.Match[bytes]) -> bytes:
		bytesFontMatrixTransformed: bytes = matchFontMatrix.group(0)
		listNumberAsString: list[bytes] = matchFontMatrix.group(1).split()
		if len(listNumberAsString) == 6:
			listNumber: list[float] = [float(numberAsString) for numberAsString in listNumberAsString]
			floatMaximumAbsoluteScale: float = max(abs(listNumber[0]), abs(listNumber[1]), abs(listNumber[2]), abs(listNumber[3]))
			booleanScaleLooksValid: bool = floatMaximumAbsoluteScale != 0.0 and floatMaximumAbsoluteScale <= 0.01
			if booleanScaleLooksValid:
				integerFontUnitsPerEmSource: int = round(1.0 / floatMaximumAbsoluteScale)
				if integerFontUnitsPerEmSource > 0:
					floatScaleFactor: float = integerFontUnitsPerEmSource / fontUnitsPerEmTarget
					listNumberScaled: list[float] = [number * floatScaleFactor for number in listNumber]
					bytesNumberScaled: bytes = ' '.join(_formatsPostScriptNumber(number) for number in listNumberScaled).encode('ascii')
					bytesFontMatrixTransformed = b'/FontMatrix [' + bytesNumberScaled + b'] def'

		return bytesFontMatrixTransformed

	return regexFontMatrix.sub(replaceFontMatrix, bytesPrefix)

def _formatsPostScriptNumber(number: float) -> str:
	stringNumber: str = format(number, '.10f').rstrip('0').rstrip('.')
	stringNumberFormatted: str = stringNumber
	if stringNumber in {'', '-0'}:
		stringNumberFormatted = '0'
	return stringNumberFormatted

def _updatesCIDStartDataBytes(bytesPrefix: bytes, bytesStartData: bytes, integerCIDMapOffset: int, integerFDBytes: int, integerGDBytes: int, integerCIDCount: int, bearingIncrement: int) -> bytes:
	integerEntryCount: int = integerCIDCount + 1
	integerEntrySize: int = integerFDBytes + integerGDBytes
	integerMapStart: int = integerCIDMapOffset
	integerMapEnd: int = integerMapStart + integerEntryCount * integerEntrySize
	if integerMapEnd > len(bytesStartData):
		message: str = f'I received {integerMapEnd = }, but I need a value less than or equal to {len(bytesStartData) = }.'
		raise ValueError(message)

	listFDByEntry: list[int] = []
	listOffsetByEntry: list[int] = []
	offsetMapRead: int = integerMapStart
	for _indexEntry in loops(integerEntryCount):
		integerFD: int = 0
		if integerFDBytes > 0:
			integerFD = int.from_bytes(bytesStartData[offsetMapRead:offsetMapRead + integerFDBytes], 'big')
			offsetMapRead += integerFDBytes
		integerOffset: int = int.from_bytes(bytesStartData[offsetMapRead:offsetMapRead + integerGDBytes], 'big')
		offsetMapRead += integerGDBytes
		listFDByEntry.append(integerFD)
		listOffsetByEntry.append(integerOffset)

	integerGlyphDataStart: int = listOffsetByEntry[0]
	if integerGlyphDataStart < integerMapEnd:
		message: str = f'I received {integerGlyphDataStart = }, but I need a value greater than or equal to {integerMapEnd = }.'
		raise ValueError(message)
	if listOffsetByEntry[-1] > len(bytesStartData):
		message: str = (
			f'I received {listOffsetByEntry[-1] = }, '
			f'but I need a value less than or equal to {len(bytesStartData) = }.'
		)
		raise ValueError(message)

	listLenIVByFD: list[int] = _readsLenIVValuesByFD(bytesPrefix, max(listFDByEntry))

	bytearrayGlyphDataTransformed: bytearray = bytearray()
	listOffsetByEntryTransformed: list[int] = []
	integerOffsetCurrent: int = integerGlyphDataStart
	for integerCID in range(integerCIDCount):
		listOffsetByEntryTransformed.append(integerOffsetCurrent)
		integerOffsetStart: int = listOffsetByEntry[integerCID]
		integerOffsetEnd: int = listOffsetByEntry[integerCID + 1]
		if integerOffsetStart != integerOffsetEnd:
			integerFDCurrent: int = listFDByEntry[integerCID]
			integerLenIV: int = listLenIVByFD[integerFDCurrent] if integerFDCurrent < len(listLenIVByFD) else 4
			bytesCharstringTransformed: bytes = _updatesType1CharStringMetric( bytesStartData[integerOffsetStart:integerOffsetEnd] , bearingIncrement , integerLenIV )
			bytearrayGlyphDataTransformed.extend(bytesCharstringTransformed)
			integerOffsetCurrent += len(bytesCharstringTransformed)
	listOffsetByEntryTransformed.append(integerOffsetCurrent)

	bytearrayMapTransformed: bytearray = bytearray()
	for indexEntry in range(integerEntryCount):
		integerFD = listFDByEntry[indexEntry]
		integerOffset = listOffsetByEntryTransformed[indexEntry]
		if integerFDBytes > 0:
			bytearrayMapTransformed.extend(integerFD.to_bytes(integerFDBytes, 'big'))
		bytearrayMapTransformed.extend(integerOffset.to_bytes(integerGDBytes, 'big'))

	return b''.join((
		bytesStartData[:integerMapStart]
		, bytes(bytearrayMapTransformed)
		, bytesStartData[integerMapEnd:integerGlyphDataStart]
		, bytes(bytearrayGlyphDataTransformed)
		, bytesStartData[listOffsetByEntry[-1]:]
	))

def _readsLenIVValuesByFD(bytesPrefix: bytes, maximumFDIndex: int) -> list[int]:
	listLenIVFromPrefix: list[int] = [int(matchLenIV.group(1)) for matchLenIV in regexLenIV.finditer(bytesPrefix)]
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

def _updatesType1CharStringMetric(bytesCharStringSource: bytes, bearingIncrement: int, integerLenIV: int) -> bytes:
	bytesPrefixDecrypted: bytes = b''
	bytesProgramSource: bytes = bytesCharStringSource
	if integerLenIV != -1:
		tupleDecrypted: tuple[bytes, int] = fontTools.misc.eexec.decrypt(bytesCharStringSource, 4330)
		bytesDecrypted: bytes = tupleDecrypted[0]
		if integerLenIV > len(bytesDecrypted):
			message: str = f'I received {integerLenIV = }, but I need a value less than or equal to {len(bytesDecrypted) = }.'
			raise ValueError(message)
		bytesPrefixDecrypted = bytesDecrypted[:integerLenIV]
		bytesProgramSource = bytesDecrypted[integerLenIV:]

	charstring: T1CharString = T1CharString(bytecode=bytesProgramSource)
	charstring.decompile()
	listProgram: list[int | float | str | bytes] = raiseIfNone(charstring.program)
	_updatesMetricOperands(listProgram, bearingIncrement)
	charstring.program = listProgram
	charstring.compile()
	objectBytecode: bytes = raiseIfNone(charstring.bytecode)
	bytesProgramTransformed: bytes = bytes(objectBytecode)

	bytesCharstringTransformed: bytes = bytesProgramTransformed
	if integerLenIV != -1:
		bytesDecryptedTransformed: bytes = bytesPrefixDecrypted + bytesProgramTransformed
		tupleEncrypted: tuple[bytes, int] = fontTools.misc.eexec.encrypt(bytesDecryptedTransformed, 4330)
		bytesEncryptedTransformed: bytes = tupleEncrypted[0]
		bytesCharstringTransformed = bytesEncryptedTransformed

	return bytesCharstringTransformed

def _updatesMetricOperands(listProgram: list[int | float | str | bytes], bearingIncrement: int) -> None:
	booleanMetricOperatorFound: bool = False
	for indexTable, table in enumerate(listProgram):
		if table == 'hsbw':
			if indexTable < 2:
				message: str = f'I could not read expected integer operands for hsbw at {indexTable = }.'
				raise TypeError(message)
			valueSideBearing: int | float | str | bytes = listProgram[indexTable - 2]
			valueAdvanceWidth: int | float | str | bytes = listProgram[indexTable - 1]
			if not isinstance(valueSideBearing, int) or not isinstance(valueAdvanceWidth, int):
				message: str = f'I could not read expected integer operands for hsbw at {indexTable = }.'
				raise TypeError(message)
			integerSideBearingBefore: int = valueSideBearing
			integerAdvanceWidthBefore: int = valueAdvanceWidth
			listProgram[indexTable - 2] = integerSideBearingBefore + bearingIncrement
			listProgram[indexTable - 1] = integerAdvanceWidthBefore + bearingIncrement * 2
			booleanMetricOperatorFound = True
			break

		if table == 'sbw':
			if indexTable < 4:
				message: str = f'I could not read expected integer operands for sbw at {indexTable = }.'
				raise TypeError(message)
			valueSideBearing: int | float | str | bytes = listProgram[indexTable - 4]
			valueAdvanceWidth: int | float | str | bytes = listProgram[indexTable - 2]
			if not isinstance(valueSideBearing, int) or not isinstance(valueAdvanceWidth, int):
				message: str = f'I could not read expected integer operands for sbw at {indexTable = }.'
				raise TypeError(message)
			integerSideBearingBefore: int = valueSideBearing
			integerAdvanceWidthBefore: int = valueAdvanceWidth
			listProgram[indexTable - 4] = integerSideBearingBefore + bearingIncrement
			listProgram[indexTable - 2] = integerAdvanceWidthBefore + bearingIncrement * 2
			booleanMetricOperatorFound = True
			break

	if not booleanMetricOperatorFound:
		message: str = 'I could not find hsbw or sbw in the Type 1 charstring program.'
		raise ValueError(message)

def _rebuildsCIDFontPostScriptBytes(bytesPrefix: bytes, bytesSuffix: bytes, bytesStartDataTransformed: bytes) -> bytes:
	integerStartDataLength: int = len(bytesStartDataTransformed)
	bytesStartDataToken: bytes = f'(Binary) {integerStartDataLength} StartData'.encode('ascii')
	bytesPrefixUpdated: bytes = regexStartData.sub(bytesStartDataToken, bytesPrefix, count=1)

	integerLineEndingLength: int = 0
	if bytesSuffix.startswith(b'\r\n'):
		integerLineEndingLength = 2
	elif bytesSuffix.startswith((b'\r', b'\n')):
		integerLineEndingLength = 1

	integerBeginDataLength: int = len(bytesStartDataToken) + 1 + integerStartDataLength + integerLineEndingLength
	bytesBeginDataToken: bytes = f'%%BeginData: {integerBeginDataLength} Binary Bytes'.encode('ascii')
	bytesPrefixUpdated = regexBeginData.sub(bytesBeginDataToken, bytesPrefixUpdated, count=1)

	return b''.join((bytesPrefixUpdated, bytesStartDataTransformed, bytesSuffix))

#======== OpenType feature file transformations ========

def artisanTransformsOpenTypeFeature(pathFilename: Path) -> None:
	bytesFeatureSource: bytes = pathFilename.read_bytes()
	stringFeatureSource: str = bytesFeatureSource.decode('utf-8')
	stringFeatureTransformed: str = _updatesOpenTypeFeatureMetricOverrides(stringFeatureSource, fontUnitsPerEm)
	bytesFeatureTransformed: bytes = stringFeatureTransformed.encode('utf-8')
	pathFilename.write_bytes(bytesFeatureTransformed)

def _updatesOpenTypeFeatureMetricOverrides(stringFeatureSource: str, fontUnitsPerEmTarget: int) -> str:
	integerSourceUnitsPerEm: int = _readsSourceUnitsPerEmFromOpenTypeFeature(stringFeatureSource)
	floatScaleFactor: float = 1.0
	if integerSourceUnitsPerEm > 0:
		floatScaleFactor = fontUnitsPerEmTarget / integerSourceUnitsPerEm

	stringFeatureTransformed: str = stringFeatureSource
	if floatScaleFactor != 1.0:
		stringFeatureTransformed = _scalesFeatureTableMetricValues(stringFeatureTransformed, 'hhea', setOpenTypeMetricNameHhea, floatScaleFactor)
		stringFeatureTransformed = _scalesFeatureTableMetricValues(stringFeatureTransformed, 'OS/2', setOpenTypeMetricNameOS2, floatScaleFactor)

	return stringFeatureTransformed

def _readsSourceUnitsPerEmFromOpenTypeFeature(stringFeatureSource: str) -> int:
	integerUnitsPerEm: int = 0

	integerTypoAscender: int | None = _readsOpenTypeMetricValueFromFeatureTable(stringFeatureSource, 'OS/2', 'TypoAscender')
	integerTypoDescender: int | None = _readsOpenTypeMetricValueFromFeatureTable(stringFeatureSource, 'OS/2', 'TypoDescender')
	integerTypoLineGap: int | None = _readsOpenTypeMetricValueFromFeatureTable(stringFeatureSource, 'OS/2', 'TypoLineGap')
	if integerTypoAscender is not None and integerTypoDescender is not None and integerTypoLineGap is not None:
		integerUnitsPerEm = integerTypoAscender - integerTypoDescender + integerTypoLineGap

	if integerUnitsPerEm <= 0:
		hheaAscender: int | None = _readsOpenTypeMetricValueFromFeatureTable(stringFeatureSource, 'hhea', 'Ascender')
		hheaDescender: int | None = _readsOpenTypeMetricValueFromFeatureTable(stringFeatureSource, 'hhea', 'Descender')
		hheaLineGap: int | None = _readsOpenTypeMetricValueFromFeatureTable(stringFeatureSource, 'hhea', 'LineGap')
		if hheaAscender is not None and hheaDescender is not None and hheaLineGap is not None:
			integerUnitsPerEm = hheaAscender - hheaDescender + hheaLineGap

	return integerUnitsPerEm

def _readsOpenTypeMetricValueFromFeatureTable(stringFeatureSource: str, stringTableName: str, stringMetricName: str) -> int | None:
	matchTable: regex.Match[str] | None = regex.compile(
		rf'(?ms)table\s+{regex.escape(stringTableName)}\s*\{{(.*?)\}}\s*{regex.escape(stringTableName)};'
	).search(stringFeatureSource)

	integerMetricValue: int | None = None
	if matchTable is not None:
		stringTableContent: str = matchTable.group(1)
		matchMetric: regex.Match[str] | None = regex.compile(
			rf'(?m)^\s*{regex.escape(stringMetricName)}\s+(-?\d+)\s*;'
		).search(stringTableContent)
		if matchMetric is not None:
			integerMetricValue = int(matchMetric.group(1))

	return integerMetricValue

def _scalesFeatureTableMetricValues(stringFeatureSource: str, stringTableName: str, setMetricName: set[str], floatScaleFactor: float) -> str:

	listStringSection: list[str] = []
	integerOffsetCurrent: int = 0
	for matchTable in regex.compile(
		rf'(?ms)(table\s+{regex.escape(stringTableName)}\s*\{{)(.*?)(\}}\s*{regex.escape(stringTableName)};)'
	).finditer(stringFeatureSource):
		stringTableContentSource: str = matchTable.group(2)
		stringTableContentTransformed: str = _scalesOpenTypeMetricLines(stringTableContentSource, setMetricName, floatScaleFactor)
		listStringSection.append(stringFeatureSource[integerOffsetCurrent:matchTable.start()])
		listStringSection.append(matchTable.group(1))
		listStringSection.append(stringTableContentTransformed)
		listStringSection.append(matchTable.group(3))
		integerOffsetCurrent = matchTable.end()

	listStringSection.append(stringFeatureSource[integerOffsetCurrent:])
	stringFeatureTransformed: str = ''.join(listStringSection)
	return stringFeatureTransformed

def _scalesOpenTypeMetricLines(stringTableContentSource: str, setMetricName: set[str], floatScaleFactor: float) -> str:
	listStringLineSource: list[str] = stringTableContentSource.splitlines(keepends=True)
	listStringLineTransformed: list[str] = []

	for stringLineSource in listStringLineSource:
		stringLineTransformed: str = stringLineSource
		matchMetricLine: regex.Match[str] | None = regexOpenTypeMetricLine.match(stringLineSource)
		if matchMetricLine is not None:
			stringMetricName: str = matchMetricLine.group(2)
			if stringMetricName in setMetricName:
				integerMetricValueSource: int = int(matchMetricLine.group(3))
				integerMetricValueTransformed: int = round(integerMetricValueSource * floatScaleFactor)
				stringLineTransformed = (
					f'{matchMetricLine.group(1)}{stringMetricName} {integerMetricValueTransformed}{matchMetricLine.group(4)}'
				)
		listStringLineTransformed.append(stringLineTransformed)

	stringTableContentTransformed: str = ''.join(listStringLineTransformed)
	return stringTableContentTransformed

#======== Font family name transformations ========

def scribeUpdatesFontFamilyNames(fontFamilyDonor: str = 'SourceHanMono', fontFamilyMonster: str = 'FrankenFont', fontDisplayNameDonor: str = 'Source Han Mono', fontDisplayNameMonster: str = 'Franken Font', workersMaximum: int = 1) -> None:
	pathMonster: Path = pathRoot / fontFamilyMonster

	listPathFilenamesCIDFontInfo: list[Path] = sorted(pathMonster.glob('glyphs/*.cidfontinfo'))
	listPathFilenamesCIDFontPostScript: list[Path] = sorted(pathMonster.glob('glyphs/*.cidfont.ps'))
	listPathFilenamesH: list[Path] = sorted((pathMonster / 'metadata').glob('*.H'))
	listPathFilenamesFontMenuNameDB: list[Path] = [pathMonster / 'metadata' / 'FontMenuNameDB']

	with Pool(processes=workersMaximum) as concurrencyManager:
		set(concurrencyManager.starmap(_updatesCIDFontInfoFamilyNames, [(pathFilename, fontFamilyDonor, fontFamilyMonster, fontDisplayNameDonor, fontDisplayNameMonster) for pathFilename in listPathFilenamesCIDFontInfo]))
		set(concurrencyManager.starmap(_updatesCIDFontPostScriptFamilyNames, [(pathFilename, fontFamilyDonor, fontFamilyMonster, fontDisplayNameDonor, fontDisplayNameMonster) for pathFilename in listPathFilenamesCIDFontPostScript]))
		set(concurrencyManager.starmap(_updatesHFileFamilyNames, [(pathFilename, fontFamilyDonor, fontFamilyMonster) for pathFilename in listPathFilenamesH]))
		set(concurrencyManager.starmap(_updatesFontMenuNameDBFamilyNames, [(pathFilename, fontFamilyDonor, fontFamilyMonster, fontDisplayNameDonor, fontDisplayNameMonster) for pathFilename in listPathFilenamesFontMenuNameDB]))

def _updatesCIDFontInfoFamilyNames(pathFilename: Path, fontFamilyDonor: str, fontFamilyMonster: str, fontDisplayNameDonor: str, fontDisplayNameMonster: str) -> None:
	stringCIDFontInfoSource: str = pathFilename.read_text(encoding='utf-8')
	stringCIDFontInfoTransformed: str = stringCIDFontInfoSource

	regexFontName: regex.Pattern[str] = regex.compile(r'^(FontName\s+\()([^)]+)(\).*)$', flags=regex.MULTILINE)
	regexFullName: regex.Pattern[str] = regex.compile(r'^(FullName\s+\()([^)]+)(\).*)$', flags=regex.MULTILINE)
	regexFamilyName: regex.Pattern[str] = regex.compile(r'^(FamilyName\s+\()([^)]+)(\).*)$', flags=regex.MULTILINE)

	stringCIDFontInfoTransformed = regexFontName.sub(lambda matchFontName: matchFontName.group(1) + matchFontName.group(2).replace(fontFamilyDonor, fontFamilyMonster) + matchFontName.group(3), stringCIDFontInfoTransformed)
	stringCIDFontInfoTransformed = regexFullName.sub(lambda matchFullName: matchFullName.group(1) + matchFullName.group(2).replace(fontDisplayNameDonor, fontDisplayNameMonster) + matchFullName.group(3), stringCIDFontInfoTransformed)
	stringCIDFontInfoTransformed = regexFamilyName.sub(lambda matchFamilyName: matchFamilyName.group(1) + matchFamilyName.group(2).replace(fontDisplayNameDonor, fontDisplayNameMonster) + matchFamilyName.group(3), stringCIDFontInfoTransformed)

	pathFilename.write_text(stringCIDFontInfoTransformed, encoding='utf-8')

def _updatesCIDFontPostScriptFamilyNames(pathFilename: Path, fontFamilyDonor: str, fontFamilyMonster: str, fontDisplayNameDonor: str, fontDisplayNameMonster: str) -> None:
	bytesPostScriptSource: bytes = pathFilename.read_bytes()
	stringPostScriptSource: str = bytesPostScriptSource.decode('latin-1')

	matchStartData: regex.Match[str] | None = regex.search(r'\(Binary\)\s+\d+\s+StartData', stringPostScriptSource)
	if matchStartData is None:
		return

	offsetBinaryStart: int = matchStartData.end()
	stringASCIIHeader: str = stringPostScriptSource[:offsetBinaryStart]
	stringBinaryRemainder: str = stringPostScriptSource[offsetBinaryStart:]

	stringASCIIHeaderTransformed: str = stringASCIIHeader
	stringASCIIHeaderTransformed = stringASCIIHeaderTransformed.replace(fontFamilyDonor, fontFamilyMonster)
	stringASCIIHeaderTransformed = stringASCIIHeaderTransformed.replace(fontDisplayNameDonor, fontDisplayNameMonster)

	stringPostScriptTransformed: str = stringASCIIHeaderTransformed + stringBinaryRemainder
	bytesPostScriptTransformed: bytes = stringPostScriptTransformed.encode('latin-1')
	pathFilename.write_bytes(bytesPostScriptTransformed)

def _updatesHFileFamilyNames(pathFilename: Path, fontFamilyDonor: str, fontFamilyMonster: str) -> None:
	stringHFileSource: str = pathFilename.read_text(encoding='utf-8')
	stringHFileTransformed: str = stringHFileSource.replace(fontFamilyDonor, fontFamilyMonster)
	pathFilename.write_text(stringHFileTransformed, encoding='utf-8')

def _updatesFontMenuNameDBFamilyNames(pathFilename: Path, fontFamilyDonor: str, fontFamilyMonster: str, fontDisplayNameDonor: str, fontDisplayNameMonster: str) -> None:
	stringFontMenuNameDBSource: str = pathFilename.read_text(encoding='utf-8')
	stringFontMenuNameDBTransformed: str = stringFontMenuNameDBSource

	stringFontMenuNameDBTransformed = stringFontMenuNameDBTransformed.replace(f'[{fontFamilyDonor}', f'[{fontFamilyMonster}')
	stringFontMenuNameDBTransformed = stringFontMenuNameDBTransformed.replace(fontDisplayNameDonor, fontDisplayNameMonster)

	pathFilename.write_text(stringFontMenuNameDBTransformed, encoding='utf-8')

#======== Metadata transformations ========

def scribeUpdatesMetadata(fontFamily: str = 'FrankenFont', workersMaximum: int = 1) -> None:
	pathMonster: Path = pathRoot / fontFamily
	listPathFilenamesCIDFontInfo: list[Path] = sorted(pathMonster.glob('glyphs/*.cidfontinfo'))
	listPathFilenamesCIDFontPostScript: list[Path] = sorted(pathMonster.glob('glyphs/*.cidfont.ps'))
	listPathFilenamesOpenTypeFeature: list[Path] = sorted(pathMonster.glob('glyphs/*.features'))

	dictionaryMetadata: dict[int, str] = getMetadataByFontWeight('', filenameFontFamilyLocale, fontFamilyLocale)
	stringCopyright: str = dictionaryMetadata[0]
	stringTrademark: str = dictionaryMetadata[7]

	with Pool(processes=workersMaximum) as concurrencyManager:
		set(concurrencyManager.starmap(_updatesCIDFontInfoMetadata, [(pathFilename, stringCopyright, stringTrademark) for pathFilename in listPathFilenamesCIDFontInfo]))
		set(concurrencyManager.starmap(_updatesCIDFontPostScriptMetadata, [(pathFilename, stringCopyright) for pathFilename in listPathFilenamesCIDFontPostScript]))
		set(concurrencyManager.starmap(_updatesOpenTypeFeatureMetadata, [(pathFilename, dictionaryMetadata) for pathFilename in listPathFilenamesOpenTypeFeature]))

def _updatesCIDFontInfoMetadata(pathFilename: Path, stringCopyright: str, stringTrademark: str) -> None:
	dictionaryMetadataUpdates: dict[str, str] = {
		'version': f'({settingsPackage.fontVersion})',
		'AdobeCopyright': f'({stringCopyright})',
		'Trademark': f'({stringTrademark})',
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

def _updatesCIDFontPostScriptMetadata(pathFilename: Path, stringCopyright: str) -> None:
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

def _updatesOpenTypeFeatureMetadata(pathFilename: Path, dictionaryMetadata: dict[int, str]) -> None:
	stringFeatureSource: str = pathFilename.read_text(encoding='utf-8')

	regexHeadRevision: regex.Pattern[str] = regex.compile(r'(table head \{[^}]*FontRevision )[\d.]+', flags=regex.DOTALL)
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
	# scientistCreatesFrankenFont(workersMaximum=14)  # noqa: ERA001
	scribeUpdatesFontFamilyNames(workersMaximum=14)
	scribeUpdatesMetadata(workersMaximum=14)
