from concurrent.futures import as_completed, Future, ProcessPoolExecutor
from copy import copy
from Integrated_Code_Fire import settingsPackage
from Integrated_Code_Fire.archivist import (
	getDictionaryLocales, getDictionaryWeights, getFilenameStem, getNameIDMetadata, getSubsetCharacters, updateMetadata)
from Integrated_Code_Fire.machineShop import machinistAppendsFont, machinistSubsetsCID
from itertools import product as CartesianProduct
from tqdm import tqdm
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from fontTools.ttLib import TTFont
	from hunterMakesPy import identifierDotAttribute
	from Integrated_Code_Fire import LocaleIn, WeightIn
	from pathlib import Path

# NOTE As the package flow improves, this module will be adsorbed or evolve. Either way, the module name ought not to be permanent.

def mergeFonts(fontFamilyCID: str, dictionaryFontsScaled: dict[str, TTFont], workersMaximum: int = 1) -> list[Path]:
	listPathFilenames: list[Path] = []
	listClaimTickets: list[Future[Path]] = []

	subsetCharacters: dict[identifierDotAttribute, dict[str, list[int]]] = getSubsetCharacters()
	dictionaryLocales: dict[str, LocaleIn] = getDictionaryLocales()
	dictionaryWeights: dict[str, WeightIn] = getDictionaryWeights()

	with ProcessPoolExecutor(workersMaximum) as concurrencyManager:

		for locale, style, weight in CartesianProduct(settingsPackage.theLocales, settingsPackage.theStyles, settingsPackage.theWeights):
			localeIn: LocaleIn = dictionaryLocales[locale]
			weightIn: WeightIn = dictionaryWeights[weight]

			lookupIDs: identifierDotAttribute = getFilenameStem(fontFamilyCID, localeIn.ascii, style)

			listClaimTickets.append(concurrencyManager.submit(_mf
				, copy(dictionaryFontsScaled[weightIn.FiraCode])
				, settingsPackage.pathWorkbenchFonts / f"{getFilenameStem(fontFamilyCID, localeIn.ascii, style, weightIn.fontFamilyCID)}.otf"
				, subsetCharacters[lookupIDs]['gids']
				, subsetCharacters[lookupIDs]['unicodes']
				, getNameIDMetadata(weightIn.IntegratedCode火, getFilenameStem(settingsPackage.filenameFontFamily, localeIn.IntegratedCode火, separator=''), getFilenameStem(settingsPackage.fontFamily, localeIn.IntegratedCode火, separator=' '))
				, settingsPackage.pathWorkbenchFonts / f"{getFilenameStem(settingsPackage.filenameFontFamily, localeIn.IntegratedCode火, style, weightIn.IntegratedCode火, '')}.ttf"
			))

		for claimTicket in tqdm(as_completed(listClaimTickets), total=len(listClaimTickets), desc = f"Merging fonts for {fontFamilyCID}"):
			listPathFilenames.append(claimTicket.result())  # noqa: PERF401

	return listPathFilenames

def _mf(ttFont: TTFont, pathFilenameCID: Path, gids: list[int], unicodes: list[int], nameIDmetadata: dict[int, str], pathFilenameWrite: Path) -> Path:
	fontCID: TTFont = machinistSubsetsCID(pathFilenameCID, gids, unicodes)

	machinistAppendsFont(ttFont, fontCID)
	fontCID.close()

	updateMetadata(ttFont, nameIDmetadata)

# TODO I'm still deeply skeptical that ALL of the following are true:
	# `fontTools.subset.Subsetter` didn't already do this.
	# `afdko.otf2ttf.otf_to_ttf` didn't already do this.
	# `ttFont.save` doesn't automatically do this.
	# There isn't a better method or function.
	# The parameters are correct.
	# These are the ONLY computations I must/should manually trigger in ALL tables and TTFont properties.
	ttFont['OS/2'].recalcAvgCharWidth(ttFont)
	ttFont['OS/2'].recalcUnicodeRanges(ttFont)
	ttFont['OS/2'].recalcCodePageRanges(ttFont)

	ttFont.save(pathFilenameWrite)
	ttFont.close()

	return pathFilenameWrite
