# Integrated Code 火

| Integrated Code 火 🡲      | 🡲 is a monospaced programming font 🡲                  | 🡲 plus 🡳             |
| ------------------------- | ----------------------------------------------------- | -------------------- |
| Integrated Code 火 日本   | 日本語スクリプトを備えた等幅プログラミング フォント。 | Japanese.            |
| Integrated Code 火 한국인 | 한글과 한자를 포함하는 고정폭 프로그래밍 폰트.        | Korean.              |
| Integrated Code 火 简化字 | 一款采用简体中文字符的等宽编程字体。                  | simplified Chinese.  |
| Integrated Code 火 台灣   | 一款包含繁體中文字元的等寬程式設計字型。              | traditional Chinese. |
| Integrated Code 火 香港   | 一個等間隔嘅編程字體, 有傳統嘅粵語字。                | Cantonese.           |

## Download 下载 다운로드 ダウンロード 下載 Integrated Code 火

| Download fonts from ["Releases"](https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest), not the repository source code.                                  |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 請從 ["Releases" / 發行版本](https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest) 下載字型，而非儲存庫的原始碼。                                        |
| ["Releases" / 릴리스](https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest) 에서 글꼴을 다운로드하십시오. 저장소 소스 코드가 아닙니다.                   |
| フォントはリポジトリのソースコードではなく、["Releases" / リリース](https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest) からダウンロードしてください。 |
| 请从 ["Releases" / 发布](https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest) 下载字体，而非仓库源代码。                                                |
| 請喺 ["Releases" / 發佈版本](https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest) 度下載字體,唔好喺 原始碼 倉庫度攞。                                   |

## Font genealogy

| "Fira"                                                  | "Source"                                                          |     | "Source Han"                                                            |     | "Noto"                                                      |
| ------------------------------------------------------- | ----------------------------------------------------------------- | --- | ----------------------------------------------------------------------- | --- | ----------------------------------------------------------- |
| [Fira Mono](https://github.com/mozilla/Fira)            | [Source Sans](https://github.com/adobe-fonts/source-sans)         |     | [Source Han Sans](https://github.com/adobe-fonts/source-han-sans)       | ⮀   | [Noto Sans CJK](https://github.com/notofonts/noto-cjk)      |
| 🡳                                                       | 🡳                                                                 |     | 🡳                                                                       |     | 🡳                                                           |
| [Fira Code](https://github.com/tonsky/FiraCode)         | [Source Code Pro](https://github.com/adobe-fonts/source-code-pro) | 🡲   | [Source Han Code JP](https://github.com/adobe-fonts/source-han-code-jp) |     | [Noto Sans Mono CJK](https://github.com/notofonts/noto-cjk) |
| 🡳                                                       |                                                                   | 🡮   | 🡳                                                                       |     |                                                             |
| [Fira Code HH](https://github.com/hunterhogan/FiraCode) |                                                                   |     | [Source Han Mono](https://github.com/adobe-fonts/source-han-mono)       |     |                                                             |

               🡮                      🡷
                   Integrated Code 火

## Some other programming fonts

The website "[Programming Fonts](https://www.programmingfonts.org/)" has previews of hundreds of fonts.

### With only Western glyphs

- [Fira Code](https://github.com/tonsky/FiraCode) is my favorite code-centric font.
- As of 2026 March 3, the last compiled version was released on 2021 December 6, and I have more recently compiled versions in [my fork of Fira Code](https://github.com/hunterhogan/FiraCode).

### With CJK / Han / Unihan glyphs

- [Maple Mono](https://github.com/subframe7536/maple-font)
- [Sarasa Gothic](https://github.com/be5invis/Sarasa-Gothic)
- [Source Han Code JP | 源ノ角ゴシック Code](https://github.com/adobe-fonts/source-han-code-jp)

## The future?

1. You contribute to the project?
2. Improve non-English text.
3. Improve configuration management.
4. Improve and generalize flow.
5. Weights:
   1. Fira Code has six different weights.
   2. Source Han Mono has seven different weights.
   3. Monospaced Noto Sans CJK has two different weights.
   4. Replace English-language weight names with weight values. "Regular", for example, may become "400". Or maybe this would break something I don't understand.
6. Glyphs:
   1. Noto Sans CJK may have updated and/or new glyphs.
   2. Source Han Code JP likely has updated and new glyphs.
   3. [GB 18030-2022](https://github.com/adobe-type-tools/Adobe-GB1/?tab=readme-ov-file#supplement-6adobe-gb1-6) defines new simplified Chinese glyphs. I suspect some of them are in Noto Sans CJK.
   4. Investigate: [Adobe-Manga1-0 Character Collection](https://github.com/adobe-type-tools/Adobe-Manga1/).
   5. Investigate: can adobe-type-tools / [CMap-resources](https://github.com/adobe-type-tools/cmap-resources) help find updated and/or new glyphs?
7. Reduce font file size.
8. Formats:
   1. ❓.otf
   2. ❓variable font
   3. ❓.woff2
   4. ❓Keep .ttc
   5. ❓abc
   6. ❓CMap
   7. ❓abbr.
   8. ❓cmap
   9. ❓wolf9
9. Create a pan-CJK variant.
10. Spacing:
    1. ❓Eliminate all full width spaces?
    2. In "words" with mixed Latin and CJK, shift the CJK towards the Latin.

## Working with the files in the repository

The repository is optimized to work with [Visual Studio Code](https://code.visualstudio.com/), but that is not required.

1. [Clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) or fork the repository. ([Visual Studio Code instructions.](https://code.visualstudio.com/docs/sourcecontrol/repos-remotes))
2. Install the Python packages in a virtual environment with ["uv"](https://docs.astral.sh/uv/); from the folder with the repository, run:

    uv sync

### Tips to make life easier

1. In the names of files and fonts, don't use separators: - (hyphen), – (en dash), — (em dash), or similar characters. For some readers, they can be ambiguous due to 一, which is an ideograph representing "1".
2. When preparing font files, only make changes in the "workbench" directory. Never change files in directories with glyph or metadata information unless you intend the change to be permanent and universal.

### Comparison of weight names

| Integrated Code 火 | Fira Code | Source Han Mono |
| ------------------ | --------- | --------------- |
| -                  | -         | ExtraLight      |
| Light              | Light     | Light           |
| Regular            | Regular   | Regular         |
| Retina             | Retina    | Normal          |
| Medium             | Medium    | Medium          |
| SemiBold           | SemiBold  | Bold            |
| Bold               | Bold      | Heavy           |

### Compile the font files

Run go.py.

### Make Five Source Han Mono Locale TTC files

Based on the out-of-date instructions in the Source Han Mono repository, this process produces one TTC file for each of the five locales in Source Han Mono. The files seem to work, and they are far smaller than the comprehensive TTC file. These files could be useful to you, and [you can download the fonts](https://github.com/hunterhogan/Integrated_code_fire_font/releases/tag/SourceHanMono1.002) from the "Release."

1. Maximize locales, styles, and weights in "_theSSOT.py".
2. Run `foundry.smithyCasts_afdko('SourceHanMono')`.
3. Run makeTTCLocale.cmd.

## Legal stuff

- Source is a trademark of Adobe in the United States and/or other countries.
- Fira Mono is a trademark of The Mozilla Corporation.
- You may license the font, Integrated Code 火, with Reserved Font Name "Integrated", under the terms of the [SIL Open Font License, Version 1.1](https://openfontlicense.org/ofl-faq/).
- You may license the files, other than the font files, in this repository of which I am the copyright holder under the terms of the [Creative Commons Attribution-NonCommercial 4.0 International Public License](https://creativecommons.org/licenses/by-nc/4.0/).

[![CC-BY-NC-4.0](https://raw.githubusercontent.com/hunterhogan/integrated_code_fire_font/refs/heads/main/.github/CC-BY-NC-4.0.png)](https://creativecommons.org/licenses/by-nc/4.0/)

### Commentary

- Adobe writing "and/or" in their trademark notice is stupid.
- The Mozilla Corporation has probably abandoned the Fira Mono trademark.

## My recovery

[![Static Badge](https://img.shields.io/badge/2011_August-Homeless_since-blue?style=flat)](https://HunterThinks.com/support)
[![YouTube Channel Subscribers](https://img.shields.io/youtube/channel/subscribers/UC3Gx7kz61009NbhpRtPP7tw)](https://www.youtube.com/@HunterHogan)
