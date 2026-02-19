# Integrated Code 火

Integrated Code 火 is a code-centric font combining [Fira Code](https://github.com/tonsky/FiraCode) and [Source Han Mono](https://github.com/adobe-fonts/source-han-mono). The duospaced Source™ Han Mono glyphs are twice the width of the monospaced Fira Code glyphs, so you can have consistent alignment.

（机器翻译） Integrated Code 火是一款以代码为核心设计的字体，融合了[Fira Code](https://github.com/tonsky/FiraCode)与[Source Han Mono](https://github.com/adobe-fonts/source-han-mono)的特性。其双倍间距的Source™ Han Mono字符宽度是等宽Fira Code字符的两倍，从而实现统一的代码对齐效果。

## Download Integrated Code 火 简化字

Download the compiled fonts from the [latest release](https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest). The compiled fonts are not in the repository source code.

从[最新版本](https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest)下载编译后的字体。编译后的字体不在仓库源代码中。

## Why?

You want a Western and Han mono-/duospaced programming font with ligatures and consistent alignment.

## Some alternative programming fonts

The website "[Programming Fonts](https://www.programmingfonts.org/)" has previews of hundreds of fonts.

### With only Western glyphs

- [Fira Code](https://github.com/tonsky/FiraCode) is my favorite code-centric font.
- As of 2026 February 13, the last compiled version was released on 2021 December 6, and I have more recently compiled versions in [my fork of Fira Code](https://github.com/hunterhogan/FiraCode).

### With CJK / Han / Unihan glyphs

- [Sarasa Gothic](https://github.com/be5invis/Sarasa-Gothic)
- [Maple Mono](https://github.com/subframe7536/maple-font)
- [Source Han Code JP | 源ノ角ゴシック Code](https://github.com/adobe-fonts/source-han-code-jp)

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

## Working with the files in the repository

The repository is optimized to work with [Visual Studio Code](https://code.visualstudio.com/), but that is not required.

1. [Clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) or fork the repository. ([Visual Studio Code instructions.](https://code.visualstudio.com/docs/sourcecontrol/repos-remotes))
2. Install the Python packages in a virtual environment with ["uv"](https://docs.astral.sh/uv/); from the folder with the repository, run:

    uv sync

### Tips to make life easier

1. In the names of files and fonts, to avoid confusion, don't use these characters as separators: - (hyphen), – (en dash), — (em dash), or similar characters. For some readers, they can be ambiguous due to 一, which is an ideograph representing "1".
2. When preparing files, only make changes in the "workbench" directory. Never change files in directories with glyph and metadata information unless you intend the change to be permanent and universal.

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

### 简化字

Run go.py.

### Make Source Han Mono Comprehensive TTC file

I followed the instructions seven-year-old instructions in the Source Han Mono repository as closely as possible, which should hypothetically produce the same file in their [Release](https://github.com/adobe-fonts/source-han-mono/releases/tag/1.002). My file is larger than the release file, and I can't figure out if my is fully functional or in what other ways it differs from the official release. I created this unnecessary process to learn how to make TTC files.

1. Run `foundry.smithyCastsFontFamily('SourceHanMono')`.
2. Run makeTTCSuper.cmd.

### Make Five Source Han Mono Locale TTC files

Based on the out-of-date instructions in the Source Han Mono repository, this process produces one TTC file for each of the five locales in Source Han Mono. The files seem to work, and they are far smaller than the comprehensive TTC file.

1. Run `foundry.smithyCastsFontFamily('SourceHanMono')`.
2. Run makeTTCLocale.cmd.

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
7. Improve font file "packaging", such as:
   1. One file instead of six.
   2. Smaller total size.
8. Create versions for other languages and writing systems.
   1. If this project were to have a well-designed process for compiling a code-centric font with Latin and simplified Chinese glyphs, it would be _relatively_ easy to expand the process to some other languages and writing systems.
   2. There seem to be tens of thousands of compatible glyphs in Source Han Mono, Source Han Code JP, and Noto Sans CJK.
   3. I strongly oppose forcing all writing systems to use Latin characters as the name of the writing system.
9. Create one file: updated pan-CJK with Fira Code.

### Potential font collections

A tentative list of font collections and names:

| Font name                 | Language              | Writing system(s)                                  |
| ------------------------- | --------------------- | -------------------------------------------------- |
| Integrated Code 火 日本   | Japanese              | 漢字, ひらがな, カタカナ Kanji, Hiragana, Katakana |
| Integrated Code 火 한국인 | Hangugeo Korean       | 한글, 漢字 Hangul, Hanja                           |
| Integrated Code 火 简化字 | Mandarin and "爱国文" | 简化字 Simplified Chinese characters               |
| Integrated Code 火 台灣   | Mandarin              | 正體字 Straight Traditional Chinese characters     |
| Integrated Code 火 香港   | Yue/Cantonese         | 繁體字 Complicated Traditional Chinese characters  |

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
