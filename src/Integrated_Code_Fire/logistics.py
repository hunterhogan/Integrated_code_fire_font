"""You can use this module to create the workbench fonts directory and copy selected files into it.

(AI generated docstring)

This module provides a small convenience function for ensuring that the shared
`pathWorkbenchFonts` workbench directory exists [1] and for copying files that
match a glob pattern from a source directory using `pathlib.Path.glob`[2] and
`shutil.copy2`[3]. The operation preserves available file metadata when
supported by the platform.

Contents
--------
Functions
	valetCopiesFilesToWorkbenchFonts
		Create `pathWorkbenchFonts` and copy files matching `theGlob` from
		`pathRoot` into `pathWorkbenchFonts`.

References
----------
[1] Integrated_Code_Fire.pathWorkbenchFonts
	Internal package reference.
[2] pathlib.Path.glob - Python standard library
	https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob
[3] shutil.copy2 - Python standard library
	https://docs.python.org/3/library/shutil.html#shutil.copy2

"""
from concurrent.futures import as_completed, Future, ProcessPoolExecutor
from Integrated_Code_Fire import LocaleIn, settingsPackage
from Integrated_Code_Fire.archivist import getDictionaryLocales
from pathlib import Path, PurePath
from tqdm import tqdm
from typing import TYPE_CHECKING
from zipfile import ZIP_DEFLATED, ZipFile
import shutil

if TYPE_CHECKING:
	from collections.abc import Iterable

def makeAssets(listPathFilenames: Iterable[Path], filenameStem: str, workersMaximum: int) -> None:
	"""You can move `.ttf` files into `pathAssets` and write `filenameZIP`.

	(AI generated docstring)

	This function creates `pathAssets`, moves each `.ttf` file matched by
	`pathWorkbenchFonts.glob(filenameMask_ttf)` into `pathAssets`, and writes a
	ZIP archive named `filenameZIP` in `pathAssets`.

	Returns
	-------
	resultNone : None
		This function returns `None`.

	Raises
	------
	OSError
		Raised if a filesystem operation fails while moving files or writing the ZIP.

	Examples
	--------
	This function is invoked by `Integrated_Code_Fire.go.go`.

	>>> from Integrated_Code_Fire.go import go
	>>> go()

	References
	----------
	[1] Integrated_Code_Fire.go.go
		Internal package reference.

	"""
	listPathFilenamesAssets: list[Path] = []
	listClaimTickets: list[Future[Iterable[Path]]] = []

	dictionaryLocales: dict[str, LocaleIn] = getDictionaryLocales()

	with ProcessPoolExecutor(workersMaximum) as concurrencyManager:
		for locale in settingsPackage.theLocales:
			localeIn: LocaleIn = dictionaryLocales[locale]
			pathFilenameZIP: Path = settingsPackage.pathAssets / f"{filenameStem}_{localeIn.ascii}.zip"
			listClaimTickets.append(concurrencyManager.submit(makeAssetsLocale, listPathFilenames, pathFilenameZIP, localeIn))

		for claimTicket in tqdm(as_completed(listClaimTickets), total = len(listClaimTickets), desc = "Making assets"):
			listPathFilenamesAssets.extend(claimTicket.result())

def makeAssetsLocale(listPathFilenames: Iterable[Path], pathFilenameZIP: Path, localeIn: LocaleIn) -> Iterable[Path]:
	settingsPackage.pathAssets.mkdir(parents=True, exist_ok=True)
	with ZipFile(pathFilenameZIP, mode = 'w', compression = ZIP_DEFLATED, compresslevel = 9) as zipWrite:
		for pathFilename in filter(lambda pathFilename: localeIn.IntegratedCode火 in pathFilename.stem, listPathFilenames):
			zipWrite.write(pathFilename, arcname = pathFilename.name)
	return frozenset([pathFilenameZIP]) # NOTE In the future, there may be more than one asset.

def valetCopiesToWorkbench(pathRoot: PurePath, theGlob: str = '*.*') -> list[Path]:
	"""You can create `pathWorkbenchFonts` and copy files matching `theGlob` from `pathRoot` into `pathWorkbenchFonts`.

	(AI generated docstring)

	This function ensures that the `pathWorkbenchFonts` directory exists [1]
	(creating parents as needed) and then iterates over each `Path` returned
	by `Path(pathRoot).glob(theGlob)`[2], copying each file to `pathWorkbenchFonts`
	using `shutil.copy2`[3]. File metadata is preserved when supported by the
	platform.

	Parameters
	----------
	pathRoot : PurePath
		Source directory from which files are copied. Accepts concrete or pure
		path objects such as `pathlib.Path` or `pathlib.PurePath`.
	theGlob : str = '*.*'
		Glob pattern used to select files to copy. Default is '*.*'.

	Returns
	-------
	resultNone : None
		This function returns `None`.

	Raises
	------
	OSError
		Raised if a filesystem operation fails while creating the directory or
		copying files.

	Examples
	--------
	This function is invoked by `Integrated_Code_Fire.go.go`[4] to stage font
	assets.

	>>> from Integrated_Code_Fire.go import pathWorkbenchSourceHanMono
	>>> from Integrated_Code_Fire.logistics import valetCopiesFilesToWorkbenchFonts
	>>> valetCopiesFilesToWorkbenchFonts(pathWorkbenchSourceHanMono, 'Simplified_Chinese*.otf')

	References
	----------
	[1] Integrated_Code_Fire.pathWorkbenchFonts
		Internal package reference.
	[2] pathlib.Path.glob - Python standard library
		https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob
	[3] shutil.copy2 - Python standard library
		https://docs.python.org/3/library/shutil.html#shutil.copy2
	[4] Integrated_Code_Fire.go.go
		Internal package reference.

	"""
	listPathFilenames: list[Path] = []
	settingsPackage.pathWorkbenchFonts.mkdir(parents=True, exist_ok=True)
	for pathFilename in Path(pathRoot).glob(theGlob):
		listPathFilenames.append(Path(shutil.copy2(pathFilename, settingsPackage.pathWorkbenchFonts)))  # noqa: PERF401
	return listPathFilenames

def valetRemovesFiles(pathRemove: Path) -> None:
	for pathFilename in pathRemove.iterdir():
		pathFilename.unlink()

	pathRemove.rmdir()

def valetRemovesWorkbench() -> None:
	for pathFilename in settingsPackage.pathWorkbench.iterdir():
		pathFilename.unlink()

	settingsPackage.pathWorkbench.rmdir()
