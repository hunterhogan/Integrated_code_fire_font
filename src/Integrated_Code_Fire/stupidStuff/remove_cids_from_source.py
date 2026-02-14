"""Remove specified CIDs from Source Han Mono source files.

This script edits the various Source Han Mono source files to remove glyphs
that will be provided by Fira Code, preventing conflicts during font merging.

Files edited:
- AI0-SourceHanMono (ordering file)
- cidfont.ps files (for all 70 weight/region/style combinations)
- sequences.txt files (10 region/style combinations)
- UTF16.H, UTF32.H, UTF32.map files (10 region/style combinations)

Usage:
    python remove_cids_from_source.py \
        --cid-list cids_to_remove.txt \
        --source-dir SourceHanMono \
        --backup-dir SourceHanMono_backup
"""

from pathlib import Path
from typing import List, Set
import argparse
import regex
import shutil

def load_cid_list(cid_list_path: Path) -> Set[int]:
    """Load the list of CIDs to remove from a text file."""
    cids = set()
    with cid_list_path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    cids.add(int(line))
                except ValueError:
                    continue
    return cids


def backup_directory(source_dir: Path, backup_dir: Path) -> None:
    """Create a backup of the entire source directory."""
    if backup_dir.exists():
        print(f"Backup directory {backup_dir} already exists. Skipping backup.")
        return

    print(f"Creating backup: {source_dir} -> {backup_dir}")
    shutil.copytree(source_dir, backup_dir)
    print("Backup complete.")


def edit_ordering_file(ordering_file: Path, cids_to_remove: Set[int]) -> int:
    """Edit the AI0-SourceHanMono ordering file to remove specified CIDs.

    Returns the number of lines removed.
    """
    if not ordering_file.exists():
        print(f"Warning: Ordering file not found: {ordering_file}")
        return 0

    lines_kept = []
    lines_removed = 0

    with ordering_file.open('r', encoding='utf-8', newline='\n') as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                lines_kept.append(line)
                continue

            parts = stripped.split('\t')
            if len(parts) < 2:
                lines_kept.append(line)
                continue

            try:
                cid = int(parts[0])
                if cid in cids_to_remove:
                    lines_removed += 1
                    continue
            except ValueError:
                pass

            lines_kept.append(line)

    # Write the filtered content back
    with ordering_file.open('w', encoding='utf-8', newline='\n') as f:
        f.writelines(lines_kept)

    return lines_removed


def edit_cidfont_ps_file(ps_file: Path, cids_to_remove: Set[int]) -> int:
    """Edit a cidfont.ps file to remove glyph definitions for specified CIDs.

    This is more complex as it needs to parse PostScript-like syntax.
    Returns the number of glyph definitions removed.
    """
    if not ps_file.exists():
        return 0

    # Read the entire file
    with ps_file.open('r', encoding='utf-8', newline='\n') as f:
        content = f.read()

    # Pattern to match CID glyph definitions
    # This is a simplified pattern and may need adjustment based on actual file format
    # Typical pattern: <CID> { ... } def
    removed_count = 0

    # Split into lines for processing
    lines = content.split('\n')
    filtered_lines = []
    in_glyph_def = False
    current_cid = None
    glyph_def_lines = []

    for line in lines:
        # Check if this starts a glyph definition
        # Pattern: "/<cidNNNN> {" or similar
        cid_start_match = regex.match(r'^/cid(\d+)\s*\{', line.strip())
        if cid_start_match:
            current_cid = int(cid_start_match.group(1))
            in_glyph_def = True
            glyph_def_lines = [line]
            continue

        if in_glyph_def:
            glyph_def_lines.append(line)
            # Check if this closes the definition
            if '}' in line:
                if current_cid in cids_to_remove:
                    removed_count += 1
                    # Don't add these lines to output
                else:
                    filtered_lines.extend(glyph_def_lines)

                in_glyph_def = False
                current_cid = None
                glyph_def_lines = []
            continue

        filtered_lines.append(line)

    # Write back
    with ps_file.open('w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(filtered_lines))

    return removed_count


def edit_unicode_mapping_file(mapping_file: Path, cids_to_remove: Set[int]) -> int:
    """Edit UTF16.H, UTF32.H, or UTF32.map files to remove mappings for specified CIDs.

    These files typically have lines like:
    <unicode_value> <cid>

    Returns the number of mappings removed.
    """
    if not mapping_file.exists():
        return 0

    lines_kept = []
    lines_removed = 0

    with mapping_file.open('r', encoding='utf-8', newline='\n') as f:
        for line in f:
            # Skip empty lines and comments
            stripped = line.strip()
            if not stripped or stripped.startswith('%'):
                lines_kept.append(line)
                continue

            # Try to extract CID from the line
            # Format varies, but typically: <hex> <cid> or similar
            parts = stripped.split()
            if len(parts) >= 2:
                try:
                    # The CID is usually the last numeric value
                    cid = int(parts[-1])
                    if cid in cids_to_remove:
                        lines_removed += 1
                        continue
                except ValueError:
                    pass

            lines_kept.append(line)

    with mapping_file.open('w', encoding='utf-8', newline='\n') as f:
        f.writelines(lines_kept)

    return lines_removed


def edit_sequences_file(sequences_file: Path, cids_to_remove: Set[int]) -> int:
    """Edit sequences.txt file to remove sequences referencing removed CIDs.

    Returns the number of sequences removed.
    """
    if not sequences_file.exists():
        return 0

    lines_kept = []
    lines_removed = 0

    with sequences_file.open('r', encoding='utf-8', newline='\n') as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                lines_kept.append(line)
                continue

            # Check if any CID in the line should be removed.
            # CIDs in sequences might appear as standalone numbers.
            should_remove = False
            for cid_as_string in regex.findall(r'\b\d+\b', stripped):
                if int(cid_as_string) in cids_to_remove:
                    should_remove = True
                    break

            if should_remove:
                lines_removed += 1
                continue

            lines_kept.append(line)

    with sequences_file.open('w', encoding='utf-8', newline='\n') as f:
        f.writelines(lines_kept)

    return lines_removed


def process_source_directory(source_dir: Path, cids_to_remove: Set[int]) -> dict:
    """Process all relevant files in the Source Han Mono directory structure.

    Returns a dictionary with counts of changes made.
    """
    results = {
        'ordering_file': 0,
        'cidfont_ps': 0,
        'unicode_mappings': 0,
        'sequences': 0
    }

    # 1. Edit AI0-SourceHanMono ordering file
    ordering_file = source_dir / 'metadata' / 'AI0-SourceHanMono'
    if ordering_file.exists():
        count = edit_ordering_file(ordering_file, cids_to_remove)
        results['ordering_file'] = count
        print(f"Removed {count} lines from {ordering_file}")

    # 2. Edit cidfont.ps files (70 combinations)
    cidfont_dir = source_dir / 'Resources'
    if cidfont_dir.exists():
        for ps_file in cidfont_dir.rglob('cidfont.ps'):
            count = edit_cidfont_ps_file(ps_file, cids_to_remove)
            results['cidfont_ps'] += count
            if count > 0:
                print(f"Removed {count} glyphs from {ps_file}")

    # 3. Edit Unicode mapping files
    for mapping_pattern in ['UTF16.H', 'UTF32.H', 'UTF32.map']:
        for mapping_file in source_dir.rglob(mapping_pattern):
            count = edit_unicode_mapping_file(mapping_file, cids_to_remove)
            results['unicode_mappings'] += count
            if count > 0:
                print(f"Removed {count} mappings from {mapping_file}")

    # 4. Edit sequences.txt files
    for sequences_file in source_dir.rglob('sequences.txt'):
        count = edit_sequences_file(sequences_file, cids_to_remove)
        results['sequences'] += count
        if count > 0:
            print(f"Removed {count} sequences from {sequences_file}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Remove specified CIDs from Source Han Mono source files'
    )
    parser.add_argument(
        '--cid-list',
        type=Path,
        required=True,
        help='Text file with CIDs to remove (one per line)'
    )
    parser.add_argument(
        '--source-dir',
        type=Path,
        default=Path('SourceHanMono'),
        help='Path to Source Han Mono directory (default: SourceHanMono)'
    )
    parser.add_argument(
        '--backup-dir',
        type=Path,
        default=Path('SourceHanMono_backup'),
        help='Path for backup (default: SourceHanMono_backup)'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating a backup (not recommended)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    args = parser.parse_args()

    # Load CID list
    print(f"Loading CID list from: {args.cid_list}")
    cids_to_remove = load_cid_list(args.cid_list)
    print(f"Loaded {len(cids_to_remove)} CIDs to remove")

    if not args.source_dir.exists():
        print(f"Error: Source directory not found: {args.source_dir}")
        return

    if args.dry_run:
        print("\n*** DRY RUN MODE - No changes will be made ***\n")

    # Create backup
    if not args.no_backup and not args.dry_run:
        backup_directory(args.source_dir, args.backup_dir)

    # Process files
    print("\nProcessing source files...")
    if not args.dry_run:
        results = process_source_directory(args.source_dir, cids_to_remove)

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Ordering file entries removed: {results['ordering_file']}")
        print(f"Glyph definitions removed: {results['cidfont_ps']}")
        print(f"Unicode mappings removed: {results['unicode_mappings']}")
        print(f"Sequences removed: {results['sequences']}")
        print("\nSource files have been updated.")
        if not args.no_backup:
            print(f"Backup saved to: {args.backup_dir}")
    else:
        print("Dry run complete. Use without --dry-run to make actual changes.")


if __name__ == '__main__':
    main()
