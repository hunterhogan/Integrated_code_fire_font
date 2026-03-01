# ruff: noqa: D103
"""You can use this module to run the Integrated_Code_Fire build assembly line.

(AI generated docstring)

This module orchestrates staging input fonts, merging fonts, cleaning temporary
font input files, writing OpenType name metadata, creating release assets, and
removing the workbench directory.

Contents
--------
Functions
	cleanWorkbench
		Remove source font input files from `pathWorkbenchFonts`.
	go
		Run the end-to-end font build assembly line.
	removeWorkbench
		Remove `pathWorkbenchFonts` and `pathWorkbench` after a successful run.

References
----------
[1] Integrated_Code_Fire.getFontInput.getFiraCode
	Internal package reference.
[2] Integrated_Code_Fire.getFontInput.getSourceHanMonoSC
	Internal package reference.
[3] Integrated_Code_Fire.mergeFonts.mergeFonts
	Internal package reference.
[4] Integrated_Code_Fire.writeMetadata.writeMetadata
	Internal package reference.
[5] Integrated_Code_Fire.makeAssets.makeAssets
	Internal package reference.

"""
from hunterMakesPy.semiotics import ansiColorReset, AnsiColors
from Integrated_Code_Fire import pathFilenameFiraCodeGlyphs, settingsPackage
from Integrated_Code_Fire.foundry import smithyCasts_afdko, smithyCastsFromGlyphs
from Integrated_Code_Fire.logistics import valetCopiesToWorkbench, valetRemovesFiles, valetRemovesWorkbench
from Integrated_Code_Fire.machineShop import getDictionaryFontsScaled
from Integrated_Code_Fire.mergeFonts import mergeFonts
from Integrated_Code_Fire.shipping import makeAssets
from pathlib import Path
from typing import TYPE_CHECKING
import sys

if TYPE_CHECKING:
	from fontTools.ttLib.ttFont import TTFont
	from pathlib import Path

ansiColors = AnsiColors()

def go(workersMaximum: int = 1) -> None:
	sys.stdout.write(f"{ansiColors.YellowOnBlue}smithyCastsGlyphs{ansiColorReset}\n")
	fontFormatFiraCode: str = 'ttf'
	pathFiraCode: Path = smithyCastsFromGlyphs(pathFilenameFiraCodeGlyphs, workersMaximum, [fontFormatFiraCode])

	fontFamily: str = 'SourceHanMono'
	listPathFilenames: list[Path] = smithyCasts_afdko(fontFamily, workersMaximum)
	pathWorkbenchFontFamily: Path = listPathFilenames[0].parent
	listPathFilenames = valetCopiesToWorkbench(pathWorkbenchFontFamily, "*.otf")
	valetRemovesFiles(pathWorkbenchFontFamily)

	dictionaryFontsScaled: dict[str, TTFont] = getDictionaryFontsScaled(pathFiraCode, f"*.{fontFormatFiraCode}")
	valetRemovesFiles(pathFiraCode)

	listPathFilenames = mergeFonts(fontFamily, dictionaryFontsScaled, workersMaximum)

	filenameZIP: str = "IntegratedCode.zip"
	makeAssets(listPathFilenames, filenameZIP)

	valetRemovesFiles(settingsPackage.pathWorkbenchFonts)
	valetRemovesWorkbench()

if __name__ == '__main__':
	go(14)
