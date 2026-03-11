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
[4] Integrated_Code_Fire.go.go
	Internal package reference.

"""
from afdko.makeotf import main as afdko_makeotf
from fontmake.font_project import FontProject
from hunterMakesPy.parseParameters import defineConcurrencyLimit
from Integrated_Code_Fire import LocaleIn, settingsPackage, WeightIn
from Integrated_Code_Fire.archivist import (
	archivistGetsLocales, archivistGetsWeights, archivistMakesFilenameStem, Z0Z_makeSourceHanMonoOptions)
from itertools import product as CartesianProduct, repeat, starmap
from multiprocessing import Pool
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
	from collections.abc import Iterable, Iterator
	from pathlib import Path

def smithyCasts_afdko(pathRoot: Path, theLocales: Iterable[str], theStyles: Iterable[str | None], theWeights: Iterable[str], fontFamilyCID: str = 'SourceHanMono', *, CPUlimit: bool | float | int | None = 1) -> list[Path]:
	workersMaximum: int = defineConcurrencyLimit(limit=CPUlimit)

	optionsValues: Iterator[tuple[str, ...]] = starmap(Z0Z_makeSourceHanMonoOptions, CartesianProduct([pathRoot], [fontFamilyCID], theLocales, theStyles, theWeights))

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
	pathFilenameWrite.parent.mkdir(parents=True, exist_ok=True)

# TODO is this REALLY the only API? No class? No function?
	afdko_makeotf([
		*optionsValues
		, '-omitMacNames'
		, '-r'
		, '-nS'
		, '-ncn'
		, '-gs'
		, '-o', str(pathFilenameWrite)
	])

	return pathFilenameWrite

def smithyCastsFromGlyphs(pathFilename: Path, workersMaximum: int = 2, fontFormats: Iterable[str] = frozenset(['otf', 'ttf'])) -> Path:
	"""Compile fonts in OTF and/or TTF formats from Glyphs source files.

	You can compile fonts from a Glyphs source file by invoking `smithyFontProject` in parallel using `multiprocessing.Pool` [1].
	The function reads the Glyphs source file from `pathFilename` and writes compiled font files to `pathWorkbenchFonts`.

	Parameters
	----------
	workersMaximum : int = 2
		Maximum number of parallel worker processes for compiling font formats.

	Returns
	-------
	listPaths : list[Path]
		List of paths to compiled font files.

	Examples
	--------
	Invoked by `go` [3] as the first step in the assembly line:

	>>> from Integrated_Code_Fire.foundry import smithyCastsFiraCode
	>>> smithyCastsFiraCode()

	Invoked directly in the `__main__` block:

	>>> if __name__ == '__main__':
	...     smithyCastsFiraCode()

	References
	----------
	[1] multiprocessing.Pool - Python Standard Library
		https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool
	[2] fontmake - Read the Docs
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
		Internal package reference.

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

