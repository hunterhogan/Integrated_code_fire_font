@PUSHD %pathWorkbenchFonts%

START "otf2ttf" /MIN CMD /C "otf2ttf SourceHanMonoSC-Bold.otf && DEL SourceHanMonoSC-Bold.otf"
START "otf2ttf" /MIN CMD /C "otf2ttf SourceHanMonoSC-Heavy.otf && DEL SourceHanMonoSC-Heavy.otf"
START "otf2ttf" /MIN CMD /C "otf2ttf SourceHanMonoSC-Light.otf && DEL SourceHanMonoSC-Light.otf"
START "otf2ttf" /MIN CMD /C "otf2ttf SourceHanMonoSC-Medium.otf && DEL SourceHanMonoSC-Medium.otf"
START "otf2ttf" /MIN CMD /C "otf2ttf SourceHanMonoSC-Normal.otf && DEL SourceHanMonoSC-Normal.otf"
START "otf2ttf" /MIN CMD /C "otf2ttf SourceHanMonoSC-Regular.otf && DEL SourceHanMonoSC-Regular.otf"

@POPD
