"""Compile Integrated Code 火 monospace programming fonts with CJK languages.

(AI generated docstring)

You can compile Integrated Code 火 fonts with a complete assembly line that compiles source fonts, scales and merges glyphs,
updates metadata, and produces distributable font files for multiple languages, scripts, and weights.

The repository contains many settings files for VS Code and Python tools.

Modules
-------
archivist
    Locale and weight mappings, filename generation, metadata updates, and character subset management.
foundry
    Font compilation from Glyphs source files using fontmake [3] and PostScript CIDFont source files using AFDKO makeotf [4].
go
    Assembly line orchestration and entry point.
logistics
    File staging, asset packaging, and workbench management.
machineShop
    Font scaling, subsetting, side bearing adjustment, and glyph merging.
mergeFonts
    Parallel font merging workflow combining the compiled fonts.

Types
-----
LocaleIn
    Locale identifier mapping between ASCII and Unicode representations.
WeightIn
    Weight identifier mapping across font families.

Configuration
-------------
PackageSettings
    Package-wide configuration including paths, font metadata, and supported locales, styles, and weights.
settingsPackage
    Package configuration instance.

References
----------
[1] Fira Code - GitHub
    https://github.com/tonsky/FiraCode
[2] Source Han Mono - Adobe Fonts
    https://github.com/adobe-fonts/source-han-mono
[3] fontmake - Google Fonts
    https://github.com/googlefonts/fontmake
[4] AFDKO (Adobe Font Development Kit for OpenType)
    https://adobe-type-tools.github.io/afdko/

"""
from Integrated_Code_Fire._theTypes import LocaleIn as LocaleIn, WeightIn as WeightIn

# isort: split
from Integrated_Code_Fire._theSSOT import (
	PackageSettings as PackageSettings, pathFilenameFiraCodeGlyphs as pathFilenameFiraCodeGlyphs,
	pathRootSourceHanMono as pathRootSourceHanMono, settingsPackage as settingsPackage, subsetOptions as subsetOptions)
