"""Merge prepared western and CJK fonts and package locale-specific release archives.

(AI generated docstring)

You can produce Integrated Code 火 fonts from warehouse inputs using the active
`settingsPackage` selections. Merging writes font files to the workbench; packaging creates the
locale archives and removes the temporary build files.

Contents
--------
Functions
	goAssets
		Package merged font files and clear the workbench.
	goMerge
		Save merged fonts for the configured locales, styles, and weights.
"""
from __future__ import annotations

from concurrent.futures import as_completed, Future, ProcessPoolExecutor
from hunterMakesPy.parseParameters import defineConcurrencyLimit
from hunterMakesPy.semiotics import ansiColor, ansiColorReset
from Integrated_Code_Fire import LocaleIn, settingsPackage, WeightIn
from Integrated_Code_Fire.archivist import (
	archivistGetsLocales, archivistGetsWeights, archivistMakesFilenameStem, archivistMakesNameIDMetadata, archivistUpdatesMetadata)
from Integrated_Code_Fire.logistics import packerMakesAssets, valetGetsWesternFontPathFilename, valetRemovesFiles, valetRemovesWorkbench
from Integrated_Code_Fire.machineShop import machinistMergesTTFFonts
from itertools import product as CartesianProduct
from tqdm import tqdm
from typing import TYPE_CHECKING
import sys
import time

if TYPE_CHECKING:
	from collections.abc import Iterable
	from fontTools.ttLib import TTFont
	from pathlib import Path

def goMerge(fontFormat: str = 'ttf', *, CPUlimit: bool | float | int | None = 1) -> Iterable[Path]:
	"""Save merged western and CJK fonts for the active locales, styles, and weights.

	(AI generated docstring)

	Parameters
	----------
	fontFormat : str = 'ttf'
		Extension used for prepared input and merged output files. Inputs must contain TrueType
		outlines compatible with the TrueType merger.
	CPUlimit : bool | float | int | None = 1
		Worker limit. Positive integers select workers; negative integers reserve CPUs.
		Fractions select proportions to use or reserve. `None`, `False`, and `0` use all CPUs;
		`True` selects one worker. The effective limit is at least one worker.

	Returns
	-------
	listPathFilenames : list[Path]
		Saved merged font paths under `settingsPackage.pathWorkbenchFonts`, in completion order.

	See Also
	--------
	`goAssets`
		Package the merged font files into locale archives and clear the workbench.

	File Replacement
	----------------
	The workbench font directory is created and matching merged font files are replaced. Each
	font receives the locale family name, weight name, version, vendor identifier, and credits.
	Prepared warehouse inputs are retained.

	Examples
	--------
	The module entry point merges warehouse fonts and packages the results.

		```python
		from Integrated_Code_Fire.go import goAssets, goMerge

		if __name__ == '__main__':
			CPUlimit = 15
			listPathFilenames = goMerge(CPUlimit=CPUlimit)
			goAssets(listPathFilenames, CPUlimit=CPUlimit)
		```
	"""
	workersMaximum: int = defineConcurrencyLimit(limit=CPUlimit)

	dictionaryLocales: dict[str, LocaleIn] = archivistGetsLocales()
	dictionaryWeights: dict[str, WeightIn] = archivistGetsWeights()

	dictionaryFontsWestern: dict[str, Path] = valetGetsWesternFontPathFilename(fontFormat)

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
				, dictionaryFontsWestern[weightIn.fontFamilyWestern]
				, pathCID / f"{archivistMakesFilenameStem(None, localeIn.ascii, style, weightIn.fontFamilyCID)}.{fontFormat}"
				, archivistMakesNameIDMetadata(weightIn.IntegratedCode火, fontFamily.replace(' ', ''), fontFamily)
				, settingsPackage.pathWorkbenchFonts / f"{archivistMakesFilenameStem(settingsPackage.fontFamily.replace(' ', ''), localeIn.IntegratedCode火, style, weightIn.IntegratedCode火, '')}.{fontFormat}"
			))

		for claimTicket in tqdm(as_completed(listClaimTickets), total=len(listClaimTickets), desc="Merging fonts"):
			listPathFilenames.append(claimTicket.result())

	return listPathFilenames

def _mergeFont(pathFilenameWestern: Path, pathFilenameHan: Path, nameIDmetadata: dict[int, str], pathFilenameWrite: Path) -> Path:
	"""I use this worker to save one merged western and CJK font with release metadata.

	(AI generated docstring)

	Parameters
	----------
	pathFilenameWestern : Path
		Prepared western font with TrueType outlines.
	pathFilenameHan : Path
		Prepared CJK subset with TrueType outlines and matching em size.
	nameIDmetadata : dict[int, str]
		Font name identifiers mapped to their release text.
	pathFilenameWrite : Path
		Destination for the merged font. Parent directories are created.

	Returns
	-------
	pathFilenameWrite : Path
		Saved font path. The merged font is closed after saving.

	File Replacement
	----------------
	The output file is replaced. Both input font files are retained.
	"""
	ttFont: TTFont = machinistMergesTTFFonts(pathFilenameWestern, pathFilenameHan)

	archivistUpdatesMetadata(ttFont, nameIDmetadata)

	pathFilenameWrite.parent.mkdir(parents=True, exist_ok=True)
	ttFont.save(pathFilenameWrite)
	ttFont.close()

	return pathFilenameWrite

def goAssets(listPathFilenames: Iterable[Path], *, CPUlimit: bool | float | int | None = 1) -> None:
	"""Package merged fonts into locale archives and remove temporary build files.

	(AI generated docstring)

	Parameters
	----------
	listPathFilenames : Iterable[Path]
		Merged font paths with locale labels in their filename stems.
	CPUlimit : bool | float | int | None = 1
		Worker limit. Positive integers select workers; negative integers reserve CPUs.
		Fractions select proportions to use or reserve. `None`, `False`, and `0` use all CPUs;
		`True` selects one worker. The effective limit is at least one worker.

	See Also
	--------
	`Integrated_Code_Fire.logistics.packerMakesAssets`
		Create archives and obtain their paths while retaining the workbench files.

	File Replacement and Removal
	----------------------------
	Matching locale ZIP archives in `settingsPackage.pathAssets` are replaced. After packaging,
	all files in `settingsPackage.pathWorkbenchFonts` and that directory are removed. Remaining
	files in `settingsPackage.pathWorkbench` and that directory are then removed. Other nested
	directories prevent cleanup from completing. Warehouse inputs and release archives are retained.
	"""
	workersMaximum: int = defineConcurrencyLimit(limit=CPUlimit)
	listPathFilenames = packerMakesAssets(listPathFilenames, workersMaximum)

	valetRemovesFiles(pathRemove=settingsPackage.pathWorkbenchFonts)
	valetRemovesWorkbench()

if __name__ == '__main__':
	CPUlimit: int = 15

	timeStart: float = time.perf_counter()

	listPathFilenames: Iterable[Path] = goMerge(CPUlimit=CPUlimit)
	goAssets(listPathFilenames, CPUlimit=CPUlimit)

	sys.stdout.write(f"{ansiColor.BlackOnYellow}Done in {time.perf_counter() - timeStart:.2f} seconds.{ansiColorReset}\n")
