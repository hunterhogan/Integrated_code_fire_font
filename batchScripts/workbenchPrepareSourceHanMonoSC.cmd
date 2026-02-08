@ECHO OFF

SET pathSource=%pathRoot%\SourceHanMonoSC
SET filenameMask=*SC*.otf
ROBOCOPY %pathSource% %pathWorkbenchFonts% %filenameMask% /NS /NC /NDL /NJH /NJS

@PUSHD %pathWorkbenchFonts%

CALL :convert Bold
CALL :convert Heavy
CALL :convert Light
CALL :convert Medium
CALL :convert Normal
CALL :convert Regular

@POPD

GOTO :EOF
:convert
SET weight=%1
SET filename=SourceHanMonoSC-%weight%.otf
SET DEL_theseFiles=DEL %filename%
SET doThis=otf2ttf %filename%

SET filename=SourceHanMonoSC-%weight%.ttf
SET "DEL_theseFiles=%DEL_theseFiles% %filename%"
SET "subsetOptions=--unicodes=3000-303F,3400-4DBF,4E00-9FFF,F900-FAFF --layout-features='*' --drop-tables= --symbol-cmap --notdef-glyph --name-languages='*' --hinting --glyph-names --legacy-cmap --name-IDs=* --name-legacy --passthrough-tables"
SET "doThis=%doThis% && fonttools subset %filename% %subsetOptions%"

SET filename=SourceHanMonoSC-%weight%.subset.ttf
SET "DEL_theseFiles=%DEL_theseFiles% %filename%"
SET "doThis=%doThis% && fonttools ttLib.scaleUpem %filename% 2000"

START "%weight%" /MIN CMD /C "%doThis% && %DEL_theseFiles%"

GOTO :EOF
