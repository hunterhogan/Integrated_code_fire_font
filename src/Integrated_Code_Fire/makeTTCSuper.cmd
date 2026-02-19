SETLOCAL enableDelayedExpansion
SET pathPS=C:\apps\Integrated_Code_Fire\SourceHanMono\glyphs
SET pathSHM=C:\apps\Integrated_Code_Fire\workbench\SourceHanMono

SET weight=ExtraLight
CALL :subroutine
SET weight=Light
CALL :subroutine
SET weight=Normal
CALL :subroutine
SET weight=Regular
CALL :subroutine
SET weight=Medium
CALL :subroutine
SET weight=Bold
CALL :subroutine
SET weight=Heavy
CALL :subroutine

PUSHd %pathSHM%

SET "listPathFilenames="

FOR /F %%G IN ('DIR /B /S *.otf') DO (
	SET "listPathFilenames= !listPathFilenames! %%G"
)

CALL otf2otc -o SourceHanMono.ttc %listPathFilenames%

POPD

GOTO :EOF
:subroutine
@REM Segregate the OTFs by weight.
ROBOCOPY %pathSHM% %pathSHM%\%weight% /MOV *.%weight%.*

@REM DIR just Italic, but use the filename for both styles.
FOR /F "tokens=1,3 delims=." %%G IN ('DIR /B %pathSHM%\%weight%\*.Italic.*.otf') DO (
	CALL tx -cff %pathPS%\%%G.%%H.OTC.cidfont.ps %pathSHM%\%weight%\%%G.%%H.cff
	CALL sfntedit -a CFF=%pathSHM%\%weight%\%%G.%%H.cff %pathSHM%\%weight%\%%G.%%H.SourceHanMono.otf

	CALL tx -cff %pathPS%\%%G.Italic.%%H.OTC.cidfont.ps %pathSHM%\%weight%\%%G.Italic.%%H.cff
	CALL sfntedit -a CFF=%pathSHM%\%weight%\%%G.Italic.%%H.cff %pathSHM%\%weight%\%%G.Italic.%%H.SourceHanMono.otf
)

PUSHd %pathSHM%\%weight%

CALL sfntedit -x CFF=CFF.%weight% -d DSIG Japan.%weight%.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%weight% -d DSIG Japan.Italic.%weight%.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%weight% -d DSIG Hong_Kong.Italic.%weight%.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%weight% -d DSIG Hong_Kong.%weight%.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%weight% -d DSIG Korea.Italic.%weight%.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%weight% -d DSIG Korea.%weight%.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%weight% -d DSIG Simplified_Chinese.Italic.%weight%.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%weight% -d DSIG Simplified_Chinese.%weight%.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%weight% -d DSIG Taiwan.Italic.%weight%.SourceHanMono.otf
CALL sfntedit -a CFF=CFF.%weight% -d DSIG Taiwan.%weight%.SourceHanMono.otf

POPD

GOTO :EOF
