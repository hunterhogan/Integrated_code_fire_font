SETLOCAL enableDelayedExpansion
SET fontFamily=SourceHanMono
SET fontFamily=FrankenFont

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
ROBOCOPY %pathSHM% %pathSHM%\%locale% /MOV %locale%.*

@REM DIR just Italic, but use the filename for both styles.
FOR /F "tokens=1,3 delims=." %%G IN ('DIR /B %pathSHM%\%locale%\*.Italic.*.otf') DO (
	CALL tx -cff %pathPS%\%%G.%%H.OTC.cidfont.ps %pathSHM%\%locale%\%%G.%%H.cff
	CALL sfntedit -a CFF=%pathSHM%\%locale%\%%G.%%H.cff %pathSHM%\%locale%\%%G.%%H.%fontFamily%.otf

	CALL tx -cff %pathPS%\%%G.Italic.%%H.OTC.cidfont.ps %pathSHM%\%locale%\%%G.Italic.%%H.cff
	CALL sfntedit -a CFF=%pathSHM%\%locale%\%%G.Italic.%%H.cff %pathSHM%\%locale%\%%G.Italic.%%H.%fontFamily%.otf
)

PUSHd %pathSHM%\%locale%

CALL sfntedit -x CFF=CFF.%locale% -d DSIG %locale%.Regular.%fontFamily%.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Bold.%fontFamily%.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.ExtraLight.%fontFamily%.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Heavy.%fontFamily%.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Italic.Bold.%fontFamily%.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Italic.ExtraLight.%fontFamily%.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Italic.Heavy.%fontFamily%.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Italic.Light.%fontFamily%.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Italic.Medium.%fontFamily%.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Italic.Normal.%fontFamily%.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Italic.Regular.%fontFamily%.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Light.%fontFamily%.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Medium.%fontFamily%.otf
CALL sfntedit -a CFF=CFF.%locale% -d DSIG %locale%.Normal.%fontFamily%.otf

POPD

PUSHd %pathSHM%

SET "listPathFilenames="

FOR /F %%G IN ('DIR /B /S %locale%\*.otf') DO (
	SET "listPathFilenames= !listPathFilenames! %%G"
)

CALL otf2otc -o %fontFamily%-%locale%.ttc %listPathFilenames%

POPD

GOTO :EOF
