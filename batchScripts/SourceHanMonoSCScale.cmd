@PUSHD %pathWorkbenchFonts%

START "scaleUpem" /MIN CMD /C "fonttools ttLib.scaleUpem SourceHanMonoSC-Bold.subset.ttf 2000 && DEL SourceHanMonoSC-Bold.subset.ttf"
START "scaleUpem" /MIN CMD /C "fonttools ttLib.scaleUpem SourceHanMonoSC-Heavy.subset.ttf 2000 && DEL SourceHanMonoSC-Heavy.subset.ttf"
START "scaleUpem" /MIN CMD /C "fonttools ttLib.scaleUpem SourceHanMonoSC-Light.subset.ttf 2000 && DEL SourceHanMonoSC-Light.subset.ttf"
START "scaleUpem" /MIN CMD /C "fonttools ttLib.scaleUpem SourceHanMonoSC-Medium.subset.ttf 2000 && DEL SourceHanMonoSC-Medium.subset.ttf"
START "scaleUpem" /MIN CMD /C "fonttools ttLib.scaleUpem SourceHanMonoSC-Normal.subset.ttf 2000 && DEL SourceHanMonoSC-Normal.subset.ttf"
START "scaleUpem" /MIN CMD /C "fonttools ttLib.scaleUpem SourceHanMonoSC-Regular.subset.ttf 2000 && DEL SourceHanMonoSC-Regular.subset.ttf"

@POPD
