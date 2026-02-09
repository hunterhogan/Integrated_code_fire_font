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

from Integrated_Code_Fire import pathAssets, pathWorkbenchFonts
from zipfile import ZIP_DEFLATED, ZipFile

filenameZIP: str = 'IntegratedCode.zip'
filenameMask_ttf: str = 'I*.ttf'

def makeAssets() -> None:
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
	pathAssets.mkdir(exist_ok = True)
	for pathFilename in pathWorkbenchFonts.glob(filenameMask_ttf):
		pathFilename.replace(pathAssets / pathFilename.name)

	with ZipFile(pathAssets / filenameZIP, mode = 'w', compression = ZIP_DEFLATED, compresslevel = 9) as zipArchive:
		for pathFilename in pathAssets.glob(filenameMask_ttf):
			zipArchive.write(pathFilename, arcname = pathFilename.name)
