# Integrated Code 火

Integrated Code 火 is a code-centric monospaced font combining [Fira Code](https://github.com/tonsky/FiraCode) and one of five locales from [Source™ Han Mono](https://github.com/adobe-fonts/source-han-mono).

(机器翻译) Integrated Code 火是一款以代码为核心的等宽字体，融合了[Fira Code](https://github.com/tonsky/FiraCode)与[Source™ Han Mono](https://github.com/adobe-fonts/source-han-mono)的五种字形方案之一。

통합 코드 火는 [Fira Code](https://github.com/tonsky/FiraCode)와 [Source™ Han Mono](https://github.com/adobe-fonts/source-han-mono)의 다섯 가지 로케일 중 하나를 결합한 코드 중심의 고정폭 폰트입니다.

統合コード火は、コード中心の等幅フォントであり、[Fira Code](https://github.com/tonsky/FiraCode) と [Source™ Han Mono](https://github.com/adobe-fonts/source-han-mono) の5つのロケールのうち1つを組み合わせたものです。

(機器翻譯。) Integrated Code 火 是一款以程式碼為核心的等寬字型，融合了 [Fira Code](https://github.com/tonsky/FiraCode) 與 [Source™ Han Mono](https://github.com/adobe-fonts/source-han-mono) 五種地區字型之一。

（機器翻譯。）Integrated Code 火是一款以程式碼為中心的等寬字體，結合了 [Fira Code](https://github.com/tonsky/FiraCode) 和 [Source™ Han Mono](https://github.com/adobe-fonts/source-han-mono) 的五個語言版本之一。

## Download 下载 다운로드 ダウンロード 下載 Integrated Code 火

Download the compiled fonts from the [latest release](https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest) because they are not in the repository source code.

请从[最新版本](https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest)下载编译后的字体，因为它们并未包含在仓库源代码中。

리포지토리 소스 코드에는 포함되어 있지 않으므로 [최신 릴리스](https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest)에서 컴파일된 글꼴을 다운로드하십시오.

コンパイル済みフォントはリポジトリのソースコードに含まれていないため、[最新版](https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest)からダウンロードしてください。

請從[最新版本](https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest)下載編譯後的字型，因為它們並未包含在儲存庫的原始碼中。

喺[最新版本](https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest)下載編譯咗嘅字體，因為佢哋唔喺存儲庫源碼入面。

### Locale variants

| Font name                 | ascii name         | Language              | Writing system(s)                                  |
| ------------------------- | ------------------ | --------------------- | -------------------------------------------------- |
| Integrated Code 火 日本   | Japan              | Japanese              | 漢字, ひらがな, カタカナ Kanji, Hiragana, Katakana |
| Integrated Code 火 한국인 | Korea              | Hangugeo Korean       | 한글, 漢字 Hangul, Hanja                           |
| Integrated Code 火 简化字 | Simplified_Chinese | Mandarin and "爱国文" | 简化字 Simplified Chinese characters               |
| Integrated Code 火 台灣   | Taiwan             | Mandarin              | 正體字 Straight Traditional Chinese characters     |
| Integrated Code 火 香港   | Hong_Kong          | Yue/Cantonese         | 繁體字 Complicated Traditional Chinese characters  |

## Font genealogy

| "Fira"                                                  | "Source"                                                          |     | "Source Han"                                                            |     | "Noto"                                                      |
| ------------------------------------------------------- | ----------------------------------------------------------------- | --- | ----------------------------------------------------------------------- | --- | ----------------------------------------------------------- |
| [Fira Mono](https://github.com/mozilla/Fira)            | [Source Sans](https://github.com/adobe-fonts/source-sans)         |     | [Source Han Sans](https://github.com/adobe-fonts/source-han-sans)       | ↔️  | [Noto Sans CJK](https://github.com/notofonts/noto-cjk)      |
| ⬇️                                                      | ⬇️                                                                |     | ⬇️                                                                      |     | ⬇️                                                          |
| [Fira Code](https://github.com/tonsky/FiraCode)         | [Source Code Pro](https://github.com/adobe-fonts/source-code-pro) | ➡️  | [Source Han Code JP](https://github.com/adobe-fonts/source-han-code-jp) |     | [Noto Sans Mono CJK](https://github.com/notofonts/noto-cjk) |
| ⬇️                                                      |                                                                   | ↘️  | ⬇️                                                                      |     |                                                             |
| [Fira Code HH](https://github.com/hunterhogan/FiraCode) |                                                                   |     | [Source Han Mono](https://github.com/adobe-fonts/source-han-mono)       |     |                                                             |

               ↘️                      ↙️
                   Integrated Code 火

## The future?

1. You contribute to the project?
2. Improve configuration management.
3. Improve and generalize flow.
4. Weights:
   1. Fira Code has six different weights.
   2. Source Han Mono has seven different weights.
   3. Monospaced Noto Sans CJK has two different weights.
   4. Replace English-language weight names with weight values. "Regular", for example, may become "400".
5. Investigate: some monospaced glyphs in Noto Sans CJK are updated replacements for the glyphs in Source Han Mono.
6. Investigate: some monospaced glyphs in Source Han Code JP are updated replacements for the glyphs in Source Han Mono.
7. Investigate: can adobe-type-tools / [CMap-resources](https://github.com/adobe-type-tools/cmap-resources) help find updated and/or new glyphs?
8. Reduce font file size.
9. Create one file: updated pan-CJK with Fira Code.

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

### Make Source Han Mono Comprehensive TTC file

I followed the instructions seven-year-old instructions in the Source Han Mono repository as closely as possible, except I didn't "subroutinize", which should hypothetically produce a similar file to their [Release](https://github.com/adobe-fonts/source-han-mono/releases/tag/1.002). My file is larger, which is expected, but I can't figure out if my file is fully functional or in what other ways it differs from the official release. I created this unnecessary process to learn how to make TTC files.

1. Run `foundry.smithyCasts_afdko('SourceHanMono')`.
2. Run makeTTCSuper.cmd.

### Make Five Source Han Mono Locale TTC files

Based on the out-of-date instructions in the Source Han Mono repository, this process produces one TTC file for each of the five locales in Source Han Mono. The files seem to work, and they are far smaller than the comprehensive TTC file.

1. Run `foundry.smithyCasts_afdko('SourceHanMono')`.
2. Run makeTTCLocale.cmd.

## Some other programming fonts

The website "[Programming Fonts](https://www.programmingfonts.org/)" has previews of hundreds of fonts.

### With only Western glyphs

- [Fira Code](https://github.com/tonsky/FiraCode) is my favorite code-centric font.
- As of 2026 February 13, the last compiled version was released on 2021 December 6, and I have more recently compiled versions in [my fork of Fira Code](https://github.com/hunterhogan/FiraCode).

### With CJK / Han / Unihan glyphs

- [Sarasa Gothic](https://github.com/be5invis/Sarasa-Gothic)
- [Maple Mono](https://github.com/subframe7536/maple-font)
- [Source Han Code JP | 源ノ角ゴシック Code](https://github.com/adobe-fonts/source-han-code-jp)

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
