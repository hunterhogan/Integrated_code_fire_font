"""Validate CID removal to ensure no CJK glyphs were accidentally removed.

This script checks that:
1. Only non-CJK Unicode ranges were removed
2. Essential CJK blocks are still present
3. The reduction is within expected bounds

Usage:
    python validate_cid_removal.py \
        --before reports/font-identifiers/SourceHanMono-Regular.otf.glyphIdentifiers.json \
        --after reports/font-identifiers/SourceHanMono-Regular-Modified.otf.glyphIdentifiers.json \
        --cid-list cids_to_remove.txt
"""

import json
import argparse
from pathlib import Path
from typing import Set, Dict, List
from collections import defaultdict


# Unicode block ranges for CJK and related scripts
UNICODE_BLOCKS = {
    # CJK Core Blocks
    'CJK_Unified_Ideographs': (0x4E00, 0x9FFF),
    'CJK_Unified_Ideographs_Ext_A': (0x3400, 0x4DBF),
    'CJK_Unified_Ideographs_Ext_B': (0x20000, 0x2A6DF),
    'CJK_Unified_Ideographs_Ext_C': (0x2A700, 0x2B73F),
    'CJK_Unified_Ideographs_Ext_D': (0x2B740, 0x2B81F),
    'CJK_Unified_Ideographs_Ext_E': (0x2B820, 0x2CEAF),
    'CJK_Unified_Ideographs_Ext_F': (0x2CEB0, 0x2EBEF),
    'CJK_Compatibility_Ideographs': (0xF900, 0xFAFF),
    'CJK_Compatibility_Ideographs_Supp': (0x2F800, 0x2FA1F),
    
    # Hangul (Korean)
    'Hangul_Syllables': (0xAC00, 0xD7AF),
    'Hangul_Jamo': (0x1100, 0x11FF),
    'Hangul_Jamo_Extended_A': (0xA960, 0xA97F),
    'Hangul_Jamo_Extended_B': (0xD7B0, 0xD7FF),
    'Hangul_Compatibility_Jamo': (0x3130, 0x318F),
    
    # Kana (Japanese)
    'Hiragana': (0x3040, 0x309F),
    'Katakana': (0x30A0, 0x30FF),
    'Katakana_Phonetic_Extensions': (0x31F0, 0x31FF),
    'Kana_Supplement': (0x1B000, 0x1B0FF),
    'Kana_Extended_A': (0x1B100, 0x1B12F),
    
    # Bopomofo (Taiwanese)
    'Bopomofo': (0x3100, 0x312F),
    'Bopomofo_Extended': (0x31A0, 0x31BF),
    
    # CJK Symbols and Punctuation
    'CJK_Symbols_Punctuation': (0x3000, 0x303F),
    'CJK_Radicals_Supplement': (0x2E80, 0x2EFF),
    'Kangxi_Radicals': (0x2F00, 0x2FDF),
    'Ideographic_Description': (0x2FF0, 0x2FFF),
    
    # Blocks that should be REMOVED (Latin, etc.)
    'Basic_Latin': (0x0000, 0x007F),
    'Latin_1_Supplement': (0x0080, 0x00FF),
    'Latin_Extended_A': (0x0100, 0x017F),
    'Latin_Extended_B': (0x0180, 0x024F),
    'Latin_Extended_Additional': (0x1E00, 0x1EFF),
    'Latin_Extended_C': (0x2C60, 0x2C7F),
    'Latin_Extended_D': (0xA720, 0xA7FF),
    'Latin_Extended_E': (0xAB30, 0xAB6F),
    
    # Fullwidth Forms (keep these - they're for CJK context)
    'Halfwidth_Fullwidth_Forms': (0xFF00, 0xFFEF),
}


def load_font_report(json_path: Path) -> dict:
    """Load a font identifier report JSON file."""
    with json_path.open('r', encoding='utf-8') as f:
        return json.load(f)


def categorize_unicode_by_block(unicode_values: Set[int]) -> Dict[str, Set[int]]:
    """Categorize Unicode values by their block."""
    categorized = defaultdict(set)
    uncategorized = set()
    
    for value in unicode_values:
        found = False
        for block_name, (start, end) in UNICODE_BLOCKS.items():
            if start <= value <= end:
                categorized[block_name].add(value)
                found = True
                break
        if not found:
            uncategorized.add(value)
    
    if uncategorized:
        categorized['Other'] = uncategorized
    
    return dict(categorized)


def extract_unicode_coverage(report: dict) -> Set[int]:
    """Extract all Unicode codepoints covered by a font."""
    unicode_set = set()
    for glyph in report['listGlyph']:
        unicode_set.update(glyph['listUnicodeScalarValue'])
    return unicode_set


def analyze_differences(before_unicode: Set[int], 
                       after_unicode: Set[int]) -> Dict[str, Set[int]]:
    """Analyze what was removed and categorize by Unicode block."""
    removed = before_unicode - after_unicode
    kept = before_unicode & after_unicode
    
    return {
        'removed': categorize_unicode_by_block(removed),
        'kept': categorize_unicode_by_block(kept)
    }


def validate_removal(analysis: Dict[str, Dict[str, Set[int]]]) -> List[str]:
    """Validate that the removal is safe and return any warnings."""
    warnings = []
    removed_blocks = analysis['removed']
    kept_blocks = analysis['kept']
    
    # Check 1: Ensure core CJK blocks are still present
    core_cjk_blocks = [
        'CJK_Unified_Ideographs',
        'Hiragana',
        'Katakana',
        'Hangul_Syllables'
    ]
    
    for block in core_cjk_blocks:
        if block in removed_blocks and len(removed_blocks[block]) > 0:
            warnings.append(f"WARNING: Some glyphs from {block} were removed! This is likely an error.")
            warnings.append(f"  Removed {len(removed_blocks[block])} glyphs from this block.")
        
        if block not in kept_blocks or len(kept_blocks[block]) == 0:
            warnings.append(f"ERROR: {block} is completely missing! This font is broken.")
    
    # Check 2: Ensure Latin blocks were mostly removed
    latin_blocks = [
        'Basic_Latin',
        'Latin_1_Supplement',
        'Latin_Extended_A',
        'Latin_Extended_B'
    ]
    
    for block in latin_blocks:
        if block in kept_blocks and len(kept_blocks[block]) > 10:
            warnings.append(f"INFO: {block} still has {len(kept_blocks[block])} glyphs.")
            warnings.append(f"  This might be intentional (e.g., for fullwidth variants).")
    
    # Check 3: Fullwidth forms should be kept
    if 'Halfwidth_Fullwidth_Forms' in removed_blocks:
        warnings.append("WARNING: Some Halfwidth/Fullwidth forms were removed.")
        warnings.append("  These are important for CJK context and should generally be kept.")
    
    return warnings


def main():
    parser = argparse.ArgumentParser(
        description='Validate CID removal from Source Han Mono'
    )
    parser.add_argument(
        '--before',
        type=Path,
        required=True,
        help='JSON report of original font'
    )
    parser.add_argument(
        '--after',
        type=Path,
        required=True,
        help='JSON report of modified font'
    )
    parser.add_argument(
        '--cid-list',
        type=Path,
        help='Optional: CID list file used for removal'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Optional: Write validation report to file'
    )
    
    args = parser.parse_args()
    
    # Load reports
    print("Loading font reports...")
    before_report = load_font_report(args.before)
    after_report = load_font_report(args.after)
    
    # Extract coverage
    before_unicode = extract_unicode_coverage(before_report)
    after_unicode = extract_unicode_coverage(after_report)
    
    # Analyze differences
    print("\nAnalyzing differences...")
    analysis = analyze_differences(before_unicode, after_unicode)
    
    # Generate report
    report_lines = []
    report_lines.append("="*70)
    report_lines.append("VALIDATION REPORT: CID Removal from Source Han Mono")
    report_lines.append("="*70)
    report_lines.append("")
    
    # Summary statistics
    total_before = len(before_unicode)
    total_after = len(after_unicode)
    total_removed = total_before - total_after
    percent_removed = (total_removed / total_before * 100) if total_before > 0 else 0
    
    report_lines.append("SUMMARY")
    report_lines.append("-"*70)
    report_lines.append(f"Unicode codepoints before: {total_before}")
    report_lines.append(f"Unicode codepoints after:  {total_after}")
    report_lines.append(f"Unicode codepoints removed: {total_removed} ({percent_removed:.1f}%)")
    report_lines.append("")
    
    # Glyph count
    glyph_before = before_report['glyphCount']
    glyph_after = after_report['glyphCount']
    glyph_removed = glyph_before - glyph_after
    glyph_percent = (glyph_removed / glyph_before * 100) if glyph_before > 0 else 0
    
    report_lines.append(f"Glyphs before: {glyph_before}")
    report_lines.append(f"Glyphs after:  {glyph_after}")
    report_lines.append(f"Glyphs removed: {glyph_removed} ({glyph_percent:.1f}%)")
    report_lines.append("")
    
    # Expected range
    if percent_removed < 5:
        report_lines.append("⚠️  Removal percentage seems LOW. Expected ~10-20% for Latin removal.")
    elif percent_removed > 30:
        report_lines.append("⚠️  Removal percentage seems HIGH. Verify no CJK was removed.")
    else:
        report_lines.append("✓ Removal percentage is within expected range.")
    report_lines.append("")
    
    # Removed blocks
    report_lines.append("REMOVED UNICODE BLOCKS")
    report_lines.append("-"*70)
    for block_name, values in sorted(analysis['removed'].items(), 
                                     key=lambda x: len(x[1]), reverse=True):
        count = len(values)
        if count > 0:
            # Check if this is a CJK block
            is_cjk = any(cjk in block_name for cjk in ['CJK', 'Hangul', 'Hiragana', 'Katakana', 'Bopomofo'])
            marker = "⚠️" if is_cjk else "✓"
            report_lines.append(f"{marker} {block_name}: {count} codepoints")
    report_lines.append("")
    
    # Kept blocks (summary)
    report_lines.append("KEPT UNICODE BLOCKS (Summary)")
    report_lines.append("-"*70)
    cjk_blocks_kept = []
    for block_name, values in sorted(analysis['kept'].items(), 
                                     key=lambda x: len(x[1]), reverse=True):
        count = len(values)
        if count > 0:
            is_cjk = any(cjk in block_name for cjk in ['CJK', 'Hangul', 'Hiragana', 'Katakana', 'Bopomofo'])
            if is_cjk:
                cjk_blocks_kept.append((block_name, count))
            # Only show blocks with significant content
            if count > 100:
                report_lines.append(f"  {block_name}: {count} codepoints")
    report_lines.append("")
    
    # Validation warnings
    warnings = validate_removal(analysis)
    if warnings:
        report_lines.append("VALIDATION WARNINGS")
        report_lines.append("-"*70)
        for warning in warnings:
            report_lines.append(warning)
        report_lines.append("")
    else:
        report_lines.append("✓ No validation warnings - removal looks good!")
        report_lines.append("")
    
    # CJK blocks verification
    report_lines.append("CJK BLOCKS VERIFICATION")
    report_lines.append("-"*70)
    for block_name, count in cjk_blocks_kept:
        report_lines.append(f"✓ {block_name}: {count} codepoints kept")
    report_lines.append("")
    
    # Print report
    report_text = "\n".join(report_lines)
    print(report_text)
    
    # Write to file if requested
    if args.output:
        with args.output.open('w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"\nValidation report written to: {args.output}")
    
    # Exit with error code if there are critical warnings
    critical_warnings = [w for w in warnings if 'ERROR' in w or 
                         ('WARNING' in w and 'CJK' in w)]
    if critical_warnings:
        print("\n❌ CRITICAL ISSUES DETECTED - Please review the warnings above!")
        return 1
    else:
        print("\n✓ Validation passed!")
        return 0


if __name__ == '__main__':
    exit(main())
