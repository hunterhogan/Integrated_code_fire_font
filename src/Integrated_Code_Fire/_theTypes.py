from typing import NamedTuple

class LocaleIn(NamedTuple):
	"""Equivalent locale identifiers in different contexts.

	You can use this type to store locale identifiers in both ASCII form for filenames and filesystem paths and Unicode form for
	display in font names. The ASCII identifier uses underscores where the Unicode identifier uses native characters.

	Attributes
	----------
	ascii : str
		ASCII locale identifier using underscores, suitable for filenames.
	IntegratedCode火 : str
		Locale identifier as presented by Integrated Code 火 when ASCII is not mandatory.

	"""
	ascii: str
	IntegratedCode火: str
	SourceHanMono: str
	SourceHanMonoOTC: str

class WeightIn(NamedTuple):
	"""Equivalent weight identifiers in different contexts.

	You can use this type to store weight identifiers for the same logical weight across different font families or naming
	contexts. Each font family uses different weight naming conventions, and this type provides a unified representation.

	Attributes
	----------
	FiraCode : str
		Weight identifier used by Fira Code fonts.
	fontFamilyCID : str
		Weight identifier used for CID font files.
	IntegratedCode火 : str
		Weight identifier used in Integrated Code 火 font names.
	SourceHanMono : str
		Weight identifier used by Source Han Mono fonts.

	"""
	FiraCode: str
	fontFamilyCID: str
	fontFamilyScaled: str
	IntegratedCode火: str
	SourceHanMono: str
