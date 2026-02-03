@ECHO OFF

SET pathSource=%pathRoot%\SourceHanMonoSC
SET filenameMask=*SC*.otf
ROBOCOPY %pathSource% %pathWorkbenchFonts% %filenameMask% /NS /NC /NDL /NJH /NJS

SET pathSource="%pathRoot%\Fira_Code_v6.99\ttf\Fira Code"
SET filenameMask=*.ttf
ROBOCOPY %pathSource% %pathWorkbenchFonts% %filenameMask% /NS /NC /NDL /NJH /NJS
