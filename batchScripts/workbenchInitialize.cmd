@ECHO OFF

IF NOT DEFINED VIRTUAL_ENV CALL .venv\Scripts\activate.bat
IF NOT DEFINED VIRTUAL_ENV ECHO I need a virtual environment & EXIT /B 1

PUSHD %VIRTUAL_ENV%\..

SET pathRoot=%CD%
SET pathWorkbench=%pathRoot%\workbench
SET pathWorkbenchFonts=%pathWorkbench%\fonts

SET pathRoot & SET pathWorkbench

SET pathSource=%pathRoot%\SourceHanMonoSC
SET filenameMask=*SC*.otf
ROBOCOPY %pathSource% %pathWorkbenchFonts% %filenameMask% /NS /NC /NDL /NJH /NJS

SET pathSource="%pathRoot%\Fira_Code_v6.99\ttf\Fira Code"
SET filenameMask=*.ttf
ROBOCOPY %pathSource% %pathWorkbenchFonts% %filenameMask% /NS /NC /NDL /NJH /NJS

