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
		Center each CJK glyph in a full-width or half-width cell of an open font.
	machinistSubsetsCID
		Retain selected CJK characters and apply the configured scale and spacing.
"""
from __future__ import annotations

from fontTools import subset
from fontTools.merge import Merger
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import scaleUpem, TTFont
from humpy_cytoolz import keyfilter
from Integrated_Code_Fire import headFlagsHinting, settingsPackage
from Integrated_Code_Fire.archivist import archivistMakesUnicodesCJK
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from collections.abc import Iterable
	from fontTools.cffLib import CharStrings
	from fontTools.misc.psCharStrings import T2CharString
	from fontTools.ttLib.ttGlyphSet import _TTGlyphSet
	from pathlib import Path

def machinistSubsetsCID(pathFilename: Path, unicodesWestern: Iterable[int], subsetOptions: subset.Options) -> TTFont:
	"""Retain the CJK characters the merged font needs and prepare their em size and metrics.

	(AI generated docstring)

	Parameters
	----------
	pathFilename : Path
		CJK font with CFF outlines and the expected source dimensions.
	unicodesWestern : Iterable[int]
		Code points of the western fonts, which the CJK font must not map.
	subsetOptions : subset.Options
		FontTools options controlling retained layout features, names, and tables.

	Returns
	-------
	ttFont : TTFont
		Open subset font with the configured em size and horizontal spacing. The caller saves
		and closes the font. The source file is retained.

	See Also
	--------
	`Integrated_Code_Fire.archivist.archivistMakesUnicodesCJK`
		Select the retained code points from the font's own character map.
	`machinistModifiesSideBearings`
		Inspect the horizontal spacing adjustment applied after subsetting.

	Character Selection
	-------------------
	The excluded code points are removed from the character map before subsetting, and the subset
	requests the remaining code points. The subset therefore omits every excluded code point, even
	one whose glyph a retained code point shares, and even one that a closure of the subsetter, such
	as the bidi mirroring closure, would otherwise add.
	"""
	ttFont: TTFont = TTFont(pathFilename)
	unicodesCJK: frozenset[int] = archivistMakesUnicodesCJK(ttFont['cmap'].buildReversed(), unicodesWestern)
	# NOTE The bidi mirroring closure of `subset.Subsetter` adds the mirror of each requested code point that the font maps,
	# such as U+2245 for U+224C. A code point that the font no longer maps cannot return.
	for cmapSubtable in ttFont['cmap'].tables:
		cmapSubtable.cmap = keyfilter(unicodesCJK.__contains__, cmapSubtable.cmap)
	subsetter: subset.Subsetter = subset.Subsetter(subsetOptions)
	subsetter.populate(unicodes=unicodesCJK)
	subsetter.subset(ttFont)
	if settingsPackage.unitsPerEm != 1000:
		scaleUpem.scale_upem(ttFont, settingsPackage.unitsPerEm)
	machinistModifiesSideBearings(ttFont, settingsPackage.width)
	return ttFont

def machinistModifiesSideBearings(ttFont: TTFont, width: int) -> None:
	"""Center each CJK glyph in a full-width or half-width cell of an open CFF font.

	(AI generated docstring)

	Parameters
	----------
	ttFont : TTFont
		Open CJK font with CFF outlines whose horizontal metrics and outlines are to change.
	width : int
		Advance width of a full-width cell. A half-width cell is `width // 2`.

	Input Mutation
	--------------
	Glyphs with an advance of one em receive the full-width cell; other glyphs with an advance
	receive the half-width cell. Each outline moves horizontally by half the change in advance,
	and the left side bearing moves with it. Zero-width glyphs retain their metrics and outlines.
	The font remains open and is not saved.
	"""
	charStrings: CharStrings = ttFont['CFF '].cff.topDictIndex[0].CharStrings
	glyphSet: _TTGlyphSet = ttFont.getGlyphSet()
	unitsPerEm: int = ttFont['head'].unitsPerEm
	for glyphName, glyph in glyphSet.items():
		if glyph.width != 0:
			widthCell: int = width
			if glyph.width < unitsPerEm:
				widthCell //= 2
			addend: int = (widthCell - glyph.width) // 2

			ttFont['hmtx'][glyphName] = (widthCell, glyph.lsb + addend)

			# NOTE In a CID-keyed font, each glyph has the `private` of its own font dictionary, and the new charstring needs it.
			charString: T2CharString = charStrings[glyphName]
			# NOTE `T2CharStringPen` writes its width as is, but a charstring stores its width as the difference from `nominalWidthX`.
			pen: T2CharStringPen = T2CharStringPen(widthCell - charString.private.nominalWidthX, None)
			glyph.draw(TransformPen(pen, (1, 0, 0, 1, addend, 0)))
			charStrings[glyphName] = pen.getCharString(charString.private, charString.globalSubrs)

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

	Hinting
	-------
	The merged font keeps the TrueType instructions of the first font only. `Merger` combines bits 2
	and 3 of `head.flags` with AND and bit 4 with OR, so the merged font receives bits 2, 3, and 4
	of the first font instead.

	See Also
	--------
	`Integrated_Code_Fire.go.goMerge`
		Merge the configured western and CJK combinations and save release font files.
	"""
	ttFont: TTFont = Merger().merge(pathFilenamesFonts)
	with TTFont(pathFilenamesFonts[0], lazy=True) as ttFontFirst:
		ttFont['head'].flags = (ttFont['head'].flags & ~headFlagsHinting) | (ttFontFirst['head'].flags & headFlagsHinting)
	return ttFont
