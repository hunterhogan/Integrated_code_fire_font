# Integrated Code 火

Integrated Code 火 is a code-centric font combining an up-to-date [Fira Code](https://github.com/tonsky/FiraCode) compile with a modified [Source Han Mono](https://github.com/adobe-fonts/source-han-mono) compile. The Source™ Han glyphs are exactly twice the width of Fira Code glyphs, and the Source Han characters are slightly more spread out than you would expect to see in normal text.

（机器翻译） Integrated Code 火是一款以代码为核心的字体，融合了最新的[Fira Code](https://github.com/tonsky/FiraCode)字形与改良版[Source Han Mono](https://github.com/adobe-fonts/source-han-mono)字形。Source™ Han字符的宽度恰好是Fira Code字符的两倍，且Source Han字符的间距比常规文本中常见的略微宽松。

## Download

Download the compiled fonts from the [latest release](https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest). The source code archives do not contain font files.

从[最新版本](https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest)下载编译好的字体。源代码存档中不包含字体文件。

## Why?

1. I used the Fira Code font when programming.
2. I sometimes use simplified Chinese ideograms as identifiers or other labels.
3. Because of the width mismatch between Fira Code and the ideograms, the vertical alignment of my code was wonky.
4. I mistakenly believed it would be easy to scale another font and glue it to Fira Code.
5. I'm tenacious.

## Comparison of weight names

| Integrated Code 火 | Fira Code | Source Han Mono |
| ------------------ | --------- | --------------- |
| -                  | -         | ExtraLight      |
| Light              | Light     | Light           |
| Regular            | Regular   | Regular         |
| Retina             | Retina    | Normal          |
| Medium             | Medium    | Medium          |
| SemiBold           | SemiBold  | Bold            |
| Bold               | Bold      | Heavy           |

## Some alternative fonts

[Fira Code](https://github.com/tonsky/FiraCode) is my favorite code-centric font; based on [Fira Mono](https://github.com/bBoxType/FiraSans).

Some fonts with CJK / Han / Unihan glyphs:

- [Sarasa Gothic](https://github.com/be5invis/Sarasa-Gothic)
- [Maple Mono](https://github.com/subframe7536/maple-font)
- [Source Han Mono](https://github.com/adobe-fonts/source-han-mono)
- [Source Han Code JP | 源ノ角ゴシック Code](https://github.com/adobe-fonts/source-han-code-jp)

The website "[Programming Fonts](https://www.programmingfonts.org/)" has previews of hundreds of fonts.

## The past

1. Mozilla founds FirefoxOS and ["Fira" font](https://github.com/mozilla/Fira) family for FirefoxOS fonts.
2. [Nikita Prokopov](https://twitter.com/nikitonsky) pursues programming perfection: forming [Fira Code](https://github.com/tonsky/FiraCode) from Fira Mono™.
3. Adobe creates [Source Sans Pro](https://github.com/adobe-fonts/source-sans).
4. Adobe makes [Source Code Pro](https://github.com/adobe-fonts/source-code-pro) based on Source Sans Pro.
5. Adobe and Google make a font together. Adobe calls it [Source Han Sans](https://github.com/adobe-fonts/source-han-sans), and [Google Fonts](https://fonts.google.com/noto/fonts) calls it [Noto Sans CJK](https://github.com/notofonts/noto-cjk).
6. Google creates a monospace version in two weights of [Noto Sans CJK](https://github.com/notofonts/noto-cjk), but it can be difficult to find.
7. Masataka Hattori and Adobe create [Source Han Code JP | 源ノ角ゴシック Code](https://github.com/adobe-fonts/source-han-code-jp) from Source Han Sans and Source Code Pro.
8. Ken Lunde and Adobe create [Source Han Mono](https://github.com/adobe-fonts/source-han-mono) from Source Han Sans, Source Code Pro, and Source Han Code JP.

## Working with the files in the repository

The repository is optimized to work with [Visual Studio Code](https://code.visualstudio.com/), but that is not required.

1. [Clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) or fork the repository. ([Visual Studio Code instructions.](https://code.visualstudio.com/docs/sourcecontrol/repos-remotes))
2. Install the Python packages in a virtual environment with ["uv"](https://docs.astral.sh/uv/); from the folder with the repository, run:

```sh
uv sync
```

## 简化字

The batch files organize calls to the Python scripts. Reminder: In file and font names, avoid using - (hyphen), – (en dash), — (em dash), or similar characters next to ideographs and Hangul: they can be ambiguous due to 一 (an ideograph representing "1").

1. Run workbenchInitialize.cmd.
2. Run workbenchMergeFonts.cmd.
3. Run releaseMoveAndCleanup.cmd.

### File names

```sh
IntegratedCode火简化字Bold.ttf
IntegratedCode火简化字SemiBold.ttf
IntegratedCode火简化字Light.ttf
IntegratedCode火简化字Medium.ttf
IntegratedCode火简化字Retina.ttf
IntegratedCode火简化字Regular.ttf
```

## The future?

1. You contribute to the project?
2. Improve automation.
3. Weights:
   1. Fira Code has six different weights.
   2. Source Han Mono has seven different weights.
   3. Monospaced Noto Sans CJK has two different weights.
   4. Replace English-language weight names with weight values. "Regular", for example, may become "400".
4. Investigate: some monospaced glyphs in Noto Sans CJK are updated replacements for the glyphs in Source Han Mono.
5. Improve font file "packaging", such as:
   1. One file instead of six.
   2. Smaller total size.
6. Create and use a [Vendor ID](https://learn.microsoft.com/en-us/typography/vendors/register).
7. Create versions for other languages and writing systems.
   1. If this project were to have a well-designed process for compiling a code-centric font with Latin and simplified Chinese glyphs, it would be *relatively* easy to expand the process to some other languages and writing systems.
   2. There seem to be tens of thousands of compatible glyphs in Source Han Mono, Source Han Code JP, and Noto Sans CJK.
   3. I strongly oppose forcing all writing systems to use Latin characters as the name of the writing system.

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
