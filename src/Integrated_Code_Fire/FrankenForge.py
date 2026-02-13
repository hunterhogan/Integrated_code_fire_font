# ruff: noqa: D100, D103, S105, TC003
# pyright: reportUnknownArgumentType=false, reportUnknownVariableType=false, reportUnknownMemberType=false
from fontTools.misc import eexec
from fontTools.misc.psCharStrings import T1CharString
from Integrated_Code_Fire import (
	bearingIncrement as bearingIncrementDefault, fontUnitsPerEm as fontUnitsPerEmDefault, settingsPackage)
from pathlib import Path
from typing import cast
import re
import shutil

regularExpressionBeginData: re.Pattern[bytes] = re.compile(rb'%%BeginData:\s*\d+\s+Binary Bytes')
regularExpressionFontMatrix: re.Pattern[bytes] = re.compile(rb'/FontMatrix\s+\[([^\]]+)\]\s+def')
regularExpressionLenIv: re.Pattern[bytes] = re.compile(rb'/lenIV\s+(-?\d+)', flags=re.IGNORECASE)
regularExpressionStartData: re.Pattern[bytes] = re.compile(rb'\(Binary\)\s+(\d+)\s+StartData')


def forgesFrankenFontFromSourceHanMono(
	pathRootSourceHanMono: Path | None = None
	, pathRootFrankenFont: Path | None = None
	, fontUnitsPerEmTarget: int = fontUnitsPerEmDefault
	, bearingIncrement: int = bearingIncrementDefault
) -> None:
	pathRootRepository: Path = settingsPackage.pathPackage.parent.parent
	pathRootSource: Path = pathRootSourceHanMono if pathRootSourceHanMono is not None else pathRootRepository / 'SourceHanMono'
	pathRootTarget: Path = pathRootFrankenFont if pathRootFrankenFont is not None else pathRootRepository / 'FrankenFont'

	if not pathRootSource.exists():
		raise FileNotFoundError(pathRootSource)

	if pathRootTarget.exists():
		shutil.rmtree(pathRootTarget)

	listPathFilenameSource: list[Path] = sorted(pathPath for pathPath in pathRootSource.rglob('*') if pathPath.is_file())
	if len(listPathFilenameSource) != 256:
		message: str = f'I received {len(listPathFilenameSource) = }, but I need 256 source files.'
		raise ValueError(message)

	for pathFilenameSource in listPathFilenameSource:
		pathFilenameTarget: Path = pathRootTarget / pathFilenameSource.relative_to(pathRootSource)
		pathFilenameTarget.parent.mkdir(parents=True, exist_ok=True)
		if _thisIsCidFontPostScriptFile(pathFilenameSource):
			forgesCidFontPostScriptFile(pathFilenameSource, pathFilenameTarget, fontUnitsPerEmTarget, bearingIncrement)
		else:
			shutil.copy2(pathFilenameSource, pathFilenameTarget)

	listPathFilenameTarget: list[Path] = sorted(pathPath for pathPath in pathRootTarget.rglob('*') if pathPath.is_file())
	if len(listPathFilenameTarget) != len(listPathFilenameSource):
		message: str = (
			f'I received {len(listPathFilenameTarget) = }, '
			f'but I need {len(listPathFilenameSource) = }.'
		)
		raise ValueError(message)


def forgesCidFontPostScriptFile(
	pathFilenameSource: Path
	, pathFilenameTarget: Path
	, fontUnitsPerEmTarget: int
	, bearingIncrement: int
) -> None:
	bytesFileSource: bytes = pathFilenameSource.read_bytes()
	matchStartData = regularExpressionStartData.search(bytesFileSource)
	if matchStartData is None:
		message: str = f'I could not find StartData in {pathFilenameSource = }.'
		raise ValueError(message)

	lengthStartData: int = int(matchStartData.group(1))
	offsetStartData: int = matchStartData.end() + 1
	offsetEndData: int = offsetStartData + lengthStartData
	if offsetEndData > len(bytesFileSource):
		message: str = f'I received {offsetEndData = }, but I need a value less than or equal to {len(bytesFileSource) = }.'
		raise ValueError(message)

	bytesPrefix: bytes = bytesFileSource[:offsetStartData]
	bytesStartData: bytes = bytesFileSource[offsetStartData:offsetEndData]
	bytesSuffix: bytes = bytesFileSource[offsetEndData:]

	integerCidMapOffset: int = _readsIntegerKeyFromPrefix(bytesPrefix, b'CIDMapOffset')
	integerFdBytes: int = _readsIntegerKeyFromPrefix(bytesPrefix, b'FDBytes')
	integerGdBytes: int = _readsIntegerKeyFromPrefix(bytesPrefix, b'GDBytes')
	integerCidCount: int = _readsIntegerKeyFromPrefix(bytesPrefix, b'CIDCount')

	bytesPrefixTransformed: bytes = _updatesFontMatrixEntries(bytesPrefix, fontUnitsPerEmTarget)
	bytesStartDataTransformed: bytes = _updatesCidStartDataBytes(
		bytesPrefix
		, bytesStartData
		, integerCidMapOffset
		, integerFdBytes
		, integerGdBytes
		, integerCidCount
		, bearingIncrement
	)
	bytesFileTransformed: bytes = _rebuildsCidFontPostScriptFile(
		bytesPrefixTransformed
		, bytesSuffix
		, bytesStartDataTransformed
	)

	pathFilenameTarget.write_bytes(bytesFileTransformed)


def _thisIsCidFontPostScriptFile(pathFilename: Path) -> bool:
	return len(pathFilename.parts) >= 2 and pathFilename.parts[-2] == 'glyphs' and pathFilename.name.endswith('.cidfont.ps')


def _readsIntegerKeyFromPrefix(bytesPrefix: bytes, keyName: bytes) -> int:
	matchKey = re.search(rb'/' + re.escape(keyName) + rb'\s+(-?\d+)', bytesPrefix)
	if matchKey is None:
		message: str = f'I could not find {keyName = } in the CID source prefix.'
		raise ValueError(message)
	return int(matchKey.group(1))


def _updatesFontMatrixEntries(bytesPrefix: bytes, fontUnitsPerEmTarget: int) -> bytes:
	def replaceFontMatrix(matchFontMatrix: re.Match[bytes]) -> bytes:
		listNumberAsString: list[bytes] = matchFontMatrix.group(1).split()
		if len(listNumberAsString) != 6:
			return matchFontMatrix.group(0)

		listNumber: list[float] = [float(numberAsString) for numberAsString in listNumberAsString]
		floatMaximumAbsoluteScale: float = max(abs(listNumber[0]), abs(listNumber[1]), abs(listNumber[2]), abs(listNumber[3]))
		if floatMaximumAbsoluteScale == 0.0 or floatMaximumAbsoluteScale > 0.01:
			return matchFontMatrix.group(0)

		integerFontUnitsPerEmSource: int = round(1.0 / floatMaximumAbsoluteScale)
		if integerFontUnitsPerEmSource <= 0:
			return matchFontMatrix.group(0)

		floatScaleFactor: float = integerFontUnitsPerEmSource / fontUnitsPerEmTarget
		listNumberScaled: list[float] = [number * floatScaleFactor for number in listNumber]
		bytesNumberScaled: bytes = ' '.join(_formatsPostScriptNumber(number) for number in listNumberScaled).encode('ascii')
		return b'/FontMatrix [' + bytesNumberScaled + b'] def'

	return regularExpressionFontMatrix.sub(replaceFontMatrix, bytesPrefix)


def _formatsPostScriptNumber(number: float) -> str:
	stringNumber: str = format(number, '.10f').rstrip('0').rstrip('.')
	if stringNumber in {'', '-0'}:
		return '0'
	return stringNumber


def _updatesCidStartDataBytes(
	bytesPrefix: bytes
	, bytesStartData: bytes
	, integerCidMapOffset: int
	, integerFdBytes: int
	, integerGdBytes: int
	, integerCidCount: int
	, bearingIncrement: int
) -> bytes:
	integerEntryCount: int = integerCidCount + 1
	integerEntrySize: int = integerFdBytes + integerGdBytes
	integerMapStart: int = integerCidMapOffset
	integerMapEnd: int = integerMapStart + integerEntryCount * integerEntrySize
	if integerMapEnd > len(bytesStartData):
		message: str = f'I received {integerMapEnd = }, but I need a value less than or equal to {len(bytesStartData) = }.'
		raise ValueError(message)

	listFdByEntry: list[int] = []
	listOffsetByEntry: list[int] = []
	offsetMapRead: int = integerMapStart
	for _indexEntry in range(integerEntryCount):
		integerFd: int = 0
		if integerFdBytes > 0:
			integerFd = int.from_bytes(bytesStartData[offsetMapRead:offsetMapRead + integerFdBytes], 'big')
			offsetMapRead += integerFdBytes
		integerOffset: int = int.from_bytes(bytesStartData[offsetMapRead:offsetMapRead + integerGdBytes], 'big')
		offsetMapRead += integerGdBytes
		listFdByEntry.append(integerFd)
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

	listLenIvByFd: list[int] = _readsLenIvValuesByFd(bytesPrefix, max(listFdByEntry))

	bytearrayGlyphDataTransformed = bytearray()
	listOffsetByEntryTransformed: list[int] = []
	integerOffsetCurrent: int = integerGlyphDataStart
	for integerCid in range(integerCidCount):
		listOffsetByEntryTransformed.append(integerOffsetCurrent)
		integerOffsetStart: int = listOffsetByEntry[integerCid]
		integerOffsetEnd: int = listOffsetByEntry[integerCid + 1]
		if integerOffsetStart != integerOffsetEnd:
			integerFdCurrent: int = listFdByEntry[integerCid]
			integerLenIv: int = listLenIvByFd[integerFdCurrent] if integerFdCurrent < len(listLenIvByFd) else 4
			bytesCharstringTransformed: bytes = _updatesType1CharstringMetric(
				bytesStartData[integerOffsetStart:integerOffsetEnd]
				, bearingIncrement
				, integerLenIv
			)
			bytearrayGlyphDataTransformed.extend(bytesCharstringTransformed)
			integerOffsetCurrent += len(bytesCharstringTransformed)
	listOffsetByEntryTransformed.append(integerOffsetCurrent)

	bytearrayMapTransformed = bytearray()
	for indexEntry in range(integerEntryCount):
		integerFd = listFdByEntry[indexEntry]
		integerOffset = listOffsetByEntryTransformed[indexEntry]
		if integerFdBytes > 0:
			bytearrayMapTransformed.extend(integerFd.to_bytes(integerFdBytes, 'big'))
		bytearrayMapTransformed.extend(integerOffset.to_bytes(integerGdBytes, 'big'))

	return b''.join((
		bytesStartData[:integerMapStart]
		, bytes(bytearrayMapTransformed)
		, bytesStartData[integerMapEnd:integerGlyphDataStart]
		, bytes(bytearrayGlyphDataTransformed)
		, bytesStartData[listOffsetByEntry[-1]:]
	))


def _readsLenIvValuesByFd(bytesPrefix: bytes, maximumFdIndex: int) -> list[int]:
	listLenIvFromFile: list[int] = [int(matchLenIv.group(1)) for matchLenIv in regularExpressionLenIv.finditer(bytesPrefix)]
	if not listLenIvFromFile:
		return [4] * (maximumFdIndex + 1)
	if len(listLenIvFromFile) == 1:
		return [listLenIvFromFile[0]] * (maximumFdIndex + 1)

	listLenIvByFd: list[int] = []
	for indexFd in range(maximumFdIndex + 1):
		if indexFd < len(listLenIvFromFile):
			listLenIvByFd.append(listLenIvFromFile[indexFd])
		else:
			listLenIvByFd.append(listLenIvFromFile[-1])
	return listLenIvByFd


def _updatesType1CharstringMetric(
	bytesCharstringSource: bytes
	, bearingIncrement: int
	, integerLenIv: int
) -> bytes:
	bytesPrefixDecrypted: bytes = b''
	bytesProgramSource: bytes = bytesCharstringSource
	if integerLenIv != -1:
		tupleDecrypted: tuple[bytes, int] = cast(tuple[bytes, int], eexec.decrypt(bytesCharstringSource, 4330))
		bytesDecrypted: bytes = tupleDecrypted[0]
		if integerLenIv > len(bytesDecrypted):
			message: str = f'I received {integerLenIv = }, but I need a value less than or equal to {len(bytesDecrypted) = }.'
			raise ValueError(message)
		bytesPrefixDecrypted = bytesDecrypted[:integerLenIv]
		bytesProgramSource = bytesDecrypted[integerLenIv:]

	charstring = T1CharString(bytecode=bytesProgramSource)
	charstring.decompile()
	objectProgram = charstring.program
	if not isinstance(objectProgram, list):
		message: str = f'I received {objectProgram = }, but I need a list from T1CharString.program.'
		raise TypeError(message)
	listProgram: list[object] = cast(list[object], objectProgram)
	_updatesMetricOperands(listProgram, bearingIncrement)
	charstring.program = listProgram
	charstring.compile()
	objectBytecode = charstring.bytecode
	if not isinstance(objectBytecode, (bytes, bytearray)):
		message: str = f'I received {objectBytecode = }, but I need bytes from T1CharString.bytecode.'
		raise TypeError(message)
	bytesProgramTransformed: bytes = bytes(objectBytecode)

	if integerLenIv == -1:
		return bytesProgramTransformed

	bytesDecryptedTransformed: bytes = bytesPrefixDecrypted + bytesProgramTransformed
	tupleEncrypted: tuple[bytes, int] = cast(tuple[bytes, int], eexec.encrypt(bytesDecryptedTransformed, 4330))
	bytesEncryptedTransformed: bytes = tupleEncrypted[0]
	return bytesEncryptedTransformed


def _updatesMetricOperands(listProgram: list[object], bearingIncrement: int) -> None:
	for indexToken, token in enumerate(listProgram):
		if token == 'hsbw':
			if indexToken < 2 or not isinstance(listProgram[indexToken - 2], int) or not isinstance(listProgram[indexToken - 1], int):
				message: str = f'I could not read expected integer operands for hsbw at {indexToken = }.'
				raise TypeError(message)
			integerSideBearingBefore: int = cast(int, listProgram[indexToken - 2])
			integerAdvanceWidthBefore: int = cast(int, listProgram[indexToken - 1])
			listProgram[indexToken - 2] = integerSideBearingBefore + bearingIncrement
			listProgram[indexToken - 1] = integerAdvanceWidthBefore + bearingIncrement * 2
			return

		if token == 'sbw':
			if (
				indexToken < 4
				or not isinstance(listProgram[indexToken - 4], int)
				or not isinstance(listProgram[indexToken - 2], int)
			):
				message: str = f'I could not read expected integer operands for sbw at {indexToken = }.'
				raise TypeError(message)
			integerSideBearingBefore: int = cast(int, listProgram[indexToken - 4])
			integerAdvanceWidthBefore: int = cast(int, listProgram[indexToken - 2])
			listProgram[indexToken - 4] = integerSideBearingBefore + bearingIncrement
			listProgram[indexToken - 2] = integerAdvanceWidthBefore + bearingIncrement * 2
			return

	message: str = 'I could not find hsbw or sbw in the Type 1 charstring program.'
	raise ValueError(message)


def _rebuildsCidFontPostScriptFile(
	bytesPrefix: bytes
	, bytesSuffix: bytes
	, bytesStartDataTransformed: bytes
) -> bytes:
	integerStartDataLength: int = len(bytesStartDataTransformed)
	bytesStartDataToken: bytes = f'(Binary) {integerStartDataLength} StartData'.encode('ascii')
	bytesPrefixUpdated: bytes = regularExpressionStartData.sub(bytesStartDataToken, bytesPrefix, count=1)

	integerLineEndingLength: int = 0
	if bytesSuffix.startswith(b'\r\n'):
		integerLineEndingLength = 2
	elif bytesSuffix.startswith((b'\r', b'\n')):
		integerLineEndingLength = 1

	integerBeginDataLength: int = len(bytesStartDataToken) + 1 + integerStartDataLength + integerLineEndingLength
	bytesBeginDataToken: bytes = f'%%BeginData: {integerBeginDataLength} Binary Bytes'.encode('ascii')
	bytesPrefixUpdated = regularExpressionBeginData.sub(bytesBeginDataToken, bytesPrefixUpdated, count=1)

	return b''.join((bytesPrefixUpdated, bytesStartDataTransformed, bytesSuffix))
