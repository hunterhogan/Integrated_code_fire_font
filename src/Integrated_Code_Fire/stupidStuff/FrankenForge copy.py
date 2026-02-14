# ruff: noqa: D100 D103
from fontTools.misc.transform import Transform
from Integrated_Code_Fire import bearingIncrement, fontUnitsPerEm, pathRoot
from multiprocessing import Pool
from pathlib import Path
from tqdm import tqdm
from typing import TYPE_CHECKING
import shutil
import subprocess
import ufoLib2

if TYPE_CHECKING:
	from ufoLib2.objects import Glyph

fontUnitsPerEmOriginal: int = 1000
scaleMultiplier: int = fontUnitsPerEm // fontUnitsPerEmOriginal

def transformerAppliesScaleAndBearingToGlyph(glyphTarget: Glyph) -> None:
	widthOriginal: int | float = glyphTarget.width

	for contour in glyphTarget.contours:
		for point in contour:
			point.x = point.x * scaleMultiplier + bearingIncrement
			point.y = point.y * scaleMultiplier

	for component in glyphTarget.components:
		componentTransform = component.transformation
		offsetHorizontal: int | float = componentTransform.dx * scaleMultiplier + bearingIncrement
		offsetVertical: int | float = componentTransform.dy * scaleMultiplier
		component.transformation = Transform( componentTransform.xx, componentTransform.xy, componentTransform.yx, componentTransform.yy, offsetHorizontal, offsetVertical )

	glyphTarget.width = widthOriginal * scaleMultiplier + bearingIncrement * 2

def completerFixesIncompleteUfoFromTx(pathUfo: Path) -> None:
	pathFilenameMetainfo: Path = pathUfo / 'metainfo.plist'
	if not pathFilenameMetainfo.exists():
		pathFilenameMetainfo.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>creator</key>
	<string>tx</string>
	<key>formatVersion</key>
	<integer>3</integer>
</dict>
</plist>
""", encoding='utf-8')

	pathFilenameLayercontents: Path = pathUfo / 'layercontents.plist'
	if not pathFilenameLayercontents.exists():
		pathFilenameLayercontents.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<array>
	<array>
		<string>public.default</string>
		<string>glyphs</string>
	</array>
</array>
</plist>
""", encoding='utf-8')

	pathFilenameLib: Path = pathUfo / 'lib.plist'
	if pathFilenameLib.exists() and pathFilenameLib.stat().st_size == 0:
		pathFilenameLib.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
</dict>
</plist>
""", encoding='utf-8')

def converterTransformsCidfontToUfo(pathFilenameCidfontSource: Path, pathUfoDestination: Path) -> None:
	subprocess.run(
		['tx', '-ufo', '-o', str(pathUfoDestination), str(pathFilenameCidfontSource)],  # noqa: S607
		check=True,
		capture_output=True,
	)
	completerFixesIncompleteUfoFromTx(pathUfoDestination)

def transformerProcessesUfo(pathUfo: Path) -> None:
	fontTarget: ufoLib2.Font = ufoLib2.Font.open(pathUfo)

	fontTarget.info.unitsPerEm = fontUnitsPerEm

	if fontTarget.info.ascender is not None:
		fontTarget.info.ascender = fontTarget.info.ascender * scaleMultiplier

	if fontTarget.info.descender is not None:
		fontTarget.info.descender = fontTarget.info.descender * scaleMultiplier

	if fontTarget.info.capHeight is not None:
		fontTarget.info.capHeight = fontTarget.info.capHeight * scaleMultiplier

	if fontTarget.info.xHeight is not None:
		fontTarget.info.xHeight = fontTarget.info.xHeight * scaleMultiplier

	if fontTarget.info.postscriptUnderlinePosition is not None:
		fontTarget.info.postscriptUnderlinePosition = fontTarget.info.postscriptUnderlinePosition * scaleMultiplier

	if fontTarget.info.postscriptUnderlineThickness is not None:
		fontTarget.info.postscriptUnderlineThickness = fontTarget.info.postscriptUnderlineThickness * scaleMultiplier

	for glyphTarget in fontTarget:
		transformerAppliesScaleAndBearingToGlyph(glyphTarget)

	fontTarget.save(pathUfo, overwrite=True)

def scientistConvertsCidfontToUfoAndTransforms(pathFilenameCidfont: Path) -> None:
	pathUfo: Path = pathFilenameCidfont.with_suffix('.ufo')

	converterTransformsCidfontToUfo(pathFilenameCidfont, pathUfo)
	transformerProcessesUfo(pathUfo)

	pathFilenameCidfont.unlink()

def scientistCreatesFrankenFont(fontFamilyDonor: str = 'SourceHanMono', fontFamilyMonster: str = 'FrankenFont', workersMaximum: int = 1) -> None:
	pathDonor: Path = pathRoot / fontFamilyDonor
	pathMonster: Path = pathRoot / fontFamilyMonster

	shutil.copytree(pathDonor, pathMonster, dirs_exist_ok=True)

	pathMonsterGlyphs: Path = pathMonster / 'glyphs'
	listPathFilenameCidfont: list[Path] = list(pathMonsterGlyphs.glob('*.cidfont.ps'))

	with Pool(processes=workersMaximum) as concurrencyManager:
		concurrencyManager.map(scientistConvertsCidfontToUfoAndTransforms, listPathFilenameCidfont)

	for pathFilename in (*Path(pathMonster, 'metadata').glob('*.txt'), *Path(pathMonster, 'metadata').glob('*.H')):
		pathFilename: Path = pathFilename.with_stem(pathFilename.stem.replace(fontFamilyDonor, fontFamilyMonster))

if __name__ == '__main__':
	scientistCreatesFrankenFont(workersMaximum=14)
