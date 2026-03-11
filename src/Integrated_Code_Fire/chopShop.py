from concurrent.futures import as_completed, Future, ProcessPoolExecutor
from fontTools import subset
from hunterMakesPy.parseParameters import defineConcurrencyLimit
from Integrated_Code_Fire import (
	LocaleIn, PackageSettings, pathFilenameFiraCodeGlyphs, pathRootSourceHanMono, settingsPackage, WeightIn)
from Integrated_Code_Fire.archivist import (
	archivistGetsLocales, archivistGetsSubsetCharacters, archivistGetsWeights, archivistMakesFilenameStem)
from Integrated_Code_Fire.foundry import smithyCasts_afdko, smithyCastsFromGlyphs
from Integrated_Code_Fire.logistics import valetCopiesToWorkbench, valetRemovesFiles, valetRemovesWorkbench
from Integrated_Code_Fire.machineShop import machinistScalesFonts, machinistSubsetsCID
from itertools import product as CartesianProduct
from tqdm import tqdm
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from collections.abc import Iterable
	from fontTools.ttLib import TTFont
	from hunterMakesPy import identifierDotAttribute
	from pathlib import Path

subsetOptionsHARDCODED: subset.Options = subset.Options(
	drop_tables = [],
	glyph_names = False,
	layout_features = '*',
	name_IDs = '',
	passthrough_tables = True,
	symbol_cmap = True,
)

subsetOptions: subset.Options = subsetOptionsHARDCODED

def glyphs(pathFilenameGlyphs: Path, fontFormat: str = 'ttf') -> None:
	pathTTFont: Path = smithyCastsFromGlyphs(pathFilenameGlyphs, 1, [fontFormat])

	dictionaryFontsScaled: dict[str, TTFont] = machinistScalesFonts(pathTTFont, f"*.{fontFormat}")
	valetRemovesFiles(pathRemove=pathTTFont)

	pathScaled: Path = settingsPackage.pathWarehouse / 'scaled'
	pathScaled.mkdir(parents=True, exist_ok=True)
	for weight, ttFont in dictionaryFontsScaled.items():
		ttFont.save(pathScaled / f"{weight}.{fontFormat}")

	valetRemovesWorkbench()

def cid(subsetOptions: subset.Options, fontFamilyCID: str = 'SourceHanMono', theLocales: Iterable[str] | None = None, theStyles: Iterable[str | None] | None = None, theWeights: Iterable[str] | None = None, *, CPUlimit: bool | float | int | None = 1) -> None:
# TODO Configuration.
	pathRoot: Path = pathRootSourceHanMono

	pathCID: Path = settingsPackage.pathWarehouse / 'CID'
	pathCID.mkdir(parents=True, exist_ok=True)
	workersMaximum: int = defineConcurrencyLimit(limit=CPUlimit)

	if (theLocales is None) or (theStyles is None) or (theWeights is None):
		settings = PackageSettings(settingsPackage.identifierPackage)
		theLocales = theLocales or settings.theLocales
		theStyles = theStyles or settings.theStyles
		theWeights = theWeights or settings.theWeights

	subsetCharacters: dict[identifierDotAttribute, dict[str, list[int]]] = archivistGetsSubsetCharacters(fontFamilyCID, theLocales, theStyles)
	dictionaryLocales: dict[str, LocaleIn] = archivistGetsLocales()
	dictionaryWeights: dict[str, WeightIn] = archivistGetsWeights()

	listPathFilenames: list[Path] = smithyCasts_afdko(pathRoot, theLocales, theStyles, theWeights, fontFamilyCID, CPUlimit=workersMaximum)

	valetCopiesToWorkbench(listPathFilenames)
	valetRemovesFiles(listPathFilenames, listPathFilenames[0].parent)

	listClaimTickets: list[Future[Path]] = []
	listPathFilenames = []
	with ProcessPoolExecutor(workersMaximum) as concurrencyManager:
		for locale, style, weight in CartesianProduct(theLocales, theStyles, theWeights):
			localeIn: LocaleIn = dictionaryLocales[locale]
			weightIn: WeightIn = dictionaryWeights[weight]

			lookupIDs: identifierDotAttribute = archivistMakesFilenameStem(fontFamilyCID, localeIn.ascii, style)

			listClaimTickets.append(concurrencyManager.submit(
					_cid
					, settingsPackage.pathWorkbenchFonts / f"{archivistMakesFilenameStem(fontFamilyCID, localeIn.ascii, style, weightIn.fontFamilyCID)}.otf"
					, subsetCharacters[lookupIDs]['gids']
					, subsetCharacters[lookupIDs]['unicodes']
					, subsetOptions
					, pathCID / f"{archivistMakesFilenameStem(None, localeIn.ascii, style, weightIn.fontFamilyCID)}.ttf"
				))

		for claimTicket in tqdm(as_completed(listClaimTickets), total=len(listClaimTickets), desc = f"Subsetting {fontFamilyCID}"):
			listPathFilenames.append(claimTicket.result())

	valetRemovesFiles(pathRemove=settingsPackage.pathWorkbenchFonts)
	valetRemovesWorkbench()

def _cid(pathFilenameCID: Path, gids: list[int], unicodes: list[int], subsetOptions: subset.Options, pathFilenameWrite: Path) -> Path:
	fontCID: TTFont = machinistSubsetsCID(pathFilenameCID, gids, unicodes, subsetOptions)
	fontCID.save(pathFilenameWrite)
	fontCID.close()
	return pathFilenameWrite

if __name__ == "__main__":
	glyphs(pathFilenameFiraCodeGlyphs)
	cid(subsetOptions, CPUlimit=-2)

