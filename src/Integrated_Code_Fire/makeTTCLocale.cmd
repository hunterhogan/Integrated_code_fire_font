SETLOCAL enableDelayedExpansion
SET pathPS=C:\apps\Integrated_Code_Fire\SourceHanMono\glyphs
SET pathSHM=C:\apps\Integrated_Code_Fire\workbench\SourceHanMono


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
ROBOCOPY %pathSHM% %pathSHM%\%locale% /MOV %locale%.*

@REM DIR just Italic, but use the filename for both styles.
FOR /F "tokens=1,3 delims=." %%G IN ('DIR /B %pathSHM%\%locale%\*.Italic.*.otf') DO (
	CALL tx -cff %pathPS%\%%G.%%H.OTC.cidfont.ps %pathSHM%\%locale%\%%G.%%H.cff
	CALL sfntedit -a CFF=%pathSHM%\%locale%\%%G.%%H.cff %pathSHM%\%locale%\%%G.%%H.SourceHanMono.otf

	CALL tx -cff %pathPS%\%%G.Italic.%%H.OTC.cidfont.ps %pathSHM%\%locale%\%%G.Italic.%%H.cff
	CALL sfntedit -a CFF=%pathSHM%\%locale%\%%G.Italic.%%H.cff %pathSHM%\%locale%\%%G.Italic.%%H.SourceHanMono.otf
)

PUSHd %pathSHM%\%locale%

CALL sfntedit -x CFF=CFF.%locale% -d DSIG %locale%.Regular.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Bold.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.ExtraLight.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Heavy.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Italic.Bold.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Italic.ExtraLight.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Italic.Heavy.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Italic.Light.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Italic.Medium.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Italic.Normal.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Italic.Regular.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Light.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Medium.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Normal.SourceHanMono.otf

POPD

PUSHd %pathSHM%

SET "listPathFilenames="

FOR /F %%G IN ('DIR /B /S %locale%\*.otf') DO (
	SET "listPathFilenames= !listPathFilenames! %%G"
)

CALL otf2otc -o SourceHanMono-%locale%.ttc %listPathFilenames%

POPD

GOTO :EOF
