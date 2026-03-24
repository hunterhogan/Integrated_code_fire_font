"""Scale fonts, subset CID fonts, adjust side bearings, and merge glyph data between fonts.

(AI generated docstring)

You can use this module to perform font manipulation operations in the Integrated Code 火 assembly line. The module provides
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
from fontTools.merge import Merger
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import scaleUpem, TTFont
from Integrated_Code_Fire import settingsPackage
from Integrated_Code_Fire.archivist import hmtx
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from fontTools.ttLib.tables._g_l_y_f import Glyph
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

# DEVELOPMENT
# 1. Don't convert to TTF.
# 2. Change width/lsb in CFF, not hmtx.
def machinistSubsetsCID(pathFilename: Path, gids: list[int], unicodes: list[int], subsetOptions: subset.Options) -> TTFont:
	"""Subset a CID font to specified glyph IDs and Unicode codepoints, convert to TrueType, and adjust side bearings.

	(AI generated docstring)

	You can load a CID font file, subset the font to specified glyph IDs and Unicode codepoints using
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
# TODO modify without converting to TTF.
	otf_to_ttf(ttFont)
	machinistModifiesSideBearingsTTF(ttFont, hmtx['increment'])
	# Z0Z_machinistModifiesSideBearingsCFF(ttFont, hmtx['increment'])  # noqa: ERA001
	return ttFont

def machinistModifiesSideBearingsTTF(ttFont: TTFont, modifyPerSide: int) -> None:
	"""Modify horizontal side bearings for all glyphs in a font.

	(AI generated docstring)

	You can adjust the horizontal side bearings of all glyphs in a font by adding `modifyPerSide` to both the
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
		width, bearingLeft = ttFont['hmtx'][glyphName]
		if width == 0:
			continue
		addend: int = modifyPerSide
		if width == 667:
			addend //= 2
		ttFont['hmtx'][glyphName] = (width + (addend * 2), bearingLeft + addend)

		glyph: Glyph = ttFont['glyf'][glyphName]
		if glyph.isComposite():
			for component in glyph.components:
				component.x += addend
			glyph.recalcBounds(ttFont['glyf'])
		elif glyph.numberOfContours != 0:
			glyph.coordinates.translate((addend, 0))
			glyph.recalcBounds(ttFont['glyf'])

def Z0Z_machinistModifiesSideBearingsCFF(ttFont: TTFont, modifyPerSide: int) -> None:  # noqa: D103
	glyphSet: _TTGlyphSet = ttFont.getGlyphSet()
	dictionaryCharStrings = ttFont['CFF '].cff.topDictIndex[0].CharStrings # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]

	penT2CharString = T2CharStringPen(None, glyphSet)  # ty:ignore[invalid-argument-type]
	for glyphName in glyphSet:
		addend: int = modifyPerSide
		if ttFont['hmtx'][glyphName][hmtx['width']] == 667:
			addend //= 2

		charString = dictionaryCharStrings[glyphName] # pyright: ignore[reportUnknownVariableType]
		glyphSet[glyphName].draw(TransformPen(penT2CharString, (1, 0, 0, 1, addend, 0)))

		dictionaryCharStrings[glyphName] = penT2CharString.getCharString(
			private = charString.private, # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
			globalSubrs = charString.globalSubrs, # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
		)

		ttFont['hmtx'][glyphName] = (ttFont['hmtx'][glyphName][hmtx['width']] + addend * 2
			, ttFont['hmtx'][glyphName][hmtx['bearingLeft']] + addend)

	for glyph in tuple(glyphSet.values())[0:9]: # pyright: ignore[reportUnknownArgumentType, reportIndexIssue, reportUnknownVariableType]
		print(f"{glyph.width = }\t{glyph.lsb = }") # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]  # noqa: T201

def Z0Z_machinistModifiesSideBearings(ttFont: TTFont, modifyPerSide: int) -> None:  # noqa: D103
	dirTTGGlyph=[ '_abc_impl', '_getGlyphAndOffset', '_getGlyphInstance',  # noqa: F841 # pyright: ignore[reportUnusedVariable]
		'draw', 'drawPoints',
		'glyphSet', 'name', 'recalcBounds',
		'height', 'lsb', 'tsb', 'width',
	]
	glyphSet = ttFont.getGlyphSet()
	dictionaryCharStrings = ttFont['CFF '].cff.topDictIndex[0].CharStrings # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType, reportAttributeAccessIssue]
	print(dictionaryCharStrings) # pyright: ignore[reportUnknownArgumentType]  # noqa: T201
	aPen = T2CharStringPen(None, glyphSet)  # ty:ignore[invalid-argument-type]
	for glyph in tuple(glyphSet.values())[0:9]: # pyright: ignore[reportUnknownArgumentType, reportIndexIssue, reportUnknownVariableType]
		addend: int = modifyPerSide
		if glyph.width == 667: # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
			addend //= 2
		print(f"{glyph.width = }\t{glyph.lsb = }") # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]  # noqa: T201
		glyph.width += addend * 2 # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
		glyph.lsb += addend # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
		glyph.draw(TransformPen(aPen, (1, 0, 0, 1, addend, 0)))
	for glyph in tuple(glyphSet.values())[0:9]: # pyright: ignore[reportUnknownArgumentType, reportIndexIssue, reportUnknownVariableType]
		print(f"{glyph.width = }\t{glyph.lsb = }") # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]  # noqa: T201

def machinistMergesFonts(*pathFilenamesFonts: Path) -> TTFont:  # noqa: D103
	return Merger().merge(pathFilenamesFonts)

if __name__ == "__main__":
	with TTFont('/apps/Integrated_Code_Fire/warehouse/scaled/Regular.ttf') as ttFont:
		print('vmtx' in ttFont)  # noqa: T201
	with TTFont('/apps/Integrated_Code_Fire/workbench/fonts/SourceHanMono.Simplified_Chinese.Regular.otf') as ttFont:
		Z0Z_machinistModifiesSideBearingsCFF(ttFont, 100)

