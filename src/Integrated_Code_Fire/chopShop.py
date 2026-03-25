"""Compile Fira Code glyphs and compile and subset Source Han Mono CID fonts for the Integrated Code 火 assembly line.

(AI generated docstring)

You can use this module to prepare and subset the font files that feed into the merge step of the Integrated Code 火 assembly
line. The module compiles Fira Code from a Glyphs source file [7] and scales the result to the target units-per-em value,
compiles Source Han Mono [8] from CIDFont source using AFDKO [5], and subsets the compiled CID fonts to locale-specific glyph
IDs and Unicode ranges before merging.

Contents
--------
Functions
	castCID
		Compile Source Han Mono OTF fonts from CIDFont source for all locale, style, and weight combinations.
	prepareGlyphs
		Compile and scale a Fira Code Glyphs source file and save scaled fonts to the warehouse.
	subsetCID
		Subset compiled CID fonts to locale-specific glyph IDs and Unicode ranges.

References
----------
[1] Integrated_Code_Fire.foundry
	Internal package reference.
[2] Integrated_Code_Fire.machineShop
	Internal package reference.
[3] Integrated_Code_Fire.logistics
	Internal package reference.
[4] fontTools
	https://fonttools.readthedocs.io/en/latest/
[5] AFDKO (Adobe Font Development Kit for OpenType)
	https://adobe-type-tools.github.io/afdko/
[6] hunterMakesPy
	https://context7.com/hunterhogan/huntermakespy
[7] Fira Code - GitHub
	https://github.com/tonsky/FiraCode
[8] Source Han Mono - Adobe Fonts
	https://github.com/adobe-fonts/source-han-mono

"""
from afdko.otf2ttf import otf_to_ttf
from concurrent.futures import as_completed, Future, ProcessPoolExecutor
from hunterMakesPy.parseParameters import defineConcurrencyLimit
from Integrated_Code_Fire import (
	LocaleIn, PackageSettings, pathFilenameFiraCodeGlyphsDEFAULT, pathRootSourceHanMonoDEFAULT, settingsPackage, subsetOptionsDEFAULT,
	WeightIn)
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

def prepareGlyphs(pathFilenameGlyphs: Path, fontFormat: str = 'ttf') -> None:
	"""Compile and scale a Fira Code Glyphs source file and save scaled fonts to the warehouse.

	(AI generated docstring)

	You can compile fonts from the Glyphs source file at `pathFilenameGlyphs` using `smithyCastsFromGlyphs` [1], scale the
	compiled fonts to the target units-per-em value using `machinistScalesFonts` [2], and save the scaled fonts to
	`settingsPackage.pathWarehouse / 'scaled'`. The function removes the intermediate compiled font file using
	`valetRemovesFiles` [3] after scaling, then cleans up the workbench using `valetRemovesWorkbench` [4].

	Parameters
	----------
	pathFilenameGlyphs : Path
		Path to the Glyphs source file to compile.
	fontFormat : str = 'ttf'
		Font format to compile and scale. Use 'ttf' for TrueType outlines or 'otf' for PostScript CFF outlines.

	Examples
	--------
	Invoked in the `__main__` block using the default Fira Code path and 'ttf' format:

	>>> from Integrated_Code_Fire.chopShop import prepareGlyphs
	>>> from Integrated_Code_Fire import pathFilenameFiraCodeGlyphsDEFAULT
	>>> prepareGlyphs(pathFilenameFiraCodeGlyphsDEFAULT, 'ttf')

	References
	----------
	[1] Integrated_Code_Fire.foundry.smithyCastsFromGlyphs
		Internal package reference.
	[2] Integrated_Code_Fire.machineShop.machinistScalesFonts
		Internal package reference.
	[3] Integrated_Code_Fire.logistics.valetRemovesFiles
		Internal package reference.
	[4] Integrated_Code_Fire.logistics.valetRemovesWorkbench
		Internal package reference.
	"""
	pathTTFont: Path = smithyCastsFromGlyphs(pathFilenameGlyphs, 1, [fontFormat])

	dictionaryFontsScaled: dict[str, TTFont] = machinistScalesFonts(pathTTFont, f"*.{fontFormat}")
	valetRemovesFiles(pathRemove=pathTTFont)

	pathScaled: Path = settingsPackage.pathWarehouse / 'scaled'
	pathScaled.mkdir(parents=True, exist_ok=True)
	for weight, ttFont in dictionaryFontsScaled.items():
		ttFont.save(pathScaled / f"{weight}.{fontFormat}")

	valetRemovesWorkbench()

def castCID(pathRootCID: Path, fontFamilyCID: str = 'SourceHanMono', theLocales: Iterable[str] | None = None, theStyles: Iterable[str | None] | None = None, theWeights: Iterable[str] | None = None, *, CPUlimit: bool | float | int | None = 1) -> frozenset[Path]:
	"""Compile Source Han Mono OTF fonts from CIDFont source for all locale, style, and weight combinations.

	(AI generated docstring)

	You can compile Source Han Mono OTF fonts by invoking `smithyCasts_afdko` [1] with the Cartesian product of `theLocales`,
	`theStyles`, and `theWeights`. When any of `theLocales`, `theStyles`, or `theWeights` is `None`, the function reads all
	three from `PackageSettings` [2]. Concurrency is bounded by `CPUlimit` using `defineConcurrencyLimit` [3].

	Parameters
	----------
	pathRootCID : Path
		Root directory containing CIDFont source files.
	fontFamilyCID : str = 'SourceHanMono'
		CIDFont family name used to locate source files and name output files.
	theLocales : Iterable[str] | None = None
		Locale identifiers to compile, or `None` to use the full locale set from `PackageSettings`.
	theStyles : Iterable[str | None] | None = None
		Style identifiers to compile, or `None` to use the full style set from `PackageSettings`. A `None` value within the
		iterable represents the upright (non-italic) style.
	theWeights : Iterable[str] | None = None
		Weight identifiers to compile, or `None` to use the full weight set from `PackageSettings`.
	CPUlimit : bool | float | int | None = 1
		Concurrency limit passed to `defineConcurrencyLimit` [3].

	Returns
	-------
	listPathFilenamesCID : frozenset[Path]
		Paths to the compiled OTF font files written to the workbench.

	Examples
	--------
	Invoked in the `__main__` block using the default Source Han Mono path and upright style only:

	>>> from Integrated_Code_Fire.chopShop import castCID
	>>> from Integrated_Code_Fire import pathRootSourceHanMonoDEFAULT
	>>> listPathFilenamesCID = castCID(pathRootSourceHanMonoDEFAULT, theStyles=[None], CPUlimit=-2)

	References
	----------
	[1] Integrated_Code_Fire.foundry.smithyCasts_afdko
		Internal package reference.
	[2] Integrated_Code_Fire.PackageSettings
		Internal package reference.
	[3] hunterMakesPy.parseParameters.defineConcurrencyLimit
		https://context7.com/hunterhogan/huntermakespy
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
	"""Subset compiled CID fonts to locale-specific glyph IDs and Unicode ranges.

	(AI generated docstring)

	You can subset Source Han Mono OTF fonts to locale-specific glyph IDs and Unicode codepoints using character subset
	definitions loaded by `archivistGetsSubsetCharacters` [1]. The function dispatches parallel subset tasks to
	`ProcessPoolExecutor` [2]: each task calls `_cidTOttf` [3] when `fontFormat` is 'ttf', or `_cid` [4] when `fontFormat`
	is 'otf'. Subset output files are written to `settingsPackage.pathWarehouse / 'CID'`. When any of `theLocales`,
	`theStyles`, or `theWeights` is `None`, the function reads all three from `PackageSettings` [5].

	Parameters
	----------
	subsetOptions : subset.Options
		fontTools subset options controlling which OpenType tables are dropped and how name and cmap entries are handled [6].
	fontFamilyCID : str = 'SourceHanMono'
		CIDFont family name used to locate input files and character subset data.
	theLocales : Iterable[str] | None = None
		Locale identifiers to process, or `None` to use the full locale set from `PackageSettings`.
	theStyles : Iterable[str | None] | None = None
		Style identifiers to process, or `None` to use the full style set from `PackageSettings`. A `None` value within the
		iterable represents the upright (non-italic) style.
	theWeights : Iterable[str] | None = None
		Weight identifiers to process, or `None` to use the full weight set from `PackageSettings`.
	fontFormat : str = 'ttf'
		Output font format. Use 'ttf' to subset and convert to TrueType outlines, or 'otf' to keep PostScript CFF outlines.
	CPUlimit : bool | float | int | None = 1
		Concurrency limit passed to `defineConcurrencyLimit` [7].

	Returns
	-------
	listPathFilenamesSubset : frozenset[Path]
		Paths to the subset output font files written to `settingsPackage.pathWarehouse / 'CID'`.

	Examples
	--------
	Invoked in the `__main__` block using default subset options, upright style only, and TTF format:

	>>> from Integrated_Code_Fire.chopShop import subsetCID
	>>> from Integrated_Code_Fire import subsetOptionsDEFAULT
	>>> listPathFilenamesSubsetCID = subsetCID(subsetOptionsDEFAULT, theStyles=[None], fontFormat='ttf', CPUlimit=-2)

	References
	----------
	[1] Integrated_Code_Fire.archivist.archivistGetsSubsetCharacters
		Internal package reference.
	[2] concurrent.futures.ProcessPoolExecutor - Python Standard Library
		https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ProcessPoolExecutor
	[3] Integrated_Code_Fire.chopShop._cidTOttf
		Internal package reference.
	[4] Integrated_Code_Fire.chopShop._cid
		Internal package reference.
	[5] Integrated_Code_Fire.PackageSettings
		Internal package reference.
	[6] fontTools.subset.Options
		https://fonttools.readthedocs.io/en/latest/subset/index.html
	[7] hunterMakesPy.parseParameters.defineConcurrencyLimit
		https://context7.com/hunterhogan/huntermakespy
	"""
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

	if fontFormat == 'otf':
		functionSubsetCID = _cid
	else:
		functionSubsetCID = _cidTOttf

	with ProcessPoolExecutor(workersMaximum) as concurrencyManager:
		for locale, style, weight in CartesianProduct(theLocales, theStyles, theWeights):
			localeIn: LocaleIn = dictionaryLocales[locale]
			weightIn: WeightIn = dictionaryWeights[weight]

			lookupIDs: identifierDotAttribute = archivistMakesFilenameStem(fontFamilyCID, localeIn.ascii, style)

			listClaimTickets.append(concurrencyManager.submit(
					functionSubsetCID
					, settingsPackage.pathWorkbenchFonts / f"{archivistMakesFilenameStem(fontFamilyCID, localeIn.ascii, style, weightIn.fontFamilyCID)}.otf"
					, subsetCharacters[lookupIDs]['gids']
					, subsetCharacters[lookupIDs]['unicodes']
					, subsetOptions
					, pathCID / f"{archivistMakesFilenameStem(None, localeIn.ascii, style, weightIn.fontFamilyCID)}.{fontFormat}"
				))

		for claimTicket in tqdm(as_completed(listClaimTickets), total=len(listClaimTickets), desc = f"Subsetting {fontFamilyCID}"):
			listPathFilenames.append(claimTicket.result())  # noqa: PERF401
	return frozenset(listPathFilenames)

def _cidTOttf(pathFilenameCID: Path, gids: list[int], unicodes: list[int], subsetOptions: subset.Options, pathFilenameWrite: Path) -> Path:
	"""I use this worker to subset an OTF CIDFont and convert the result to TrueType outlines.

	I use this as a parallel worker function dispatched by `subsetCID` [1] via `ProcessPoolExecutor`. The function calls
	`machinistSubsetsCID` [2] to subset the font, then calls `otf_to_ttf` [3] to convert PostScript CFF outlines to
	TrueType outlines, saves the font to `pathFilenameWrite`, and returns `pathFilenameWrite`.

	Parameters
	----------
	pathFilenameCID : Path
		Path to the input OTF CIDFont file.
	gids : list[int]
		Glyph IDs to keep in the subset.
	unicodes : list[int]
		Unicode codepoints to keep in the subset.
	subsetOptions : subset.Options
		fontTools subset options.
	pathFilenameWrite : Path
		Destination path for the output TTF file.

	Returns
	-------
	pathFilenameWrite : Path
		Path to the written TTF output file.

	References
	----------
	[1] Integrated_Code_Fire.chopShop.subsetCID
		Internal package reference.
	[2] Integrated_Code_Fire.machineShop.machinistSubsetsCID
		Internal package reference.
	[3] afdko.otf2ttf.otf_to_ttf
		https://adobe-type-tools.github.io/afdko/
	"""
	fontCID: TTFont = machinistSubsetsCID(pathFilenameCID, gids, unicodes, subsetOptions)
	otf_to_ttf(fontCID)
	fontCID.save(pathFilenameWrite)
	fontCID.close()
	return pathFilenameWrite

def _cid(pathFilenameCID: Path, gids: list[int], unicodes: list[int], subsetOptions: subset.Options, pathFilenameWrite: Path) -> Path:
	"""I use this worker to subset an OTF CIDFont and save the result in OTF format.

	I use this as a parallel worker function dispatched by `subsetCID` [1] via `ProcessPoolExecutor`. The function calls
	`machinistSubsetsCID` [2] to subset the font, saves the font to `pathFilenameWrite`, and returns `pathFilenameWrite`.

	Parameters
	----------
	pathFilenameCID : Path
		Path to the input OTF CIDFont file.
	gids : list[int]
		Glyph IDs to keep in the subset.
	unicodes : list[int]
		Unicode codepoints to keep in the subset.
	subsetOptions : subset.Options
		fontTools subset options.
	pathFilenameWrite : Path
		Destination path for the output OTF file.

	Returns
	-------
	pathFilenameWrite : Path
		Path to the written OTF output file.

	References
	----------
	[1] Integrated_Code_Fire.chopShop.subsetCID
		Internal package reference.
	[2] Integrated_Code_Fire.machineShop.machinistSubsetsCID
		Internal package reference.
	"""
	fontCID: TTFont = machinistSubsetsCID(pathFilenameCID, gids, unicodes, subsetOptions)
	fontCID.save(pathFilenameWrite)
	fontCID.close()
	return pathFilenameWrite

if __name__ == "__main__":
	fontFormat: str = 'ttf'

	if doThis := True:
		prepareGlyphs(pathFilenameFiraCodeGlyphsDEFAULT, fontFormat)

	if doThis := True:
		listPathFilenamesCID: frozenset[Path] = castCID(pathRootSourceHanMonoDEFAULT, theStyles=[None], CPUlimit=-2)
	else:
		listPathFilenamesCID = frozenset(Path('/apps/Integrated_Code_Fire/workbench/SourceHanMono').glob('*.otf'))

	if doThis := True:
		listPathFilenamesWorkbench: frozenset[Path] = valetCopiesToWorkbench(listPathFilenamesCID)
		listPathFilenamesSubsetCID: frozenset[Path] = subsetCID(subsetOptionsDEFAULT, theStyles=[None], fontFormat=fontFormat, CPUlimit=-2)

	if cleanUp := True:
		valetRemovesFiles(listPathFilenamesCID, next(iter(listPathFilenamesCID)).parent)
		valetRemovesFiles(listPathFilenamesWorkbench, settingsPackage.pathWorkbenchFonts)
		valetRemovesWorkbench()
