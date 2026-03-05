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
from Integrated_Code_Fire import settingsPackage
from Integrated_Code_Fire.archivist import archivistMakesFilenameStem, lookupAFDKOCharacterSet
from itertools import product as CartesianProduct, repeat
from multiprocessing import Pool
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
	from collections.abc import Iterable
	from pathlib import Path

def smithyCasts_afdko(fontFamilyCID: str = 'SourceHanMono', workersMaximum: int = 1) -> list[Path]:
	"""Compile all `fontFamilyCID` font variants across the locales, weights, and styles set in `settingsPackage`.

	The function uses `multiprocessing.Pool.starmap` [1] to invoke `smithy_makeotf` for each variant in parallel.

	Parameters
	----------
	workersMaximum : int = 1
		Maximum number of parallel worker processes for compiling font variants.

	Returns
	-------
	listPathFilename : list[Path]
		List of paths to compiled font files.

	References
	----------
	[1] multiprocessing.Pool.starmap - Python Standard Library
		https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool.starmap
	[2] AFDKO makeotf - Read the Docs
		https://adobe-type-tools.github.io/afdko/AFDKO-Overview.html#makeotf
	[3] itertools.product - Python Standard Library
		https://docs.python.org/3/library/itertools.html#itertools.product

	"""
	with Pool(processes=workersMaximum) as concurrencyManager:
		listPathFilename: list[Path] = concurrencyManager.starmap(smithy_makeotf
			, CartesianProduct([fontFamilyCID], settingsPackage.theLocales, settingsPackage.theStyles, settingsPackage.theWeights))

	return listPathFilename

def smithy_makeotf(fontFamilyCID: str, locale: str, style: Literal['Italic'] | None = None, weight: str = 'Regular') -> Path:
	"""Compile a single `fontFamilyCID` font variant using AFDKO makeotf.

	You can compile a `fontFamilyCID` font file for a specified locale, weight, and style using AFDKO `makeotf` [1]. The
	function constructs file paths for the PostScript CIDFont source file, OpenType features file, CID font info file, character
	set mappings, Unicode sequences, and font menu name database. The function writes the compiled OpenType font file to
	`pathWorkbench` [2] in a subdirectory named `'fontFamilyCID'`.

	Parameters
	----------
	locale : str
		Font locale defined in `lookupAFDKOCharacterSet`.
	weight : str = 'Regular'
		Font weight defined in the source files for `fontFamilyCID`.
	style : Literal['Italic'] | None = None
		Font style defined in the source files for `fontFamilyCID` or `None` for upright.

	Returns
	-------
	pathFilename : Path
		Path to the compiled OpenType font file.

	Examples
	--------
	Invoked by `smithyCastsSourceHanMono` via `multiprocessing.Pool.starmap` [3]:

	>>> from Integrated_Code_Fire.foundry import smithyCastsFont
	>>> smithyCastsFont('Simplified_Chinese', 'Bold', None)

	References
	----------
	[1] AFDKO makeotf - Read the Docs
		https://adobe-type-tools.github.io/afdko/AFDKO-Overview.html#makeotf
	[2] Integrated_Code_Fire.settingsPackage
		Internal package reference.

	"""
	pathFontFamily: Path = settingsPackage.pathRoot / fontFamilyCID
	pathCompiled: Path = settingsPackage.pathWorkbench / fontFamilyCID
	pathCompiled.mkdir(parents=True, exist_ok=True)

	filenameStemGlyphs: str = archivistMakesFilenameStem(fontFamilyCID, locale, style, weight)
	filenameStemMetadata: str = archivistMakesFilenameStem(fontFamilyCID, locale, style)

	pathFilename: Path = pathCompiled / f"{filenameStemGlyphs}.otf"

# TODO is this REALLY the only API? No class? No function?
	afdko_makeotf([
		'-f', str((pathFontFamily / 'glyphs') / f"{filenameStemGlyphs}.cidfont.ps")
		, '-ff', str((pathFontFamily / 'glyphs') / f"{filenameStemGlyphs}.features")
		, '-fi', str((pathFontFamily / 'glyphs') / f"{filenameStemGlyphs}.cidfontinfo")
		, '-cs', lookupAFDKOCharacterSet[locale]
		, '-ch', str((pathFontFamily / 'metadata') / f"{filenameStemMetadata}.UTF32-H")
		, '-ci', str((pathFontFamily / 'metadata') / f"{filenameStemMetadata}.sequences")
		, '-omitMacNames'
		, '-mf', str((pathFontFamily / 'metadata') / 'FontMenuNameDB')
		, '-r'
		, '-nS'
		, '-omitDSIG'
		, '-ncn'
		, '-gs'
		, '-o', str(pathFilename)
	])

	return pathFilename

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
	Invoked by `go` [3] as the first step in the build assembly line:

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

