"""You can use this module to run the Integrated_Code_Fire build assembly line.

(AI generated docstring)

This module orchestrates staging input fonts, merging fonts, cleaning temporary
font input files, writing OpenType name metadata, creating release assets, and
removing the workbench directory.

Contents
--------
Functions
	cleanWorkbench
		Remove source font input files from `pathWorkbenchFonts`.
	go
		Run the end-to-end font build assembly line.
	removeWorkbench
		Remove `pathWorkbenchFonts` and `pathWorkbench` after a successful run.

References
----------
[1] Integrated_Code_Fire.getFontInput.getFiraCode
	Internal package reference.
[2] Integrated_Code_Fire.getFontInput.getSourceHanMonoSC
	Internal package reference.
[3] Integrated_Code_Fire.mergeFonts.mergeFonts
	Internal package reference.
[4] Integrated_Code_Fire.writeMetadata.writeMetadata
	Internal package reference.
[5] Integrated_Code_Fire.makeAssets.makeAssets
	Internal package reference.

"""
from Integrated_Code_Fire import pathWorkbenchSourceHanMono
from Integrated_Code_Fire.foundry import smithyCastsFiraCode, smithyCastsFontFamily
from Integrated_Code_Fire.logistics import cleanWorkbench, removeWorkbench, valetCopiesFilesToWorkbenchFonts
from Integrated_Code_Fire.mergeFonts import mergeFonts
from Integrated_Code_Fire.shipping import makeAssets
from Integrated_Code_Fire.writeMetadata import writeMetadata

def go(workersMaximum: int = 1) -> None:
	"""You can run the end-to-end font build assembly line.

	(AI generated docstring)

	This function invokes `getFiraCode`, `getSourceHanMonoSC`, `mergeFonts`,
	`cleanWorkbench`, `writeMetadata`, `makeAssets`, and `removeWorkbench`.

	Returns
	-------
	resultNone : None
		This function returns `None`.

	Raises
	------
	Exception
		Raised if any invoked function fails during the build assembly line.

	Examples
	--------
	This module invokes `go` when `__name__ == '__main__'`.

	>>> from Integrated_Code_Fire.go import go
	>>> go()

	References
	----------
	[1] Integrated_Code_Fire.getFontInput.getFiraCode
		Internal package reference.
	[2] Integrated_Code_Fire.getFontInput.getSourceHanMonoSC
		Internal package reference.
	[3] Integrated_Code_Fire.mergeFonts.mergeFonts
		Internal package reference.
	[4] Integrated_Code_Fire.writeMetadata.writeMetadata
		Internal package reference.
	[5] Integrated_Code_Fire.makeAssets.makeAssets
		Internal package reference.

	"""
	smithyCastsFiraCode()
	fontFamily: str = 'SourceHanMono'
	smithyCastsFontFamily(fontFamily, workersMaximum)
	valetCopiesFilesToWorkbenchFonts(pathWorkbenchSourceHanMono, 'Simplified_Chinese*.otf')
	mergeFonts()
	cleanWorkbench()
	writeMetadata()
	makeAssets()
	removeWorkbench()

if __name__ == '__main__':
	go(14)
