# ruff: noqa: D103 D100
from concurrent.futures import as_completed, Future, ProcessPoolExecutor
from copy import copy
from Integrated_Code_Fire import settingsPackage
from Integrated_Code_Fire.archivist import dictionaryWeights, getFilenameStem
from Integrated_Code_Fire.machineShop import machinistAppendsFont, machinistSubsetsOTF
from itertools import product as CartesianProduct
from tqdm import tqdm
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from fontTools.ttLib import TTFont
	from Integrated_Code_Fire import WeightIn
	from pathlib import Path

def mergeFonts(fontFamily: str, dictionaryFontsScaled: dict[str, TTFont], workersMaximum: int = 1) -> list[Path]:
	listPathFilename: list[Path] = []
	listClaimTickets: list[Future[None]] = []

	with ProcessPoolExecutor(workersMaximum) as concurrencyManager:

		for locale, style, weight in CartesianProduct(settingsPackage.listLocales, settingsPackage.listStyles, settingsPackage.listWeights):
			weightIn: WeightIn = dictionaryWeights[weight]
			ttFont: TTFont = copy(dictionaryFontsScaled[weightIn.FiraCode]) # NOTE This is one part of the flow that will prevent merging Italic.
			pathFilenameGids: Path = settingsPackage.pathRoot / fontFamily / 'metadata' / f"{getFilenameStem(fontFamily, locale, style)}.gids"
			gids: list[int] = list(map(int, pathFilenameGids.read_text('utf-8').splitlines()))
			pathFilenameOTC: Path = settingsPackage.pathWorkbenchFonts / f"{fontFamily}.{locale}.{weightIn.SourceHanMono}.otf"
			pathFilenameWrite: Path = settingsPackage.pathWorkbenchFonts / f"{settingsPackage.filenameFontFamilyLocale简化字}{weightIn.IntegratedCode}.ttf"
			listClaimTickets.append(concurrencyManager.submit(_mf, ttFont, pathFilenameOTC, gids, pathFilenameWrite))
			listPathFilename.append(pathFilenameWrite)

		for _claimTicket in tqdm(as_completed(listClaimTickets), total=len(listClaimTickets), desc = f"Merging fonts for {fontFamily}"):
			pass

	return listPathFilename

def _mf(ttFont: TTFont, pathFilenameOTF: Path, gids: list[int], pathFilenameWrite: Path) -> None:
	fontAppend: TTFont = machinistSubsetsOTF(pathFilenameOTF, gids)

	machinistAppendsFont(ttFont, fontAppend)

	ttFont.save(pathFilenameWrite)
	ttFont.close()
	fontAppend.close()
