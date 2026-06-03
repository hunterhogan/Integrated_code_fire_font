"""Extract CIDs of vertical-only glyphs from Source Han Mono feature files.

This module parses OpenType feature files to identify glyphs that are used
exclusively for vertical text layout.
"""

from __future__ import annotations

from pathlib import Path
import argparse
import json
import re as regex

class VerticalGlyphExtractor:
    """Extract vertical-only glyph CIDs from OpenType feature files."""

    def __init__(self, repo_root: Path | None = None):
        self.repo_root = Path(repo_root) if repo_root else Path(__file__).parent
        self.vertical_cids: set[int] = set()
        self.glyph_classes: dict[str, set[int]] = {}

    def parse_glyph_class(self, class_def: str) -> set[int]:
        """Parse a glyph class definition and extract CIDs."""
        cids = set()
        for match in regex.finditer(r'\\(\d+)(?:-\\(\d+))?', class_def):
            start_cid = int(match.group(1))
            end_cid = int(match.group(2)) if match.group(2) else start_cid
            cids.update(range(start_cid, end_cid + 1))
        return cids

    def extract_classes_from_feature(self, content: str) -> dict[str, set[int]]:
        """Extract glyph class definitions from feature file content."""
        classes = {}
        pattern = r'@(\w+)\s*=\s*\[((?:[^\[\]]|\[[^\]]*\])*)\];'

        for match in regex.finditer(pattern, content, regex.MULTILINE):
            class_name = match.group(1)
            class_body = match.group(2)
            classes[class_name] = self.parse_glyph_class(class_body)

        return classes

    def extract_substitutions_from_content(self, content: str) -> set[int]:
        """Extract vertical glyph CIDs from feature lookups."""
        vertical_cids = set()

        # Pattern 1: substitute \CID1 by \CID2;
        for match in regex.finditer(r'substitute\s+\\(\d+)\s+by\s+\\(\d+);', content):
            target_cid = int(match.group(2))
            vertical_cids.add(target_cid)

        # Pattern 2: substitute @ClassA by @ClassB;
        for match in regex.finditer(r'substitute\s+@(\w+)\s+by\s+@(\w+);', content):
            target_class = match.group(2)
            if target_class in self.glyph_classes:
                vertical_cids.update(self.glyph_classes[target_class])

        return vertical_cids

    def extract_from_feature_block(self, content: str, feature_name: str) -> set[int]:
        """Extract vertical glyphs from a specific feature block."""
        pattern = rf'feature\s+{feature_name}\s*\{{((?:[^{{}}]|\{{[^{{}}]*\}})*)\}}\s*{feature_name};'
        match = regex.search(pattern, content, regex.DOTALL)

        if not match:
            return set()

        feature_content = match.group(1)
        vertical_cids = self.extract_substitutions_from_content(feature_content)

        # Also extract from referenced lookups
        lookup_refs = regex.findall(r'lookup\s+(vert_\w+);', feature_content)
        for lookup_name in lookup_refs:
            lookup_pattern = rf'lookup\s+{lookup_name}\s*\{{((?:[^{{}}]|\{{[^{{}}]*\}})*)\}}\s*{lookup_name};'
            lookup_match = regex.search(lookup_pattern, content, regex.DOTALL)
            if lookup_match:
                vertical_cids.update(
                    self.extract_substitutions_from_content(lookup_match.group(1))
                )

        return vertical_cids

    def parse_feature_file(self, filepath: Path) -> set[int]:
        """Parse a single feature file and extract vertical glyph CIDs."""
        try:
            content = filepath.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Warning: Could not read {filepath}: {e}")
            return set()

        self.glyph_classes = self.extract_classes_from_feature(content)

        vertical_cids = set()
        vertical_cids.update(self.extract_from_feature_block(content, 'vert'))
        vertical_cids.update(self.extract_from_feature_block(content, 'vrt2'))

        return vertical_cids

    def find_all_feature_files(self) -> list[Path]:
        """Find all feature files in the repository."""
        feature_files = []
        weight_dirs = ['ExtraLight', 'Light', 'Normal', 'Regular', 'Medium', 'Bold', 'Heavy']

        for weight in weight_dirs:
            weight_path = self.repo_root / weight / 'OTC'
            if weight_path.exists():
                feature_files.extend(weight_path.glob('features.OTC.*'))

        return feature_files

    def extract_all_vertical_glyphs(self) -> set[int]:
        """Extract vertical glyph CIDs from all feature files."""
        all_vertical_cids = set()
        feature_files = self.find_all_feature_files()

        print(f"Found {len(feature_files)} feature files to process")

        for filepath in feature_files:
            print(f"Processing {filepath.relative_to(self.repo_root)}...")
            cids = self.parse_feature_file(filepath)
            all_vertical_cids.update(cids)
            print(f"  Found {len(cids)} vertical glyphs")

        self.vertical_cids = all_vertical_cids
        return all_vertical_cids

    def get_statistics(self) -> dict[str, int]:
        """Get statistics about vertical glyphs."""
        return {
            'total_vertical_glyphs': len(self.vertical_cids),
            'min_cid': min(self.vertical_cids) if self.vertical_cids else 0,
            'max_cid': max(self.vertical_cids) if self.vertical_cids else 0,
        }

    def export_to_file(self, output_path: Path, format: str = 'text'):
        """Export vertical glyph CIDs to a file."""
        if format == 'text':
            with output_path.open('w') as f:
                f.write("# Vertical-only glyph CIDs in Source Han Mono\n")
                f.write(f"# Total: {len(self.vertical_cids)} glyphs\n\n")
                for cid in sorted(self.vertical_cids):
                    f.write(f"{cid}\n")

        elif format == 'csv':
            with output_path.open('w') as f:
                f.write("CID\n")
                for cid in sorted(self.vertical_cids):
                    f.write(f"{cid}\n")

        elif format == 'json':
            output_path.write_text(json.dumps({
                'vertical_cids': sorted(list(self.vertical_cids)),
                'statistics': self.get_statistics()
            }, indent=2))

        print(f"Exported {len(self.vertical_cids)} CIDs to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Extract vertical-only glyph CIDs from Source Han Mono'
    )
    parser.add_argument('--repo-root', type=Path, help='Path to repository root')
    parser.add_argument('--output', type=Path, help='Output file path')
    parser.add_argument('--format', choices=['text', 'csv', 'json'], default='text')
    parser.add_argument('--stats-only', action='store_true', help='Only show statistics')

    args = parser.parse_args()

    extractor = VerticalGlyphExtractor(args.repo_root)

    print("Extracting vertical-only glyphs from feature files...")
    vertical_cids = extractor.extract_all_vertical_glyphs()

    print("\n" + "=" * 50)
    print("Statistics:")
    for key, value in extractor.get_statistics().items():
        print(f"  {key}: {value}")
    print("=" * 50)

    if not args.stats_only:
        output_path = args.output or Path('vertical_glyphs.txt')
        extractor.export_to_file(output_path, args.format)
        print(f"\nResults written to {output_path}")

    if vertical_cids:
        sample = sorted(list(vertical_cids))[:10]
        print(f"\nSample CIDs (first 10): {sample}")


if __name__ == '__main__':
    main()
