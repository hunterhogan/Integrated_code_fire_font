"""Download."""
from hunterMakesPy.filesystemToolkit import makeDirsSafely
from Integrated_Code_Fire import URLSourceHanMono
from Integrated_Code_Fire.unpackDownload import pathFilenameSourceHanMono
from typing import TYPE_CHECKING
import urllib3

if TYPE_CHECKING:
	from pathlib import Path

def downloadURLToHere(url: str, pathFilename: Path) -> None:
	"""Download the file to here."""
	makeDirsSafely(pathFilename.parent)
	httpManager = urllib3.PoolManager()
	with httpManager.request("GET", url, preload_content=False) as getHTTP, pathFilename.open("wb") as writeStreamBinary:
		for bytesStreamed in getHTTP.stream(1024 * 1024):
			writeStreamBinary.write(bytesStreamed)

downloadURLToHere(URLSourceHanMono, pathFilenameSourceHanMono)

