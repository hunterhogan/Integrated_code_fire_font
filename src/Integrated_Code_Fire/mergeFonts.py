# ruff: noqa: D103 D100
from concurrent.futures import as_completed, Future, ProcessPoolExecutor
from copy import copy
from fontTools import subset
from Integrated_Code_Fire import settingsPackage
from Integrated_Code_Fire.archivist import (
	dictionaryLocales, dictionaryWeights, getFilenameStem, getNameIDMetadata, updateFontFile)
from Integrated_Code_Fire.machineShop import machinistAppendsFont, machinistSubsetsOTF
from itertools import product as CartesianProduct
from tqdm import tqdm
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from fontTools.ttLib import TTFont
	from Integrated_Code_Fire import LocaleIn, WeightIn
	from pathlib import Path

def mergeFonts(fontFamilyOTC: str, dictionaryFontsScaled: dict[str, TTFont], workersMaximum: int = 1) -> list[Path]:
	listPathFilenames: list[Path] = []
	listClaimTickets: list[Future[None]] = []

	with ProcessPoolExecutor(workersMaximum) as concurrencyManager:

		for locale, style, weight in CartesianProduct(settingsPackage.listLocales, settingsPackage.listStyles, settingsPackage.listWeights):
			weightIn: WeightIn = dictionaryWeights[weight]
			localeIn: LocaleIn = dictionaryLocales[locale]
			ttFont: TTFont = copy(dictionaryFontsScaled[weightIn.FiraCode]) # NOTE This is one part of the flow that will prevent merging Italic.
			pathFilenameGids: Path = settingsPackage.pathRoot / fontFamilyOTC / 'metadata' / f"{getFilenameStem(fontFamilyOTC, localeIn.ascii, style)}.gids"
			gids: list[int] = list(map(int, pathFilenameGids.read_text('utf-8').splitlines()))
			pathFilenameUnicodes: Path = pathFilenameGids.with_suffix('.unicodes')
			unicodes: list[int] = subset.parse_unicodes(','.join(pathFilenameUnicodes.read_text('utf-8').splitlines()))
			pathFilenameOTC: Path = settingsPackage.pathWorkbenchFonts / f"{getFilenameStem(fontFamilyOTC, localeIn.ascii, style, weightIn.SourceHanMono)}.otf"
			pathFilenameWrite: Path = settingsPackage.pathWorkbenchFonts / f"{getFilenameStem(settingsPackage.filenameFontFamily, localeIn.IntegratedCode, style, weightIn.IntegratedCode, '')}.ttf"
			nameIDmetadata: dict[int, str] = getNameIDMetadata(weightIn.IntegratedCode, getFilenameStem(settingsPackage.filenameFontFamily, localeIn.IntegratedCode, separator=''), getFilenameStem(settingsPackage.fontFamily, localeIn.IntegratedCode, separator=' '))
			listClaimTickets.append(concurrencyManager.submit(_mf, ttFont, pathFilenameOTC, gids, unicodes, nameIDmetadata, pathFilenameWrite))
			listPathFilenames.append(pathFilenameWrite)

		for _claimTicket in tqdm(as_completed(listClaimTickets), total=len(listClaimTickets), desc = f"Merging fonts for {fontFamilyOTC}"):
			pass

	return listPathFilenames

def _mf(ttFont: TTFont, pathFilenameOTF: Path, gids: list[int], unicodes: list[int], nameIDmetadata: dict[int, str], pathFilenameWrite: Path) -> None:
	fontAppend: TTFont = machinistSubsetsOTF(pathFilenameOTF, gids, unicodes)

	machinistAppendsFont(ttFont, fontAppend)

	updateFontFile(ttFont, nameIDmetadata)

	ttFont.save(pathFilenameWrite)
	ttFont.close()
	fontAppend.close()
