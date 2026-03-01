# ruff: noqa
from afdko.otf2ttf import otf_to_ttf
from fontTools import subset
from fontTools.ttLib import scaleUpem, TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph
from hunterMakesPy import raiseIfNone
from Integrated_Code_Fire import settingsPackage, subsetOptions
from Integrated_Code_Fire.archivist import hmtx
from pathlib import Path
from tlz.dicttoolz import merge  # pyright: ignore[reportMissingModuleSource]

def getDictionaryFontsScaled(pathFonts: Path, theGlob: str) -> dict[str, TTFont]:
	"""weight: TTFont."""
	dictionaryFontsScaled: dict[str, TTFont] = {}
	for pathFilename in pathFonts.glob(theGlob):
		font: TTFont = TTFont(pathFilename)
		scaleUpem.scale_upem(font, settingsPackage.unitsPerEm)
		dictionaryFontsScaled[pathFilename.stem.removeprefix(f"{pathFonts.name}-")] = font
	return dictionaryFontsScaled

def machinistSubsetsOTF(pathFilename: Path, gids: list[int]) -> TTFont:
	ttFont: TTFont = TTFont(pathFilename)
	subsetter = subset.Subsetter(subsetOptions)
	subsetter.populate(gids = gids)
	subsetter.subset(ttFont)
	otf_to_ttf(ttFont)
	machinistModifiesSideBearings(ttFont, hmtx['increment'])
	return ttFont

def machinistModifiesSideBearings(ttFont: TTFont, modifyPerSide: int) -> None:
	glyphOrder: list[str] = ttFont.getGlyphOrder()

	for glyphName in glyphOrder:
		glyph: Glyph = ttFont['glyf'][glyphName]
		if glyph.isComposite():
			for component in glyph.components:
				component.x += modifyPerSide
			glyph.recalcBounds(ttFont['glyf'])
		elif glyph.numberOfContours != 0:
			glyph.coordinates.translate((modifyPerSide, 0))
			glyph.recalcBounds(ttFont['glyf'])

		ttFont['hmtx'][glyphName] = (ttFont['hmtx'][glyphName][hmtx['width']] + hmtx['increment'] * 2
			, ttFont['hmtx'][glyphName][hmtx['bearingLeft']] + hmtx['increment'])

def machinistAppendsFont(ttFont: TTFont, fontAppend: TTFont) -> None:
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
	GlyphOrder: list[str] = ttFont.getGlyphOrder()
	glyphsAppend: list[str] = [glyph for glyph in fontAppend.getGlyphOrder() if glyph not in frozenset(GlyphOrder)]
	cmapHan: dict[int, str] = raiseIfNone(fontAppend.getBestCmap())

	for glyph in glyphsAppend:
		ttFont['glyf'].glyphs[glyph] = fontAppend['glyf'].glyphs[glyph]
		ttFont['hmtx'][glyph] = fontAppend['hmtx'][glyph]

	ttFont.setGlyphOrder(GlyphOrder + glyphsAppend)
	ttFont['maxp'].numGlyphs = len(ttFont.getGlyphOrder())

	for table in ttFont['cmap'].tables:
		if table.format == 4:
			continue
		if not table.isUnicode():
			continue
		table.cmap = merge(cmapHan, table.cmap)

	ttFont['OS/2'].recalcAvgCharWidth(ttFont)
	ttFont['OS/2'].recalcUnicodeRanges(ttFont)
	ttFont['OS/2'].recalcCodePageRanges(ttFont)

	ttFont.recalcBBoxes = True
	ttFont.recalcTimestamp = True
	ttFont['hhea'].recalc(ttFont)
