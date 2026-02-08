"""You can use this module to merge Latin monospace glyphs from Fira Code with scaled CJK glyphs from Source Han Mono into combined fonts.

(AI generated docstring)

This module provides utilities to adjust glyph bearings, merge glyph outlines
and horizontal metrics, and update relevant font tables so that a Latin
monospace font (Fira Code) and a scaled CJK Source Han Mono subset can be
combined into a single output font. The primary workflow is implemented by
`mergeFonts`, which iterates configured `FontPairConfiguration` entries,
applies a horizontal bearing increment to the Source Han Mono font,
merges glyphs and cmap entries into the Fira Code base font, and writes the
resulting output files.

Contents
--------
Functions
	applyBearingIncrementToFont
		Apply a horizontal bearing increment to all glyphs and metrics of a font.
	buildFontPairConfigurations
		Build the default list of font pair configurations for merging.
	mergeFonts
		Run the full merge workflow for all configured font pairs.
	mergeSourceFontIntoBaseFont
		Merge glyphs, metrics, and Unicode mappings from a source font into a
		base font.

Classes
	FontPairConfiguration
		Dataclass that describes file names and weight name for a font pair.

Variables
	bearingIncrement
		Horizontal bearing increment (in font units) applied to Source Han Mono
		glyphs.

References
----------
[1] fontTools - Read the Docs
	https://fonttools.readthedocs.io/en/latest/
[2] hunterMakesPy - Context7
	https://context7.com/hunterhogan/huntermakespy
[3] Integrated_Code_Fire.pathWorkbenchFonts
	Internal package reference.

"""

from copy import deepcopy
from dataclasses import dataclass
from fontTools.ttLib import TTFont
from hunterMakesPy import raiseIfNone
from Integrated_Code_Fire import pathWorkbenchFonts
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
	from fontTools.ttLib.tables._g_l_y_f import Glyph, table__g_l_y_f
	from fontTools.ttLib.tables._h_m_t_x import table__h_m_t_x
	from fontTools.ttLib.tables.O_S_2f_2 import table_O_S_2f_2

bearingIncrement: int = 200
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


@dataclass(frozen=True)
class FontPairConfiguration:
	"""You can use this dataclass to describe a font pair used by the merging workflow.

	(AI generated docstring)

	Attributes
	----------
	weightName : str
		The human-readable weight name for the font pair (for example
		'Bold').
	filenameFiraCode : str
		The file name of the Fira Code font used as the base font.
	filenameSourceHanMonoScaled : str
		The file name of the scaled Source Han Mono subset to merge into the
		base font.
	filenameOutput : str
		The file name to write the merged output font to.

	References
	----------
	[1] Integrated_Code_Fire.mergeFonts - internal usage
		Internal dataclass used by `mergeFonts` and related helpers.
	"""

	weightName: str
	filenameFiraCode: str
	filenameSourceHanMonoScaled: str
	filenameOutput: str

def buildFontPairConfigurations() -> list[FontPairConfiguration]:
	"""You can build the default list of FontPairConfiguration objects used by the module.

	(AI generated docstring)

	Returns
	-------
	listFontPairConfigurations : list[FontPairConfiguration]
		The list of `FontPairConfiguration` objects describing each font pair
		to process.

	References
	----------
	[1] FontPairConfiguration
		Internal dataclass defined in this module.
	"""
	listFontPairConfigurations: list[FontPairConfiguration] = [
		FontPairConfiguration(
			weightName = 'Bold'
			, filenameFiraCode = 'FiraCode-Bold.ttf'
			, filenameSourceHanMonoScaled = 'SourceHanMonoSC-Heavy.subset-scaled.ttf'
			, filenameOutput = 'IntegratedCode火简化字Bold.ttf'
		)
		, FontPairConfiguration(
			weightName = 'Light'
			, filenameFiraCode = 'FiraCode-Light.ttf'
			, filenameSourceHanMonoScaled = 'SourceHanMonoSC-Light.subset-scaled.ttf'
			, filenameOutput = 'IntegratedCode火简化字Light.ttf'
		)
		, FontPairConfiguration(
			weightName = 'Medium'
			, filenameFiraCode = 'FiraCode-Medium.ttf'
			, filenameSourceHanMonoScaled = 'SourceHanMonoSC-Medium.subset-scaled.ttf'
			, filenameOutput = 'IntegratedCode火简化字Medium.ttf'
		)
		, FontPairConfiguration(
			weightName = 'Retina'
			, filenameFiraCode = 'FiraCode-Retina.ttf'
			, filenameSourceHanMonoScaled = 'SourceHanMonoSC-Normal.subset-scaled.ttf'
			, filenameOutput = 'IntegratedCode火简化字Retina.ttf'
		)
		, FontPairConfiguration(
			weightName = 'SemiBold'
			, filenameFiraCode = 'FiraCode-SemiBold.ttf'
			, filenameSourceHanMonoScaled = 'SourceHanMonoSC-Bold.subset-scaled.ttf'
			, filenameOutput = 'IntegratedCode火简化字SemiBold.ttf'
		)
		, FontPairConfiguration(
			weightName = 'Regular'
			, filenameFiraCode = 'FiraCode-Regular.ttf'
			, filenameSourceHanMonoScaled = 'SourceHanMonoSC-Regular.subset-scaled.ttf'
			, filenameOutput = 'IntegratedCode火简化字Regular.ttf'
		)
	]
	return listFontPairConfigurations

def applyBearingIncrementToFont(fontSourceHanMono: TTFont, bearingIncrement: int) -> None:
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
	tableGlyf: table__g_l_y_f = fontSourceHanMono['glyf']
	tableHmtx: table__h_m_t_x = fontSourceHanMono['hmtx']
	glyphOrder: list[str] = fontSourceHanMono.getGlyphOrder()
	advanceWidthIncrement: int = bearingIncrement * 2

	for glyphName in glyphOrder:
		glyph: Glyph = tableGlyf[glyphName]
		if glyph.isComposite():
			for component in glyph.components:
				component.x += bearingIncrement
			glyph.recalcBounds(tableGlyf)
		elif glyph.numberOfContours != 0:
			glyph.coordinates.translate((bearingIncrement, 0))
			glyph.recalcBounds(tableGlyf)

		advanceWidth: int
		leftSideBearing: int
		advanceWidth, leftSideBearing = tableHmtx[glyphName]
		tableHmtx[glyphName] = (
			advanceWidth + advanceWidthIncrement
			, leftSideBearing + bearingIncrement
		)

def mergeSourceFontIntoBaseFont(fontBase: TTFont, fontSource: TTFont) -> None:
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
	- Copies Unicode mappings from `fontSource.getBestCmap()` into all Unicode `cmap` subtables of `fontBase` where the codepoint is not already present.
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
	listGlyphNamesToAdd: list[str] = [
		glyphName
		for glyphName in listGlyphOrderSource
		if glyphName not in setGlyphOrderBase
	]

	tableGlyfBase: table__g_l_y_f = fontBase['glyf']
	tableHmtxBase: table__h_m_t_x = fontBase['hmtx']
	tableGlyfSource: table__g_l_y_f = fontSource['glyf']
	tableHmtxSource: table__h_m_t_x = fontSource['hmtx']

	for glyphName in listGlyphNamesToAdd:
		tableGlyfBase.glyphs[glyphName] = deepcopy(tableGlyfSource.glyphs[glyphName])
		tableHmtxBase.metrics[glyphName] = tableHmtxSource.metrics[glyphName]

	listGlyphOrderMerged: list[str] = listGlyphOrderBase + listGlyphNamesToAdd
	fontBase.setGlyphOrder(listGlyphOrderMerged)
	fontBase['maxp'].numGlyphs = len(listGlyphOrderMerged)

	cmapSource: dict[int, str] = raiseIfNone(fontSource.getBestCmap())

	tableCmap: CmapSubtable
	for tableCmap in fontBase['cmap'].tables:
		if not tableCmap.isUnicode():
			continue
		unicodeCodepoint: int
		glyphName: str
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

def mergeFonts() -> None:
	"""You can run the full font pair merging workflow described by the module's `FontPairConfiguration` objects.

	(AI generated docstring)

	This function iterates the list returned by `buildFontPairConfigurations`, opens each configured Fira Code base font and scaled Source Han Mono subset, applies a horizontal bearing increment to the Source Han Mono font using `applyBearingIncrementToFont`, merges the source font into the base font with `mergeSourceFontIntoBaseFont`, and writes the resulting merged font to disk at the configured output file name (`filenameOutput`). The function uses `pathWorkbenchFonts` from the `Integrated_Code_Fire` package to construct file paths.

	Returns
	-------
	None : None
		This function performs file I/O and mutates font objects; it returns
		nothing.

	Examples
	--------
	Run the module directly (this file includes a `__main__` guard that
	calls `mergeFonts`):

	```python
	if __name__ == '__main__':
		mergeFonts()
	```

	References
	----------
	[1] fontTools - TTFont and table APIs used for reading, writing and
		recalculation.
		https://fonttools.readthedocs.io/en/latest/
	[2] Integrated_Code_Fire.pathWorkbenchFonts
		Internal package reference.
	"""
	listFontPairConfigurations: list[FontPairConfiguration] = buildFontPairConfigurations()
	fontPairConfiguration: FontPairConfiguration
	for fontPairConfiguration in listFontPairConfigurations:
		pathFilenameFiraCode = pathWorkbenchFonts / fontPairConfiguration.filenameFiraCode
		pathFilenameSourceHanMono = pathWorkbenchFonts / fontPairConfiguration.filenameSourceHanMonoScaled
		pathFilenameOutput = pathWorkbenchFonts / fontPairConfiguration.filenameOutput

		fontSourceHanMono: TTFont = TTFont(pathFilenameSourceHanMono)
		applyBearingIncrementToFont(fontSourceHanMono, bearingIncrement)

		fontBase: TTFont = TTFont(pathFilenameFiraCode)
		mergeSourceFontIntoBaseFont(fontBase, fontSourceHanMono)
		fontBase.save(pathFilenameOutput)
		fontBase.close()
		fontSourceHanMono.close()

if __name__ == '__main__':
	mergeFonts()
