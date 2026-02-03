@ECHO OFF

IF NOT DEFINED VIRTUAL_ENV CALL .venv\Scripts\activate.bat
IF NOT DEFINED VIRTUAL_ENV ECHO I need a virtual environment & EXIT /B 1

PUSHD %VIRTUAL_ENV%\..

SET pathRoot=%CD%
SET pathWorkbench=%pathRoot%\workbench
SET pathWorkbenchFonts=%pathWorkbench%\fonts

SET pathRoot & SET pathWorkbench
