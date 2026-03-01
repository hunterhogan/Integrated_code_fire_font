from fontTools import subset
from hunterMakesPy import PackageSettings as humpy_PackageSettings
from pathlib import Path
from socket import gethostname
from sys import modules as sysModules
from typing import ClassVar, Final, Literal
import dataclasses
import platformdirs

#======== Eliminate hardcoding, which sometimes means adding the value to `settingsPackage`. ========
fontVersionHARDCODED: float = 0.005
# NOTE Update this? ^^^^^^^^^^^^^^^

subsetOptionsHARDCODED = subset.Options(
	drop_tables = [],
	glyph_names = False,
	layout_features = '*',
	legacy_cmap = True,
	name_IDs = '*',
	name_languages = '*',
	name_legacy = True,
	passthrough_tables = True,
	symbol_cmap = True,
)

if 'google.colab' in sysModules:
	pathRootHARDCODED: Path = Path("/content/drive/MyDrive")
else:
	pathRootHARDCODED = Path(platformdirs.user_data_dir(appauthor=False))

if gethostname() == 'duda':
	pathRootHARDCODED = Path('/apps/Integrated_Code_Fire')

#======== Subclass `PackageSettings` to add package-specific settings. ========

@dataclasses.dataclass
class PackageSettings(humpy_PackageSettings):
	achVendID: str = '1INT' # See "Registering Vendor ID 1INT.pdf".
	fontFamily: Final[str] = 'Integrated Code 火'
	unitsPerEm: int = 1000
	fontVersion: float = fontVersionHARDCODED
	pathRoot: Path = pathRootHARDCODED
	listLocales: ClassVar[list[str]] = ['Simplified_Chinese'] #, 'Hong_Kong', 'Japan', 'Korea', 'Taiwan']
	listWeights: ClassVar[list[str]] = ['Light', 'Normal', 'Regular', 'Medium', 'Bold', 'Heavy'] #, 'ExtraLight']
	listStyles: ClassVar[list[Literal['Italic'] | None]] = [None] #, 'Italic']

	pathAssets: Path = dataclasses.field(init=False)
	pathWorkbench: Path = dataclasses.field(init=False)
	pathWorkbenchFonts: Path = dataclasses.field(init=False)

	filenameFontFamily: str = dataclasses.field(init=False)

	def __post_init__(self, identifierPackageFALLBACK: str) -> None:
		super().__post_init__(identifierPackageFALLBACK)

		self.pathRoot = self.pathRoot / self.identifierPackage
		if gethostname() == 'duda':
			self.pathRoot = pathRootHARDCODED

		self.pathAssets = self.pathRoot / 'assets'
		self.pathWorkbench = self.pathRoot / 'workbench'
		self.pathWorkbenchFonts = self.pathWorkbench / 'fonts'

		self.filenameFontFamily = self.fontFamily.replace(' ', '')

#-------- Package settings. ---------------------------------------------

settingsPackage = PackageSettings('Integrated_Code_Fire')

#======== Centralized settings that have not yet found their home, such as in `settingsPackage`. ========

subsetOptions: subset.Options = subsetOptionsHARDCODED

pathFilenameFiraCodeGlyphs: Path = settingsPackage.pathRoot / 'FiraCode' / 'FiraCode.glyphs'
