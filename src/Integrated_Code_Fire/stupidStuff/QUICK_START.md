# Quick Start: Using fontIdentifierReport.py for Your Font Merge

## TL;DR - Yes, you can use it

**Answer to your question:** Yes, `fontIdentifierReport.py` is EXACTLY the right tool for identifying which glyphs to remove from Source Han Mono. Your strategy is sound.

## What You Get

I've created three Python scripts to work with `fontIdentifierReport.py`:

1. **`compare_font_coverage.py`** - Compares Fira Code and Source Han Mono to identify conflicting CIDs
2. **`remove_cids_from_source.py`** - Edits Source Han Mono source files to remove those CIDs
3. **`validate_cid_removal.py`** - Validates that you didn't accidentally remove CJK glyphs

## Quick Workflow

```bash
# 1. Generate reports for both fonts
python fontIdentifierReport.py

# 2. Compare and get CID removal list
python src\Integrated_Code_Fire\compare_font_coverage.py ^
    --fira-code C:\apps\Integrated_Code_Fire\reports\font-identifiers\FiraCode-Regular.otf.glyphIdentifiers.json ^
    --source-han-mono C:\apps\Integrated_Code_Fire\reports\font-identifiers\Simplified_Chinese.Regular.SourceHanMono.otf.glyphIdentifiers.json ^
    --output cids_to_remove.txt ^
    --detailed

# 3. Remove CIDs from source files (creates backup automatically)
python remove_cids_from_source.py \
    --cid-list cids_to_remove.txt \
    --source-dir SourceHanMono

# 4. Recompile Source Han Mono with your existing build process

# 5. Validate the result
python validate_cid_removal.py \
    --before reports/font-identifiers/SourceHanMono-Regular.otf.glyphIdentifiers.json \
    --after reports/font-identifiers/SourceHanMono-Regular-NEW.otf.glyphIdentifiers.json
```

## Which Files Get Edited

The `remove_cids_from_source.py` script will edit:

- ✅ `AI0-SourceHanMono` - The main CID ordering file
- ✅ All 70 `cidfont.ps` files - Glyph definitions (7 weights × 5 regions × 2 styles)
- ✅ All 10 sets of Unicode mapping files - `UTF16.H`, `UTF32.H`, `UTF32.map`
- ✅ All 10 `sequences.txt` files - Glyph sequences

## What Gets Removed

Expected: **~800-1500 CIDs** covering:

- Basic Latin (ASCII: A-Z, a-z, 0-9, punctuation)
- Latin-1 Supplement (accented characters)
- Latin Extended (additional accented characters)
- Math operators, arrows, box drawing
- Various symbols Fira Code provides

**NOT removed:** All CJK characters, Hiragana, Katakana, Hangul, Bopomofo, etc.

## Safety Features

- **Automatic backup** before making changes
- **Dry run mode** to preview changes
- **Validation script** to catch accidental CJK removal
- **Detailed reports** showing exactly what was removed

## Expected Results

After removal and recompilation:

- Source Han Mono: ~20,000 glyphs (down from ~21,000)
- No overlap with Fira Code's ~2,600 glyphs
- Clean merge possible without conflicts
- Smaller intermediate font files

## See Full Documentation

Read `WORKFLOW_GLYPH_REMOVAL.md` for:

- Detailed step-by-step instructions
- Troubleshooting guide
- Understanding of each file type
- Tips for conservative vs. aggressive removal

## Why This Approach Works

Your insight is correct! By removing conflicting glyphs from Source Han Mono's **source files** before compilation:

1. ✅ No runtime glyph conflicts during merge
2. ✅ Smaller intermediate font files
3. ✅ Cleaner Unicode mapping tables
4. ✅ Easier to debug issues
5. ✅ More maintainable pipeline

This is much better than trying to resolve conflicts after both fonts are compiled!

## Questions?

The scripts include:

- `--help` flags for all options
- Detailed docstrings
- Error checking and validation
- Progress reporting

Start with the `--dry-run` flag to see what would happen before making actual changes.
