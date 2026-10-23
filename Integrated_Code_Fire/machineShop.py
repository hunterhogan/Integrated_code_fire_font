"""Prepare CJK horizontal metrics and combine prepared TrueType fonts.

(AI generated docstring)

You can retain selected CJK characters, scale their font coordinates, and adjust horizontal
advance widths and side bearing values. Font merging combines already prepared TrueType fonts;
character selection, mapping changes, and metadata updates belong to other operations.

Contents
--------
Functions
	machinistMergesTTFFonts
		Combine prepared TrueType fonts into one open font.
	machinistModifiesSideBearings
		Change horizontal advance and side bearing values in an open font.
	machinistSubsetsCID
		Retain selected CJK characters and apply the configured scale and spacing.
"""
from __future__ import annotations

from fontTools import subset
from fontTools.merge import Merger
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import scaleUpem, TTFont
from Integrated_Code_Fire import settingsPackage
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from fontTools.ttLib.ttGlyphSet import _TTGlyphSet
	from pathlib import Path

def machinistSubsetsCID(pathFilename: Path, gids: list[int], unicodes: list[int], subsetOptions: subset.Options) -> TTFont:
	"""Retain selected CJK glyphs and prepare their em size and horizontal metrics.

	(AI generated docstring)

	Parameters
	----------
	pathFilename : Path
		CJK font with CFF outlines and the expected source dimensions.
	gids : list[int]
		Glyph identifiers to retain alongside the Unicode selections.
	unicodes : list[int]
		Unicode code points to retain alongside the glyph selections.
	subsetOptions : subset.Options
		FontTools options controlling retained layout features, names, and tables.

	Returns
	-------
	ttFont : TTFont
		Open subset font with the configured em size and horizontal spacing. The caller saves
		and closes the font. The source file is retained.

	See Also
	--------
	`machinistModifiesSideBearings`
		Inspect the horizontal spacing adjustment applied after subsetting.
	"""
	ttFont: TTFont = TTFont(pathFilename)
	subsetter = subset.Subsetter(subsetOptions)
	subsetter.populate(gids=gids, unicodes=unicodes)
	subsetter.subset(ttFont)
	if settingsPackage.unitsPerEm != 1000:
		scaleUpem.scale_upem(ttFont, settingsPackage.unitsPerEm)
	machinistModifiesSideBearings(ttFont, settingsPackage.incrementSourceHanMono)
	return ttFont

def machinistModifiesSideBearings(ttFont: TTFont, modifyPerSide: int) -> None:
	"""Change horizontal advance and side bearing values in an open CJK font.

	(AI generated docstring)

	Parameters
	----------
	ttFont : TTFont
		Open CJK font whose horizontal metrics are to change.
	modifyPerSide : int
		Font units to add to each side of a glyph. Negative values reduce spacing.

	Input Mutation
	--------------
	The horizontal advance increases by twice the per-side adjustment, and the left side bearing
	increases by the per-side adjustment. Glyphs with the configured
	`settingsPackage.widthHalfSourceHanMono` advance receive half the per-side adjustment,
	rounded down. Zero-width glyphs retain their metrics. The font remains open and is not saved.
	"""
	glyphSet: _TTGlyphSet = ttFont.getGlyphSet()
	for glyphName, glyph in glyphSet.items():
		if glyph.width != 0:
			addend: int = modifyPerSide
			if glyph.width == settingsPackage.widthHalfSourceHanMono:
				addend //= 2

			ttFont['hmtx'][glyphName] = (glyph.width + (addend * 2), glyph.lsb + addend)

			glyph.draw(TransformPen(T2CharStringPen(glyph.width + (addend * 2), glyphSet), (1, 0, 0, 1, addend, 0)))

def machinistMergesTTFFonts(*pathFilenamesFonts: Path) -> TTFont:
	"""Combine prepared TrueType font files into one open font.

	(AI generated docstring)

	Parameters
	----------
	*pathFilenamesFonts : Path
		Fonts to combine, in merge order. Supply fonts with compatible em sizes and TrueType
		outlines. Character coverage and spacing should already be prepared.

	Returns
	-------
	ttFont : TTFont
		Merged font containing glyphs and layout data from the inputs. The caller sets release
		metadata, saves the font, and closes the font. Input files are retained.

	See Also
	--------
	`Integrated_Code_Fire.go.goMerge`
		Merge the configured western and CJK combinations and save release font files.
	"""
	return Merger().merge(pathFilenamesFonts)
