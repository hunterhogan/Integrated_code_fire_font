"""You can generate CSV and JSON reports that enumerate glyph identifiers, CID keying metadata, and Unicode mappings for font files in a workspace.

This module provides small data structures and utility functions to inspect
fonts using fontTools and to emit per-font reports consumed by downstream
tools or manual review. Run the module as a script to discover fonts under
the project's default "workbench" glob patterns and write reports to
"reports/font-identifiers".

(AI generated docstring)

Public identifiers
------------------
GlyphIdentifierRecord
	Dataclass storing per-glyph identification data.
FontIdentifierReport
	Dataclass summarizing a font's identity metadata and glyph list.
buildFontIdentifierReport
	Create a FontIdentifierReport for a single font file.
writeReportsForFontPaths
	Write CSV and JSON reports for multiple font files.

References
----------
[1] fontTools TTFont: https://fonttools.readthedocs.io/.
[2] pathlib.Path: https://docs.python.org/3/library/pathlib.html.
[3] csv, json stdlib modules: https://docs.python.org/3/library/csv.html
	and https://docs.python.org/3/library/json.html.
"""

from dataclasses import asdict, dataclass
from fontTools.ttLib import TTFont
from pathlib import Path
from typing import TYPE_CHECKING
import csv
import json

if TYPE_CHECKING:
	from collections.abc import Iterable, Iterator, Sequence
	from fontTools.cffLib import TopDict

@dataclass(frozen=True, slots=True)
class GlyphIdentifierRecord:
	"""You can use GlyphIdentifierRecord to hold identification data for one glyph.

	Parameters
	----------
	glyphIndex : int
		Glyph index within the font's glyph order.
	glyphName : str
		Glyph name as returned by TTFont.getGlyphOrder().
	characterIdentifierCid : int | None
		CID assigned by CID-keyed fonts when available, else None.
	sourceHanMonoCid : int | None
		Corresponding Source Han Mono CID from project metadata when found, else None.
	listUnicodeScalarValue : list[int]
		Sorted list of Unicode scalar values mapped to this glyph.

	(AI generated docstring)

	References
	----------
	[1] fontTools TTFont and getGlyphOrder: https://fonttools.readthedocs.io/.
	"""

	glyphIndex: int
	glyphName: str
	characterIdentifierCid: int | None
	sourceHanMonoCid: int | None
	listUnicodeScalarValue: list[int]

@dataclass(frozen=True, slots=True)
class FontIdentifierReport:
	"""You can use FontIdentifierReport to summarize identification metadata for a font.

	Parameters
	----------
	pathFont : str
		Filesystem path of the font file as a string.
	fontFormat : str
		Short font format indicator (for example 'OTF' or 'TTF/TrueType').
	isCidKeyed : bool
		True when the font contains CID-keying metadata.
	cidRegistryOrderingSupplement : str | None
		ROS tuple string from a CFF/CFF2 top dict when CID-keyed, else None.
	glyphCount : int
		Number of glyphs included in the report.
	listGlyph : list[GlyphIdentifierRecord]
		List of per-glyph identification records in glyph index order.

	(AI generated docstring)

	References
	----------
	[1] fontTools TTFont: https://fonttools.readthedocs.io/.
	"""

	pathFont: str
	fontFormat: str
	isCidKeyed: bool
	cidRegistryOrderingSupplement: str | None
	glyphCount: int
	listGlyph: list[GlyphIdentifierRecord]

def _buildSourceHanMonoGlyphNameToCidLookup(pathWorkspaceRoot: Path) -> dict[str, int]:
	"""I build a glyph-name -> Source Han Mono CID mapping by reading the 'AI0-SourceHanMono' ordering file in the project's SourceHanMono/metadata directory.

	The file is expected to be UTF-8 text with tab-separated fields where the
	first column is the integer CID and the last column is the glyph name. If
	the ordering file is not present I return an empty dictionary.

	Parameters
	----------
	pathWorkspaceRoot : Path
		Root path of the repository or workspace to resolve the metadata file.

	Returns
	-------
	dict[str, int]
		Mapping from glyph name to Source Han Mono CID.

	(AI generated docstring)

	References
	----------
	[1] pathlib.Path: https://docs.python.org/3/library/pathlib.html.
	"""
	pathOrderingFile: Path = pathWorkspaceRoot / 'SourceHanMono' / 'metadata' / 'AI0-SourceHanMono'
	if not pathOrderingFile.exists():
		return {}

	dictionaryGlyphNameToCid: dict[str, int] = {}
	with pathOrderingFile.open('r', encoding='utf-8', newline='\n') as fileInput:
		for line in fileInput:
			lineStripped: str = line.strip()
			if not lineStripped:
				continue
			listField: list[str] = lineStripped.split('\t')
			if len(listField) < 2:
				continue
			cidValue: int = int(listField[0])
			glyphName: str = listField[-1]
			dictionaryGlyphNameToCid[glyphName] = cidValue

	return dictionaryGlyphNameToCid

def _iterFontPathsFromGlobPatterns(pathWorkspaceRoot: Path, listGlobPattern: Sequence[str]) -> Iterator[Path]:
	"""I iterate over filesystem paths matching glob patterns under the workspace root and yield Path objects for each match.

	Parameters
	----------
	pathWorkspaceRoot : Path
		Root directory used to resolve glob patterns.
	listGlobPattern : Sequence[str]
		Sequence of glob pattern strings passed to Path.glob().

	Yields
	------
	Path
		Path objects for matching files.

	(AI generated docstring)

	References
	----------
	[1] pathlib.Path.glob: https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob.
	"""
	for globPattern in listGlobPattern:
		yield from pathWorkspaceRoot.glob(globPattern)

def _getCidKeyingMetadata(ttFont: TTFont) -> tuple[bool, str | None, list[int] | None]:
	"""I examine a TTFont for CID-keying metadata and return a small tuple.

	If the font contains a CFF or CFF2 table and its top dict exposes an ROS
	(Registry/Ordering/Supplement) I return (True, ROS-as-string,
	charset-as-list-of-int) when possible. If no CID keying is present I return
	(False, None, None).

	Parameters
	----------
	ttFont : TTFont
		A fontTools.TTFont instance already opened for the font file.

	Returns
	-------
	tuple[bool, str | None, list[int] | None]
		Triple of (isCidKeyed, ROS string or None, list of character identifier CIDs
		or None).

	(AI generated docstring)

	References
	----------
	[1] fontTools cffLib TopDict and ROS: https://fonttools.readthedocs.io/.
	"""
	setTableTag: set[str] = set(ttFont.keys())

	if 'CFF ' in setTableTag:
		topDict: TopDict = ttFont['CFF '].cff.topDictIndex[0]
		ros: tuple[str, ...] | None = getattr(topDict, 'ROS', None)
		charsetObject: Iterable[int] | None = getattr(topDict, 'charset', None)
		if ros is None:
			return (False, None, None)

		listCharacterIdentifierCid: list[int] | None = None
		try:
			if charsetObject is not None:
				listCharacterIdentifierCid = [int(value) for value in list(charsetObject)]
		except (TypeError, ValueError):
			listCharacterIdentifierCid = None

		return (True, str(ros), listCharacterIdentifierCid)

	if 'CFF2' in setTableTag:
		topDict: TopDict = ttFont['CFF2'].cff.topDictIndex[0]
		ros: tuple[str, ...] | None = getattr(topDict, 'ROS', None)
		charsetObject: Iterable[int] | None = getattr(topDict, 'charset', None)
		if ros is None:
			return (False, None, None)

		listCharacterIdentifierCid: list[int] | None = None
		try:
			if charsetObject is not None:
				listCharacterIdentifierCid = [int(value) for value in list(charsetObject)]
		except (TypeError, ValueError):
			listCharacterIdentifierCid = None

		return (True, str(ros), listCharacterIdentifierCid)

	return (False, None, None)

def _invertsBestCmap(bestCmap: dict[int, str] | None) -> dict[str, list[int]]:
	"""I invert a best cmap mapping (unicode -> glyphName) into (glyphName -> sorted list of unicode scalars).

	Parameters
	----------
	bestCmap : dict[int, str] | None
		Mapping from Unicode scalar value to glyph name as returned by
		ttFont.getBestCmap(). If None I return an empty dictionary.

	Returns
	-------
	dict[str, list[int]]
		Mapping from glyph name to a sorted list of Unicode scalar integers.

	(AI generated docstring)

	References
	----------
	[1] fontTools TTFont.getBestCmap: https://fonttools.readthedocs.io/.
	"""
	if bestCmap is None:
		return {}

	dictionaryGlyphNameToUnicodeScalarValue: dict[str, list[int]] = {}
	for unicodeScalarValue, glyphName in bestCmap.items():
		dictionaryGlyphNameToUnicodeScalarValue.setdefault(glyphName, []).append(int(unicodeScalarValue))

	for glyphName in dictionaryGlyphNameToUnicodeScalarValue:
		dictionaryGlyphNameToUnicodeScalarValue[glyphName].sort()

	return dictionaryGlyphNameToUnicodeScalarValue

def buildFontIdentifierReport(pathFont: Path , dictionaryGlyphNameToSourceHanMonoCid: dict[str, int]) -> FontIdentifierReport:
	"""You can create a FontIdentifierReport for the font file at pathFont.

	The function opens the file with fontTools.TTFont, reads glyph order and the
	best cmap, inspects CFF/CFF2 CID keying metadata when present, and builds
	a list of GlyphIdentifierRecord values. The returned FontIdentifierReport
	contains per-font metadata and the per-glyph list.

	Parameters
	----------
	pathFont : Path
		Filesystem path to a font file (for example .ttf, .otf, .woff, .woff2).
	dictionaryGlyphNameToSourceHanMonoCid : dict[str, int]
		Optional mapping used to annotate glyphs with a Source Han Mono CID.

	Returns
	-------
	FontIdentifierReport
		Report object containing font metadata and the list of glyph records.

	(AI generated docstring)

	References
	----------
	[1] fontTools TTFont: https://fonttools.readthedocs.io/.
	"""
	with TTFont(str(pathFont)) as ttFont:
		listGlyphName: list[str] = list(ttFont.getGlyphOrder())
		dictionaryGlyphNameToUnicodeScalarValue: dict[str, list[int]] = _invertsBestCmap(ttFont.getBestCmap())

		isCidKeyed: bool
		cidRegistryOrderingSupplement: str | None
		listCharacterIdentifierCidFromCharset: list[int] | None
		isCidKeyed, cidRegistryOrderingSupplement, listCharacterIdentifierCidFromCharset = _getCidKeyingMetadata(ttFont)

		listCharacterIdentifierCidByGlyphIndex: list[int | None] = [None for _ in listGlyphName]

		if isCidKeyed:
			listCharacterIdentifierCidFromGlyphName: list[int | None] = []
			for glyphName in listGlyphName:
				if glyphName.startswith('cid') and glyphName[3:].isdigit():
					listCharacterIdentifierCidFromGlyphName.append(int(glyphName[3:]))
				else:
					listCharacterIdentifierCidFromGlyphName.append(None)

			if any(value is not None for value in listCharacterIdentifierCidFromGlyphName):
				listCharacterIdentifierCidByGlyphIndex = listCharacterIdentifierCidFromGlyphName
			elif listCharacterIdentifierCidFromCharset is not None:
				if len(listCharacterIdentifierCidFromCharset) == len(listGlyphName):
					listCharacterIdentifierCidByGlyphIndex = [int(value) for value in listCharacterIdentifierCidFromCharset]
				elif len(listCharacterIdentifierCidFromCharset) == (len(listGlyphName) - 1):
					listCharacterIdentifierCidByGlyphIndex = [None] + [int(value) for value in listCharacterIdentifierCidFromCharset]

		listGlyph: list[GlyphIdentifierRecord] = []
		for glyphIndex, glyphName in enumerate(listGlyphName):
			listGlyph.append(
				GlyphIdentifierRecord(
					glyphIndex = int(glyphIndex)
					, glyphName = glyphName
					, characterIdentifierCid = listCharacterIdentifierCidByGlyphIndex[glyphIndex]
					, sourceHanMonoCid = dictionaryGlyphNameToSourceHanMonoCid.get(glyphName)
					, listUnicodeScalarValue = list(dictionaryGlyphNameToUnicodeScalarValue.get(glyphName, []))
				)
			)

		fontFormat: str = 'OTF' if ttFont.sfntVersion == 'OTTO' else 'TTF/TrueType'
		return FontIdentifierReport(
			pathFont = str(pathFont)
			, fontFormat = fontFormat
			, isCidKeyed = bool(isCidKeyed)
			, cidRegistryOrderingSupplement = cidRegistryOrderingSupplement
			, glyphCount = len(listGlyphName)
			, listGlyph = listGlyph
		)

def _writesCsvReport(pathOutputCsv: Path, report: FontIdentifierReport) -> None:
	"""I write a FontIdentifierReport to a CSV file with a single header row.

	The CSV contains one row per glyph and a final set of columns describing
	the font path and basic metadata. Unicode scalar values are rendered as
	four-digit uppercase hex values separated by spaces.

	Parameters
	----------
	pathOutputCsv : Path
		Destination CSV file path; parent directories are created if necessary.
	report : FontIdentifierReport
		Report object to serialize.

	Returns
	-------
	None

	(AI generated docstring)

	References
	----------
	[1] csv module: https://docs.python.org/3/library/csv.html.
	"""
	pathOutputCsv.parent.mkdir(parents=True, exist_ok=True)

	with pathOutputCsv.open('w', encoding='utf-8', newline='') as fileOutput:
		csvWriter = csv.writer(fileOutput)
		csvWriter.writerow([
			'fontPath'
			, 'fontFormat'
			, 'isCidKeyed'
			, 'cidRegistryOrderingSupplement'
			, 'glyphIndex'
			, 'glyphName'
			, 'characterIdentifierCid'
			, 'sourceHanMonoCid'
			, 'unicodeScalarValuesHex'
		])
		for glyphRecord in report.listGlyph:
			unicodeScalarValuesHex: str = ' '.join(f"{value:04X}" for value in glyphRecord.listUnicodeScalarValue)
			csvWriter.writerow([
				report.pathFont
				, report.fontFormat
				, int(report.isCidKeyed)
				, report.cidRegistryOrderingSupplement
				, glyphRecord.glyphIndex
				, glyphRecord.glyphName
				, glyphRecord.characterIdentifierCid
				, glyphRecord.sourceHanMonoCid
				, unicodeScalarValuesHex
			])

def _writesJsonReport(pathOutputJson: Path, report: FontIdentifierReport) -> None:
	"""I write a FontIdentifierReport to a JSON file using a stable, readable format.

	The function converts the dataclass to native Python containers with
	asdict() and serializes with json.dump(..., ensure_ascii=False, indent=2).

	Parameters
	----------
	pathOutputJson : Path
		Destination JSON file path; parent directories are created if necessary.
	report : FontIdentifierReport
		Report object to serialize.

	Returns
	-------
	None

	(AI generated docstring)

	References
	----------
	[1] json module: https://docs.python.org/3/library/json.html.
	"""
	pathOutputJson.parent.mkdir(parents=True, exist_ok=True)

	dictionaryReport = asdict(report)
	with pathOutputJson.open('w', encoding='utf-8', newline='\n') as fileOutput:
		json.dump(dictionaryReport, fileOutput, ensure_ascii=False, indent=2)
		fileOutput.write('\n')

def _defaultGlobPatterns() -> list[str]:
	"""I return the project's default glob patterns for font discovery.

	Returns
	-------
	list[str]
		List of glob pattern strings used to discover fonts under the workspace.

	(AI generated docstring)

	References
	----------
	[1] Glob patterns understood by pathlib.Path.glob: https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob.
	"""
	return [
		r'workbench/**/*.ttf'
		, r'workbench/**/*.otf'
		, r'workbench/**/*.woff'
		, r'workbench/**/*.woff2'
	]

def writeReportsForFontPaths(listFontPath: Sequence[Path] , pathOutputDirectory: Path , dictionaryGlyphNameToSourceHanMonoCid: dict[str, int]) -> None:
	"""You can write CSV and JSON reports for each font in listFontPath.

	The function calls buildFontIdentifierReport for each entry and emits two
	files per font into pathOutputDirectory: a CSV and a JSON file suffixed
	with ".glyphIdentifiers.csv" and ".glyphIdentifiers.json" respectively.

	Parameters
	----------
	listFontPath : Sequence[Path]
		Sequence of font file paths to process.
	pathOutputDirectory : Path
		Directory where per-font report files will be written.
	dictionaryGlyphNameToSourceHanMonoCid : dict[str, int]
		Mapping used to annotate glyphs with Source Han Mono CIDs.

	Returns
	-------
	None

	(AI generated docstring)

	References
	----------
	[1] buildFontIdentifierReport in this module.
	"""
	for pathFont in listFontPath:
		report: FontIdentifierReport = buildFontIdentifierReport(pathFont, dictionaryGlyphNameToSourceHanMonoCid)
		pathOutputCsv: Path = pathOutputDirectory / f"{pathFont.name}.glyphIdentifiers.csv"
		pathOutputJson: Path = pathOutputDirectory / f"{pathFont.name}.glyphIdentifiers.json"
		_writesCsvReport(pathOutputCsv, report)
		_writesJsonReport(pathOutputJson, report)

if __name__ == '__main__':
	pathWorkspaceRoot: Path = Path.cwd()
	pathOutputDirectory: Path = pathWorkspaceRoot / 'reports' / 'font-identifiers'
	listGlobPattern: list[str] = _defaultGlobPatterns()
	listFontPath: list[Path] = sorted(set(_iterFontPathsFromGlobPatterns(pathWorkspaceRoot, listGlobPattern)))

	if not listFontPath:
		message: str = f"No fonts found in {pathWorkspaceRoot}"
		raise FileNotFoundError(message)

	dictionaryGlyphNameToSourceHanMonoCid: dict[str, int] = _buildSourceHanMonoGlyphNameToCidLookup(pathWorkspaceRoot)
	writeReportsForFontPaths(listFontPath, pathOutputDirectory, dictionaryGlyphNameToSourceHanMonoCid)
