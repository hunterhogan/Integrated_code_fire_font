@PUSHD %pathWorkbenchFonts%

@SET "subsetOptions=--layout-features='*' --drop-tables= --symbol-cmap --notdef-glyph --name-languages='*' --hinting --glyph-names --legacy-cmap --name-IDs=* --name-legacy --passthrough-tables"
@SET unicodesRangesSC="3000-303F,3400-4DBF,4E00-9FFF,F900-FAFF"

fonttools subset SourceHanMonoSC-Bold.ttf --unicodes=%unicodesRangesSC% %subsetOptions%
fonttools subset SourceHanMonoSC-Heavy.ttf --unicodes=%unicodesRangesSC% %subsetOptions%
fonttools subset SourceHanMonoSC-Light.ttf --unicodes=%unicodesRangesSC% %subsetOptions%
fonttools subset SourceHanMonoSC-Medium.ttf --unicodes=%unicodesRangesSC% %subsetOptions%
fonttools subset SourceHanMonoSC-Normal.ttf --unicodes=%unicodesRangesSC% %subsetOptions%
fonttools subset SourceHanMonoSC-Regular.ttf --unicodes=%unicodesRangesSC% %subsetOptions%

DEL SourceHanMonoSC-Bold.ttf
DEL SourceHanMonoSC-Heavy.ttf
DEL SourceHanMonoSC-Light.ttf
DEL SourceHanMonoSC-Medium.ttf
DEL SourceHanMonoSC-Normal.ttf
DEL SourceHanMonoSC-Regular.ttf

@POPD
