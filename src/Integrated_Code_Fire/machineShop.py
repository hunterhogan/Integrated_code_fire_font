"""Scale fonts, subset CID fonts, adjust side bearings, and merge glyph data between fonts.

(AI generated docstring)

You can use this module to perform font manipulation operations in the Integrated Code 火 assembly line. The module provides
functions that operate on `fontTools.ttLib.TTFont` [3] instances, including CID subsetting with `fontTools.subset.Subsetter` [1]
and multi-font merging with `fontTools.merge.Merger` [2].

Contents
--------
Functions
	machinistMergesTTFFonts
		Merge multiple TrueType font files into one `TTFont` instance.
	machinistModifiesSideBearings
		Modify horizontal side bearings for all glyphs in a font.
	machinistSubsetsCID
		Subset a CID font and widen retained glyphs.

References
----------
[1] fontTools.subset.Subsetter
	https://fonttools.readthedocs.io/en/latest/subset/index.html
[2] fontTools.merge.Merger
	https://fonttools.readthedocs.io/en/latest/merge.html
[3] fontTools.ttLib.TTFont
	https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html

"""
from fontTools import subset
from fontTools.merge import Merger
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import scaleUpem, TTFont
from Integrated_Code_Fire import incrementHARDCODED, settingsPackage, widthHalfSourceHanMonoHARDCODED
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from fontTools.ttLib.ttGlyphSet import _TTGlyphSet
	from pathlib import Path

def machinistSubsetsCID(pathFilename: Path, gids: list[int], unicodes: list[int], subsetOptions: subset.Options) -> TTFont:
	"""Subset a CID font and widen retained glyphs.

	You can load a CID font file, subset the CID font to `gids` and `unicodes` with `fontTools.subset.Subsetter` [1], scale the
	CID font to `settingsPackage.unitsPerEm` when needed, and widen retained glyphs with `machinistModifiesSideBearings` [2].

	Parameters
	----------
	pathFilename : Path
		Path to CID font file to subset.
	gids : list[int]
		List of glyph IDs to retain in the subset.
	unicodes : list[int]
		List of Unicode codepoints to retain in the subset.
	subsetOptions : subset.Options
		Subsetting options passed to `fontTools.subset.Subsetter` [1].

	Returns
	-------
	ttFont : fontTools.ttLib.TTFont
		Subsetted font instance with adjusted side bearings.

	References
	----------
	[1] fontTools.subset.Subsetter
		https://fonttools.readthedocs.io/en/latest/subset/index.html
	[2] Integrated_Code_Fire.machineShop.machinistModifiesSideBearings
		Internal package reference.
	"""
	ttFont: TTFont = TTFont(pathFilename)
	subsetter = subset.Subsetter(subsetOptions)
	subsetter.populate(gids = gids, unicodes = unicodes)
	subsetter.subset(ttFont)
	if settingsPackage.unitsPerEm != 1000:
		scaleUpem.scale_upem(ttFont, settingsPackage.unitsPerEm)
	machinistModifiesSideBearings(ttFont, incrementHARDCODED)
	return ttFont

def machinistModifiesSideBearings(ttFont: TTFont, modifyPerSide: int) -> None:
	"""Modify horizontal side bearings for all glyphs in a font.

	(AI generated docstring)

	You can use this function to modify the horizontal side bearings of all glyphs in a
	`fontTools.ttLib.TTFont` instance. The function adjusts the advance width and left
	side bearing for each glyph by `modifyPerSide`, except for half-width glyphs which
	receive half the modification increment.

	Parameters
	----------
	ttFont : fontTools.ttLib.TTFont
		The font instance to modify.
	modifyPerSide : int
		The amount to add to each side bearing.

	References
	----------
	[1] fontTools.ttLib.TTFont
		https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html
	"""
	glyphSet: _TTGlyphSet = ttFont.getGlyphSet()
	# TODO This doesn't seem to modify the 'CFF ' table, so I'm not sure it really works on CID-keyed fonts.
	for glyphName, glyph in glyphSet.items():
		if glyph.width == 0:
			continue

		addend: int = modifyPerSide
		if glyph.width == widthHalfSourceHanMonoHARDCODED:
			addend //= 2

		ttFont['hmtx'][glyphName] = (glyph.width + (addend * 2), glyph.lsb + addend)

		glyph.draw(TransformPen(T2CharStringPen(glyph.width + (addend * 2), glyphSet), (1, 0, 0, 1, addend, 0))) # ty:ignore[invalid-argument-type] https://github.com/astral-sh/ty/issues/2799

def machinistMergesTTFFonts(*pathFilenamesFonts: Path) -> TTFont:
	"""Merge multiple TrueType font files into one `TTFont` instance.

	You can use this function to merge multiple TrueType font files with `fontTools.merge.Merger` [1]. The assembly line calls
	`machinistMergesTTFFonts` after CID fonts have already been converted away from CID-keyed outlines, because direct merging of
	CID-keyed fonts is not viable for the western and Han sources used here.

	Parameters
	----------
	*pathFilenamesFonts : Path
		Input font file paths passed to `fontTools.merge.Merger` [1].

	Returns
	-------
	ttFont : TTFont
		Merged font instance.

	References
	----------
	[1] fontTools.merge.Merger
		https://fonttools.readthedocs.io/en/latest/merge.html
	"""
	return Merger().merge(pathFilenamesFonts)
