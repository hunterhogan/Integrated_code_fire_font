# ruff: noqa: D100, D103, TC003
from afdko.makeotf import main as afdko_makeotf
from fontmake.font_project import FontProject
from Integrated_Code_Fire import pathFilenameFiraCodeGlyphs, pathWorkbench, pathWorkbenchFonts, settingsPackage
from itertools import product as CartesianProduct
from multiprocessing import Pool
from pathlib import Path
from typing import Literal

truthy = None

# TODO concurrency options for faster throughput? It seems like I can at least divide otf and ttf.
def smithyCastsFiraCode() -> None:
	FontProject().run_from_glyphs( # pyright: ignore[reportUnknownMemberType]
		glyphs_path=str(pathFilenameFiraCodeGlyphs)
		, output=('otf', 'ttf')
		, output_dir=str(pathWorkbenchFonts)
		, interpolate=True
		, autohint=False
	)

def smithyCastsSourceHanMono(workersMaximum: int = 1) -> None:
	listLocales: list[str] = ['Hong_Kong', 'Japan', 'Korea', 'Simplified_Chinese', 'Taiwan']
	listWeights: list[str] = ['ExtraLight','Light','Normal','Regular','Medium','Bold','Heavy']
	listStyles: list[Literal['Italic'] | None] = [None, 'Italic']

	with Pool(processes=workersMaximum) as concurrencyManager:
		concurrencyManager.starmap(smithyCastsFont, CartesianProduct(listLocales, listWeights, listStyles))

def smithyCastsFont(locale: str, weight: str = 'Regular', style: Literal['Italic'] | None = None) -> None:
	fontFamilyHARDCODED: str = 'SourceHanMono'
	fontFamily: str = fontFamilyHARDCODED
	pathRoot: Path = settingsPackage.pathPackage.parent.parent / fontFamily
	pathCompiled: Path = pathWorkbench / fontFamily
	pathCompiled.mkdir(parents=True, exist_ok=True)

	afdko_makeotf([
		'-f', str((pathRoot / 'glyphs') / '.'.join(filter(truthy, [locale, style, weight, 'OTC', 'cidfont', 'ps'])))
		, '-ff', str((pathRoot / 'glyphs') / '.'.join(filter(truthy, [locale, style, weight, 'OTC', 'features'])))
		, '-fi', str((pathRoot / 'glyphs') / '.'.join(filter(truthy, [locale, style, weight, 'OTC', 'cidfontinfo'])))
		, '-cs', _getCharacterSet(locale)
		, '-ch', str((pathRoot / 'metadata') / '.'.join(filter(truthy, [locale, style, fontFamily, 'UTF32', 'H'])))
		, '-ci', str((pathRoot / 'metadata') / '.'.join(filter(truthy, [locale, style, fontFamily, 'sequences', 'txt'])))
		, '-omitMacNames'
		, '-mf', str((pathRoot / 'metadata') / 'FontMenuNameDB')
		, '-r'
		, '-nS'
		, '-omitDSIG'
		, '-ncn'
		, '-gs'
		, '-o', str(pathCompiled / '.'.join(filter(truthy, [locale, style, weight, fontFamily, 'otf'])))
	])

def _getCharacterSet(locale: str) -> str:
	return {'Hong_Kong': '2', 'Japan': '1', 'Korea': '3', 'Simplified_Chinese': '25', 'Taiwan': '2'}[locale]

if __name__ == '__main__':
	smithyCastsFiraCode()
	smithyCastsSourceHanMono(14)

