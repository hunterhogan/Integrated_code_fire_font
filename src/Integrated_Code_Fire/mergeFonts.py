"""Orchestrate parallel font merging for all locale, style, and weight combinations.

(AI generated docstring)

You can use this module to merge scaled Fira Code fonts with subsetted Source Han Mono fonts for all combinations of locales,
styles, and weights. The module uses `concurrent.futures.ProcessPoolExecutor` [1] to parallelize font merging operations and
produces TrueType font files with updated OpenType metadata.

Contents
--------
Functions
	mergeFonts
		Merge scaled Fira Code fonts with subsetted Source Han Mono fonts for all locale, style, and weight combinations.

References
----------
[1] concurrent.futures.ProcessPoolExecutor - Python Standard Library
	https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ProcessPoolExecutor
[2] fontTools.ttLib.TTFont
	https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html
[3] Integrated_Code_Fire.go.go
	Internal package reference.

"""
from concurrent.futures import as_completed, Future, ProcessPoolExecutor
from copy import copy
from Integrated_Code_Fire import settingsPackage
from Integrated_Code_Fire.archivist import (
	archivistGetsLocales, archivistGetsSubsetCharacters, archivistGetsWeights, archivistMakesFilenameStem,
	archivistMakesNameIDMetadata, archivistUpdatesMetadata)
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

def mergeFonts(fontFamilyCID: str, dictionaryFontsScaled: dict[str, TTFont], workersMaximum: int = 1) -> frozenset[Path]:
	"""Merge scaled Fira Code fonts with subsetted Source Han Mono fonts for all locale, style, and weight combinations.

	(AI generated docstring)

	You can use this function to create the merged Integrated Code 火 font files. The function loads character subset definitions,
	creates copies of scaled Fira Code fonts, subsets Source Han Mono fonts for each locale and style combination, merges the
	fonts, updates OpenType metadata, recalculates font metrics, and writes the result to disk. The function uses
	`concurrent.futures.ProcessPoolExecutor` [1] to parallelize merging operations across all locale, style, and weight
	combinations.

	Parameters
	----------
	fontFamilyCID : str
		CID font family identifier, typically `'SourceHanMono'`.
	dictionaryFontsScaled : dict[str, TTFont]
		Mapping from weight identifier to scaled Fira Code `TTFont` [2] instance.
	workersMaximum : int = 1
		Maximum number of parallel worker processes for merging operations.

	Returns
	-------
	listPathFilenames : frozenset[Path]
		Frozen set of paths to merged TrueType font files.

	References
	----------
	[1] concurrent.futures.ProcessPoolExecutor - Python Standard Library
		https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ProcessPoolExecutor
	[2] fontTools.ttLib.TTFont
		https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html
	[3] Integrated_Code_Fire.go.go
		Internal package reference.

	"""
	listPathFilenames: list[Path] = []
	listClaimTickets: list[Future[Path]] = []

	subsetCharacters: dict[identifierDotAttribute, dict[str, list[int]]] = archivistGetsSubsetCharacters()
	dictionaryLocales: dict[str, LocaleIn] = archivistGetsLocales()
	dictionaryWeights: dict[str, WeightIn] = archivistGetsWeights()

	with ProcessPoolExecutor(workersMaximum) as concurrencyManager:

		for locale, style, weight in CartesianProduct(settingsPackage.theLocales, settingsPackage.theStyles, settingsPackage.theWeights):
			localeIn: LocaleIn = dictionaryLocales[locale]
			weightIn: WeightIn = dictionaryWeights[weight]

			lookupIDs: identifierDotAttribute = archivistMakesFilenameStem(fontFamilyCID, localeIn.ascii, style)

			listClaimTickets.append(concurrencyManager.submit(
				_mf
				, copy(dictionaryFontsScaled[weightIn.FiraCode])
				, settingsPackage.pathWorkbenchFonts / f"{archivistMakesFilenameStem(fontFamilyCID, localeIn.ascii, style, weightIn.fontFamilyCID)}.otf"
				, subsetCharacters[lookupIDs]['gids']
				, subsetCharacters[lookupIDs]['unicodes']
				, archivistMakesNameIDMetadata(weightIn.IntegratedCode火, archivistMakesFilenameStem(settingsPackage.filenameFontFamily, localeIn.IntegratedCode火, separator=''), archivistMakesFilenameStem(settingsPackage.fontFamily, localeIn.IntegratedCode火, separator=' '))
				, settingsPackage.pathWorkbenchFonts / f"{archivistMakesFilenameStem(settingsPackage.filenameFontFamily, localeIn.IntegratedCode火, style, weightIn.IntegratedCode火, '')}.ttf"
			))

		for claimTicket in tqdm(as_completed(listClaimTickets), total=len(listClaimTickets), desc = f"Merging fonts for {fontFamilyCID}"):
			listPathFilenames.append(claimTicket.result())  # noqa: PERF401

	return frozenset(listPathFilenames)

def _mf(ttFont: TTFont, pathFilenameCID: Path, gids: list[int], unicodes: list[int], nameIDmetadata: dict[int, str], pathFilenameWrite: Path) -> Path:
	fontCID: TTFont = machinistSubsetsCID(pathFilenameCID, gids, unicodes)

	machinistAppendsFont(ttFont, fontCID)
	fontCID.close()

	archivistUpdatesMetadata(ttFont, nameIDmetadata)

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
