"""Prepare western fonts and compile and subset CJK fonts for Integrated Code 火.

(AI generated docstring)

You can populate the warehouse with western fonts and CJK subsets ready to merge. Western
preparation applies configured character mappings and optional scaling. CJK preparation compiles
source fonts, retains the stored character selections, and adjusts horizontal spacing.

Contents
--------
Functions
	castCID
		Compile CJK source fonts for selected locales, styles, and weights.
	prepareGlyphs
		Store western fonts with the configured mappings and em size.
	subsetCID
		Store CJK subsets with TrueType or CFF outlines.
"""
from __future__ import annotations

from afdko.otf2ttf import otf_to_ttf
from concurrent.futures import as_completed, Future, ProcessPoolExecutor
from fontTools.ttLib import scaleUpem, TTFont
from hunterMakesPy.parseParameters import defineConcurrencyLimit
from Integrated_Code_Fire import (
	autohintOptionsDEFAULT, headFlagsIntegerPPEM, LocaleIn, PackageSettings, pathFilenameFiraCodeGlyphsDEFAULT, pathRootSourceHanMonoDEFAULT,
	settingsPackage, subsetOptionsDEFAULT, WeightIn)
from Integrated_Code_Fire.archivist import archivistGetsLocales, archivistGetsUnicodes, archivistGetsWeights, archivistMakesFilenameStem
from Integrated_Code_Fire.foundry import smithyCasts_afdko, smithyCastsFromGlyphs
from Integrated_Code_Fire.logistics import (
	valetCopiesToWorkbench, valetGetsWesternFontPathFilename, valetRemovesFiles, valetRemovesWorkbench)
from Integrated_Code_Fire.machineShop import machinistSubsetsCID
from Integrated_Code_Fire.qualityControl import checkAdvanceWidths, checkHan, checkWestern
from itertools import chain, product as CartesianProduct
from more_itertools import consume
from operator import attrgetter, methodcaller
from pathlib import Path
from tqdm import tqdm
from ttfautohint import ttfautohint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from collections.abc import Iterable
	from fontTools import subset
	from ttfautohint.options import UserOptions

def prepareGlyphs(listPathFilenamesTTFont: Iterable[Path], autohintOptions: UserOptions, *, CPUlimit: bool | float | int | None = 1) -> Iterable[Path]:
	"""Prepare western fonts with the configured character mappings and em size.

	(AI generated docstring)

	Parameters
	----------
	listPathFilenamesTTFont : Iterable[Path]
		Compiled western fonts. Input stems follow the source directory name and a hyphen, then
		the weight label; output filenames retain the weight label and extension.
	autohintOptions : UserOptions
		Keyword options for `ttfautohint.ttfautohint`, normally `autohintOptionsDEFAULT`.
	CPUlimit : bool | float | int | None = 1
		Accepted concurrency setting. Preparation remains sequential regardless of this value.

	Returns
	-------
	listPathFilenames : frozenset[Path]
		Prepared font paths under `warehouse/western` for an em size of `2000`, or under
		`warehouse/scaled` for another configured em size.

	See Also
	--------
	`Integrated_Code_Fire.logistics.valetGetsWesternFontPathFilename`
		Obtain the prepared paths for the active weights.

	Character Mappings
	------------------
	The western fonts receive `settingsPackage.cmapUpdates`. The supplied configuration maps
	U+22EF (`⋯`) to the existing `"ellipsis"` glyph, also used for U+2026 (`…`).

	Hinting
	-------
	`ttfautohint` hints each prepared font after the character mappings and em size change, so the
	hints describe the final outlines. Each font also sets `head.flags` bit 3, which forces integer
	ppem values, as hinted fonts require. Merging retains the hints of the first font only, so the
	western font must precede the CJK font in the merge.

	File Replacement
	----------------
	Prepared files with matching weight names are replaced. The input files are retained.

	Quality Control
	---------------
	`Integrated_Code_Fire.qualityControl.checkWestern` checks each saved font and writes its
	findings to standard output. The findings do not stop the build.
	"""
	_workersMaximum: int = defineConcurrencyLimit(limit=CPUlimit)

	listPathFilenames: Iterable[Path] = []

	if settingsPackage.unitsPerEm == 2000:
		pathWrite: Path = settingsPackage.pathWarehouse / 'western'
	else:
		pathWrite: Path = settingsPackage.pathWarehouse / 'scaled'
	pathWrite.mkdir(parents=True, exist_ok=True)

	for pathFilename in listPathFilenamesTTFont:
		ttFont: TTFont = TTFont(pathFilename)
		consume(map(methodcaller('update', settingsPackage.cmapUpdates), map(attrgetter('cmap'), ttFont['cmap'].tables)))
		if settingsPackage.unitsPerEm != 2000:
			scaleUpem.scale_upem(ttFont, settingsPackage.unitsPerEm)
		ttFont['head'].flags |= headFlagsIntegerPPEM
		weight: str = pathFilename.stem.removeprefix(f"{pathFilename.parent.name}-")
		pathFilenameWrite: Path = pathWrite / f"{weight}{pathFilename.suffix}"
		ttFont.save(pathFilenameWrite)
		ttfautohint(**(autohintOptions | {'in_file': pathFilenameWrite, 'out_file': pathFilenameWrite}))
		checkWestern(pathFilenameWrite)
		listPathFilenames.append(pathFilenameWrite)

	return frozenset(listPathFilenames)

def castCID(pathRootCID: Path, fontFamilyCID: str = 'SourceHanMono', theLocales: Iterable[str] | None = None, theStyles: Iterable[str | None] | None = None, theWeights: Iterable[str] | None = None, *, CPUlimit: bool | float | int | None = 1) -> frozenset[Path]:
	"""Compile CJK source fonts for selected locales, styles, and weights.

	(AI generated docstring)

	Parameters
	----------
	pathRootCID : Path
		Source checkout containing CID font source files, normally Source Han Mono.
	fontFamilyCID : str = 'SourceHanMono'
		Source family label used in filenames and compilation settings.
	theLocales : Iterable[str]
		Locale keys. Defaults to the locales in a fresh `PackageSettings`.
	theStyles : Iterable[str | None]
		Styles, with an element of `None` selecting upright style. Defaults to upright and
		italic styles in a fresh `PackageSettings`.
	theWeights : Iterable[str]
		Weight keys. Defaults to all seven weights in a fresh `PackageSettings`.
	CPUlimit : bool | float | int | None = 1
		Worker limit. Positive integers select workers; negative integers reserve CPUs.
		Fractions select proportions to use or reserve. `None`, `False`, and `0` use all CPUs;
		`True` selects one worker. The effective limit is at least one worker.

	Returns
	-------
	listPathFilenames : frozenset[Path]
		Compiled OTF font paths under `settingsPackage.pathWorkbench / fontFamilyCID`.

	See Also
	--------
	`subsetCID`
		Retain the required CJK characters after compilation and staging.
	`Integrated_Code_Fire.logistics.valetCopiesToWorkbench`
		Stage the compiled fonts where `subsetCID` expects them.

	Selection Defaults
	------------------
	Omitting any selection, or supplying `None`, enables class defaults for each omitted or
	empty selection. Nonempty supplied selections are retained. If all three selections are
	supplied, empty selections remain empty.

	File Replacement
	----------------
	The output directory is created and compiled fonts with matching filenames are replaced.
	"""
	workersMaximum: int = defineConcurrencyLimit(limit=CPUlimit)

	if (theLocales is None) or (theStyles is None) or (theWeights is None):
		settings = PackageSettings(settingsPackage.identifierPackage)
		theLocales = theLocales or settings.theLocales
		theStyles = theStyles or settings.theStyles
		theWeights = theWeights or settings.theWeights

	return frozenset(smithyCasts_afdko(pathRootCID, theLocales, theStyles, theWeights, fontFamilyCID, CPUlimit=workersMaximum))

def subsetCID(subsetOptions: subset.Options, fontFamilyCID: str = 'SourceHanMono'
			, theLocales: Iterable[str] | None = None, theStyles: Iterable[str | None] | None = None, theWeights: Iterable[str] | None = None
			, fontFormat: str = 'ttf', *, CPUlimit: bool | float | int | None = 1) -> frozenset[Path]:
	"""Store CJK font subsets with the selected characters and horizontal spacing.

	(AI generated docstring)

	You can prepare the CJK contribution to merged fonts. Each subset retains the characters that
	`Integrated_Code_Fire.archivist.archivistMakesUnicodesHan` selects from the font's own character
	map. The input fonts must already be staged in `settingsPackage.pathWorkbenchFonts`, and the
	prepared western fonts of the active weights must already be in the warehouse, because the CJK
	subsets omit every character that the western fonts map.

	Parameters
	----------
	subsetOptions : subset.Options
		FontTools options controlling retained glyphs, layout features, names, and tables.
	fontFamilyCID : str = 'SourceHanMono'
		Family label of the staged font filenames.
	theLocales : Iterable[str]
		Locale keys. Defaults to the locales in a fresh `PackageSettings`.
	theStyles : Iterable[str | None]
		Styles, with an element of `None` selecting upright style. Defaults to upright and
		italic styles in a fresh `PackageSettings`.
	theWeights : Iterable[str]
		Weight keys. Defaults to all seven weights in a fresh `PackageSettings`.
	fontFormat : {'ttf', 'otf'} = 'ttf'
		Output format, also the format of the prepared western fonts. `"otf"` retains CFF outlines;
		`"ttf"` converts to TrueType outlines.
	CPUlimit : bool | float | int | None = 1
		Worker limit. Positive integers select workers; negative integers reserve CPUs.
		Fractions select proportions to use or reserve. `None`, `False`, and `0` use all CPUs;
		`True` selects one worker. The effective limit is at least one worker.

	Returns
	-------
	listPathFilenames : frozenset[Path]
		Prepared subset paths under `settingsPackage.pathWarehouse / 'CID'`.

	See Also
	--------
	`castCID`
		Compile the CJK input fonts before staging and subsetting.
	`Integrated_Code_Fire.go.goMerge`
		Combine the prepared TrueType subsets with western fonts.

	Selection Defaults
	------------------
	Omitting any selection, or supplying `None`, enables class defaults for each omitted or
	empty selection. Nonempty supplied selections are retained. If all three selections are
	supplied, empty selections remain empty.

	File Replacement
	----------------
	The warehouse CJK directory is created and subset files with matching names are replaced.
	The staged input fonts are retained.
	"""
	if (theLocales is None) or (theStyles is None) or (theWeights is None):
		settings = PackageSettings(settingsPackage.identifierPackage)
		theLocales = theLocales or settings.theLocales
		theStyles = theStyles or settings.theStyles
		theWeights = theWeights or settings.theWeights

	unicodesWestern: frozenset[int] = frozenset(chain.from_iterable(map(archivistGetsUnicodes, valetGetsWesternFontPathFilename(fontFormat).values())))
	dictionaryLocales: dict[str, LocaleIn] = archivistGetsLocales()
	dictionaryWeights: dict[str, WeightIn] = archivistGetsWeights()

	pathCID: Path = settingsPackage.pathWarehouse / 'CID'
	pathCID.mkdir(parents=True, exist_ok=True)
	listClaimTickets: list[Future[Path]] = []
	listPathFilenames: list[Path] = []
	workersMaximum: int = defineConcurrencyLimit(limit=CPUlimit)

	if fontFormat == 'otf':
		functionSubsetCID = _cid
	else:
		functionSubsetCID = _cidTOttf

	with ProcessPoolExecutor(workersMaximum) as concurrencyManager:
		for locale, style, weight in CartesianProduct(theLocales, theStyles, theWeights):
			localeIn: LocaleIn = dictionaryLocales[locale]
			weightIn: WeightIn = dictionaryWeights[weight]

			listClaimTickets.append(concurrencyManager.submit(
					functionSubsetCID
					, settingsPackage.pathWorkbenchFonts / f"{archivistMakesFilenameStem(fontFamilyCID, localeIn.ascii, style, weightIn.fontFamilyCID)}.otf"
					, unicodesWestern
					, subsetOptions
					, pathCID / f"{archivistMakesFilenameStem(None, localeIn.ascii, style, weightIn.fontFamilyCID)}.{fontFormat}"
				))

		listPathFilenames.extend(claimTicket.result() for claimTicket in tqdm(as_completed(listClaimTickets), total=len(listClaimTickets), desc=f"Subsetting {fontFamilyCID}"))
	return frozenset(listPathFilenames)

def _cidTOttf(pathFilenameCID: Path, unicodesWestern: frozenset[int], subsetOptions: subset.Options, pathFilenameWrite: Path) -> Path:
	"""I use this worker to save a CJK subset with TrueType outlines and adjusted metrics.

	(AI generated docstring)

	Parameters
	----------
	pathFilenameCID : Path
		Staged CJK font with CFF outlines.
	unicodesWestern : frozenset[int]
		Code points of the western fonts, which the subset must not map.
	subsetOptions : subset.Options
		FontTools subsetting options.
	pathFilenameWrite : Path
		Destination TTF file in the prepared CJK warehouse.

	Returns
	-------
	pathFilenameWrite : Path
		Path to the saved font. The font is closed after saving.

	File Replacement
	----------------
	The output file is replaced with the subset. The outline conversion keeps the advance widths
	from CJK preparation and sets each left side bearing from the converted outline.

	Quality Control
	---------------
	`Integrated_Code_Fire.qualityControl.checkHan` checks the saved font and writes its findings to
	standard output. The findings do not stop the build.
	"""
	fontCID: TTFont = machinistSubsetsCID(pathFilenameCID, unicodesWestern, subsetOptions)
	otf_to_ttf(fontCID)
	fontCID.save(pathFilenameWrite)
	fontCID.close()
	checkHan(pathFilenameWrite)
	return pathFilenameWrite

def _cid(pathFilenameCID: Path, unicodesWestern: frozenset[int], subsetOptions: subset.Options, pathFilenameWrite: Path) -> Path:
	"""I use this worker to save a CJK subset while retaining CFF outlines.

	(AI generated docstring)

	Parameters
	----------
	pathFilenameCID : Path
		Staged CJK font with CFF outlines.
	unicodesWestern : frozenset[int]
		Code points of the western fonts, which the subset must not map.
	subsetOptions : subset.Options
		FontTools subsetting options.
	pathFilenameWrite : Path
		Destination OTF file in the prepared CJK warehouse.

	Returns
	-------
	pathFilenameWrite : Path
		Path to the saved font. The font is closed after saving.

	File Replacement
	----------------
	The output file is replaced with the subset and its adjusted horizontal metrics.

	Quality Control
	---------------
	`Integrated_Code_Fire.qualityControl.checkAdvanceWidths` checks the saved font and writes its
	findings to standard output. The findings do not stop the build.
	"""
	fontCID: TTFont = machinistSubsetsCID(pathFilenameCID, unicodesWestern, subsetOptions)
	fontCID.save(pathFilenameWrite)
	fontCID.close()
	checkAdvanceWidths(pathFilenameWrite, settingsPackage.width)
	return pathFilenameWrite

if __name__ == "__main__":
	fontFormat: str = 'ttf'
	CPUlimit: int = 1

	doGlyphs = True
	doCID = True
	doSubset = True
	doCleanUp = True

	listPathFilenamesTTFont: Iterable[Path] = frozenset()

	if doGlyphs:
		pathTTFont: Path | None = smithyCastsFromGlyphs(pathFilenameFiraCodeGlyphsDEFAULT, 1, [fontFormat])
		listPathFilenamesTTFont = pathTTFont.glob(f"*.{fontFormat}")
		prepareGlyphs(listPathFilenamesTTFont, autohintOptionsDEFAULT, CPUlimit=CPUlimit)
	else:
		pathTTFont = None

	if doCID:
		listPathFilenamesCID: frozenset[Path] = castCID(pathRootSourceHanMonoDEFAULT, theStyles=[None], CPUlimit=CPUlimit)
	else:
		listPathFilenamesCID = frozenset(Path('/apps/Integrated_Code_Fire/workbench/SourceHanMono').glob('*.otf'))

	if doSubset:
		listPathFilenamesWorkbench: frozenset[Path] = valetCopiesToWorkbench(listPathFilenamesCID)
		listPathFilenamesSubsetCID: frozenset[Path] = subsetCID(subsetOptionsDEFAULT, theStyles=[None], fontFormat=fontFormat, CPUlimit=CPUlimit)
	else:
		listPathFilenamesWorkbench: frozenset[Path] = frozenset()

	if doCleanUp:
		if pathTTFont:
			valetRemovesFiles(listPathFilenamesTTFont, pathTTFont)
		valetRemovesFiles(listPathFilenamesCID, next(iter(listPathFilenamesCID)).parent)
		valetRemovesFiles(listPathFilenamesWorkbench, settingsPackage.pathWorkbenchFonts)
		valetRemovesWorkbench()
