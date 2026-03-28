"""Merge western and CJK fonts and package release assets.

You can use this module to merge prepared western fonts with subsetted CID fonts, update OpenType metadata, package locale
archives, and remove temporary assembly-line artifacts. The module provides the merge stage in `goMerge` and the packaging and
cleanup stage in `goAssets`.

Contents
--------
Functions
	goAssets
		Package merged fonts into locale archives and remove temporary artifacts.
	goMerge
		Merge prepared western fonts with subsetted CID fonts.

References
----------
[1] Integrated_Code_Fire.archivist
	Internal package reference.
[2] Integrated_Code_Fire.logistics
	Internal package reference.
[3] Integrated_Code_Fire.machineShop
	Internal package reference.

"""
from concurrent.futures import as_completed, Future, ProcessPoolExecutor
from hunterMakesPy.parseParameters import defineConcurrencyLimit
from hunterMakesPy.semiotics import ansiColorReset, AnsiColors
from Integrated_Code_Fire import LocaleIn, settingsPackage, WeightIn
from Integrated_Code_Fire.archivist import (
	archivistGetsLocales, archivistGetsWeights, archivistMakesFilenameStem, archivistMakesNameIDMetadata, archivistUpdatesMetadata)
from Integrated_Code_Fire.logistics import packerMakesAssets, valetGetsWesternFontPathFilename, valetRemovesFiles, valetRemovesWorkbench
from Integrated_Code_Fire.machineShop import machinistMergesTTFFonts
from itertools import product as CartesianProduct
from pathlib import Path
from tqdm import tqdm
from typing import TYPE_CHECKING
import sys
import time

if TYPE_CHECKING:
	from collections.abc import Iterable
	from fontTools.ttLib import TTFont
	from pathlib import Path

ansiColors = AnsiColors()

def goMerge(fontFormat: str = 'ttf', *, CPUlimit: bool | float | int | None = 1) -> Iterable[Path]:
	"""Merge prepared western fonts with subsetted CID fonts.

	(AI generated docstring)

	You can use this function to merge prepared western fonts with subsetted CID fonts for every configured locale, style, and
	weight combination. The function loads western font paths from `valetGetsWesternFontPathFilename` [1], derives name-table
	metadata with `archivistMakesNameIDMetadata` [2], dispatches `_mergeFont` workers in parallel, and writes merged fonts into
	`settingsPackage.pathWorkbenchFonts`.

	Parameters
	----------
	fontFormat : str = 'ttf'
		Font file format used for both western input files and subsetted CID input files.
	CPUlimit : bool | float | int | None = 1
		Concurrency limit passed to `defineConcurrencyLimit` [3].

	Returns
	-------
	pathFilenamesMerged : list[Path]
		Merged font file paths written into `settingsPackage.pathWorkbenchFonts`.

	Examples
	--------
	The `__main__` block uses `goMerge` to produce the merged fonts that `goAssets` packages [4].

	>>> listPathFilenames: Iterable[Path] = goMerge(CPUlimit=CPUlimit)

	References
	----------
	[1] Integrated_Code_Fire.logistics.valetGetsWesternFontPathFilename
		Internal package reference.
	[2] Integrated_Code_Fire.archivist.archivistMakesNameIDMetadata
		Internal package reference.
	[3] hunterMakesPy.parseParameters.defineConcurrencyLimit
		https://context7.com/hunterhogan/huntermakespy
	[4] Integrated_Code_Fire.go.goAssets
		Internal package reference.

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

		for claimTicket in tqdm(as_completed(listClaimTickets), total=len(listClaimTickets), desc = "Merging fonts"):
			listPathFilenames.append(claimTicket.result())

	return listPathFilenames

def _mergeFont(pathFilenameWestern: Path, pathFilenameHan: Path, nameIDmetadata: dict[int, str], pathFilenameWrite: Path) -> Path:
	"""I use this worker to merge one western font with one subsetted CID font.

	(AI generated docstring)

	I use this function as the parallel worker dispatched by `goMerge` [1]. The function merges `pathFilenameWestern` and
	`pathFilenameHan` with `machinistMergesTTFFonts` [2], updates OpenType metadata with `archivistUpdatesMetadata` [3], writes
	the merged font to `pathFilenameWrite`, and returns `pathFilenameWrite`.

	Parameters
	----------
	pathFilenameWestern : Path
		Path to the prepared western font file.
	pathFilenameHan : Path
		Path to the subsetted CID-derived font file.
	nameIDmetadata : dict[int, str]
		Name-table values written into the merged font.
	pathFilenameWrite : Path
		Destination path for the merged font file.

	Returns
	-------
	pathFilenameWrite : Path
		Path to the written merged font file.

	References
	----------
	[1] Integrated_Code_Fire.go.goMerge
		Internal package reference.
	[2] Integrated_Code_Fire.machineShop.machinistMergesTTFFonts
		Internal package reference.
	[3] Integrated_Code_Fire.archivist.archivistUpdatesMetadata
		Internal package reference.
	"""
	ttFont: TTFont = machinistMergesTTFFonts(pathFilenameWestern, pathFilenameHan)

	archivistUpdatesMetadata(ttFont, nameIDmetadata)

	pathFilenameWrite.parent.mkdir(parents=True, exist_ok=True)
	ttFont.save(pathFilenameWrite)
	ttFont.close()

	return pathFilenameWrite

def goAssets(listPathFilenames: Iterable[Path], *, CPUlimit: bool | float | int | None = 1) -> None:
	"""Package merged fonts into locale archives and remove temporary artifacts.

	You can use this function to package the merged font files produced by `goMerge` [1] into locale-specific ZIP archives with
	`packerMakesAssets` [2]. After packaging, the function removes `settingsPackage.pathWorkbenchFonts` and `settingsPackage.pathWorkbench`
	to leave only warehouse and asset outputs.

	Parameters
	----------
	listPathFilenames : Iterable[Path]
		Merged font file paths to package.
	CPUlimit : bool | float | int | None = 1
		Concurrency limit passed to `defineConcurrencyLimit` [3].

	References
	----------
	[1] Integrated_Code_Fire.go.goMerge
		Internal package reference.
	[2] Integrated_Code_Fire.logistics.packerMakesAssets
		Internal package reference.
	[3] hunterMakesPy.parseParameters.defineConcurrencyLimit
		https://context7.com/hunterhogan/huntermakespy
	"""
	workersMaximum: int = defineConcurrencyLimit(limit=CPUlimit)
	listPathFilenames = packerMakesAssets(listPathFilenames, workersMaximum)

	valetRemovesFiles(pathRemove=settingsPackage.pathWorkbenchFonts)
	valetRemovesWorkbench()

if __name__ == '__main__':
	CPUlimit: int = -1

	timeStart: float = time.perf_counter()

	listPathFilenames: Iterable[Path] = goMerge(CPUlimit=CPUlimit)
	goAssets(listPathFilenames, CPUlimit=CPUlimit)

	sys.stdout.write(f"{ansiColors.BlackOnYellow}Done in {time.perf_counter() - timeStart:.2f} seconds.{ansiColorReset}\n")

# cid-keyed to name-keyed _in-place_
# merge.
# don't create assets.
# sfntedit to share tables.
# otf2otc.
