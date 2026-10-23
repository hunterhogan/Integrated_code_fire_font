"""Stage font files, package release archives, and remove temporary build files.

(AI generated docstring)

You can copy files to the workbench, locate prepared western fonts, and create locale-specific
ZIP archives. Cleanup operations remove files and their immediate directory; cleanup operations
do not recursively remove nested directories.

Contents
--------
Functions
	packerMakesAssets
		Create one release archive for each active locale.
	packerMakesAssetsLocale
		Create a release archive for one locale.
	valetCopiesToWorkbench
		Copy selected files to the workbench font directory.
	valetGetsWesternFontPathFilename
		Locate prepared western fonts by weight.
	valetRemovesFiles
		Remove selected files and optionally clear an immediate directory.
	valetRemovesWorkbench
		Clear and remove the workbench after its subdirectories have been removed.
"""
from __future__ import annotations

from concurrent.futures import as_completed, Future, ProcessPoolExecutor
from Integrated_Code_Fire import LocaleIn, settingsPackage, WeightIn
from Integrated_Code_Fire.archivist import archivistGetsLocales, archivistGetsWeights
from pathlib import Path
from tqdm import tqdm
from typing import TYPE_CHECKING
from zipfile import ZIP_DEFLATED, ZipFile

if TYPE_CHECKING:
	from collections.abc import Iterable
	from pathlib import PurePath

def packerMakesAssets(listPathFilenames: Iterable[Path], workersMaximum: int) -> frozenset[Path]:
	"""Create one ZIP archive for each locale in the active font configuration.

	(AI generated docstring)

	Parameters
	----------
	listPathFilenames : Iterable[Path]
		Merged font paths. Filename stems must contain the locale display labels used by
		`LocaleIn.IntegratedCode火`.
	workersMaximum : int
		Maximum number of locales packaged concurrently.

	Returns
	-------
	listPathFilenamesAssets : frozenset[Path]
		Archive paths under `settingsPackage.pathAssets`, named with the ASCII family and locale
		labels, such as `"IntegratedCodeFire_Japan.zip"`.

	See Also
	--------
	`packerMakesAssetsLocale`
		Create an archive for a single locale at a specified path.

	File Replacement
	----------------
	The assets directory is created and matching locale archives are replaced. Input fonts
	are retained.
	"""
	listPathFilenamesAssets: list[Path] = []
	listClaimTickets: list[Future[Iterable[Path]]] = []

	dictionaryLocales: dict[str, LocaleIn] = archivistGetsLocales()

	with ProcessPoolExecutor(workersMaximum) as concurrencyManager:
		for locale in settingsPackage.theLocales:
			localeIn: LocaleIn = dictionaryLocales[locale]
			pathFilenameZIP: Path = settingsPackage.pathAssets / f"{settingsPackage.fontFamilyASCII.replace(' ', '')}_{localeIn.ascii}.zip"
			listClaimTickets.append(concurrencyManager.submit(packerMakesAssetsLocale, listPathFilenames, pathFilenameZIP, localeIn))

		for claimTicket in tqdm(as_completed(listClaimTickets), total=len(listClaimTickets), desc="Making assets"):
			listPathFilenamesAssets.extend(claimTicket.result())

	return frozenset(listPathFilenamesAssets)

# TODO Learn how to create one family with all locales and weights.
def packerMakesAssetsLocale(listPathFilenames: Iterable[Path], pathFilenameZIP: Path, localeIn: LocaleIn) -> frozenset[Path]:
	"""Create a ZIP archive containing the supplied fonts for one locale.

	(AI generated docstring)

	Parameters
	----------
	listPathFilenames : Iterable[Path]
		Font paths to consider. Files are included when their stem contains
		`localeIn.IntegratedCode火`.
	pathFilenameZIP : Path
		Archive destination. The configured assets directory is created; another destination
		directory must already exist.
	localeIn : LocaleIn
		Locale labels used to select fonts by their filename stems.

	Returns
	-------
	listPathFilenamesAssets : frozenset[Path]
		A set containing `pathFilenameZIP`.

	File Replacement
	----------------
	The archive is created or replaced with the matching files stored by basename. No input
	fonts are removed. No license files or other documentation are added automatically.
	"""
	settingsPackage.pathAssets.mkdir(parents=True, exist_ok=True)
	with ZipFile(pathFilenameZIP, mode='w', compression=ZIP_DEFLATED, compresslevel=9) as zipWrite:
		for pathFilename in filter(lambda pathFilename: localeIn.IntegratedCode火 in pathFilename.stem, listPathFilenames):
			zipWrite.write(pathFilename, arcname=pathFilename.name)

	# Using a list makes it easy to add more assets in the future.
	return frozenset([pathFilenameZIP])

def valetCopiesToWorkbench(listPathFilenames: Iterable[Path] | None = None, pathRoot: PurePath | None = None, theGlob: str = '*.*') -> frozenset[Path]:
	"""Copy selected files to the workbench font directory.

	(AI generated docstring)

	Parameters
	----------
	listPathFilenames : Iterable[Path] | None = None
		Explicit files to copy after any directory matches. `None` skips explicit files.
	pathRoot : PurePath | None = None
		Directory to search with `theGlob`. `None` skips the directory search.
	theGlob : str = '*.*'
		Glob pattern relative to `pathRoot`. The pattern applies only to the directory search.

	Returns
	-------
	listPathFilenamesCopied : frozenset[Path]
		Destination paths under `settingsPackage.pathWorkbenchFonts`. Repeated destinations
		appear once in the result.

	File Replacement
	----------------
	The destination directory is created. Files with matching basenames replace existing files.
	Directory matches are copied before explicit paths, so a later explicit path wins a name
	collision. Within each source, the last copied file wins; unordered inputs and glob results
	do not guarantee which file wins. Source files are retained.
	"""
	listPathFilenamesCopied: list[Path] = []
	settingsPackage.pathWorkbenchFonts.mkdir(parents=True, exist_ok=True)

	if pathRoot is not None:
		for pathFilename in Path(pathRoot).glob(theGlob):
			listPathFilenamesCopied.append(pathFilename.copy_into(settingsPackage.pathWorkbenchFonts))  # ruff: ignore[manual-list-comprehension]

	if listPathFilenames is not None:
		for pathFilename in listPathFilenames:
			listPathFilenamesCopied.append(pathFilename.copy_into(settingsPackage.pathWorkbenchFonts))  # ruff: ignore[manual-list-comprehension]

	return frozenset(listPathFilenamesCopied)

def valetGetsWesternFontPathFilename(fontFormat: str) -> dict[str, Path]:
	"""Locate prepared western font files by their western weight labels.

	(AI generated docstring)

	Parameters
	----------
	fontFormat : str
		Filename extension without a dot, normally `"ttf"`.

	Returns
	-------
	dictionaryFontsWestern : dict[str, Path]
		Western weight labels mapped to paths for `settingsPackage.theWeights`. Paths point to
		`warehouse/western` for an em size of `2000`, or `warehouse/scaled` otherwise. The files
		are not opened or checked for existence.
	"""
	western: str = 'western'
	if settingsPackage.unitsPerEm != 2000:
		western: str = 'scaled'

	dictionaryFontsWestern: dict[str, Path] = {}
	dictionaryWeights: dict[str, WeightIn] = archivistGetsWeights()
	for weight in settingsPackage.theWeights:
		pathFilename: Path = settingsPackage.pathWarehouse / western / f"{dictionaryWeights[weight].fontFamilyWestern}.{fontFormat}"
		dictionaryFontsWestern[dictionaryWeights[weight].fontFamilyWestern] = pathFilename
	return dictionaryFontsWestern

def valetRemovesFiles(listPathFilenames: Iterable[Path] | None = None, pathRemove: Path | None = None) -> None:
	"""Remove selected files and optionally clear and remove an immediate directory.

	(AI generated docstring)

	Parameters
	----------
	listPathFilenames : Iterable[Path] | None = None
		Files to remove first. `None` skips this selection.
	pathRemove : Path | None = None
		Directory whose remaining entries and then the directory itself are removed. `None`
		skips this selection.

	File Removal
	------------
	Both selections apply when both are supplied. Directory cleanup removes immediate files,
	including files absent from `listPathFilenames`. Nested directories prevent cleanup from
	completing. A failure can leave earlier files already removed.
	"""
	if listPathFilenames is not None:
		for pathFilename in listPathFilenames:
			pathFilename.unlink()

	if pathRemove is not None:
		for pathFilename in pathRemove.iterdir():
			pathFilename.unlink()
		pathRemove.rmdir()

def valetRemovesWorkbench() -> None:
	"""Remove the remaining workbench files and the workbench directory.

	(AI generated docstring)

	File Removal
	------------
	Every immediate file in `settingsPackage.pathWorkbench` is removed, followed by the directory
	itself. All workbench subdirectories must already have been removed. A nested directory
	prevents cleanup from completing and indicates an unfinished or unexpected build state.
	A failure can leave earlier files already removed.
	"""
	for pathFilename in settingsPackage.pathWorkbench.iterdir():
		pathFilename.unlink()

	settingsPackage.pathWorkbench.rmdir()
