# Workflow: Removing Conflicting Glyphs from Source Han Mono

This document describes how to use `fontIdentifierReport.py` and the companion scripts to identify and remove glyphs from Source Han Mono that will be provided by Fira Code.

## Overview

Your strategy is correct: by removing Latin/ASCII glyphs from Source Han Mono *before* compilation, you avoid conflicts during the merge and reduce the size of the intermediate Source Han Mono font.

## Prerequisites

1. Compiled Fira Code fonts (`.ttf` or `.otf` files)
2. Source Han Mono source files (the repository structure with all 70 combinations)
3. Python environment with fontTools installed (`uv sync` as mentioned in your README)

## Step-by-Step Workflow

### Step 1: Set Up Your Workspace

```bash
# Ensure your directory structure looks like this:
# .
# ├── fontIdentifierReport.py
# ├── compare_font_coverage.py
# ├── remove_cids_from_source.py
# ├── workbench/
# │   ├── FiraCode/
# │   │   ├── FiraCode-Regular.ttf
# │   │   ├── FiraCode-Bold.ttf
# │   │   └── ... (other weights)
# │   └── SourceHanMono/
# │       ├── SourceHanMono-Regular.otf
# │       ├── SourceHanMono-Bold.otf
# │       └── ... (sample compiled fonts for analysis)
# └── SourceHanMono/
#     ├── metadata/
#     │   └── AI0-SourceHanMono
#     └── Resources/
#         └── ... (source files for 70 combinations)
```

### Step 2: Generate Font Identifier Reports

```bash
# This will scan workbench/ and create reports in reports/font-identifiers/
python fontIdentifierReport.py
```

This creates:
- `reports/font-identifiers/FiraCode-Regular.ttf.glyphIdentifiers.csv`
- `reports/font-identifiers/FiraCode-Regular.ttf.glyphIdentifiers.json`
- `reports/font-identifiers/SourceHanMono-Regular.otf.glyphIdentifiers.csv`
- `reports/font-identifiers/SourceHanMono-Regular.otf.glyphIdentifiers.json`
- ... (for all fonts in workbench/)

### Step 3: Analyze Coverage and Identify Conflicting CIDs

```bash
# Compare Fira Code Regular with Source Han Mono Regular
python compare_font_coverage.py \
    --fira-code reports/font-identifiers/FiraCode-Regular.ttf.glyphIdentifiers.json \
    --source-han-mono reports/font-identifiers/SourceHanMono-Regular.otf.glyphIdentifiers.json \
    --output cids_to_remove.txt \
    --detailed

# This creates:
# - cids_to_remove.txt (list of CIDs to remove)
# - cids_to_remove.detailed.txt (detailed report with Unicode mappings)
```

### Step 4: Review the CID List

Open `cids_to_remove.txt` and `cids_to_remove.detailed.txt` to verify:

```bash
# View summary
head -20 cids_to_remove.txt

# View detailed mappings
head -50 cids_to_remove.detailed.txt

# Count how many CIDs will be removed
grep -v '^#' cids_to_remove.txt | grep -v '^$' | wc -l
```

**Expected CID ranges to remove:**
- Basic Latin (A-Z, a-z, 0-9, punctuation): ~100 CIDs
- Latin-1 Supplement: ~100 CIDs
- Latin Extended-A/B: ~200-300 CIDs
- Math operators, arrows, box drawing: ~200 CIDs
- Various symbols and punctuation: ~200-500 CIDs
- **Total: ~800-1500 CIDs** (exact number depends on Fira Code's coverage)

### Step 5: Remove CIDs from Source Han Mono Source Files

**IMPORTANT: This step modifies your source files. Make sure you have backups!**

```bash
# Dry run first to see what would happen
python remove_cids_from_source.py \
    --cid-list cids_to_remove.txt \
    --source-dir SourceHanMono \
    --backup-dir SourceHanMono_backup \
    --dry-run

# If everything looks good, do the actual removal
python remove_cids_from_source.py \
    --cid-list cids_to_remove.txt \
    --source-dir SourceHanMono \
    --backup-dir SourceHanMono_backup
```

This will:
1. Create a backup at `SourceHanMono_backup/`
2. Edit `AI0-SourceHanMono` ordering file
3. Edit all 70 `cidfont.ps` files
4. Edit all 10 sets of Unicode mapping files (`UTF16.H`, `UTF32.H`, `UTF32.map`)
5. Edit all 10 `sequences.txt` files

### Step 6: Verify the Changes

```bash
# Check that the ordering file was modified
wc -l SourceHanMono_backup/metadata/AI0-SourceHanMono
wc -l SourceHanMono/metadata/AI0-SourceHanMono

# The second number should be smaller by the number of CIDs removed

# Spot-check a cidfont.ps file
diff SourceHanMono_backup/Resources/.../cidfont.ps \
     SourceHanMono/Resources/.../cidfont.ps | head -50
```

### Step 7: Recompile Source Han Mono

Now compile your modified Source Han Mono using your existing build process:

```bash
# Your compilation command (from your go.py or build script)
# This will create .otf files without the conflicting glyphs
```

### Step 8: Verify No Conflicts

After compilation, run the identifier report again to verify:

```bash
# Place newly compiled Source Han Mono in workbench/
python fontIdentifierReport.py

# Check for remaining overlaps
python compare_font_coverage.py \
    --fira-code reports/font-identifiers/FiraCode-Regular.ttf.glyphIdentifiers.json \
    --source-han-mono reports/font-identifiers/SourceHanMono-Regular.NEW.otf.glyphIdentifiers.json \
    --output verification.txt

# This should show 0 or very few conflicts
```

## Understanding the Files to Edit

### 1. AI0-SourceHanMono (Ordering File)
- Location: `SourceHanMono/metadata/AI0-SourceHanMono`
- Format: Tab-separated values: `<CID>\t<glyph_name>`
- Purpose: Defines the CID-to-glyph-name mapping
- **Action:** Remove lines where the CID is in your removal list

### 2. cidfont.ps Files
- Location: `SourceHanMono/Resources/<region>/<style>/<weight>/cidfont.ps`
- Count: 70 files (7 weights × 5 regions × 2 styles)
- Format: PostScript-like syntax with glyph definitions
- Purpose: Contains the actual glyph outlines
- **Action:** Remove glyph definitions for CIDs in your removal list

### 3. Unicode Mapping Files
- Locations:
  - `SourceHanMono/Resources/<region>/<style>/sequences.txt`
  - `SourceHanMono/Resources/<region>/<style>/UTF16.H`
  - `SourceHanMono/Resources/<region>/<style>/UTF32.H`
  - `SourceHanMono/Resources/<region>/<style>/UTF32.map`
- Count: 10 sets (5 regions × 2 styles)
- Purpose: Map Unicode codepoints to CIDs
- **Action:** Remove mappings where the CID is in your removal list

### 4. Features Files
- Location: `SourceHanMono/Resources/<region>/<style>/<weight>/features`
- Count: 70 files
- Purpose: OpenType feature definitions (ligatures, substitutions, etc.)
- **Action:** May need manual review if features reference removed CIDs

## Tips and Considerations

### Which Weight to Analyze?
- Use **Regular** weight for your initial analysis
- The Unicode coverage should be identical across weights
- The same CID list applies to all 70 combinations

### Conservative vs. Aggressive Removal
- **Conservative:** Only remove CIDs that map to ASCII/Latin (U+0000-U+00FF)
- **Recommended:** Remove all CIDs covered by Fira Code (includes math, arrows, box drawing)
- **Aggressive:** Remove even more to minimize Source Han Mono size (requires careful analysis)

### Double-Width Glyphs
Source Han Mono has some "fullwidth" versions of Latin characters (e.g., U+FF21-FF5A). These are *not* the same as regular ASCII:
- **U+0041** (A) - Regular Latin A → Remove (Fira Code provides)
- **U+FF21** (Ａ) - Fullwidth Latin A → Keep (Source Han Mono provides)

The script should handle this correctly by checking exact Unicode values.

### Features and Ligatures
Fira Code has programming ligatures (==, !=, >=, etc.). Make sure:
1. These ligatures are in your Fira Code → Source Han Mono merge
2. Source Han Mono features don't conflict with Fira Code features

### Testing
After modification, test your merged font with:
- Code samples using ASCII/Latin
- Code samples using CJK characters
- Mixed content (e.g., Chinese variable names with English operators)

## Troubleshooting

### "Too Many CIDs Removed"
If you accidentally remove CJK CIDs:
1. Restore from backup: `rm -rf SourceHanMono && cp -r SourceHanMono_backup SourceHanMono`
2. Review your `cids_to_remove.txt` - check for CIDs with high numbers
3. Verify Unicode ranges in the detailed report

### "Not Enough CIDs Removed"
If Latin characters still conflict:
1. Check that you analyzed the correct Fira Code variant (Regular, not Retina)
2. Look at `cids_to_remove.detailed.txt` to see exact Unicode coverage
3. Manually add missing CIDs if needed

### "Compilation Fails After Modification"
If the modified source files won't compile:
1. Check for syntax errors in edited `.ps` files
2. Verify that references in `features` files are still valid
3. Ensure all cross-references between files are consistent
4. Restore from backup and try a more conservative removal

## Next Steps

After successfully removing conflicting glyphs:

1. **Compile pan-CJK with reduced glyphs** (your Step 1.2 in README)
2. **Extract ~2600 glyphs from Fira Code** (your Step 2)
3. **Merge the fonts** (your Step 3)
4. **Compile final pan-CJK + Fira Code** (your Step 4)

## Additional Resources

- [fontTools Documentation](https://fonttools.readthedocs.io/)
- [Source Han Mono Repository](https://github.com/adobe-fonts/source-han-mono)
- [Fira Code Repository](https://github.com/tonsky/FiraCode)
- Your project README for overall goals and structure

## Summary

Yes, you can absolutely use `fontIdentifierReport.py` to figure out what to change! The workflow is:

1. ✅ Generate reports for both fonts
2. ✅ Compare Unicode coverage
3. ✅ Identify conflicting CIDs
4. ✅ Edit Source Han Mono source files
5. ✅ Recompile with reduced glyphs
6. ✅ Merge with Fira Code

This approach is much cleaner than trying to resolve conflicts post-merge!
