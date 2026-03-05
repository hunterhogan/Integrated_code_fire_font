"""Scale fonts, subset CID fonts, adjust side bearings, and merge glyph data between fonts.

(AI generated docstring)

You can use this module to perform font manipulation operations in the Integrated Code 火 build assembly line. The module provides
functions to scale fonts to a target units-per-em value, subset CID fonts to specified glyph IDs and Unicode codepoints, adjust
horizontal side bearings, and merge glyph outlines and metrics from one font into another.

Contents
--------
Functions
	machinistScalesFonts
		Scale multiple font files to the target units-per-em value.
	machinistSubsetsCID
		Subset a CID font to specified glyph IDs and Unicode codepoints, convert to TrueType, and adjust side bearings.
	machinistModifiesSideBearings
		Modify horizontal side bearings for all glyphs in a font.
	machinistAppendsFont
		Merge glyph outlines, horizontal metrics, and Unicode mappings from one font into another.

Variables
	subsetOptions
		Global `fontTools.subset.Options` instance used for font subsetting.

References
----------
[1] fontTools
	https://fonttools.readthedocs.io/en/latest/
[2] afdko.otf2ttf
	https://adobe-type-tools.github.io/afdko/
[3] hunterMakesPy
	https://context7.com/hunterhogan/huntermakespy

"""
from afdko.otf2ttf import otf_to_ttf
from fontTools import subset
from fontTools.ttLib import scaleUpem, TTFont
from hunterMakesPy import raiseIfNone
from Integrated_Code_Fire import settingsPackage
from Integrated_Code_Fire._theSSOT import subsetOptionsHARDCODED
from Integrated_Code_Fire.archivist import hmtx
from tlz.dicttoolz import merge  # pyright: ignore[reportMissingModuleSource]
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from fontTools.ttLib.tables._g_l_y_f import Glyph
	from pathlib import Path

subsetOptions: subset.Options = subsetOptionsHARDCODED

def machinistScalesFonts(pathFonts: Path, theGlob: str) -> dict[str, TTFont]:
	"""Scale multiple font files to the target units-per-em value.

	(AI generated docstring)

	You can use this function to load font files matching `theGlob` from `pathFonts` and scale each font to
	`settingsPackage.unitsPerEm` [1]. The function returns a mapping from weight identifier to scaled `TTFont` [2] instance.
	Weight identifiers are extracted from filenames by removing the `pathFonts.name` prefix.

	Parameters
	----------
	pathFonts : Path
		Directory containing font files to scale.
	theGlob : str
		Glob pattern for selecting font files.

	Returns
	-------
	dictionaryFontsScaled : dict[str, TTFont]
		Mapping from weight identifier to scaled `TTFont` instance.

	References
	----------
	[1] Integrated_Code_Fire.settingsPackage
		Internal package reference.
	[2] fontTools.ttLib.TTFont
		https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html
	[3] fontTools.ttLib.scaleUpem.scale_upem
		https://fonttools.readthedocs.io/en/latest/ttLib/scaleUpem.html

	"""
	dictionaryFontsScaled: dict[str, TTFont] = {}
	for pathFilename in pathFonts.glob(theGlob):
		font: TTFont = TTFont(pathFilename)
		scaleUpem.scale_upem(font, settingsPackage.unitsPerEm)
		dictionaryFontsScaled[pathFilename.stem.removeprefix(f"{pathFonts.name}-")] = font
	return dictionaryFontsScaled

def machinistSubsetsCID(pathFilename: Path, gids: list[int], unicodes: list[int]) -> TTFont:
	"""Subset a CID font to specified glyph IDs and Unicode codepoints, convert to TrueType, and adjust side bearings.

	(AI generated docstring)

	You can use this function to load a CID font file, subset the font to specified glyph IDs and Unicode codepoints using
	`fontTools.subset.Subsetter` [1], convert the result to TrueType format using `afdko.otf2ttf.otf_to_ttf` [2], and adjust
	horizontal side bearings by the increment specified in `hmtx['increment']`.

	Parameters
	----------
	pathFilename : Path
		Path to CID font file to subset.
	gids : list[int]
		List of glyph IDs to retain in the subset.
	unicodes : list[int]
		List of Unicode codepoints to retain in the subset.

	Returns
	-------
	ttFont : fontTools.ttLib.TTFont
		Subsetted and converted TrueType font instance with adjusted side bearings.

	References
	----------
	[1] fontTools.subset.Subsetter
		https://fonttools.readthedocs.io/en/latest/subset/index.html
	[2] afdko.otf2ttf.otf_to_ttf
		https://adobe-type-tools.github.io/afdko/
	[3] Integrated_Code_Fire.archivist.hmtx
		Internal package reference.

	"""
	ttFont: TTFont = TTFont(pathFilename)
	subsetter = subset.Subsetter(subsetOptions)
	subsetter.populate(gids = gids, unicodes = unicodes)
	subsetter.subset(ttFont)
	otf_to_ttf(ttFont)
	machinistModifiesSideBearings(ttFont, hmtx['increment'])
	return ttFont

def machinistModifiesSideBearings(ttFont: TTFont, modifyPerSide: int) -> None:
	"""Modify horizontal side bearings for all glyphs in a font.

	(AI generated docstring)

	You can use this function to adjust the horizontal side bearings of all glyphs in a font by adding `modifyPerSide` to both the
	left and right side bearings. The function translates glyph coordinates for simple glyphs, adjusts component positions for
	composite glyphs, recalculates bounds, and updates the `hmtx` table [1].

	Parameters
	----------
	ttFont : fontTools.ttLib.TTFont
		Font instance to modify.
	modifyPerSide : int
		Value to add to each side bearing. Positive values increase spacing, negative values decrease spacing.

	References
	----------
	[1] fontTools.ttLib.TTFont
		https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html

	"""
	for glyphName in ttFont.getGlyphOrder():
		glyph: Glyph = ttFont['glyf'][glyphName]
		if glyph.isComposite():
			for component in glyph.components:
				component.x += modifyPerSide
			glyph.recalcBounds(ttFont['glyf'])
		elif glyph.numberOfContours != 0:
			glyph.coordinates.translate((modifyPerSide, 0))
			glyph.recalcBounds(ttFont['glyf'])

		ttFont['hmtx'][glyphName] = (ttFont['hmtx'][glyphName][hmtx['width']] + modifyPerSide * 2
			, ttFont['hmtx'][glyphName][hmtx['bearingLeft']] + modifyPerSide)

def machinistAppendsFont(ttFont: TTFont, fontAppend: TTFont) -> None:
	"""Merge glyph outlines, horizontal metrics, and Unicode-to-glyph mappings from one `TTFont` into another.

	(AI generated docstring)

	You can use this function to merge glyphs, metrics, and Unicode mappings from `fontAppend` into `ttFont`. The function appends
	glyphs that do not already exist in `ttFont`, copies horizontal metrics from the `hmtx` table [1], merges the `glyf` table
	[1], updates the glyph order, and merges Unicode codepoint mappings from all `cmap` subtables [1].

	Parameters
	----------
	ttFont : fontTools.ttLib.TTFont
		Destination `TTFont` instance that will receive glyphs and mappings from `fontAppend`.
	fontAppend : fontTools.ttLib.TTFont
		Source `TTFont` instance whose glyphs, metrics, and cmap entries will be copied into `ttFont`.

	Implementation Notes
	--------------------
	This function:
	- Appends glyphs from `fontAppend` that do not exist in `ttFont` to the `glyf` table and copies horizontal metrics from `hmtx`.
	- Recomputes the merged glyph order and updates `maxp.numGlyphs`.
	- Copies Unicode mappings from `fontAppend.getBestCmap()` [2] into all Unicode `cmap` subtables of `ttFont` where the codepoint is not already present.
	- Skips `cmap` format 4 tables and non-Unicode tables.

	The function uses `raiseIfNone` [3] to assert that `fontAppend.getBestCmap()` returns a mapping.

	References
	----------
	[1] fontTools.ttLib.TTFont
		https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html
	[2] fontTools.ttLib.TTFont.getBestCmap
		https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html#fontTools.ttLib.TTFont.getBestCmap
	[3] hunterMakesPy.raiseIfNone
		https://context7.com/hunterhogan/huntermakespy

	"""
	GlyphOrder: list[str] = ttFont.getGlyphOrder()
	glyphsAppend: list[str] = [glyph for glyph in fontAppend.getGlyphOrder() if glyph not in frozenset(GlyphOrder)]
	cmapAppend: dict[int, str] = raiseIfNone(fontAppend.getBestCmap())

	for glyph in glyphsAppend:
		ttFont['hmtx'][glyph] = fontAppend['hmtx'][glyph]

	ttFont['glyf'].glyphs = merge(fontAppend['glyf'].glyphs, ttFont['glyf'].glyphs)

	ttFont.setGlyphOrder(GlyphOrder + glyphsAppend)
	ttFont['maxp'].numGlyphs = len(ttFont.getGlyphOrder())

	for table in ttFont['cmap'].tables:
		if table.format == 4:
			del table
			continue
		if not table.isUnicode():
			continue
		table.cmap = merge(cmapAppend, table.cmap)
