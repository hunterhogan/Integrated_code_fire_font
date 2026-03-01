SETLOCAL enableDelayedExpansion
SET fontFamily=SourceHanMono

SET pathPS=C:\apps\Integrated_Code_Fire\%fontFamily%\glyphs
SET pathSHM=C:\apps\Integrated_Code_Fire\workbench\%fontFamily%

SET locale=Hong_Kong
CALL :subroutine
SET locale=Japan
CALL :subroutine
SET locale=Korea
CALL :subroutine
SET locale=Simplified_Chinese
CALL :subroutine
SET locale=Taiwan
CALL :subroutine

GOTO :EOF
:subroutine
@REM Segregate the OTFs by locale.
ROBOCOPY %pathSHM% %pathSHM%\%locale% /MOV *.%locale%.*

@REM DIR just Italic, but use the filename for both styles.
FOR /F "tokens=1,2,4 delims=." %%G IN ('DIR /B %pathSHM%\%locale%\*.Italic.*.otf') DO (
	CALL tx -cff %pathPS%\%%G.%%H.%%I.cidfont.ps %pathSHM%\%locale%\%%G.%%H.%%I.cff
	CALL sfntedit -a CFF=%pathSHM%\%locale%\%%G.%%H.%%I.cff %pathSHM%\%locale%\%%G.%%H.%%I.otf

	CALL tx -cff %pathPS%\%%G.%%H.Italic.%%I.cidfont.ps %pathSHM%\%locale%\%%G.%%H.Italic.%%I.cff
	CALL sfntedit -a CFF=%pathSHM%\%locale%\%%G.%%H.Italic.%%I.cff %pathSHM%\%locale%\%%G.%%H.Italic.%%I.otf
)

PUSHd %pathSHM%\%locale%

CALL sfntedit -x CFF=CFF.%locale% -d DSIG %fontFamily%.%locale%.Regular.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %fontFamily%.%locale%.Bold.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %fontFamily%.%locale%.ExtraLight.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %fontFamily%.%locale%.Heavy.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %fontFamily%.%locale%.Italic.Bold.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %fontFamily%.%locale%.Italic.ExtraLight.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %fontFamily%.%locale%.Italic.Heavy.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %fontFamily%.%locale%.Italic.Light.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %fontFamily%.%locale%.Italic.Medium.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %fontFamily%.%locale%.Italic.Normal.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %fontFamily%.%locale%.Italic.Regular.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %fontFamily%.%locale%.Light.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %fontFamily%.%locale%.Medium.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %fontFamily%.%locale%.Normal.otf

POPD

PUSHd %pathSHM%

SET "listPathFilenames="

FOR /F %%G IN ('DIR /B /S %locale%\*.otf') DO (
	SET "listPathFilenames= !listPathFilenames! %%G"
)

CALL otf2otc -o %fontFamily%-%locale%.ttc %listPathFilenames%

POPD

GOTO :EOF
