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

from Integrated_Code_Fire import pathWorkbench, pathWorkbenchFonts
from Integrated_Code_Fire.getFontInput import getFiraCode, getSourceHanMonoSC
from Integrated_Code_Fire.makeAssets import makeAssets
from Integrated_Code_Fire.mergeFonts import mergeFonts
from Integrated_Code_Fire.writeMetadata import writeMetadata

def cleanWorkbench() -> None:
	"""You can remove source font input files from `pathWorkbenchFonts`.

	(AI generated docstring)

	This function deletes each `Path` in `pathWorkbenchFonts` that matches the
	glob pattern `'FiraCode*.ttf'` and deletes each `Path` in `pathWorkbenchFonts`
	that matches the glob pattern `'SourceHanMonoSC*.otf'`.

	Returns
	-------
	resultNone : None
		This function returns `None`.

	Raises
	------
	OSError
		Raised if a filesystem operation fails while deleting files.

	Examples
	--------
	This function is invoked by `go`.

	>>> from Integrated_Code_Fire.go import go
	>>> go()

	References
	----------
	[1] Integrated_Code_Fire.go.go
		Internal package reference.

	"""
	for pathFilename in pathWorkbenchFonts.glob('FiraCode*.ttf'):
		pathFilename.unlink()

	for pathFilename in pathWorkbenchFonts.glob('SourceHanMonoSC*.otf'):
		pathFilename.unlink()

def removeWorkbench() -> None:
	"""You can remove `pathWorkbenchFonts` and `pathWorkbench`.

	(AI generated docstring)

	This function deletes each file in `pathWorkbenchFonts`, removes the
	`pathWorkbenchFonts` directory, deletes each file in `pathWorkbench`, and
	removes the `pathWorkbench` directory.

	Returns
	-------
	resultNone : None
		This function returns `None`.

	Raises
	------
	OSError
		Raised if a filesystem operation fails while deleting files or directories.

	Examples
	--------
	This function is invoked by `go`.

	>>> from Integrated_Code_Fire.go import go
	>>> go()

	References
	----------
	[1] Integrated_Code_Fire.go.go
		Internal package reference.

	"""
	for pathFilename in pathWorkbenchFonts.iterdir():
		pathFilename.unlink()

	pathWorkbenchFonts.rmdir()

	for pathFilename in pathWorkbench.iterdir():
		pathFilename.unlink()

	pathWorkbench.rmdir()

def go() -> None:
	"""You can run the end-to-end font build assembly line.

	(AI generated docstring)

	This function invokes `getFiraCode`, `getSourceHanMonoSC`, `mergeFonts`,
	`cleanWorkbench`, `writeMetadata`, `makeAssets`, and `removeWorkbench`.

	Returns
	-------
	resultNone : None
		This function returns `None`.

	Raises
	------
	Exception
		Raised if any invoked function fails during the build assembly line.

	Examples
	--------
	This module invokes `go` when `__name__ == '__main__'`.

	>>> from Integrated_Code_Fire.go import go
	>>> go()

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
	getFiraCode()
	getSourceHanMonoSC()
	mergeFonts()
	cleanWorkbench()
	writeMetadata()
	makeAssets()
	removeWorkbench()

if __name__ == '__main__':
	go()
