"""You can use this module to merge Latin monospace glyphs from Fira Code with scaled CJK glyphs from Source Han Mono into combined fonts.

(AI generated docstring)

This module converts Source Han Mono OpenType fonts to TrueType outlines,
subsets them to the configured Unicode ranges, scales units-per-em, applies a
horizontal bearing increment, and merges the result into the Fira Code base
font. The primary workflow is implemented by `mergeFonts`, which iterates
`dictionaryWeights` to resolve weight names and writes the merged output
files.

Contents
--------
Functions
	applyBearingIncrementToFont
		Apply a horizontal bearing increment to all glyphs and metrics of a font.
	mergeFonts
		Run the full merge workflow for all configured font pairs.
	mergeSourceFontIntoBaseFont
		Merge glyphs, metrics, and Unicode mappings from a source font into a
		base font.

Variables
	bearingIncrement
		Horizontal bearing increment (in font units) applied to Source Han Mono
		glyphs.

References
----------
[1] fontTools - Read the Docs
	https://fonttools.readthedocs.io/en/latest/
[2] Integrated_Code_Fire.pathWorkbenchFonts
	Internal package reference.

"""
# ruff: noqa: D103
from concurrent.futures import as_completed, Future, ProcessPoolExecutor
from copy import deepcopy
from fontTools import subset
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import newTable, scaleUpem, TTFont
from hunterMakesPy import raiseIfNone
from Integrated_Code_Fire import (
	dictionaryWeights, hmtx, maximumErrorUnitsPerEm, postTableFormat, reverseContourDirection, settingsPackage,
	subsetOptions, unicodeSC, WeightIn)
from tqdm import tqdm
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from fontTools.ttLib.tables._g_l_y_f import Glyph, table__g_l_y_f
	from fontTools.ttLib.tables.O_S_2f_2 import table_O_S_2f_2
	from fontTools.ttLib.ttGlyphSet import _TTGlyph, _TTGlyphSet
	from pathlib import Path

def _glyphSetConvertsCubicToQuadratic(glyphSet: _TTGlyphSet, maximumErrorUnitsPerEm: float, *, reverseContourDirection: bool) -> dict[str, Glyph]:
	dictionaryGlyphNameToGlyph: dict[str, Glyph] = {}
	for glyphName in iter(glyphSet):
		glyphObject: _TTGlyph = glyphSet[glyphName]
		penTrueTypeGlyph = TTGlyphPen(glyphSet)  # ty:ignore[invalid-argument-type]
		penCubicToQuadratic = Cu2QuPen(penTrueTypeGlyph, maximumErrorUnitsPerEm, reverse_direction = reverseContourDirection)
		glyphObject.draw(penCubicToQuadratic) # pyright: ignore[reportArgumentType]
		dictionaryGlyphNameToGlyph[glyphName] = penTrueTypeGlyph.glyph()
	return dictionaryGlyphNameToGlyph

def _updatesHorizontalMetrics(ttFont: TTFont, tableGlyf: table__g_l_y_f) -> None:
	for glyphName, glyphObject in tableGlyf.glyphs.items():
		if hasattr(glyphObject, 'xMin'):
			ttFont['hmtx'][glyphName] = (ttFont['hmtx'][glyphName][hmtx['width']], glyphObject.xMin)

def reinvent_otf2ttf(ttFont: TTFont) -> None:
	glyphOrder: list[str] = ttFont.getGlyphOrder()

	ttFont['loca'] = newTable('loca')
	ttFont['glyf'] = newTable('glyf')
	ttFont['glyf'].glyphOrder = glyphOrder
	ttFont['glyf'].glyphs = _glyphSetConvertsCubicToQuadratic(ttFont.getGlyphSet(), maximumErrorUnitsPerEm, reverseContourDirection = reverseContourDirection)
	del ttFont['CFF ']
	if 'VORG' in ttFont:
		del ttFont['VORG']
	ttFont['glyf'].compile(ttFont)
	_updatesHorizontalMetrics(ttFont, ttFont['glyf'])

	ttFont['maxp'] = newTable('maxp')
	ttFont['maxp'].tableVersion = 0x00010000
	ttFont['maxp'].maxZones = 1  # ty:ignore[unresolved-attribute]
	ttFont['maxp'].maxTwilightPoints = 0  # ty:ignore[unresolved-attribute]
	ttFont['maxp'].maxStorage = 0  # ty:ignore[unresolved-attribute]
	ttFont['maxp'].maxFunctionDefs = 0  # ty:ignore[unresolved-attribute]
	ttFont['maxp'].maxInstructionDefs = 0  # ty:ignore[unresolved-attribute]
	ttFont['maxp'].maxStackElements = 0  # ty:ignore[unresolved-attribute]
	ttFont['maxp'].maxSizeOfInstructions = 0  # ty:ignore[unresolved-attribute]
	ttFont['maxp'].maxComponentElements = max((len(glyf.components)
			for glyf in filter(lambda glyf: hasattr(glyf, 'components'), ttFont['glyf'].glyphs.values())), default = 0)
	ttFont['maxp'].compile(ttFont)

	ttFont['post'].formatType = postTableFormat  # ty:ignore[unresolved-attribute]
	ttFont['post'].extraNames = list[str]()
	ttFont['post'].mapping = dict[str, int]()
	ttFont['post'].glyphOrder = glyphOrder
	try:
		ttFont['post'].compile(ttFont)
	except OverflowError:
		ttFont['post'].formatType = 3  # ty:ignore[unresolved-attribute]
		ttFont['post'].compile(ttFont)

	ttFont.sfntVersion = "\000\001\000\000"

def _subsetUnicodes(ttFont: TTFont, unicodes: list[int], options: subset.Options) -> None:
	subsetter = subset.Subsetter(options)
	subsetter.populate(unicodes = unicodes)
	subsetter.subset(ttFont)

def _reconstructOTF(pathFilename: Path, listUnicode: list[int]) -> TTFont:
	ttFont: TTFont = TTFont(pathFilename)
	reinvent_otf2ttf(ttFont)
	_subsetUnicodes(ttFont, listUnicode, deepcopy(subsetOptions))
	incrementBearing(ttFont, hmtx['increment'])
	return ttFont

def incrementBearing(ttFont: TTFont, bearingIncrement: int) -> None:
	"""You can apply a horizontal bearing increment to every glyph outline and metric in a `TTFont` object.

	(AI generated docstring)

	Parameters
	----------
	fontSourceHanMono : fontTools.ttLib.TTFont
		The Source Han Mono `TTFont` object that will be mutated by this
		operation.
	bearingIncrement : int
		The horizontal increment, in font units, to apply to glyph
		coordinates and left side bearings.

	Returns
	-------
	None : None
		This function mutates `fontSourceHanMono` in-place and returns
		nothing.

	Implementation Notes
	--------------------
	This function adjusts composite glyph component offsets and translates
	simple glyph coordinates by `bearingIncrement`. The function also
	increases each glyph's advance width by `bearingIncrement * 2` and
	increases left side bearings by `bearingIncrement`. After geometry
	updates, glyph bounds are recomputed using `glyph.recalcBounds` and
	metrics are updated in the `hmtx` table.

	References
	----------
	[1] fontTools - TTFont, glyph and hmtx table behavior
		https://fonttools.readthedocs.io/en/latest/
	"""
	glyphOrder: list[str] = ttFont.getGlyphOrder()

	for glyphName in glyphOrder:
		glyph: Glyph = ttFont['glyf'][glyphName]
		if glyph.isComposite():
			for component in glyph.components:
				component.x += bearingIncrement
			glyph.recalcBounds(ttFont['glyf'])
		elif glyph.numberOfContours != 0:
			glyph.coordinates.translate((bearingIncrement, 0))
			glyph.recalcBounds(ttFont['glyf'])

		ttFont['hmtx'][glyphName] = (ttFont['hmtx'][glyphName][hmtx['width']] + hmtx['increment'] * 2
			, ttFont['hmtx'][glyphName][hmtx['bearingLeft']] + hmtx['increment'])

def reinventMerging(fontBase: TTFont, fontSource: TTFont) -> None:
	"""You can merge glyph outlines, horizontal metrics, and Unicode-to-glyph mappings from one `TTFont` into another.

	(AI generated docstring)

	Parameters
	----------
	fontBase : fontTools.ttLib.TTFont
		The destination `TTFont` object that will be extended with glyphs and
		mappings from `fontSource`.
	fontSource : fontTools.ttLib.TTFont
		The source `TTFont` object whose glyphs, metrics, and cmap entries
		will be copied into `fontBase`.

	Returns
	-------
	None : None
		This function mutates `fontBase` in-place and returns nothing.

	Implementation Notes
	--------------------
	This function:
	- Appends glyphs from `fontSource` that do not exist in `fontBase` to the `glyf` table and copies horizontal metrics from `hmtx`.
	- Recomputes the merged glyph order and updates `maxp.numGlyphs`.
	- Copies Unicode mappings from `fontSource.getBestCmap()` into all Unicode `cmap` sub-tables of `fontBase` where the codepoint is not already present.
	- Recalculates `OS/2` fields (avgCharWidth, unicodeRanges, codePageRanges) and recalculates `hhea` and bounding boxes by setting recalc flags.

	The function uses `raiseIfNone` to assert that `fontSource.getBestCmap()` returns a mapping.

	References
	----------
	[1] fontTools - TTFont and font table manipulation
		https://fonttools.readthedocs.io/en/latest/
	[2] hunterMakesPy.raiseIfNone
		https://context7.com/hunterhogan/huntermakespy
	[3] Integrated_Code_Fire.pathWorkbenchFonts
		Internal package reference.
	"""
	listGlyphOrderBase: list[str] = list(fontBase.getGlyphOrder())
	setGlyphOrderBase: set[str] = set(listGlyphOrderBase)
	listGlyphOrderSource: list[str] = list(fontSource.getGlyphOrder())
	listGlyphNamesToAdd: list[str] = [ glyphName for glyphName in listGlyphOrderSource if glyphName not in setGlyphOrderBase ]
	cmapSource: dict[int, str] = raiseIfNone(fontSource.getBestCmap())

	for glyphName in listGlyphNamesToAdd:
		fontBase['glyf'].glyphs[glyphName] = deepcopy(fontSource['glyf'].glyphs[glyphName])
		fontBase['hmtx'][glyphName] = fontSource['hmtx'][glyphName]

	fontBase.setGlyphOrder(listGlyphOrderBase + listGlyphNamesToAdd)
	fontBase['maxp'].numGlyphs = len(listGlyphOrderBase) + len(listGlyphNamesToAdd)

	for tableCmap in fontBase['cmap'].tables:
		if not tableCmap.isUnicode():
			continue
		for unicodeCodepoint, glyphName in cmapSource.items():
			if unicodeCodepoint not in tableCmap.cmap:
				tableCmap.cmap[unicodeCodepoint] = glyphName

	tableOs2: table_O_S_2f_2 = fontBase['OS/2']
	tableOs2.recalcAvgCharWidth(fontBase)
	tableOs2.recalcUnicodeRanges(fontBase)
	tableOs2.recalcCodePageRanges(fontBase)

	fontBase['hhea'].recalc(fontBase)
	fontBase.recalcBBoxes = True
	fontBase.recalcTimestamp = True

def _buildsPreparedFontV2(pathFilename: Path, listUnicode: list[int]) -> TTFont:
	ttFont: TTFont = TTFont(pathFilename)
	reinvent_otf2ttf(ttFont)
	_subsetUnicodes(ttFont, listUnicode, deepcopy(subsetOptions))
	return ttFont

def mergeFontsV2(fontFamily: str) -> list[Path]:
	listPathFilename: list[Path] = []
	listUnicodeCodepoint: list[int] = subset.parse_unicodes(','.join(unicodeSC))

	for weightName, weightValues in dictionaryWeights.items():
		fontSource: TTFont = _buildsPreparedFontV2(
			settingsPackage.pathWorkbenchFonts / f"Simplified_Chinese.{weightValues.SourceHanMono}.{fontFamily}.otf",
			listUnicodeCodepoint
		)
		fontBase: TTFont = TTFont(settingsPackage.pathWorkbenchFonts / f"FiraCode-{weightValues.FiraCode}.ttf")
		reinventMerging(fontBase, fontSource)
		pathOutput: Path = settingsPackage.pathWorkbenchFonts / f"{settingsPackage.filenameFontFamilyLocale简化字}{weightName}.ttf"
		fontBase.save(pathOutput)
		fontBase.close()
		fontSource.close()
		listPathFilename.append(pathOutput)

	return listPathFilename

def mergeFonts(fontFamily: str, workersMaximum: int = 1) -> list[Path]:
	listPathFilename: list[Path] = []
	listClaimTickets: list[Future[Path]] = []
	listUnicode: list[int] = subset.parse_unicodes(','.join(unicodeSC))

	with ProcessPoolExecutor(workersMaximum) as concurrencyManager:
		for weightName, weightValues in dictionaryWeights.items():
			listClaimTickets.append(concurrencyManager.submit(_mf, fontFamily, listUnicode, weightName, weightValues))

		for claimTicket in tqdm(as_completed(listClaimTickets), total=len(listClaimTickets), desc = "Merging fonts"):
			listPathFilename.append(claimTicket.result())  # noqa: PERF401

	return listPathFilename

def _mf(fontFamily: str, listUnicode: list[int], weightName: str, weightValues: WeightIn) -> Path:
	fontSourceHanMono: TTFont = _reconstructOTF(settingsPackage.pathWorkbenchFonts / f"Simplified_Chinese.{weightValues.SourceHanMono}.{fontFamily}.otf", listUnicode)
	fontBase: TTFont = TTFont(settingsPackage.pathWorkbenchFonts / f"FiraCode-{weightValues.FiraCode}.ttf")
	scaleUpem.scale_upem(fontBase, settingsPackage.unitsPerEm)
	reinventMerging(fontBase, fontSourceHanMono)
	pathFilename: Path = settingsPackage.pathWorkbenchFonts / f"{settingsPackage.filenameFontFamilyLocale简化字}{weightName}.ttf"
	fontBase.save(pathFilename)
	fontBase.close()
	fontSourceHanMono.close()
	return pathFilename
