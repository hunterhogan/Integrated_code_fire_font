"""Semiotic System Overview for Integrated_Code_Fire

This package uses an agent-actor naming system where functions encode _who_ performs _what action_ on _which object_. The identifier structure makes the assembly line visible through the names themselves.

Agent-Actor Pattern
-------------------
Functions are named as `agentVerbsObject[Qualifier]`, where the agent is a role in the font production assembly line:

archivist
	Provides domain data, encodes metadata, writes persistent artifacts, updates font metadata.
	Examples: `archivistProvidesLocales`, `archivistEncodesFilenameStem`, `archivistUpdatesMetadata`

machinist
	Transforms font structures: scales metrics, subsets glyphs, modifies bearings, merges fonts.
	Examples: `machinistScalesFonts`, `machinistSubsetsCID`, `machinistMergesFonts`

smithy
	Casts (compiles) fonts from source files using external tools (fontmake, AFDKO).
	Examples: `smithyCastsFromGlyphs`, `smithyCastsAFDKO`, `smithyCastsMakeOTF`

valet
	Performs logistics: copies files to staging areas, removes temporary artifacts.
	Examples: `valetCopiesToWorkbench`, `valetRemovesFiles`, `valetRemovesWorkbench`

packager
	Creates distributable assets: archives fonts, writes release packages.
	Examples: `packagerCreatesAssets`, `packagerCreatesAssetsLocale`

External Standard Identifiers
------------------------------
Identifiers from external standards (OpenType, AFDKO, fontTools) are preserved exactly to maintain traceability:

- OpenType table fields: `achVendID`, `unitsPerEm`, `fontRevision`, `platformID`, `platEncID`, `langID`
- AFDKO parameters: character set identifiers, makeotf arguments
- fontTools API: `TTFont`, `glyf`, `hmtx`, `cmap` table names
- Source font family names: `FiraCode`, `SourceHanMono`

Type Prefixes
-------------
Collections use semantic type prefixes when the structure is part of the domain concept:

- `dictionary...`: dict structures mapping domain keys to domain values
- `list...`: ordered sequences where order is semantically meaningful
- `path...`: filesystem paths (leverages pathlib's semantic type)
- `frozenset...`: immutable sets (type prefix used when set semantics are central)

Variable names use full words in camelCase. No abbreviations, no single-letter names, no truncations.

Naming Boundaries
-----------------
The semiotic system applies to:
- Function and method names (agent-actor pattern)
- Parameter names (full semantic descriptors)
- Local variable names (domain concepts, not implementation accidents)
- Module-level bindings (semantic constants, configuration, lookup tables)

The system does _not_ override:
- External standard identifiers (preserved for compatibility and traceability)
- Language keywords and built-in names
- Third-party API contracts

This system makes the codebase self-documenting: skimming function names reveals the assembly line structure, and each identifier encodes its role, action, and target without requiring prose explanation.

"""
