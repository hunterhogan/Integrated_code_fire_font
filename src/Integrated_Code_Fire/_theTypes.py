from typing import NamedTuple

class LocaleIn(NamedTuple):
	ascii: str
	IntegratedCode: str

class WeightIn(NamedTuple):
	IntegratedCode: str
	FiraCode: str
	SourceHanMono: str
