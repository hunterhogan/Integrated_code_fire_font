"""Compile fonts from source files using fontmake and AFDKO makeotf.

You can compile fonts from Glyphs and CIDFont source files. The module compiles fonts from Glyphs source files using `fontmake`
[1] and compiles fonts from PostScript CIDFont source files using AFDKO `makeotf` [2]. The module uses `multiprocessing.Pool` [3]
for parallel compilation of multiple font variants.

Contents
--------
Functions
	smithy_makeotf
		Compile a single CID font variant using AFDKO makeotf.
	smithyCasts_afdko
		Compile all CID font variants across locales, weights, and styles.
	smithyCastsFromGlyphs
		Compile fonts in OTF and TTF formats from Glyphs source.
	smithyFontProject
		Compile fonts from Glyphs source in a specified format using fontmake.

References
----------
[1] fontmake - Google Fonts
	https://github.com/googlefonts/fontmake
[2] AFDKO (Adobe Font Development Kit for OpenType)
	https://adobe-type-tools.github.io/afdko/
[3] multiprocessing.Pool - Python Standard Library
	https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool

"""
from afdko.makeotf import main as afdko_makeotf
from fontmake.font_project import FontProject
from hunterMakesPy.parseParameters import defineConcurrencyLimit
from Integrated_Code_Fire import LocaleIn, settingsPackage, WeightIn
from Integrated_Code_Fire.archivist import archivistGetsLocales, archivistGetsWeights, archivistMakesFilenameStem, Z0Z_make_afdkoOptions
from itertools import product as CartesianProduct, repeat, starmap
from multiprocessing import Pool
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
	from collections.abc import Iterable, Iterator
	from pathlib import Path

def smithyCasts_afdko(pathRoot: Path, theLocales: Iterable[str], theStyles: Iterable[str | None], theWeights: Iterable[str], fontFamilyCID: str = 'SourceHanMono', *, CPUlimit: bool | float | int | None = 1) -> list[Path]:
	"""Compile all CID font variants across locales, weights, and styles.

	(AI generated docstring)

	You can compile multiple CID font variants in parallel using AFDKO `makeotf` [1]. The function generates AFDKO option
	tuples using `archivistMakesFilenameStem` [2] and `Z0Z_make_afdkoOptions` [2] for each combination of `theLocales`,
	`theStyles`, and `theWeights`. The function uses `multiprocessing.Pool` [3] to invoke `smithy_makeotf` in parallel
	for each variant, with concurrency controlled by `CPUlimit` processed through `defineConcurrencyLimit` [4].

	Parameters
	----------
	pathRoot : Path
		Root directory containing CIDFont source files.
	theLocales : Iterable[str]
		Locale identifiers for font variants to compile.
	theStyles : Iterable[str | None]
		Style identifiers for font variants to compile, where `None` represents upright/roman style.
	theWeights : Iterable[str]
		Weight identifiers for font variants to compile.
	fontFamilyCID : str = 'SourceHanMono'
		Font family name for CIDFont source files.
	CPUlimit : bool | float | int | None = 1
		Maximum concurrency limit passed to `defineConcurrencyLimit` [4].

	Returns
	-------
	listPathFilenames : list[Path]
		Paths to compiled OTF font files.

	Examples
	--------
	Invoked from chopShop to compile Source Han Mono variants:

	>>> from Integrated_Code_Fire.foundry import smithyCasts_afdko
	>>> from pathlib import Path
	>>> pathRootCID = Path('CID')
	>>> theLocales = ['Japan', 'Korea']
	>>> theStyles = [None, 'Italic']
	>>> theWeights = ['Regular', 'Bold']
	>>> frozenset(smithyCasts_afdko(pathRootCID, theLocales, theStyles, theWeights, 'SourceHanMono', CPUlimit=2))

	References
	----------
	[1] AFDKO (Adobe Font Development Kit for OpenType)
		https://adobe-type-tools.github.io/afdko/
	[2] Integrated_Code_Fire.archivist
	[3] multiprocessing.Pool - Python Standard Library
		https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool
	[4] hunterMakesPy.parseParameters.defineConcurrencyLimit - Context7
		https://context7.com/hunterhogan/huntermakespy

	"""
	workersMaximum: int = defineConcurrencyLimit(limit=CPUlimit)

	optionsValues: Iterator[tuple[str, ...]] = starmap(Z0Z_make_afdkoOptions, CartesianProduct([pathRoot], [fontFamilyCID], theLocales, theStyles, theWeights))

	dictionaryLocales: dict[str, LocaleIn] = archivistGetsLocales()
	dictionaryWeights: dict[str, WeightIn] = archivistGetsWeights()

	listPathFilenamesWrite: list[Path] = []

	pathWrite: Path = settingsPackage.pathWorkbench / fontFamilyCID
	pathWrite.mkdir(parents=True, exist_ok=True)
	for locale, style, weight in CartesianProduct(theLocales, theStyles, theWeights):
		filenameStemWrite: str = archivistMakesFilenameStem(fontFamilyCID, dictionaryLocales[locale].ascii, style, dictionaryWeights[weight].fontFamilyCID)
		pathFilenameWrite: Path = pathWrite / f"{filenameStemWrite}.otf"
		listPathFilenamesWrite.append(pathFilenameWrite)

	with Pool(processes=workersMaximum) as concurrencyManager:
		listPathFilenames: list[Path] = concurrencyManager.starmap(smithy_makeotf, zip(optionsValues, listPathFilenamesWrite, strict=True))

	return listPathFilenames

def smithy_makeotf(optionsValues: tuple[str, ...], pathFilenameWrite: Path) -> Path:
	"""Compile a single CID font variant using AFDKO makeotf.

	(AI generated docstring)

	You can compile a CID font by invoking AFDKO `makeotf` [1] with command-line options.

	Parameters
	----------
	optionsValues : tuple[str, ...]
		Command-line options for AFDKO makeotf, generated by `Z0Z_make_afdkoOptions` [2].
	pathFilenameWrite : Path
		Output path for compiled OTF font file.

	Returns
	-------
	pathFilenameWrite : Path
		Path to compiled OTF font file.

	References
	----------
	[1] AFDKO (Adobe Font Development Kit for OpenType)
		https://adobe-type-tools.github.io/afdko/
	[2] Integrated_Code_Fire.archivist.Z0Z_make_afdkoOptions
	"""
	pathFilenameWrite.parent.mkdir(parents=True, exist_ok=True)

	# TODO is this REALLY the only API? No class? No function?
	afdko_makeotf([
		*optionsValues
		, '-omitMacNames'
		, '-r'
		, '-nS'
		, '-ncn'
		, '-nshw'
		, '-o', str(pathFilenameWrite)
	])

	return pathFilenameWrite

def smithyCastsFromGlyphs(pathFilename: Path, workersMaximum: int = 2, fontFormats: Iterable[str] = frozenset(['otf', 'ttf'])) -> Path:
	"""Compile fonts in OTF and TTF formats from Glyphs source files.

	(AI generated docstring)

	You can compile fonts from a Glyphs source file by invoking `smithyFontProject` in parallel using `multiprocessing.Pool` [1].
	The function reads the Glyphs source file from `pathFilename`, compiles each format in `fontFormats` using separate worker
	processes, and writes compiled font files to directories under `settingsPackage.pathWorkbench` [2].

	Parameters
	----------
	pathFilename : Path
		Path to Glyphs source file.
	workersMaximum : int = 2
		Maximum number of parallel worker processes for compiling font formats.
	fontFormats : Iterable[str] = frozenset(['otf', 'ttf'])
		Output font formats to compile, where each format is either `'otf'` for OpenType CFF or `'ttf'` for TrueType.

	Returns
	-------
	pathWorkbench : Path
		Path to directory containing compiled font files.

	Examples
	--------
	Invoked from chopShop to compile Fira Code in TTF format:

	>>> from Integrated_Code_Fire.foundry import smithyCastsFromGlyphs
	>>> from pathlib import Path
	>>> pathFilenameGlyphs = Path('FiraCode.glyphs')
	>>> pathTTFont = smithyCastsFromGlyphs(pathFilenameGlyphs, 1, ['ttf'])

	References
	----------
	[1] multiprocessing.Pool - Python Standard Library
		https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool
	[2] Integrated_Code_Fire.settingsPackage
	[3] fontmake - Google Fonts
		https://github.com/googlefonts/fontmake
	"""
	with Pool(processes=workersMaximum) as concurrencyManager:
		listPaths: list[Path] = concurrencyManager.starmap(smithyFontProject, zip(repeat(pathFilename), fontFormats))
	return listPaths.pop()

def smithyFontProject(pathFilename: Path, fontFormat: Literal['otf', 'ttf']) -> Path:
	"""Compile fonts from Glyphs source in a specified output format.

	You can compile fonts from a Glyphs source file using `fontmake.font_project.FontProject` [1]. The function interpolates font
	instances, disables autohinting, and writes the compiled font files to an output directory under
	`settingsPackage.pathWorkbench` [2].

	Parameters
	----------
	pathFilename : Path
		Path to Glyphs source file.
	fontFormat : Literal['otf', 'ttf']
		Output font format, either `'otf'` for OpenType CFF or `'ttf'` for TrueType.

	Returns
	-------
	pathDirectory : Path
		Path to directory containing compiled font files.

	References
	----------
	[1] fontmake.font_project.FontProject - Google Fonts
		https://github.com/googlefonts/fontmake
	[2] Integrated_Code_Fire.settingsPackage
	"""
	output_dir: Path = settingsPackage.pathWorkbench / pathFilename.stem
	output_dir.mkdir(parents=True, exist_ok=True)
	FontProject().run_from_glyphs(
		glyphs_path=pathFilename
		, output=(fontFormat,)
		, output_dir=output_dir
		, interpolate=True
		, autohint=False
	)
	return output_dir

