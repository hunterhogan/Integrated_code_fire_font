@ECHO OFF

IF NOT DEFINED VIRTUAL_ENV CALL .venv\Scripts\activate.bat
IF NOT DEFINED VIRTUAL_ENV ECHO I need a virtual environment & EXIT /B 1

PUSHD %VIRTUAL_ENV%\..

SET pathRoot=%CD%
SET pathWorkbench=%pathRoot%\workbench
SET pathWorkbenchFonts=%pathWorkbench%\fonts

@REM I compiled these on my local system. I've not had luck when downloading from the official repo.
SET pathSource=%pathRoot%\SourceHanMonoSC
SET filenameMask=*SC*.otf
ROBOCOPY %pathSource% %pathWorkbenchFonts% %filenameMask% /NS /NC /NDL /NJH /NJS

SET filenameZIP=FiraCode.zip
SET URL=https://github.com/hunterhogan/FiraCode/releases/download/6.900HH/Fira_Code_v6.900HH.zip
CALL curl -o %pathWorkbench%\%filenameZIP% -L %URL%

SET zipPathInternal=ttf\Fira Code
CALL 7z e -aoa "-o%pathWorkbenchFonts%" "%pathWorkbench%\%filenameZIP%" "%zipPathInternal%\*"
