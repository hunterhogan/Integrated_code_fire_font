"""You can use this module to stage input font files in `pathWorkbenchFonts`.

(AI generated docstring)

This module downloads the Fira Code ZIP archive from `URL` and extracts the
Fira Code `.ttf` files into `pathWorkbenchFonts`. This module also copies
Source Han Mono SC `.otf` files from `pathSourceHanMonoSC` into
`pathWorkbenchFonts`.

Contents
--------
Variables
	URL
		Download URL for the Fira Code ZIP archive.

Functions
	getFiraCode
		Download the Fira Code ZIP archive and extract `.ttf` files.
	getSourceHanMonoSC
		Copy Source Han Mono SC `.otf` files into `pathWorkbenchFonts`.

References
----------
[1] urllib3
	https://urllib3.readthedocs.io/en/stable/
[2] GitHub release asset for `URL`.
	https://github.com/hunterhogan/FiraCode/releases/download/6.900HH/Fira_Code_v6.900HH.zip

"""

from Integrated_Code_Fire import pathSourceHanMonoSC, pathWorkbench, pathWorkbenchFonts
from pathlib import Path, PurePosixPath
import shutil
import urllib3
import zipfile

URL: str = 'https://github.com/hunterhogan/FiraCode/releases/download/6.900HH/Fira_Code_v6.900HH.zip'

def getFiraCode() -> None:
	"""You can download Fira Code and extract `.ttf` files into `pathWorkbenchFonts`.

	(AI generated docstring)

	This function creates `pathWorkbenchFonts`, downloads `URL` using `urllib3`,
	writes the ZIP archive to `pathWorkbench / 'FiraCode.zip'`, and extracts only
	the ZIP members whose parent path is `PurePosixPath('ttf/Fira Code')`.

	This function writes extracted `.ttf` files into `pathWorkbenchFonts` using
	`shutil.copyfileobj`.

	Returns
	-------
	resultNone : None
		This function returns `None`.

	Raises
	------
	urllib3.exceptions.HTTPError
		Raised if `urllib3.PoolManager.request` fails to perform the HTTP request.
	OSError
		Raised if the filesystem operation fails while writing or extracting files.
	zipfile.BadZipFile
		Raised if `pathWorkbench / 'FiraCode.zip'` is not a valid ZIP archive.

	Examples
	--------
	This function is invoked by `Integrated_Code_Fire.go.go`.

	>>> from Integrated_Code_Fire.getFontInput import getFiraCode
	>>> getFiraCode()

	References
	----------
	[1] urllib3
		https://urllib3.readthedocs.io/en/stable/
	[2] GitHub release asset for `URL`.
		https://github.com/hunterhogan/FiraCode/releases/download/6.900HH/Fira_Code_v6.900HH.zip
	[3] Integrated_Code_Fire.go.go
		Internal package reference.

	"""
	pathWorkbenchFonts.mkdir(parents=True, exist_ok=True)

	pathFilenameZIP: Path = pathWorkbench / 'FiraCode.zip'

	HTTPmanager: urllib3.PoolManager = urllib3.PoolManager()
	response: urllib3.BaseHTTPResponse = HTTPmanager.request('GET', URL)
	pathFilenameZIP.write_bytes(response.data)
	response.release_conn()

	zipPathInternal: PurePosixPath = PurePosixPath('ttf/Fira Code')

	with zipfile.ZipFile(pathFilenameZIP) as readZIP:
		for zipInfo in readZIP.infolist():
			if (
				(not zipInfo.is_dir())
				and (PurePosixPath(zipInfo.filename).parent == zipPathInternal)
			):
				pathFilenameWorkbenchFont: Path = pathWorkbenchFonts / Path(zipInfo.filename).name
				with (
					readZIP.open(zipInfo) as archiveMemberHandle
					, pathFilenameWorkbenchFont.open('wb') as workbenchFontHandle
				):
					shutil.copyfileobj(archiveMemberHandle, workbenchFontHandle)

def getSourceHanMonoSC() -> None:
	"""You can copy Source Han Mono SC `.otf` files into `pathWorkbenchFonts`.

	(AI generated docstring)

	This function creates `pathWorkbenchFonts` and copies each `Path` matched by
	`pathSourceHanMonoSC.glob('*SC*.otf')` into `pathWorkbenchFonts` using
	`shutil.copy2`.

	Returns
	-------
	resultNone : None
		This function returns `None`.

	Raises
	------
	OSError
		Raised if the filesystem operation fails while copying files.

	Examples
	--------
	This function is invoked by `Integrated_Code_Fire.go.go`.

	>>> from Integrated_Code_Fire.getFontInput import getSourceHanMonoSC
	>>> getSourceHanMonoSC()

	References
	----------
	[1] Integrated_Code_Fire.go.go
		Internal package reference.

	"""
	pathWorkbenchFonts.mkdir(parents=True, exist_ok=True)
	for pathFilename in pathSourceHanMonoSC.glob('*SC*.otf'):
		shutil.copy2(pathFilename, pathWorkbenchFonts)
