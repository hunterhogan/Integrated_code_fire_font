"""Check prepared, subset, and merged fonts.

(AI generated docstring)

The build calls `checkWestern`, `checkHan`, and `checkMerged` after it saves each font, so problems
appear while the build runs. Each check writes its findings to standard output and returns the
most severe FontBakery status. The module entry point runs the checks that are slow, that need the
Fira Code source checkout, or that only inform.

Contents
--------
Functions
	checkAdvanceWidths
		Find advance widths that do not fit the one-cell and two-cell grid.
	checkFontBakery
		Run selected FontBakery checks on one font.
	checkHan
		Check one prepared CJK font with TrueType outlines.
	checkMerged
		Check one merged font against its western and CJK sources.
	checkShaping
		Compare the HarfBuzz shaping of text in a font and in its source font.
	checkSideBearings
		Find TrueType glyphs whose left side bearing differs from the outline.
	checkWestern
		Check one prepared western font.
	parseAutohintArguments
		Obtain the `ttfautohint` option arguments from a Fira Code build script.
"""
from __future__ import annotations

from fontbakery.checkrunner import CheckRunner
from fontbakery.configuration import Configuration
from fontbakery.fonts_profile import get_module, profile_factory, setup_context
from fontbakery.reporters.terminal import TerminalReporter
from fontbakery.status import ERROR, FAIL, FATAL, INFO, PASS, WARN
from fontTools.ttLib import TTFont
from functools import partial
from Integrated_Code_Fire import (
	autohintOptionsDEFAULT, boxOfCheckIDsHinting, boxOfCheckIDsMerged, pathFilenameFiraCode_build_ttfDEFAULT, settingsPackage, textShaping)
from Integrated_Code_Fire.archivist import archivistGetsUnicodes
from Integrated_Code_Fire.logistics import valetGetsWesternFontPathFilename
from itertools import compress, repeat
from operator import attrgetter, itemgetter, methodcaller, ne
from ttfautohint.options import format_kwargs
from typing import TYPE_CHECKING
import shlex
import sys
import uharfbuzz

if TYPE_CHECKING:
	from collections.abc import Sequence
	from fontbakery.status import Status
	from pathlib import Path

def checkFontBakery(pathFilename: Path, boxOfCheckIDs: Sequence[str] | None, *, succinct: bool = True) -> Status:
	"""Run selected FontBakery checks on one font.

	(AI generated docstring)

	Parameters
	----------
	pathFilename : Path
		Font to check.
	boxOfCheckIDs : Sequence[str] | None
		FontBakery check identifiers from the universal profile, or `None` for every check in the
		profile.
	succinct : bool = True
		Write one line per result. `False` also writes each message, such as the sizes that
		`hinting_impact` measures.

	Returns
	-------
	status : Status
		The most severe status, or `PASS` if no check reports a result. FontBakery writes results
		of `INFO` or worse to standard output.
	"""
	checkRunner: CheckRunner = CheckRunner(profile_factory(get_module('fontbakery.profiles.universal'))
		, setup_context([str(pathFilename)])
		, Configuration(explicit_checks=boxOfCheckIDs))
	terminalReporter: TerminalReporter = TerminalReporter(runner=checkRunner, loglevels=[INFO, WARN, FAIL, FATAL, ERROR], succinct=succinct, print_progress=False)
	checkRunner.run([terminalReporter])
	return terminalReporter.worst_check_status or PASS

def checkAdvanceWidths(pathFilename: Path, width: int) -> Status:
	"""Find advance widths that do not fit the one-cell and two-cell grid.

	(AI generated docstring)

	Parameters
	----------
	pathFilename : Path
		Font to check.
	width : int
		Advance width of a two-cell glyph, normally `settingsPackage.width`. A one-cell glyph is
		`width // 2`.

	Returns
	-------
	status : Status
		`FAIL` if any advance width is not 0, `width // 2`, or `width`; otherwise `PASS`.
	"""
	with TTFont(pathFilename, lazy=True) as ttFont:
		advanceWidths: frozenset[int] = frozenset(map(itemgetter(0), ttFont['hmtx'].metrics.values())) - {0, width // 2, width}
	if advanceWidths:
		message: str = f"{pathFilename.name}: I found `{sorted(advanceWidths) = }`, but each advance width must be 0, {width // 2}, or {width}."
		sys.stdout.write(f"{message}\n")
		return FAIL
	return PASS

def checkSideBearings(pathFilename: Path) -> Status:
	"""Find TrueType glyphs whose left side bearing differs from the outline.

	(AI generated docstring)

	Parameters
	----------
	pathFilename : Path
		Font with TrueType outlines.

	Returns
	-------
	status : Status
		`FAIL` if the `hmtx` left side bearing of a glyph with an outline differs from the `glyf`
		minimum x coordinate; otherwise `PASS`. Renderers disagree about where such glyphs belong.
	"""
	with TTFont(pathFilename, lazy=True) as ttFont:
		glyphNames: list[str] = list(compress(ttFont.getGlyphOrder(), map(attrgetter('numberOfContours'), map(ttFont['glyf'].__getitem__, ttFont.getGlyphOrder()))))
		glyphNamesMismatched: list[str] = list(compress(glyphNames, map(ne
			, map(attrgetter('xMin'), map(ttFont['glyf'].__getitem__, glyphNames))
			, map(itemgetter(1), map(ttFont['hmtx'].__getitem__, glyphNames))
			, strict=True)))
	if glyphNamesMismatched:
		message: str = f"{pathFilename.name}: I found {len(glyphNamesMismatched)} glyphs, such as `{glyphNamesMismatched[0:5] = }`, whose left side bearing differs from the outline minimum x."
		sys.stdout.write(f"{message}\n")
		return FAIL
	return PASS

def _shapeText(pathFilename: Path, text: str) -> list[tuple[str, tuple[int, int, int, int]]]:
	font: uharfbuzz.Font = uharfbuzz.Font(uharfbuzz.Face(uharfbuzz.Blob.from_file_path(str(pathFilename))))
	buffer: uharfbuzz.Buffer = uharfbuzz.Buffer()
	buffer.add_str(text)
	buffer.guess_segment_properties()
	uharfbuzz.shape(font, buffer)
	return list(zip(map(font.glyph_to_string, map(attrgetter('codepoint'), buffer.glyph_infos)), map(attrgetter('position'), buffer.glyph_positions), strict=True))

def checkShaping(pathFilename: Path, pathFilenameSource: Path, text: str) -> Status:
	"""Compare the HarfBuzz shaping of text in a font and in its source font.

	(AI generated docstring)

	Parameters
	----------
	pathFilename : Path
		Font to check, normally a merged font.
	pathFilenameSource : Path
		Font that contributed the glyphs and layout for `text`.
	text : str
		Text to shape as one run.

	Returns
	-------
	status : Status
		`FAIL` if any glyph name, advance, or offset differs; otherwise `PASS`.
	"""
	glyphsShaped: list[tuple[str, tuple[int, int, int, int]]] = _shapeText(pathFilename, text)
	glyphsSource: list[tuple[str, tuple[int, int, int, int]]] = _shapeText(pathFilenameSource, text)
	if glyphsShaped != glyphsSource:
		glyphsDiffering: list[tuple[tuple[str, tuple[int, int, int, int]], tuple[str, tuple[int, int, int, int]]]] = list(
			compress(zip(glyphsShaped, glyphsSource, strict=False), map(ne, glyphsShaped, glyphsSource, strict=False)))
		message: str = f"{pathFilename.name}: I shaped {len(text)} characters into {len(glyphsShaped)} glyphs, but `{pathFilenameSource}` shapes them into {len(glyphsSource)} glyphs, and {len(glyphsDiffering)} paired glyphs differ, such as `{glyphsDiffering[0:3] = }` as (shaped, source) pairs of (glyph name, (x offset, y offset, x advance, y advance))."
		sys.stdout.write(f"{message}\n")
		return FAIL
	return PASS

def checkWestern(pathFilename: Path) -> Status:
	"""Check one prepared western font.

	(AI generated docstring)

	Parameters
	----------
	pathFilename : Path
		Prepared and hinted western font with TrueType outlines.

	Returns
	-------
	status : Status
		The most severe status of the hinting checks in `boxOfCheckIDsHinting`, the advance width
		grid, and the side bearings.
	"""
	return max(checkFontBakery(pathFilename, boxOfCheckIDsHinting), checkAdvanceWidths(pathFilename, settingsPackage.width), checkSideBearings(pathFilename))

def checkHan(pathFilename: Path) -> Status:
	"""Check one prepared CJK font with TrueType outlines.

	(AI generated docstring)

	Parameters
	----------
	pathFilename : Path
		Prepared CJK subset with TrueType outlines.

	Returns
	-------
	status : Status
		The most severe status of the advance width grid and the side bearings.
	"""
	return max(checkAdvanceWidths(pathFilename, settingsPackage.width), checkSideBearings(pathFilename))

def checkMerged(pathFilename: Path, pathFilenameWestern: Path, pathFilenameHan: Path) -> Status:
	"""Check one merged font against its western and CJK sources.

	(AI generated docstring)

	Parameters
	----------
	pathFilename : Path
		Merged font with release metadata.
	pathFilenameWestern : Path
		Prepared western font, the first font of the merge.
	pathFilenameHan : Path
		Prepared CJK subset, the second font of the merge.

	Returns
	-------
	status : Status
		The most severe status of the FontBakery checks in `boxOfCheckIDsMerged`, the advance
		width grid, the side bearings, and two shaping comparisons. The western comparison shapes
		`textShaping` and every character of the western font. The CJK comparison shapes every
		character that only the CJK font contributes.
	"""
	unicodesWestern: frozenset[int] = archivistGetsUnicodes(pathFilenameWestern)
	unicodesHan: frozenset[int] = archivistGetsUnicodes(pathFilenameHan)
	return max(checkFontBakery(pathFilename, boxOfCheckIDsMerged)
		, checkAdvanceWidths(pathFilename, settingsPackage.width)
		, checkSideBearings(pathFilename)
		, checkShaping(pathFilename, pathFilenameWestern, textShaping + ''.join(map(chr, unicodesWestern)))
		, checkShaping(pathFilename, pathFilenameHan, ''.join(map(chr, unicodesHan - unicodesWestern)))
	)

def parseAutohintArguments(build_ttf: str) -> list[str]:
	"""Obtain the `ttfautohint` option arguments from a Fira Code build script.

	(AI generated docstring)

	Parameters
	----------
	build_ttf : str
		Text of Fira Code `script/build_ttf.sh`.

	Returns
	-------
	autohintArguments : list[str]
		Arguments of the first line that begins with `ttfautohint `, without the command and the
		input and output file arguments that end the line.
	"""
	return shlex.split(next(filter(methodcaller('startswith', 'ttfautohint '), map(str.strip, build_ttf.splitlines()))))[1:-2]

if __name__ == '__main__':
	fontFormat: str = 'ttf'

	# Compare `autohintOptionsDEFAULT` with the Fira Code source checkout, which changes only when Fira Code changes.
	doAutohintArguments: bool = True
	# Report the file size cost of hinting, which only informs.
	doHintingImpact: bool = True
	# Run the entire FontBakery universal profile, which takes about 5 minutes per merged font and reports
	# problems inherited from Fira Code and Source Han Mono as well.
	doUniversal: bool = False

	listPathFilenamesWestern: list[Path] = [*valetGetsWesternFontPathFilename(fontFormat).values()]
	listPathFilenamesUniversal: list[Path] = [*listPathFilenamesWestern, *settingsPackage.pathWorkbenchFonts.glob(f"*.{fontFormat}")]

	listStatus: list[Status] = [PASS]

	if doAutohintArguments:
		autohintArgumentsFiraCode: list[str] = parseAutohintArguments(pathFilenameFiraCode_build_ttfDEFAULT.read_text(encoding='utf-8'))
		autohintArguments: list[str] = format_kwargs(**autohintOptionsDEFAULT)
		if frozenset(autohintArgumentsFiraCode) != frozenset(autohintArguments):
			message: str = f"I received `{autohintArguments = }` from `autohintOptionsDEFAULT`, but Fira Code `build_ttf.sh` uses `{autohintArgumentsFiraCode = }`."
			sys.stdout.write(f"{message}\n")
			listStatus.append(FAIL)

	if doHintingImpact:
		listStatus.extend(map(partial(checkFontBakery, succinct=False), listPathFilenamesWestern, repeat(['hinting_impact']), strict=False))

	if doUniversal:
		listStatus.extend(map(checkFontBakery, listPathFilenamesUniversal, repeat(None), strict=False))

	sys.exit(int(FAIL <= max(listStatus)))
