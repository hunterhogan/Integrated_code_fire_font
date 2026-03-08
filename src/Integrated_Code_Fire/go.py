"""Orchestrate the Integrated Code 火 font assembly line.

You can run the complete Integrated Code 火 assembly line. The module compiles multiple fonts from source, scales and merges
fonts, updates OpenType metadata, packages release assets as ZIP archives, and removes temporary assembly line artifacts.

Contents
--------
Functions
	go
		Run the complete font assembly line.

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
from concurrent.futures import as_completed, Future, ProcessPoolExecutor
from copy import copy
from fontTools.ttLib import TTFont
from hunterMakesPy.parseParameters import defineConcurrencyLimit
from hunterMakesPy.semiotics import ansiColorReset, AnsiColors
from Integrated_Code_Fire import LocaleIn, settingsPackage, WeightIn
from Integrated_Code_Fire.archivist import (
	archivistGetsLocales, archivistGetsWeights, archivistMakesFilenameStem, archivistMakesNameIDMetadata,
	archivistUpdatesMetadata)
from Integrated_Code_Fire.logistics import (
	packerMakesAssets, valetGetsScaledFont, valetRemovesFiles, valetRemovesWorkbench)
from Integrated_Code_Fire.machineShop import machinistAppendsFont
from itertools import product as CartesianProduct
from pathlib import Path
from tqdm import tqdm
from typing import TYPE_CHECKING
import sys
import time

if TYPE_CHECKING:
	from collections.abc import Iterable
	from pathlib import Path

ansiColors = AnsiColors()

def go(fontFormat: str = 'ttf', *, CPUlimit: bool | float | int | None = 1) -> None:
	"""Run the complete Integrated Code 火 font assembly line.

	(AI generated docstring)

	You can execute all stages of the font assembly line process: compile Fira Code from Glyphs source using
	`smithyCastsFromGlyphs` [1], compile Source Han Mono from CIDFont source using `smithyCasts_afdko` [1], stage compiled CID
	fonts to the workbench, scale Fira Code fonts to the target units-per-em value using `machinistScalesFonts` [2], merge scaled
	Fira Code with subsetted Source Han Mono using `mergeFonts` [3], package merged fonts into locale-specific ZIP archives using
	`packerMakesAssets` [4], and remove temporary assembly line artifacts.

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
	workersMaximum: int = defineConcurrencyLimit(limit=CPUlimit)

	dictionaryLocales: dict[str, LocaleIn] = archivistGetsLocales()
	dictionaryWeights: dict[str, WeightIn] = archivistGetsWeights()

	dictionaryFontsScaled: dict[str, TTFont] = valetGetsScaledFont(fontFormat)

	pathCID: Path = settingsPackage.pathWarehouse / 'CID'

	listPathFilenames: Iterable[Path] = []
	listClaimTickets: list[Future[Path]] = []

	with ProcessPoolExecutor(workersMaximum) as concurrencyManager:

		for locale, style, weight in CartesianProduct(settingsPackage.theLocales, settingsPackage.theStyles, settingsPackage.theWeights):
			localeIn: LocaleIn = dictionaryLocales[locale]
			weightIn: WeightIn = dictionaryWeights[weight]

			fontFamily: str = archivistMakesFilenameStem(settingsPackage.fontFamily, localeIn.IntegratedCode火, separator=' ')

			listClaimTickets.append(concurrencyManager.submit(
				_mergeFont
				, copy(dictionaryFontsScaled[weightIn.fontFamilyScaled])
				, pathCID / f"{archivistMakesFilenameStem(None, localeIn.ascii, style, weightIn.fontFamilyCID)}.{fontFormat}"
				, archivistMakesNameIDMetadata(weightIn.IntegratedCode火, fontFamily.replace(' ', ''), fontFamily)
				, settingsPackage.pathWorkbenchFonts / f"{archivistMakesFilenameStem(settingsPackage.fontFamily.replace(' ', ''), localeIn.IntegratedCode火, style, weightIn.IntegratedCode火, '')}.{fontFormat}"
			))

		for claimTicket in tqdm(as_completed(listClaimTickets), total=len(listClaimTickets), desc = "Merging fonts"):
			listPathFilenames.append(claimTicket.result())

	listPathFilenames = packerMakesAssets(listPathFilenames, workersMaximum)

	valetRemovesFiles(pathRemove=settingsPackage.pathWorkbenchFonts)
	valetRemovesWorkbench()

def _mergeFont(ttFont: TTFont, pathFilenameHan: Path, nameIDmetadata: dict[int, str], pathFilenameWrite: Path) -> Path:
	fontHan = TTFont(pathFilenameHan)
	machinistAppendsFont(ttFont, fontHan)
	fontHan.close()

	archivistUpdatesMetadata(ttFont, nameIDmetadata)

# TODO I'm still deeply skeptical that ALL of the following are true:
	# `fontTools.subset.Subsetter` didn't already do this.
	# `afdko.otf2ttf.otf_to_ttf` didn't already do this.
	# `ttFont.save` doesn't automatically do this.
	# There isn't a better method or function.
	# The parameters are correct.
	# These are the ONLY computations I must/should manually trigger in ALL tables and TTFont properties.
	ttFont['OS/2'].recalcAvgCharWidth(ttFont)
	ttFont['OS/2'].recalcUnicodeRanges(ttFont)
	ttFont['OS/2'].recalcCodePageRanges(ttFont)

	pathFilenameWrite.parent.mkdir(parents=True, exist_ok=True)
	ttFont.save(pathFilenameWrite)
	ttFont.close()

	return pathFilenameWrite

if __name__ == '__main__':
	timeStart: float = time.perf_counter()
	go(CPUlimit=-1)
	sys.stdout.write(f"{ansiColors.BlackOnYellow}Done in {time.perf_counter() - timeStart:.2f} seconds.{ansiColorReset}\n")
