from concurrent.futures import as_completed, Future, ProcessPoolExecutor
from hunterMakesPy.parseParameters import defineConcurrencyLimit
from Integrated_Code_Fire import (
	LocaleIn, PackageSettings, pathFilenameFiraCodeGlyphs, pathRootSourceHanMono, settingsPackage, subsetOptions, WeightIn)
from Integrated_Code_Fire.archivist import (
	archivistGetsLocales, archivistGetsSubsetCharacters, archivistGetsWeights, archivistMakesFilenameStem)
from Integrated_Code_Fire.foundry import smithyCasts_afdko, smithyCastsFromGlyphs
from Integrated_Code_Fire.logistics import valetCopiesToWorkbench, valetRemovesFiles, valetRemovesWorkbench
from Integrated_Code_Fire.machineShop import machinistScalesFonts, machinistSubsetsCID
from itertools import product as CartesianProduct
from pathlib import Path
from tqdm import tqdm
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from collections.abc import Iterable
	from fontTools import subset
	from fontTools.ttLib import TTFont
	from hunterMakesPy import identifierDotAttribute
	from pathlib import Path

def prepareGlyphs(pathFilenameGlyphs: Path, fontFormat: str = 'ttf') -> None:
	pathTTFont: Path = smithyCastsFromGlyphs(pathFilenameGlyphs, 1, [fontFormat])

	dictionaryFontsScaled: dict[str, TTFont] = machinistScalesFonts(pathTTFont, f"*.{fontFormat}")
	valetRemovesFiles(pathRemove=pathTTFont)

	pathScaled: Path = settingsPackage.pathWarehouse / 'scaled'
	pathScaled.mkdir(parents=True, exist_ok=True)
	for weight, ttFont in dictionaryFontsScaled.items():
		ttFont.save(pathScaled / f"{weight}.{fontFormat}")

	valetRemovesWorkbench()

def castCID(pathRootCID: Path, fontFamilyCID: str = 'SourceHanMono', theLocales: Iterable[str] | None = None, theStyles: Iterable[str | None] | None = None, theWeights: Iterable[str] | None = None, *, CPUlimit: bool | float | int | None = 1) -> frozenset[Path]:
	workersMaximum: int = defineConcurrencyLimit(limit=CPUlimit)

	if (theLocales is None) or (theStyles is None) or (theWeights is None):
		settings = PackageSettings(settingsPackage.identifierPackage)
		theLocales = theLocales or settings.theLocales
		theStyles = theStyles or settings.theStyles
		theWeights = theWeights or settings.theWeights

	return frozenset(smithyCasts_afdko(pathRootCID, theLocales, theStyles, theWeights, fontFamilyCID, CPUlimit=workersMaximum))

def subsetCID(subsetOptions: subset.Options, fontFamilyCID: str = 'SourceHanMono', theLocales: Iterable[str] | None = None, theStyles: Iterable[str | None] | None = None, theWeights: Iterable[str] | None = None, *, CPUlimit: bool | float | int | None = 1) -> frozenset[Path]:
	if (theLocales is None) or (theStyles is None) or (theWeights is None):
		settings = PackageSettings(settingsPackage.identifierPackage)
		theLocales = theLocales or settings.theLocales
		theStyles = theStyles or settings.theStyles
		theWeights = theWeights or settings.theWeights

	subsetCharacters: dict[identifierDotAttribute, dict[str, list[int]]] = archivistGetsSubsetCharacters(fontFamilyCID, theLocales, theStyles)
	dictionaryLocales: dict[str, LocaleIn] = archivistGetsLocales()
	dictionaryWeights: dict[str, WeightIn] = archivistGetsWeights()

	pathCID: Path = settingsPackage.pathWarehouse / 'CID'
	pathCID.mkdir(parents=True, exist_ok=True)
	listClaimTickets: list[Future[Path]] = []
	listPathFilenames: list[Path] = []
	workersMaximum: int = defineConcurrencyLimit(limit=CPUlimit)
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
			listPathFilenames.append(claimTicket.result())  # noqa: PERF401
	return frozenset(listPathFilenames)

def _cid(pathFilenameCID: Path, gids: list[int], unicodes: list[int], subsetOptions: subset.Options, pathFilenameWrite: Path) -> Path:
	fontCID: TTFont = machinistSubsetsCID(pathFilenameCID, gids, unicodes, subsetOptions)
	fontCID.save(pathFilenameWrite)
	fontCID.close()
	return pathFilenameWrite

if __name__ == "__main__":
	prepareGlyphs(pathFilenameFiraCodeGlyphs)

	listPathFilenamesCID: frozenset[Path] = castCID(pathRootSourceHanMono, theStyles=[None], CPUlimit=-2)
	listPathFilenamesWorkbench: frozenset[Path] = valetCopiesToWorkbench(listPathFilenamesCID)

	listPathFilenamesSubsetCID: frozenset[Path] = subsetCID(subsetOptions, theStyles=[None], CPUlimit=-2)

	valetRemovesFiles(listPathFilenamesCID, next(iter(listPathFilenamesCID)).parent)
	valetRemovesFiles(listPathFilenamesWorkbench, settingsPackage.pathWorkbenchFonts)
	valetRemovesWorkbench()
