# Integrated Code 火

**Fira Code ligatures, with Chinese, Japanese, and Korean on the same grid.**

[Download fonts][releases] · [Choose a variant](#choose-your-variant) · [Install](#install)

Integrated Code 火 combines Fira Code's programming glyphs with regional CJK glyphs from
Source Han Mono. Full-width CJK glyphs occupy two Latin character cells, so code and CJK text
can share a monospaced layout.

![Programming text and five regional CJK samples in Integrated Code 火 Regular.][preview]

- **Five regional variants:** Japanese, Korean, simplified Chinese, Taiwan, and Hong Kong.
- **Six upright weights:** Light, Regular, Retina, Medium, SemiBold, and Bold.
- **Programming ligatures:** Fira Code's combinations for operators and other code punctuation.
- **TrueType fonts:** individual `.ttf` files, packaged by locale.

## Choose your variant

Choose the variant for the glyph forms used in your language or region. Every variant uses the
same western font; the CJK glyph forms differ by locale. You can install more than one variant.

| Language or region            | Family to select in your editor | Download ZIP                     |
| ----------------------------- | ------------------------------- | -------------------------------- |
| 日本語 · Japanese             | Integrated Code 火 日本         | [Japan][japan]                   |
| 한국어 · Korean               | Integrated Code 火 한국인       | [Korea][korea]                   |
| 简体中文 · Simplified Chinese | Integrated Code 火 简化字       | [Simplified_Chinese][simplified] |
| 台灣 · Traditional Chinese    | Integrated Code 火 台灣         | [Taiwan][taiwan]                 |
| 香港 · Hong Kong / Cantonese  | Integrated Code 火 香港         | [Hong_Kong][hongkong]            |

Download the font ZIP from [Releases][releases]. Each locale archive contains the six weights.
GitHub's **Source code** downloads contain the build sources.

## Install

1. Download and extract the ZIP for your locale.
2. Install the `.ttf` files using your operating system's font installer.
3. Select the family name from the table above in your editor or terminal.
4. Enable font ligatures in editors that support them if you want the programming ligatures.

The font ZIP is ready to install. Python and the font build tools are needed only to build your
own font files.

## What to expect

Fira Code supplies the western characters and programming features. Source Han Mono supplies the
selected CJK characters, including regional ideograph forms, kana, and hangul. The font combines
these sources with spacing adjusted for a two-cell CJK width.

Ligatures change how supported character combinations appear; the underlying text stays the same.
Editors and terminals differ in their support for ligatures and OpenType features.

The characters `⋯` (U+22EF) and `…` (U+2026) use the same one-cell ellipsis glyph.

The downloads contain upright fonts. Italic, variable-font, and webfont builds are not included in
these locale archives.

## Font origins

Integrated Code 火 brings together two branches of font development.

- [Fira Mono] → [Fira Code] → [Fira Code HH], the source used for the western fonts.
- [Source Han Sans] and [Source Code Pro] → [Source Han Mono], a pan-CJK relative of
  [Source Han Code JP].

Fira Code is my favorite code-centric font. I also publish compiled Fira Code fonts in
[my fork][Fira Code HH] for people who want Fira Code on its own.

<details>
<summary>Other programming fonts</summary>

With Chinese, Japanese, and/or Korean glyphs.

- [Maple Mono](https://github.com/subframe7536/maple-font)
- [Sarasa Gothic](https://github.com/be5invis/Sarasa-Gothic)
- [GLG-Mono](https://github.com/junghan0611/GLG-Mono)
- [PlemolJP (プレモル ジェイピー)](https://github.com/yuru7/PlemolJP)
- [Source Han Code JP]

With western glyphs.

- [Fira Code]
- [Fira Code HH]

</details>

<details>
<summary>Build the font or contribute</summary>

### Set up the build environment

The build tools require Python 3.14 or later. Clone this repository and install its dependencies
with `uv sync`, then activate the project virtual environment before running the Python scripts.
For PowerShell.

```powershell
uv sync
. .\.venv\Scripts\Activate.ps1
```

Compiling the source fonts also requires local checkouts of [Fira Code HH] and [Source Han Mono].
By default, the build expects `FiraCode/FiraCode.glyphs` and the `source-han-mono` checkout under
this project's parent directory. Font settings and source locations are in
[Integrated_Code_Fire/_theSSOT.py](Integrated_Code_Fire/_theSSOT.py).

### Build stages

The assembly line separates character selection, font preparation, merging, and packaging.
Run the stages needed for the inputs you are changing.

1. **Character selections.** Run `python Integrated_Code_Fire/archivist.py` to regenerate the
   locale and style selections in `Integrated_Code_Fire/dataCenter`. The selections exclude
   western characters and vertical glyph forms. Regeneration replaces these persistent inputs.
2. **Source compilation and preparation.** Review the build switches in
   [chopShop.py](Integrated_Code_Fire/chopShop.py), then run
   `python Integrated_Code_Fire/chopShop.py`. Western fonts are prepared under
   `warehouse/western` or `warehouse/scaled`; CJK subsets are prepared under `warehouse/CID`.
3. **Merging and packaging.** Run `python Integrated_Code_Fire/go.py` with the prepared warehouse
   inputs. The active configuration selects five locales and six upright weights. Merged fonts
   are written to `workbench/fonts`, locale ZIP archives are written to `assets`, and temporary
   workbench files are removed after packaging.

Keep temporary font edits in `workbench`. Changes to the warehouse fonts or character selections
become persistent inputs to later builds. Build outputs with matching filenames are replaced.

### Weight matching

| Integrated Code 火 | Fira Code | Source Han Mono |
| ------------------ | --------- | --------------- |
| Light              | Light     | Light           |
| Regular            | Regular   | Regular         |
| Retina             | Retina    | Normal          |
| Medium             | Medium    | Medium          |
| SemiBold           | SemiBold  | Bold            |
| Bold               | Bold      | Heavy           |

Source Han Mono's ExtraLight weight has no matching Fira Code weight and is not selected for the
release fonts. Some preparation functions use the broader defaults of a fresh `PackageSettings`,
including italic styles and ExtraLight. Use explicit selections when you want those functions to
match the active release configuration.

### Contributions

Corrections to the non-English text, improvements to CJK coverage and spacing, smaller font files,
and additional font formats are welcome. [Open an issue][issues] to discuss a change.

</details>

## Licenses and credits

- The font, Integrated Code 火, is available under the [SIL Open Font License, Version 1.1](OFL-1.1),
  with Reserved Font Name "Integrated".
- Files other than the fonts for which I am the copyright holder are available under the
  [Creative Commons Attribution-NonCommercial 4.0 International Public License](LICENSE).
- Source is a trademark of Adobe in the United States and/or other countries.
- Fira Mono is a trademark of The Mozilla Corporation.

[![SIL Open Font License](.github/OFLLogoRectColor.png)](OFL-1.1)
[![CC-BY-NC-4.0](https://raw.githubusercontent.com/hunterhogan/Integrated_code_fire_font/refs/heads/main/.github/CC-BY-NC-4.0.png)](https://creativecommons.org/licenses/by-nc/4.0/)

By law, authors retain their copyrights unless they grant exceptions. The [Attribution-NonCommercial 4.0 International Deed](https://github.com/hunterhogan/Integrated_code_fire_font#License-1-ov-file) outlines how you may use this work.

The restriction on commercial use (without a license) limits advantage-taking, unjust enrichment, and exploitation. You would be morally wrong if you were to enrich yourself by using this work while I am denied healthcare, housing, security of property, and the safety of my person.

To obtain and retain the right to use this work, you incur the cost of attributing the work to me. Your nominal cost might accrue as a benefit that mitigates my suffering or saves my life.

## My recovery

[![Homeless since 2011 August][recovery-badge]][support]

[releases]: https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest
[japan]: https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest/download/IntegratedCodeFire_Japan.zip
[korea]: https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest/download/IntegratedCodeFire_Korea.zip
[simplified]: https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest/download/IntegratedCodeFire_Simplified_Chinese.zip
[taiwan]: https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest/download/IntegratedCodeFire_Taiwan.zip
[hongkong]: https://github.com/hunterhogan/Integrated_code_fire_font/releases/latest/download/IntegratedCodeFire_Hong_Kong.zip
[issues]: https://github.com/hunterhogan/Integrated_code_fire_font/issues
[Fira Mono]: https://github.com/mozilla/Fira
[Fira Code]: https://github.com/tonsky/FiraCode
[Fira Code HH]: https://github.com/hunterhogan/FiraCode
[Source Han Sans]: https://github.com/adobe-fonts/source-han-sans
[Source Code Pro]: https://github.com/adobe-fonts/source-code-pro
[Source Han Mono]: https://github.com/adobe-fonts/source-han-mono
[Source Han Code JP]: https://github.com/adobe-fonts/source-han-code-jp

[preview]: .github/font-preview.svg
[recovery-badge]: https://img.shields.io/badge/2011_August-Homeless_since-blue?style=flat
[support]: https://HunterThinks.com/support
