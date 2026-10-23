"""I use this module to keep locale and weight identities consistent across font families.

(AI generated docstring)

Contents
--------
Classes
	LocaleIn
		Store locale labels for filenames, display names, and Source Han Mono source files.
	WeightIn
		Store weight labels for western fonts, CJK fonts, and Integrated Code 火.
"""
from __future__ import annotations

from typing import NamedTuple

class LocaleIn(NamedTuple):
	"""Store matching locale labels for font names, filenames, and CJK source files.

	(AI generated docstring)

	You can describe one locale using the labels required by each font family. The fields retain the
	source labels so that filenames and visible font names refer to the same locale.

	Attributes
	----------
	ascii : str
		Locale label used in build filenames, such as `"Japan"` or `"Simplified_Chinese"`.
	IntegratedCode火 : str
		Locale label shown in the installed font family name, such as `"日本"`.
	SourceHanMono : str
		Source Han Mono locale code used in character maps, such as `"JP"`.
	SourceHanMonoOTC : str
		Source Han Mono locale code used in collection source filenames, such as `"J"`.
	"""
	ascii: str
	IntegratedCode火: str
	SourceHanMono: str
	SourceHanMonoOTC: str

class WeightIn(NamedTuple):
	"""Store matching weight labels for western fonts, CJK fonts, and Integrated Code 火.

	(AI generated docstring)

	You can pair weights whose names differ between font families. For example, Integrated Code 火
	`"Bold"` pairs Fira Code `"Bold"` with Source Han Mono `"Heavy"`. A field can contain empty text
	when that font family has no corresponding weight.

	Attributes
	----------
	FiraCode : str
		Weight label used by the Fira Code source.
	fontFamilyCID : str
		Weight label used in compiled CJK font filenames.
	fontFamilyWestern : str
		Weight label used in prepared western font filenames.
	IntegratedCode火 : str
		Weight label shown in Integrated Code 火 font names.
	SourceHanMono : str
		Weight label used by the Source Han Mono source.
	"""
	FiraCode: str
	fontFamilyCID: str
	fontFamilyWestern: str
	IntegratedCode火: str
	SourceHanMono: str
