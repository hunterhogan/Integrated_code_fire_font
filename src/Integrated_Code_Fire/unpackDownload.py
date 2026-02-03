"""IDK if this works because I can't see OTF in fontforge."""
from fontTools.ttLib.ttCollection import TTCollection
from hunterMakesPy.filesystemToolkit import makeDirsSafely
from Integrated_Code_Fire import filenameSourceHanMono, pathRootWorkbench
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pathlib import Path

pathFilenameSourceHanMono: Path = pathRootWorkbench / 'downloads' / filenameSourceHanMono
pathRootFonts = pathRootWorkbench / 'fonts'
makeDirsSafely(pathRootFonts)
listPathFilenamesSourceHanMono: list[Path] = []

TTCSourceHanMono: TTCollection = TTCollection(str(pathFilenameSourceHanMono))
for ttf in TTCSourceHanMono:
	ttfName: str = ttf['name'].getBestFullName()
	if ' SC' in ttfName and 'Italic' not in ttfName:
		pathFilename = pathRootFonts / f"{ttfName.replace(' ', '')}.ttf"
		listPathFilenamesSourceHanMono.append(pathFilename)
		ttf.save(str(pathFilename))
