"""You can use this module to compile Fira Code and Source Han Mono fonts from source files using fontmake and AFDKO makeotf.

(AI generated docstring)

This module provides the font compilation (casting) functions for the
Integrated_Code_Fire build assembly line. The module compiles Fira Code fonts
from Glyphs source files using `fontmake` [1] and compiles Source Han Mono
fonts from PostScript CIDFont source files using AFDKO `makeotf` [2]. The
module uses `multiprocessing.Pool` [3] for parallel compilation of multiple
font variants.

Contents
--------
Functions
	smithyCastsFiraCode
		Compile Fira Code fonts in OTF and TTF formats from Glyphs source.
	smithyCastsFontFormat
		Compile Fira Code fonts in a specified format using fontmake.
	smithyCastsSourceHanMono
		Compile all Source Han Mono font variants across locales, weights, and styles.
	smithyCastsFont
		Compile a single Source Han Mono font variant using AFDKO makeotf.

References
----------
[1] fontmake - Read the Docs
	https://github.com/googlefonts/fontmake
[2] AFDKO (Adobe Font Development Kit for OpenType) - Read the Docs
	https://adobe-type-tools.github.io/afdko/
[3] multiprocessing.Pool - Python Standard Library
	https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool
[4] Integrated_Code_Fire.go.go
	Internal package reference.

"""
from afdko.makeotf import main as afdko_makeotf
from fontmake.font_project import FontProject
from Integrated_Code_Fire import (
	lookupAFDKOCharacterSet, pathFilenameFiraCodeGlyphs, pathRoot, pathWorkbench, pathWorkbenchFonts)
from itertools import product as CartesianProduct
from multiprocessing import Pool
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
	from pathlib import Path

truthy = None

def smithyCastsFiraCode(workersMaximum: int = 2) -> None:
	"""You can compile Fira Code fonts in both OTF and TTF formats from Glyphs source files.

	(AI generated docstring)

	This function compiles Fira Code fonts by invoking `smithyCastsFontFormat`
	for both `'otf'` and `'ttf'` output formats in parallel using
	`multiprocessing.Pool` [1]. The function reads the Glyphs source file from
	`pathFilenameFiraCodeGlyphs` and writes compiled font files to
	`pathWorkbenchFonts`.

	Parameters
	----------
	workersMaximum : int = 2
		Maximum number of parallel worker processes for compiling font formats.

	Returns
	-------
	resultNone : None
		This function performs file I/O and returns `None`.

	Raises
	------
	Exception
		Raised if `fontmake` [2] encounters errors during font compilation.
	OSError
		Raised if filesystem operations fail while reading source files or
		writing compiled fonts.

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
	[3] Integrated_Code_Fire.go.go
		Internal package reference.
	[4] Integrated_Code_Fire.smithyCastsFontFormat
		Internal package reference.
	[5] Integrated_Code_Fire.pathFilenameFiraCodeGlyphs
		Internal package reference.
	[6] Integrated_Code_Fire.pathWorkbenchFonts
		Internal package reference.

	"""
	listOutputFormats: list[Literal['otf', 'ttf']] = ['otf', 'ttf']

	with Pool(processes=workersMaximum) as concurrencyManager:
		concurrencyManager.map(smithyCastsFontFormat, listOutputFormats)

def smithyCastsFontFormat(fontFormat: Literal['otf', 'ttf']) -> None:
	"""You can compile Fira Code fonts from Glyphs source in a specified output format.

	(AI generated docstring)

	This function uses `fontmake.font_project.FontProject` [1] to compile Fira
	Code fonts from the Glyphs source file at `pathFilenameFiraCodeGlyphs` [2].
	The function interpolates font instances, disables autohinting, and writes
	the compiled font files to `pathWorkbenchFonts` [3].

	Parameters
	----------
	fontFormat : Literal['otf', 'ttf']
		Output font format, either `'otf'` for OpenType CFF or `'ttf'` for
		TrueType.

	Returns
	-------
	resultNone : None
		This function performs file I/O and returns `None`.

	Raises
	------
	Exception
		Raised if `fontmake` [1] encounters errors during font compilation.
	OSError
		Raised if filesystem operations fail while reading source files or
		writing compiled fonts.

	Examples
	--------
	Invoked by `smithyCastsFiraCode` via `multiprocessing.Pool.map` [4]:

	>>> from Integrated_Code_Fire.foundry import smithyCastsFontFormat
	>>> smithyCastsFontFormat('ttf')

	References
	----------
	[1] fontmake.font_project.FontProject - Read the Docs
		https://github.com/googlefonts/fontmake
	[2] Integrated_Code_Fire.pathFilenameFiraCodeGlyphs
		Internal package reference.
	[3] Integrated_Code_Fire.pathWorkbenchFonts
		Internal package reference.
	[4] multiprocessing.Pool.map - Python Standard Library
		https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool.map

	"""
	FontProject().run_from_glyphs(
		glyphs_path=str(pathFilenameFiraCodeGlyphs)
		, output=(fontFormat,)
		, output_dir=str(pathWorkbenchFonts)
		, interpolate=True
		, autohint=False
	)

def smithyCastsFontFamily(fontFamily: str = 'SourceHanMono', workersMaximum: int = 1) -> None:
	"""You can compile all Source Han Mono font variants across five locales, seven weights, and two styles.

	(AI generated docstring)

	This function compiles Source Han Mono fonts for all combinations of locales
	(`'Hong_Kong'`, `'Japan'`, `'Korea'`, `'Simplified_Chinese'`, `'Taiwan'`),
	weights (`'ExtraLight'`, `'Light'`, `'Normal'`, `'Regular'`, `'Medium'`,
	`'Bold'`, `'Heavy'`), and styles (`None`, `'Italic'`). The function uses
	`multiprocessing.Pool.starmap` [1] to invoke `smithyCastsFont` for each
	variant in parallel. The total number of font files compiled is 70 (5 locales
	× 7 weights × 2 styles).

	Parameters
	----------
	workersMaximum : int = 1
		Maximum number of parallel worker processes for compiling font variants.

	Returns
	-------
	resultNone : None
		This function performs file I/O and returns `None`.

	Raises
	------
	Exception
		Raised if AFDKO `makeotf` [2] encounters errors during font compilation.
	OSError
		Raised if filesystem operations fail while reading source files or
		writing compiled fonts.

	Examples
	--------
	Invoked by `go` [3] with 14 worker processes:

	>>> from Integrated_Code_Fire.foundry import smithyCastsSourceHanMono
	>>> smithyCastsSourceHanMono(14)

	Invoked directly in the `__main__` block:

	>>> if __name__ == '__main__':
	...     smithyCastsSourceHanMono(14)

	References
	----------
	[1] multiprocessing.Pool.starmap - Python Standard Library
		https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool.starmap
	[2] AFDKO makeotf - Read the Docs
		https://adobe-type-tools.github.io/afdko/AFDKO-Overview.html#makeotf
	[3] Integrated_Code_Fire.go.go
		Internal package reference.
	[4] Integrated_Code_Fire.smithyCastsFont
		Internal package reference.
	[5] itertools.product - Python Standard Library
		https://docs.python.org/3/library/itertools.html#itertools.product

	"""  # noqa: RUF002
	listLocales: list[str] = ['Hong_Kong', 'Japan', 'Korea', 'Simplified_Chinese', 'Taiwan']
	listWeights: list[str] = ['ExtraLight', 'Light', 'Normal', 'Regular', 'Medium', 'Bold', 'Heavy']
	listStyles: list[Literal['Italic'] | None] = [None, 'Italic']

	with Pool(processes=workersMaximum) as concurrencyManager:
		concurrencyManager.starmap(smithyCastsFont, CartesianProduct([fontFamily], listLocales, listWeights, listStyles))

def smithyCastsFont(fontFamily: str, locale: str, weight: str = 'Regular', style: Literal['Italic'] | None = None) -> None:
	"""You can compile a single Source Han Mono font variant using AFDKO makeotf.

	(AI generated docstring)

	This function compiles a Source Han Mono font file for a specified locale,
	weight, and style using AFDKO `makeotf` [1]. The function constructs file
	paths for the PostScript CIDFont source file, OpenType features file, CID
	font info file, character set mappings, Unicode sequences, and font menu name
	database. The function writes the compiled OpenType font file to
	`pathWorkbench` [2] in a subdirectory named `'SourceHanMono'`.

	Parameters
	----------
	locale : str
		Font locale, one of `'Hong_Kong'`, `'Japan'`, `'Korea'`,
		`'Simplified_Chinese'`, or `'Taiwan'`.
	weight : str = 'Regular'
		Font weight, one of `'ExtraLight'`, `'Light'`, `'Normal'`, `'Regular'`,
		`'Medium'`, `'Bold'`, or `'Heavy'`.
	style : Literal['Italic'] | None = None
		Font style, either `'Italic'` or `None` for upright.

	Returns
	-------
	resultNone : None
		This function performs file I/O and returns `None`.

	Raises
	------
	Exception
		Raised if AFDKO `makeotf` [1] encounters errors during font compilation.
	OSError
		Raised if filesystem operations fail while reading source files or
		writing compiled fonts.
	KeyError
		Raised if `locale` is not one of the five supported locale identifiers.

	Examples
	--------
	Invoked by `smithyCastsSourceHanMono` via `multiprocessing.Pool.starmap` [3]:

	>>> from Integrated_Code_Fire.foundry import smithyCastsFont
	>>> smithyCastsFont('Simplified_Chinese', 'Bold', None)

	References
	----------
	[1] AFDKO makeotf - Read the Docs
		https://adobe-type-tools.github.io/afdko/AFDKO-Overview.html#makeotf
	[2] Integrated_Code_Fire.pathWorkbench
		Internal package reference.
	[3] multiprocessing.Pool.starmap - Python Standard Library
		https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool.starmap
	[4] Integrated_Code_Fire.settingsPackage
		Internal package reference.

	"""
	pathFontFamily: Path = pathRoot / fontFamily
	pathCompiled: Path = pathWorkbench / fontFamily
	pathCompiled.mkdir(parents=True, exist_ok=True)

	afdko_makeotf([
		'-f', str((pathFontFamily / 'glyphs') / '.'.join(filter(truthy, [locale, style, weight, 'OTC', 'cidfont', 'ps'])))
		, '-ff', str((pathFontFamily / 'glyphs') / '.'.join(filter(truthy, [locale, style, weight, 'OTC', 'features'])))
		, '-fi', str((pathFontFamily / 'glyphs') / '.'.join(filter(truthy, [locale, style, weight, 'OTC', 'cidfontinfo'])))
		, '-cs', lookupAFDKOCharacterSet[locale]
		, '-ch', str((pathFontFamily / 'metadata') / '.'.join(filter(truthy, [locale, style, fontFamily, 'UTF32', 'H'])))
		, '-ci', str((pathFontFamily / 'metadata') / '.'.join(filter(truthy, [locale, style, fontFamily, 'sequences', 'txt'])))
		, '-omitMacNames'
		, '-mf', str((pathFontFamily / 'metadata') / 'FontMenuNameDB')
		, '-r'
		, '-nS'
		, '-omitDSIG'
		, '-ncn'
		, '-gs'
		, '-o', str(pathCompiled / '.'.join(filter(truthy, [locale, style, weight, fontFamily, 'otf'])))
	])

if __name__ == '__main__':
	smithyCastsFiraCode()
	smithyCastsFontFamily('SourceHanMono', 14)
	smithyCastsFontFamily('FrankenFont', 14)

