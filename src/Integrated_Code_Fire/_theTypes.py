from typing import NamedTuple

class LocaleIn(NamedTuple):
	"""Store equivalent locale identifiers across naming systems.

	You can use this type to store locale identifiers in both ASCII form for filenames and filesystem paths and Unicode form for
	display in font names. The fields also store the abbreviations required by Source Han Mono source filenames and OTC assets.

	Parameters
	----------
	ascii : str
		ASCII locale identifier using underscores, suitable for filenames.
	IntegratedCode火 : str
		Locale identifier as presented by Integrated Code 火 when ASCII is not mandatory.
	SourceHanMono : str
		Locale identifier used by Source Han Mono source files.
	SourceHanMonoOTC : str
		Locale identifier used by Source Han Mono OTC source files.

	Attributes
	----------
	ascii : str
		ASCII locale identifier using underscores, suitable for filenames.
	IntegratedCode火 : str
		Locale identifier as presented by Integrated Code 火 when ASCII is not mandatory.
	SourceHanMono : str
		Locale identifier used by Source Han Mono source files.
	SourceHanMonoOTC : str
		Locale identifier used by Source Han Mono OTC source files.

	"""
	ascii: str
	IntegratedCode火: str
	SourceHanMono: str
	SourceHanMonoOTC: str

class WeightIn(NamedTuple):
	"""Store equivalent weight identifiers across naming systems.

	You can use this type to store weight identifiers for the same logical weight across different font families or naming
	contexts. Each font family uses different weight naming conventions, and this type provides a unified representation.

	Parameters
	----------
	FiraCode : str
		Weight identifier used by Fira Code fonts.
	fontFamilyCID : str
		Weight identifier used for CID font files.
	fontFamilyWestern : str
		Weight identifier used for western font filenames in the warehouse.
	IntegratedCode火 : str
		Weight identifier used in Integrated Code 火 font names.
	SourceHanMono : str
		Weight identifier used by Source Han Mono fonts.

	Attributes
	----------
	FiraCode : str
		Weight identifier used by Fira Code fonts.
	fontFamilyCID : str
		Weight identifier used for CID font files.
	fontFamilyWestern : str
		Weight identifier used for western font filenames in the warehouse.
	IntegratedCode火 : str
		Weight identifier used in Integrated Code 火 font names.
	SourceHanMono : str
		Weight identifier used by Source Han Mono fonts.

	"""
	FiraCode: str
	fontFamilyCID: str
	fontFamilyWestern: str
	IntegratedCode火: str
	SourceHanMono: str
