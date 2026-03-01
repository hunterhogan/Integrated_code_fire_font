"""You can use this module to move built font files into `pathAssets` and zip the release.

(AI generated docstring)

This module moves `.ttf` files from `pathWorkbenchFonts` into `pathAssets` and
creates a ZIP archive containing the `.ttf` files.

Contents
--------
Variables
	filenameMask_ttf
		Glob pattern used to select `.ttf` files.
	filenameZIP
		ZIP filename written into `pathAssets`.

Functions
	makeAssets
		Move `.ttf` files into `pathAssets` and write `filenameZIP`.

References
----------
[1] Integrated_Code_Fire.go.go
	Internal package reference.

"""
from Integrated_Code_Fire import settingsPackage
from Integrated_Code_Fire.archivist import dictionaryLocales
from typing import TYPE_CHECKING
from zipfile import ZIP_DEFLATED, ZipFile

if TYPE_CHECKING:
	from collections.abc import Iterable
	from Integrated_Code_Fire import LocaleIn
	from pathlib import Path

def makeAssets(listPathFilenames: Iterable[Path], filenameStem: str) -> None:
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
	settingsPackage.pathAssets.mkdir(parents=True, exist_ok=True)

	for locale in settingsPackage.listLocales:
		localeIn: LocaleIn = dictionaryLocales[locale]
		pathFilenameZIP: Path = settingsPackage.pathAssets / f"{filenameStem}_{localeIn.ascii}.zip"
		with ZipFile(pathFilenameZIP, mode = 'w', compression = ZIP_DEFLATED, compresslevel = 9) as zipWrite:
			for pathFilename in filter(lambda pathFilename: localeIn.IntegratedCode in pathFilename.stem, listPathFilenames):
				zipWrite.write(pathFilename, arcname = pathFilename.name)
