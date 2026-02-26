# ruff: noqa: D103 D100 D101
from fontTools.misc.transform import Transform
from glyphsLib import load_to_ufos, to_glyphs  # pyright: ignore[reportUnknownVariableType]
from hunterMakesPy import raiseIfNone
from Integrated_Code_Fire import pathFilenameFiraCodeGlyphs, pathFilenameGlyphs, settingsPackage
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
	from fontTools.designspaceLib import DesignSpaceDocument
	from glyphsLib.classes import GSFont, GSInstance
	from pathlib import Path
	from ufoLib2 import Font

fontFamily: str = 'FrankenFont'

class GlyphsDesignspacePayload(TypedDict):
	data: list[GSInstance]
	designspace: DesignSpaceDocument

def artisanRescalesGlyphs(pathFilenameInput: Path, pathFilenameOutput: Path) -> None:
	pathFilenameOutput.parent.mkdir(parents=True, exist_ok=True)

	listUFOs: list[Font]
	dictionaryDesignspacePayload: GlyphsDesignspacePayload
	listUFOs, dictionaryDesignspacePayload = load_to_ufos(pathFilenameInput, include_instances=True)
	designspaceDocument: DesignSpaceDocument = dictionaryDesignspacePayload['designspace']
	scaleRatio: float = settingsPackage.unitsPerEm / raiseIfNone(listUFOs[0].info.unitsPerEm)
	scaleTransform: Transform = Transform().scale(scaleRatio, scaleRatio)

	for ufo in listUFOs:
		for glyph in ufo:
			for contour in glyph.contours:
				for point in contour.points:
					point.x = point.x * scaleRatio
					point.y = point.y * scaleRatio
			for component in glyph.components:
				component.transformation = scaleTransform.transform(component.transformation)
			if glyph.width:
				glyph.width = int(glyph.width * scaleRatio)
		ufo.info.unitsPerEm = settingsPackage.unitsPerEm

	font: GSFont = to_glyphs(designspaceDocument)
	font.save(pathFilenameOutput)

if __name__ == '__main__':
	artisanRescalesGlyphs(pathFilenameFiraCodeGlyphs, pathFilenameGlyphs)

