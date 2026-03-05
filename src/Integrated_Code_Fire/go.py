"""Orchestrate the Integrated Code 火 font build assembly line.

You can run the complete Integrated Code 火 build assembly line. The module compiles multiple fonts from source, scales and merges
fonts, updates OpenType metadata, packages release assets as ZIP archives, and removes temporary build artifacts.

Contents
--------
Functions
    go
        Run the complete font build assembly line.

References
----------
[1] Integrated_Code_Fire.foundry
    Internal package reference.
[2] Integrated_Code_Fire.machineShop
    Internal package reference.
[3] Integrated_Code_Fire.mergeFonts
    Internal package reference.
[4] Integrated_Code_Fire.logistics
    Internal package reference.

"""
from hunterMakesPy.semiotics import ansiColorReset, AnsiColors
from Integrated_Code_Fire import pathFilenameFiraCodeGlyphs, settingsPackage
from Integrated_Code_Fire.foundry import smithyCasts_afdko, smithyCastsFromGlyphs
from Integrated_Code_Fire.logistics import (
	packerMakesAssets, valetCopiesToWorkbench, valetRemovesFiles, valetRemovesWorkbench)
from Integrated_Code_Fire.machineShop import machinistScalesFonts
from Integrated_Code_Fire.mergeFonts import mergeFonts
from pathlib import Path
from typing import TYPE_CHECKING
import sys
import time

if TYPE_CHECKING:
	from collections.abc import Iterable, Sequence
	from fontTools.ttLib.ttFont import TTFont
	from pathlib import Path

ansiColors = AnsiColors()

def go(workersMaximum: int = 1) -> None:
	"""Run the complete Integrated Code 火 font build assembly line.

	(AI generated docstring)

	You can use this function to execute all stages of the font build process: compile Fira Code from Glyphs source using
	`smithyCastsFromGlyphs` [1], compile Source Han Mono from CIDFont source using `smithyCasts_afdko` [1], stage compiled CID
	fonts to the workbench, scale Fira Code fonts to the target units-per-em value using `machinistScalesFonts` [2], merge scaled
	Fira Code with subsetted Source Han Mono using `mergeFonts` [3], package merged fonts into locale-specific ZIP archives using
	`packerMakesAssets` [4], and remove temporary build artifacts.

	Parameters
	----------
	workersMaximum : int = 1
		Maximum number of parallel worker processes for compilation, merging, and packaging operations.

	References
	----------
	[1] Integrated_Code_Fire.foundry
		Internal package reference.
	[2] Integrated_Code_Fire.machineShop.machinistScalesFonts
		Internal package reference.
	[3] Integrated_Code_Fire.mergeFonts.mergeFonts
		Internal package reference.
	[4] Integrated_Code_Fire.logistics.packerMakesAssets
		Internal package reference.

	"""
# TODO Configuration setting.
	fontFormatFiraCode: str = 'ttf'
# TODO Configuration setting.
	fontFamilyCID: str = 'SourceHanMono'
# TODO Configuration setting.
	filenameStemZIP: str = "IntegratedCodeFire"

	sys.stdout.write(f"{ansiColors.YellowOnBlue}smithyCastsGlyphs{ansiColorReset}\n")
	pathFiraCode: Path = smithyCastsFromGlyphs(pathFilenameFiraCodeGlyphs, workersMaximum, [fontFormatFiraCode])

	listPathFilenamesCID: Sequence[Path] = smithyCasts_afdko(fontFamilyCID, workersMaximum)
	listPathFilenames: Iterable[Path] = valetCopiesToWorkbench(listPathFilenamesCID)
	valetRemovesFiles(listPathFilenamesCID, listPathFilenamesCID[0].parent)

	dictionaryFontsScaled: dict[str, TTFont] = machinistScalesFonts(pathFiraCode, f"*.{fontFormatFiraCode}")
	valetRemovesFiles(pathRemove=pathFiraCode)

	listPathFilenames = mergeFonts(fontFamilyCID, dictionaryFontsScaled, workersMaximum)

	listPathFilenames = packerMakesAssets(listPathFilenames, filenameStemZIP, workersMaximum)

	valetRemovesFiles(pathRemove=settingsPackage.pathWorkbenchFonts)
	valetRemovesWorkbench()

if __name__ == '__main__':
	timeStart: float = time.perf_counter()
	go(14)
	sys.stdout.write(f"{ansiColors.BlackOnYellow}Done in {time.perf_counter() - timeStart:.2f} seconds.{ansiColorReset}\n")
