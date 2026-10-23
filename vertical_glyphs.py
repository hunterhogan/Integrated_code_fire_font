# ruff: file-ignore[no-self-use]
# ruff: file-ignore[print]
"""Inspect the glyph targets of Source Han Mono vertical substitutions.

(AI generated docstring)

You can scan the Source Han Mono feature files for the `vert` and `vrt2` features, collect their
CID substitution targets, and export a candidate exclusion list for horizontal fonts. A target
of a vertical substitution is not proof that a glyph has no horizontal use.

Contents
--------
Classes
	VerticalGlyphExtractor
		Collect and export CIDs referenced by vertical substitutions.
Functions
	main
		Run extraction and reporting from command-line arguments.
"""

from __future__ import annotations

from pathlib import Path
import argparse
import json
import re as regex

class VerticalGlyphExtractor:
	"""Collect glyph targets from Source Han Mono vertical feature definitions.

	(AI generated docstring)

	You can inspect direct CID substitutions and class substitutions in `vert` and `vrt2` features,
	including referenced lookups whose names begin with `"vert_"`. The parser recognizes the feature
	syntax used by the source files; the parser is not a general OpenType feature compiler.

	Attributes
	----------
	repo_root : Path
		Source Han Mono checkout containing the weight directories.
	vertical_cids : set[int]
		Combined target CIDs stored by the most recent full extraction. Initially empty.
	glyph_classes : dict[str, set[int]]
		Class names mapped to CIDs for the most recently parsed feature file. Initially empty.
	"""

	def __init__(self, repo_root: Path | None = None) -> None:
		"""Select a Source Han Mono checkout and start with empty extraction results.

		(AI generated docstring)

		Parameters
		----------
		repo_root : Path
			Source checkout. Omitted input and `None` use the directory containing this script.
		"""
		self.repo_root = Path(repo_root) if repo_root else Path(__file__).parent
		self.vertical_cids: set[int] = set()
		self.glyph_classes: dict[str, set[int]] = {}

	def parse_glyph_class(self, class_def: str) -> set[int]:
		"""Read decimal CID references and inclusive CID ranges from a glyph class.

		(AI generated docstring)

		Parameters
		----------
		class_def : str
			Class body containing backslash-prefixed CID numbers and optional CID ranges.

		Returns
		-------
		cids : set[int]
			Referenced CIDs, with each range expanded to include both endpoints.
		"""
		cids: set[int] = set()
		for match in regex.finditer(r'\\(\d+)(?:-\\(\d+))?', class_def):
			start_cid = int(match.group(1))
			end_cid = int(match.group(2)) if match.group(2) else start_cid
			cids.update(range(start_cid, end_cid + 1))
		return cids

	def extract_classes_from_feature(self, content: str) -> dict[str, set[int]]:
		"""Read named glyph classes from feature text.

		(AI generated docstring)

		Parameters
		----------
		content : str
			Feature file text containing class definitions with CID references.

		Returns
		-------
		classes : dict[str, set[int]]
			Class names without the `@` prefix mapped to their CIDs. Later definitions replace
			earlier definitions with the same name. The stored `glyph_classes` is unchanged.
		"""
		classes: dict[str, set[int]] = {}
		pattern = r'@(\w+)\s*=\s*\[((?:[^\[\]]|\[[^\]]*\])*)\];'

		for match in regex.finditer(pattern, content, regex.MULTILINE):
			class_name = match.group(1)
			class_body = match.group(2)
			classes[class_name] = self.parse_glyph_class(class_body)

		return classes

	def extract_substitutions_from_content(self, content: str) -> set[int]:
		"""Collect the target CIDs of direct and class-to-class substitutions.

		(AI generated docstring)

		Parameters
		----------
		content : str
			Feature or lookup text using the `substitute ... by ...;` form.

		Returns
		-------
		vertical_cids : set[int]
			Direct target CIDs and members of target classes present in `glyph_classes`. Undefined
			target classes contribute no CIDs. Source CIDs are not included merely for being sources.
		"""
		vertical_cids: set[int] = set()

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
		"""Collect substitution targets from a named feature and its vertical lookups.

		(AI generated docstring)

		Parameters
		----------
		content : str
			Complete feature file text containing the feature block and lookup definitions.
		feature_name : str
			Feature tag to inspect, normally `"vert"` or `"vrt2"`.

		Returns
		-------
		vertical_cids : set[int]
			Targets from the first matching feature block and referenced lookups whose names begin
			with `"vert_"`. A missing feature produces an empty set. Class substitutions use the
			currently stored `glyph_classes`.
		"""
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
		"""Collect vertical substitution targets from one feature file.

		(AI generated docstring)

		Parameters
		----------
		filepath : Path
			UTF-8 Source Han Mono feature file.

		Returns
		-------
		vertical_cids : set[int]
			Combined targets from `vert` and `vrt2` features. The stored `vertical_cids` is unchanged.

		Input Mutation
		--------------
		The extractor replaces `glyph_classes` with the class definitions in this feature file.
		"""
		content = filepath.read_text(encoding='utf-8')

		self.glyph_classes = self.extract_classes_from_feature(content)

		vertical_cids: set[int] = set()
		vertical_cids.update(self.extract_from_feature_block(content, 'vert'))
		vertical_cids.update(self.extract_from_feature_block(content, 'vrt2'))

		return vertical_cids

	def find_all_feature_files(self) -> list[Path]:
		"""Locate Source Han Mono collection feature files across the seven source weights.

		(AI generated docstring)

		Returns
		-------
		feature_files : list[Path]
			Paths matching `features.OTC.*` in each existing weight directory's `OTC` subdirectory.
			Missing weight directories contribute no paths. No matches produce an empty list.
		"""
		feature_files: list[Path] = []
		weight_dirs = ['ExtraLight', 'Light', 'Normal', 'Regular', 'Medium', 'Bold', 'Heavy']

		for weight in weight_dirs:
			weight_path = self.repo_root / weight / 'OTC'
			if weight_path.exists():
				feature_files.extend(weight_path.glob('features.OTC.*'))

		return feature_files

	def extract_all_vertical_glyphs(self) -> set[int]:
		"""Collect and store vertical substitution targets from all matching feature files.

		(AI generated docstring)

		Returns
		-------
		all_vertical_cids : set[int]
			Union of the target CIDs found across the source files. The returned set is also stored
			as `vertical_cids`.

		Extraction State
		----------------
		The extractor replaces `vertical_cids` and retains `glyph_classes` from the last parsed file.
		Progress is printed for each feature file.
		"""
		all_vertical_cids: set[int] = set()
		feature_files = self.find_all_feature_files()

		for filepath in feature_files:
			print(f"Processing {filepath.relative_to(self.repo_root)}...")
			cids = self.parse_feature_file(filepath)
			all_vertical_cids.update(cids)
			print(f"  Found {len(cids)} vertical glyphs")

		self.vertical_cids = all_vertical_cids
		return all_vertical_cids

	def get_statistics(self) -> dict[str, int]:
		"""Inspect the size and numeric range of the stored vertical CID selection.

		(AI generated docstring)

		Returns
		-------
		statistics : dict[str, int]
			`"total_vertical_glyphs"` gives the selected CID count. `"min_cid"` and `"max_cid"`
			give its bounds; both bounds are `0` when the selection is empty.
		"""
		return {
			'total_vertical_glyphs': len(self.vertical_cids),
			'min_cid': min(self.vertical_cids) if self.vertical_cids else 0,
			'max_cid': max(self.vertical_cids) if self.vertical_cids else 0,
		}

	def export_to_file(self, output_path: Path, output_format: str = 'text') -> None:
		"""Export the stored vertical CID selection as text, CSV, or JSON.

		(AI generated docstring)

		Parameters
		----------
		output_path : Path
			Destination file in an existing directory.
		output_format : {'text', 'csv', 'json'} = 'text'
			Text includes comment headers and one CID per line. CSV includes a `"CID"` header.
			JSON includes `"vertical_cids"` and `"statistics"`. Every format orders CIDs numerically.

		File Replacement
		----------------
		The destination is created or replaced with UTF-8 text. An export status message is printed.
		"""
		if output_format == 'text':
			with output_path.open('w', encoding='utf-8') as f:
				f.write("# Vertical-only glyph CIDs in Source Han Mono\n")
				f.write(f"# Total: {len(self.vertical_cids)} glyphs\n\n")
				for cid in sorted(self.vertical_cids):
					f.write(f"{cid}\n")

		elif output_format == 'csv':
			with output_path.open('w', encoding='utf-8') as f:
				f.write("CID\n")
				for cid in sorted(self.vertical_cids):
					f.write(f"{cid}\n")

		elif output_format == 'json':
			output_path.write_text(json.dumps({
				'vertical_cids': sorted(self.vertical_cids),
				'statistics': self.get_statistics()
			}, indent=2), encoding='utf-8')

		print(f"Exported {len(self.vertical_cids)} CIDs to {output_path}")

def main() -> None:
	"""Inspect vertical substitution targets using command-line selections.

	(AI generated docstring)

	You can select a Source Han Mono checkout with `--repo-root`, an export path with `--output`,
	and `text`, `csv`, or `json` with `--format`. Extraction progress, statistics, and up to ten
	sample CIDs are printed. `--stats-only` skips the export; otherwise the default destination
	is `vertical_glyphs.txt` in the current directory.

	File Replacement
	----------------
	Unless `--stats-only` is selected, the output file is created or replaced.
	"""
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
		sample = sorted(vertical_cids)[:10]
		print(f"\nSample CIDs (first 10): {sample}")

if __name__ == '__main__':
	main()
