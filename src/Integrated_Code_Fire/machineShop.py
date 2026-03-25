"""Scale fonts, subset CID fonts, adjust side bearings, and merge glyph data between fonts.

(AI generated docstring)

You can use this module to perform font manipulation operations in the Integrated Code 火 assembly line. The module provides
functions to scale fonts to a target units-per-em value, subset CID fonts to specified glyph IDs and Unicode codepoints, adjust
horizontal side bearings, and merge glyph outlines and metrics from one font into another.

Contents
--------
Functions
	machinistMergesTTFFonts
		Merge glyph outlines, horizontal metrics, and Unicode mappings between fonts.
	machinistModifiesSideBearings
		Modify horizontal side bearings for all glyphs in a font.
	machinistScalesFonts
		Scale multiple font files to the target units-per-em value.
	machinistSubsetsCID
		Subset a CID font to specified glyph IDs and Unicode codepoints and adjust side bearings.

References
----------
[1] fontTools
	https://fonttools.readthedocs.io/en/latest/
[2] afdko.otf2ttf
	https://adobe-type-tools.github.io/afdko/
[3] hunterMakesPy
	https://context7.com/hunterhogan/huntermakespy

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

def machinistScalesFonts(pathFonts: Path, theGlob: str) -> dict[str, TTFont]:
	"""Scale multiple font files to the target units-per-em value.

	(AI generated docstring)

	You can load font files matching `theGlob` from `pathFonts` and scale each font to
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

def machinistSubsetsCID(pathFilename: Path, gids: list[int], unicodes: list[int], subsetOptions: subset.Options) -> TTFont:
	"""Subset a CID font to specified glyph IDs and Unicode codepoints and adjust side bearings.

	You can load a CID font file, subset the font to specified glyph IDs and Unicode codepoints using
	`fontTools.subset.Subsetter` [1], and adjust horizontal side bearings by the increment specified
	in `incrementHARDCODED`.

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
	"""
	ttFont: TTFont = TTFont(pathFilename)
	subsetter = subset.Subsetter(subsetOptions)
	subsetter.populate(gids = gids, unicodes = unicodes)
	subsetter.subset(ttFont)
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

	for glyphName, glyph in glyphSet.items():
		if glyph.width == 0:
			continue

		addend: int = modifyPerSide
		if glyph.width == widthHalfSourceHanMonoHARDCODED:
			addend //= 2

		ttFont['hmtx'][glyphName] = (glyph.width + (addend * 2), glyph.lsb + addend)

		glyph.draw(TransformPen(T2CharStringPen(glyph.width + (addend * 2), glyphSet), (1, 0, 0, 1, addend, 0))) # ty:ignore[invalid-argument-type] https://github.com/astral-sh/ty/issues/2799

def machinistMergesTTFFonts(*pathFilenamesFonts: Path) -> TTFont:
	"""FontTools can't merge CID-keyed fonts.

	afdko mergefonts requires both fonts to be CID-keyed, but Fira Code is not CID-keyed.
	"""
	return Merger().merge(pathFilenamesFonts)
