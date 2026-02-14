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
from Integrated_Code_Fire import pathRoot, pathWorkbench, pathWorkbenchFonts, pathWorkbenchSourceHanMono
from pathlib import Path, PurePath
from typing import TYPE_CHECKING
import shutil

if TYPE_CHECKING:
	from collections.abc import Sequence

def librarianGetsUnicode() -> Sequence[str]:  # noqa: D103
	qq = 'SourceHanMono'
	ww = 'Simplified_Chinese.UTF32.map'
	pathFilename: Path = pathRoot / qq / 'metadata' / ww
	rr = pathFilename.read_text(encoding='utf-8')
	# return [line[11:None] for line in rr.splitlines()]  # noqa: ERA001
	return ['0x' + line[1:9] for line in rr.splitlines()]


def valetCopiesFilesToWorkbenchFonts(pathRoot: PurePath, theGlob: str = '*.*') -> None:
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
	pathWorkbenchFonts.mkdir(parents=True, exist_ok=True)
	for pathFilename in Path(pathRoot).glob(theGlob):
		shutil.copy2(pathFilename, pathWorkbenchFonts)

# TODO removeWorkbench: smarter, but avoid nukes, or have some way of knowing it's ok to nuke it.
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

	for pathFilename in pathWorkbenchSourceHanMono.iterdir():
		pathFilename.unlink()

	pathWorkbenchSourceHanMono.rmdir()

	for pathFilename in pathWorkbench.iterdir():
		pathFilename.unlink()

	pathWorkbench.rmdir()

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

	for pathFilename in pathWorkbenchFonts.glob('*SourceHanMono*.otf'):
		pathFilename.unlink()

if __name__ == '__main__':
	zz = librarianGetsUnicode()
	print(zz[0:50])  # noqa: T201
