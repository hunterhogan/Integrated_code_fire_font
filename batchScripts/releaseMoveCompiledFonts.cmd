@ECHO OFF

SET pathDestination="%pathRoot%\fonts"
SET filenameMask=I*.ttf
ROBOCOPY %pathWorkbenchFonts% %pathDestination% %filenameMask% /MOV /NS /NC /NDL /NJH /NJS /unicode
