SETLOCAL enableDelayedExpansion
SET fontFamily=SourceHanMono

SET pathPS=C:\apps\Integrated_Code_Fire\%fontFamily%\glyphs
SET pathSHM=C:\apps\Integrated_Code_Fire\workbench\%fontFamily%

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

CALL otf2otc -o %fontFamily%.ttc %listPathFilenames%

POPD

GOTO :EOF
:subroutine
@REM Segregate the OTFs by weight.
ROBOCOPY %pathSHM% %pathSHM%\%weight% /MOV *.%weight%.*

@REM DIR just Italic, but use the filename for both styles.
FOR /F "tokens=1,2,4 delims=." %%G IN ('DIR /B %pathSHM%\%weight%\*.Italic.*.otf') DO (
	CALL tx -cff %pathPS%\%%G.%%H.%%I.cidfont.ps %pathSHM%\%weight%\%%G.%%H.%%I.cff
	CALL sfntedit -a CFF=%pathSHM%\%weight%\%%G.%%H.%%I.cff %pathSHM%\%weight%\%%G.%%H.%%I.otf

	CALL tx -cff %pathPS%\%%G.%%H.Italic.%%I.cidfont.ps %pathSHM%\%weight%\%%G.%%H.Italic.%%I.cff
	CALL sfntedit -a CFF=%pathSHM%\%weight%\%%G.%%H.Italic.%%I.cff %pathSHM%\%weight%\%%G.%%H.Italic.%%I.otf
)

PUSHd %pathSHM%\%weight%

CALL sfntedit -x CFF=CFF.%weight% -d DSIG %fontFamily%.Japan.%weight%.otf
CALL sfntedit -a CFF=CFF.%weight% -d DSIG %fontFamily%.Japan.Italic.%weight%.otf
CALL sfntedit -a CFF=CFF.%weight% -d DSIG %fontFamily%.Hong_Kong.Italic.%weight%.otf
CALL sfntedit -a CFF=CFF.%weight% -d DSIG %fontFamily%.Hong_Kong.%weight%.otf
CALL sfntedit -a CFF=CFF.%weight% -d DSIG %fontFamily%.Korea.Italic.%weight%.otf
CALL sfntedit -a CFF=CFF.%weight% -d DSIG %fontFamily%.Korea.%weight%.otf
CALL sfntedit -a CFF=CFF.%weight% -d DSIG %fontFamily%.Simplified_Chinese.Italic.%weight%.otf
CALL sfntedit -a CFF=CFF.%weight% -d DSIG %fontFamily%.Simplified_Chinese.%weight%.otf
CALL sfntedit -a CFF=CFF.%weight% -d DSIG %fontFamily%.Taiwan.Italic.%weight%.otf
CALL sfntedit -a CFF=CFF.%weight% -d DSIG %fontFamily%.Taiwan.%weight%.otf

POPD

GOTO :EOF
