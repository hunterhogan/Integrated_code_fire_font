"""Compile Glyphs source files and PostScript CID font source files.

(AI generated docstring)

You can create western font instances from Glyphs source or compile regional CJK fonts from
PostScript CID source. Compiled files are stored under the temporary workbench for preparation.

Contents
--------
Functions
	smithyCasts_afdko
		Compile selected CJK locale, style, and weight combinations.
	smithyCastsFromGlyphs
		Compile font instances in one or more formats from Glyphs source.
	smithyFontProject
		Compile font instances in one format from Glyphs source.
	smithy_makeotf
		Compile one CJK font using prepared AFDKO options.
"""
from __future__ import annotations

from afdko import makeotf
from fontmake.font_project import FontProject
from hunterMakesPy.parseParameters import defineConcurrencyLimit
from Integrated_Code_Fire import LocaleIn, settingsPackage, WeightIn
from Integrated_Code_Fire.archivist import archivistGetsLocales, archivistGetsWeights, archivistMakesFilenameStem, make_afdkoOptions
from itertools import product as CartesianProduct, repeat, starmap
from multiprocessing import Pool
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from collections.abc import Iterable, Iterator
	from pathlib import Path
	from typing import Literal

def smithyCasts_afdko(pathRoot: Path, theLocales: Iterable[str], theStyles: Iterable[str | None], theWeights: Iterable[str], fontFamilyCID: str = 'SourceHanMono', *, CPUlimit: bool | float | int | None = 1) -> list[Path]:
	"""Compile CJK font variants for the selected locales, styles, and weights.

	(AI generated docstring)

	Parameters
	----------
	pathRoot : Path
		Source checkout containing CID font source files and associated resources.
	theLocales : Iterable[str]
		Locale keys from `Integrated_Code_Fire.archivist.archivistGetsLocales`.
	theStyles : Iterable[str | None]
		Styles to compile. An element of `None` selects upright style.
	theWeights : Iterable[str]
		Weight keys from `Integrated_Code_Fire.archivist.archivistGetsWeights`.
	fontFamilyCID : str = 'SourceHanMono'
		Family label used in source and output filenames.
	CPUlimit : bool | float | int | None = 1
		Worker limit. Positive integers select workers; negative integers reserve CPUs.
		Fractions select proportions to use or reserve. `None`, `False`, and `0` use all CPUs;
		`True` selects one worker. The effective limit is at least one worker.

	Returns
	-------
	listPathFilenames : list[Path]
		Compiled OTF paths under `settingsPackage.pathWorkbench / fontFamilyCID`, in the
		iteration order of the requested locale, style, and weight combinations.

	File Replacement
	----------------
	The output directory is created and compiled font files with matching names are replaced.
	"""
	workersMaximum: int = defineConcurrencyLimit(limit=CPUlimit)

	optionsValues: Iterator[tuple[str, ...]] = starmap(make_afdkoOptions, CartesianProduct([pathRoot], [fontFamilyCID], theLocales, theStyles, theWeights))

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
	"""Compile one CJK font from the sources selected by AFDKO options.

	(AI generated docstring)

	Parameters
	----------
	optionsValues : tuple[str, ...]
		Source and locale options, normally produced by
		`Integrated_Code_Fire.archivist.make_afdkoOptions`.
	pathFilenameWrite : Path
		Destination OTF file. Parent directories are created.

	Returns
	-------
	pathFilenameWrite : Path
		Path to the compiled font.

	File Replacement
	----------------
	The output file is replaced. Compilation uses release settings and omits Macintosh names.
	"""
	pathFilenameWrite.parent.mkdir(parents=True, exist_ok=True)

	makeotf.CheckEnvironment()
	makeOTFParams: makeotf.MakeOTFParams = makeotf.MakeOTFParams()
	makeotf.getOptions(makeOTFParams, [
		*optionsValues
		, '-omitMacNames'
		, '-r'
		, '-nS'
		, '-ncn'
		, '-nshw'
		, '-o', str(pathFilenameWrite)
	])
	makeotf.checkInputFile(makeOTFParams)
	makeotf.setMissingParams(makeOTFParams)
	makeotf.setOptionsFromFontInfo(makeOTFParams)
	makeotf.convertFontIfNeeded(makeOTFParams)
	makeotf.checkROS(makeOTFParams)
	if makeOTFParams.saveOptions == 'true':
		makeotf.saveOptionsFile(makeOTFParams)
	makeotf.runMakeOTF(makeOTFParams)

	return pathFilenameWrite

def smithyCastsFromGlyphs(pathFilename: Path, workersMaximum: int = 2, fontFormats: Iterable[str] = frozenset(['otf', 'ttf'])) -> Path:
	"""Compile font instances from Glyphs source in the requested output formats.

	(AI generated docstring)

	Parameters
	----------
	pathFilename : Path
		Glyphs source file defining the font instances to compile.
	workersMaximum : int = 2
		Maximum number of formats compiled concurrently.
	fontFormats : Iterable[str] = frozenset(['otf', 'ttf'])
		Formats to compile. Use `"otf"` for CFF outlines or `"ttf"` for TrueType outlines.
		Supply at least one format.

	Returns
	-------
	pathWorkbench : Path
		Shared output directory, `settingsPackage.pathWorkbench / pathFilename.stem`.

	File Replacement
	----------------
	The output directory is created and compiled instances with matching filenames are replaced.

	Examples
	--------
	The western preparation entry point in `chopShop` compiles one format before preparation.

		```python
		from Integrated_Code_Fire import pathFilenameFiraCodeGlyphsDEFAULT
		from Integrated_Code_Fire.foundry import smithyCastsFromGlyphs

		if __name__ == '__main__':
			fontFormat = 'ttf'
			pathTTFont = smithyCastsFromGlyphs(pathFilenameFiraCodeGlyphsDEFAULT, 1, [fontFormat])
		```
	"""
	with Pool(processes=workersMaximum) as concurrencyManager:
		listPaths: list[Path] = concurrencyManager.starmap(smithyFontProject, zip(repeat(pathFilename), fontFormats))
	return listPaths.pop()

def smithyFontProject(pathFilename: Path, fontFormat: Literal['otf', 'ttf']) -> Path:
	"""Compile the instances in a Glyphs source file to one font format.

	(AI generated docstring)

	Parameters
	----------
	pathFilename : Path
		Glyphs source file containing the font design and instance definitions.
	fontFormat : {'otf', 'ttf'}
		CFF or TrueType output format.

	Returns
	-------
	output_dir : Path
		Output directory containing the compiled instances, under
		`settingsPackage.pathWorkbench / pathFilename.stem`.

	See Also
	--------
	`smithyCastsFromGlyphs`
		Compile several output formats in the same build.

	File Replacement
	----------------
	The output directory is created and font instances with matching filenames are replaced.
	Instances are interpolated without autohinting.
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
