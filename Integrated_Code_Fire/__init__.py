"""Build Integrated Code 火 programming fonts with Fira Code and regional CJK glyphs.

(AI generated docstring)

You can prepare Fira Code and Source Han Mono fonts, combine their glyphs, and produce
locale-specific font archives. The supplied build settings select five locales and six upright
weights. Installing this Python package provides build tools; font users can install the release
font files directly.

Modules
-------
archivist
	Select characters and manage locale names, weight names, filenames, and font metadata.
chopShop
	Prepare western fonts and compile and subset CJK fonts.
foundry
	Compile Glyphs source and PostScript CID font source.
go
	Merge prepared fonts and package release archives.
logistics
	Copy intermediate files, package archives, and remove temporary files.
machineShop
	Subset CJK fonts, change horizontal metrics, and merge TrueType fonts.

Subpackages
-----------
dataCenter
	Supply character selections and CJK glyph exclusions.

Contents
--------
Types
	LocaleIn
		Store matching locale identifiers for the font families and source files.
	PackageSettings
		Configure font metadata, character selections, dimensions, and build directories.
	WeightIn
		Store matching weight identifiers for the font families and source files.
Settings
	pathFilenameFiraCodeGlyphsDEFAULT
		Locate the expected Fira Code Glyphs source file.
	pathRootSourceHanMonoDEFAULT
		Locate the expected Source Han Mono source checkout.
	settingsPackage
		Provide the active configuration shared by the build operations.
	subsetOptionsDEFAULT
		Provide the shared CJK subsetting options.
"""
from __future__ import annotations

from Integrated_Code_Fire._theTypes import LocaleIn as LocaleIn, WeightIn as WeightIn

# isort: split
from Integrated_Code_Fire._theSSOT import (
	PackageSettings as PackageSettings, pathFilenameFiraCodeGlyphsDEFAULT as pathFilenameFiraCodeGlyphsDEFAULT,
	pathRootSourceHanMonoDEFAULT as pathRootSourceHanMonoDEFAULT, settingsPackage as settingsPackage,
	subsetOptionsDEFAULT as subsetOptionsDEFAULT)
