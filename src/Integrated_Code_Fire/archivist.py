"""You can use this module to write OpenType name metadata into built `.ttf` files.

(AI generated docstring)

This module updates each built `.ttf` font file in `pathWorkbenchFonts` by
setting `TTFont['head'].fontRevision`, `TTFont['OS/2'].achVendID`, and selected
name records in `TTFont['name']`. The name record values are produced by
`getMetadataByFontWeight`.

This module also provides `updateCIDFontInfoVersion` to update version numbers
in CIDFont info files before compilation.

Contents
--------
Variables
	fontVersion
		Font revision value written into the `head` table.
	fontVersionHARDCODED
		Hard-coded value used to initialize `fontVersion`.
	langID
		Name record language identifier used by `updateFontFile`.
	platEncID
		Name record platform encoding identifier used by `updateFontFile`.
	platformID
		Name record platform identifier used by `updateFontFile`.

Functions
	getMetadataByFontWeight
		Build the name record value mapping for a specific `weight`.
	updateFontFile
		Update one `.ttf` font file in place.
	writeMetadata
		Update all built `.ttf` font files in `pathWorkbenchFonts`.
	updateCIDFontInfoVersion
		Update version number in CIDFont info files before compilation.

References
----------
[1] fontTools `TTFont` documentation.
	https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html
[2] Integrated_Code_Fire.go.go
	Internal package reference.

"""
from fontTools import subset
from hunterMakesPy import Ordinals
from hunterMakesPy.filesystemToolkit import writeStringToHere
from Integrated_Code_Fire import LocaleIn, settingsPackage, WeightIn
from itertools import filterfalse, product as CartesianProduct
from pathlib import Path
from tlz.dicttoolz import keyfilter, keymap  # pyright: ignore[reportMissingModuleSource]
from tlz.functoolz import complement, compose, curry as syntacticCurry  # pyright: ignore[reportMissingModuleSource]
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from collections.abc import Iterable, Iterator
	from fontTools.ttLib import TTFont
	from hunterMakesPy import identifierDotAttribute
	from pathlib import Path

"""Notes in case I run out of sofunty IDs.

CID subfont names:
Alphabetic
AlphabeticDigits
Bopomofo
Dingbats
DingbatsDigits
Generic
HDingbats
HKana
Hangul
Ideographs
Italic
ItalicCJK
ItalicDigits
Kana
Monospace
MonospaceCJK
MonospaceDigits
VKana

Enclosed CJK Letters and Months
3200-32FE
NOTE Keep 0x32FF

vertical stuff, which _might_ make it possible to use fontTools.Merger.
		, filterfalse(between吗(0x3300, 0x33FF)
		, filterfalse(between吗(0xFB00, 0xFB4F)
		, filterfalse(between吗(0xFE10, 0xFE4F)

Based ONLY on looking at SourceHanMono.Simplified_Chinese.Regular.otf:
Ranges I can exclude.
Small Form Variants (punctuation, so I'd like to push users towards the ligatures (to avoid "Issues"), but users might want these forms for inline documentation, so idk.)
FE50-FE6F

"""
#======== Boolean antecedents ================================================

@syntacticCurry
def between吗[小于: Ordinals](floor: 小于, ceiling: 小于, comparand: 小于) -> bool:
	"""Inclusive `floor <= comparand <= ceiling`."""
	return floor <= comparand <= ceiling

#======== Settings that have not yet found their home, such as a dataclass or function. ========

hmtx: dict[str, int] = {
	'bearingLeft' : 1,
	'increment' : 100,
	'width' : 0,
}

name: dict[str, int] = {
	'langID' : 0x0409,
	'platEncID' : 1,
	'platformID' : 3,
}

lookupAFDKOCharacterSet: dict[str, str] = {
	'Hong_Kong': '2',
	'Japan': '1',
	'Korea': '3',
	'Simplified_Chinese': '25',
	'Taiwan': '2',
}
"""Locale identifiers to AFDKO makeotf character set identifiers.

Maps font locale identifiers to Adobe CID character collection ROS
(Registry-Ordering-Supplement) identifiers for use with AFDKO makeotf -cs
argument [1].

The character set identifiers correspond to:
- '1': Adobe-Japan1 (Japanese)
- '2': Adobe-CNS1 (Traditional Chinese: Hong Kong, Taiwan)
- '3': Adobe-Korea1 (Korean)
- '25': Adobe-GB1 (Simplified Chinese)

References
----------
[1] AFDKO makeotf - Read the Docs
	https://adobe-type-tools.github.io/afdko/AFDKO-Overview.html#makeotf
[2] Adobe CMap Resources - GitHub
	https://github.com/adobe-type-tools/cmap-resources
"""

def getFilenameStem(fontFamily: str, locale: str | None = None, style: str | None = None, weight: str | None = None, separator: str = '.') -> str:
	"""Get stem.

	Common filename suffixes:
	- cidfont.ps  # NOTE that this is now the only "faux suffix" because it has a '.', so I might want to change it.
	- cidfontinfo
	- features
	- gids
	- otf
	- sequences
	- ttf
	- unicodes
	- UTF32-map
	- UTF32-H
	"""
	notNone = None # Ironic, no?
	return separator.join(filter(notNone, [fontFamily, locale, style, weight]))

def getDictionaryLocales() -> dict[str, LocaleIn]:
	"""Keyed to `settingsPackage.theLocales`."""
	return {
		'Hong_Kong': LocaleIn('Hong_Kong', '香港'),
		'Japan': LocaleIn('Japan', '日本'),
		'Korea': LocaleIn('Korea', '한국인'),
		'Simplified_Chinese': LocaleIn('Simplified_Chinese', '简化字'),
		'Taiwan': LocaleIn('Taiwan', '台灣'),
	}

def getDictionaryWeights() -> dict[str, WeightIn]:
	"""Keyed to SourceHanMono weight names."""
	return {
		'Bold': WeightIn(IntegratedCode火='SemiBold', FiraCode='SemiBold', fontFamilyCID='Bold', SourceHanMono='Bold'),
		'Heavy': WeightIn(IntegratedCode火='Bold', FiraCode='Bold', fontFamilyCID='Heavy', SourceHanMono='Heavy'),
		'Light': WeightIn(IntegratedCode火='Light', FiraCode='Light', fontFamilyCID='Light', SourceHanMono='Light'),
		'Medium': WeightIn(IntegratedCode火='Medium', FiraCode='Medium', fontFamilyCID='Medium', SourceHanMono='Medium'),
		'Normal': WeightIn(IntegratedCode火='Retina', FiraCode='Retina', fontFamilyCID='Normal', SourceHanMono='Normal'),
		'Regular': WeightIn(IntegratedCode火='Regular', FiraCode='Regular', fontFamilyCID='Regular', SourceHanMono='Regular'),
	}

def getNameIDMetadata(weight: str, filenameFontFamily: str, fontFamily: str) -> dict[int, str]:
	"""You can build a name record mapping for a given `weight`.

	(AI generated docstring)

	This function returns a `dict[int, str]` that maps a TrueType name record
	identifier to a name record value. The returned mapping is used by
	`updateFontFile` to update `TTFont['name']`.

	Parameters
	----------
	weight : str
		Font weight suffix derived from the `.ttf` filename stem.
	filenameFontFamilyLocale : str
		Font family locale derived from the `.ttf` filename stem.
	fontFamilyLocale : str
		Font family locale derived from the `.ttf` filename stem.

	Returns
	-------
	dictionaryNameIDToNameRecordValue : dict[int, str]
		Mapping from name record identifier to name record value.

	References
	----------
	[1] fontTools `TTFont` documentation.
		https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html
	[2] Integrated_Code_Fire.writeMetadata.updateFontFile
		Internal package reference.

	"""
	return {
		0: 'Copyright 2026 Hunter Hogan (https://www.patreon.com/integrated), with Reserved Font Name \u2018Integrated.\u2019',
		1: fontFamily,
		2: weight,
		3: f"{settingsPackage.fontVersion};{settingsPackage.achVendID};{filenameFontFamily}{weight}",
		4: f"{fontFamily} {weight}",
		5: f"Version {settingsPackage.fontVersion}",
		6: f"{filenameFontFamily}{weight}",
		7: 'Fira Mono is a trademark of The Mozilla Corporation. Source is a trademark of Adobe in the United States and/or other countries.',
		8: 'Carrois Corporate; Edenspiekermann AG; Nikita Prokopov; Adobe',
		9: 'Carrois Corporate; Edenspiekermann AG; Nikita Prokopov; Ryoko NISHIZUKA 西塚涼子 (kana, bopomofo & ideographs); Paul D. Hunt (Latin, Italic, Greek & Cyrillic); Sandoll Communications 산돌커뮤니케이션, Soo-young JANG 장수영 & Joo-yeon KANG 강주연 (hangul elements, letters & syllables)',
		10: 'For Adobe: Dr. Ken Lunde (project architect, glyph set definition & overall production); Masataka HATTORI 服部正貴 (production & ideograph elements)',
		11: 'https://www.patreon.com/integrated',
		12: 'https://tonsky.me http://www.adobe.com/type/',
		13: 'This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: http://scripts.sil.org/OFL',
		14: 'http://scripts.sil.org/OFL',
		16: fontFamily,
		17: weight,
	}

def getSubsetCharacters() -> dict[identifierDotAttribute, dict[str, list[int]]]:
	subsetCharacters: dict[identifierDotAttribute, dict[str, list[int]]] = {}

	fontFamilyCID: str = 'SourceHanMono'
	pathMetadata: Path = settingsPackage.pathRoot / fontFamilyCID / 'metadata'
	dictionaryLocales: dict[str, LocaleIn] = getDictionaryLocales()

	for locale, style in CartesianProduct(settingsPackage.theLocales, settingsPackage.theStyles):
		filenameStem: identifierDotAttribute = getFilenameStem(fontFamilyCID, dictionaryLocales[locale].ascii, style)
		subsetCharacters[filenameStem] = {}

		formatCharacterIDs: str = 'gids'
		pathFilename: Path = pathMetadata / f"{filenameStem}.{formatCharacterIDs}"
		subsetCharacters[filenameStem][formatCharacterIDs] = list(map(int, pathFilename.read_text('utf-8').splitlines()))

		formatCharacterIDs: str = 'unicodes'
		pathFilename: Path = pathMetadata / f"{filenameStem}.{formatCharacterIDs}"
		subsetCharacters[filenameStem][formatCharacterIDs] = subset.parse_unicodes(','.join(pathFilename.read_text('utf-8').splitlines()))

	return subsetCharacters

def getUnicodeFiraCode() -> frozenset[int]:
	return frozenset([13, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46,
	47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77,
	78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106,
	107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 160, 161, 162, 163, 164,
	165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189,
	190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214,
	215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239,
	240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264,
	265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289,
	290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314,
	315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339,
	340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364,
	365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 402, 508, 509, 510, 511, 536, 537,
	538, 539, 567, 697, 698, 700, 710, 711, 713, 728, 729, 730, 731, 732, 733, 768, 769, 770, 771, 772, 773, 774, 775, 776, 778,
	779, 780, 783, 787, 788, 806, 807, 821, 822, 834, 837, 880, 881, 882, 883, 884, 885, 886, 887, 890, 891, 892, 893, 894, 895,
	900, 901, 902, 903, 904, 905, 906, 908, 910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 920, 921, 922, 923, 924, 925, 926,
	927, 928, 929, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 949, 950, 951, 952,
	953, 954, 955, 956, 957, 958, 959, 960, 961, 962, 963, 964, 965, 966, 967, 968, 969, 970, 971, 972, 973, 974, 975, 976, 977,
	978, 979, 980, 981, 982, 983, 984, 985, 986, 987, 988, 989, 990, 991, 992, 993, 1008, 1009, 1010, 1011, 1012, 1013, 1014,
	1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035,
	1036, 1037, 1038, 1039, 1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056,
	1057, 1058, 1059, 1060, 1061, 1062, 1063, 1064, 1065, 1066, 1067, 1068, 1069, 1070, 1071, 1072, 1073, 1074, 1075, 1076, 1077,
	1078, 1079, 1080, 1081, 1082, 1083, 1084, 1085, 1086, 1087, 1088, 1089, 1090, 1091, 1092, 1093, 1094, 1095, 1096, 1097, 1098,
	1099, 1100, 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116, 1117, 1118, 1119,
	1120, 1121, 1122, 1123, 1124, 1125, 1126, 1127, 1128, 1129, 1130, 1131, 1132, 1133, 1134, 1135, 1136, 1137, 1138, 1139, 1140,
	1141, 1142, 1143, 1144, 1145, 1162, 1163, 1164, 1165, 1166, 1167, 1168, 1169, 1170, 1171, 1172, 1173, 1174, 1175, 1176, 1177,
	1178, 1179, 1180, 1181, 1182, 1183, 1184, 1185, 1186, 1187, 1188, 1189, 1190, 1191, 1192, 1193, 1194, 1195, 1196, 1197, 1198,
	1199, 1200, 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211, 1212, 1213, 1214, 1215, 1216, 1217, 1218, 1219,
	1220, 1221, 1222, 1223, 1224, 1225, 1226, 1227, 1228, 1229, 1230, 1231, 1232, 1233, 1234, 1235, 1236, 1237, 1238, 1239, 1240,
	1241, 1242, 1243, 1244, 1245, 1246, 1247, 1248, 1249, 1250, 1251, 1252, 1253, 1254, 1255, 1256, 1257, 1258, 1259, 1260, 1261,
	1262, 1263, 1264, 1265, 1266, 1267, 1268, 1269, 1270, 1271, 1272, 1273, 1274, 1275, 1276, 1277, 1278, 1279, 1280, 1281, 1282,
	1283, 1284, 1285, 1286, 1287, 1288, 1289, 1290, 1291, 1292, 1293, 1294, 1295, 1296, 1297, 1298, 1299, 1300, 1301, 1302, 1303,
	1304, 1305, 1306, 1307, 1308, 1309, 1310, 1311, 1312, 1313, 1314, 1315, 1316, 1317, 1318, 1319, 1320, 1321, 1322, 1323, 1324,
	1325, 1326, 1327, 5125, 5130, 7808, 7809, 7810, 7811, 7812, 7813, 7838, 7922, 7923, 7936, 7937, 7938, 7939, 7940, 7941, 7942,
	7943, 7944, 7945, 7946, 7947, 7948, 7949, 7950, 7951, 7952, 7953, 7954, 7955, 7956, 7957, 7960, 7961, 7962, 7963, 7964, 7965,
	7968, 7969, 7970, 7971, 7972, 7973, 7974, 7975, 7976, 7977, 7978, 7979, 7980, 7981, 7982, 7983, 7984, 7985, 7986, 7987, 7988,
	7989, 7990, 7991, 7992, 7993, 7994, 7995, 7996, 7997, 7998, 7999, 8000, 8001, 8002, 8003, 8004, 8005, 8008, 8009, 8010, 8011,
	8012, 8013, 8016, 8017, 8018, 8019, 8020, 8021, 8022, 8023, 8025, 8027, 8029, 8031, 8032, 8033, 8034, 8035, 8036, 8037, 8038,
	8039, 8040, 8041, 8042, 8043, 8044, 8045, 8046, 8047, 8048, 8049, 8050, 8051, 8052, 8053, 8054, 8055, 8056, 8057, 8058, 8059,
	8060, 8061, 8064, 8065, 8066, 8067, 8068, 8069, 8070, 8071, 8072, 8073, 8074, 8075, 8076, 8077, 8078, 8079, 8080, 8081, 8082,
	8083, 8084, 8085, 8086, 8087, 8088, 8089, 8090, 8091, 8092, 8093, 8094, 8095, 8096, 8097, 8098, 8099, 8100, 8101, 8102, 8103,
	8104, 8105, 8106, 8107, 8108, 8109, 8110, 8111, 8112, 8113, 8114, 8115, 8116, 8118, 8119, 8120, 8121, 8122, 8123, 8124, 8125,
	8126, 8127, 8128, 8129, 8130, 8131, 8132, 8134, 8135, 8136, 8137, 8138, 8139, 8140, 8141, 8142, 8143, 8144, 8145, 8146, 8147,
	8150, 8151, 8152, 8153, 8154, 8155, 8157, 8158, 8159, 8160, 8161, 8162, 8163, 8164, 8165, 8166, 8167, 8168, 8169, 8170, 8171,
	8172, 8173, 8174, 8175, 8178, 8179, 8180, 8182, 8183, 8184, 8185, 8186, 8187, 8188, 8189, 8190, 8199, 8200, 8203, 8210, 8211,
	8212, 8213, 8214, 8215, 8216, 8217, 8218, 8220, 8221, 8222, 8224, 8225, 8226, 8230, 8240, 8249, 8250, 8260, 8266, 8304, 8308,
	8309, 8310, 8311, 8312, 8313, 8314, 8315, 8316, 8317, 8318, 8319, 8320, 8321, 8322, 8323, 8324, 8325, 8326, 8327, 8328, 8329,
	8330, 8331, 8332, 8333, 8334, 8364, 8367, 8377, 8378, 8381, 8450, 8461, 8467, 8469, 8470, 8473, 8474, 8477, 8482, 8484, 8494,
	8531, 8532, 8533, 8534, 8535, 8536, 8537, 8538, 8539, 8540, 8541, 8542, 8543, 8586, 8587, 8592, 8593, 8594, 8595, 8596, 8597,
	8598, 8599, 8600, 8601, 8617, 8618, 8624, 8625, 8626, 8627, 8670, 8671, 8676, 8677, 8678, 8679, 8680, 8681, 8682, 8704, 8706,
	8707, 8708, 8709, 8710, 8711, 8712, 8713, 8714, 8715, 8716, 8717, 8718, 8719, 8721, 8722, 8725, 8727, 8729, 8730, 8734, 8743,
	8744, 8745, 8746, 8747, 8756, 8757, 8758, 8759, 8769, 8770, 8771, 8772, 8773, 8774, 8775, 8776, 8777, 8778, 8779, 8800, 8801,
	8802, 8804, 8805, 8834, 8835, 8836, 8837, 8838, 8839, 8840, 8841, 8842, 8843, 8860, 8866, 8867, 8868, 8869, 8870, 8871, 8872,
	8873, 8874, 8875, 8876, 8877, 8878, 8879, 8960, 8962, 8963, 8964, 8965, 8966, 8976, 8984, 8992, 8993, 8996, 8997, 8998, 8999,
	9000, 9003, 9095, 9096, 9099, 9115, 9116, 9117, 9118, 9119, 9120, 9121, 9122, 9123, 9124, 9125, 9126, 9127, 9128, 9129, 9130,
	9131, 9132, 9133, 9166, 9167, 9216, 9217, 9218, 9219, 9220, 9221, 9222, 9223, 9224, 9225, 9226, 9227, 9228, 9229, 9230, 9231,
	9232, 9233, 9234, 9235, 9236, 9237, 9238, 9239, 9240, 9241, 9242, 9243, 9244, 9245, 9246, 9247, 9248, 9249, 9250, 9251, 9252,
	9253, 9254, 9472, 9473, 9474, 9475, 9476, 9477, 9478, 9479, 9480, 9481, 9482, 9483, 9484, 9485, 9486, 9487, 9488, 9489, 9490,
	9491, 9492, 9493, 9494, 9495, 9496, 9497, 9498, 9499, 9500, 9501, 9502, 9503, 9504, 9505, 9506, 9507, 9508, 9509, 9510, 9511,
	9512, 9513, 9514, 9515, 9516, 9517, 9518, 9519, 9520, 9521, 9522, 9523, 9524, 9525, 9526, 9527, 9528, 9529, 9530, 9531, 9532,
	9533, 9534, 9535, 9536, 9537, 9538, 9539, 9540, 9541, 9542, 9543, 9544, 9545, 9546, 9547, 9548, 9549, 9550, 9551, 9552, 9553,
	9554, 9555, 9556, 9557, 9558, 9559, 9560, 9561, 9562, 9563, 9564, 9565, 9566, 9567, 9568, 9569, 9570, 9571, 9572, 9573, 9574,
	9575, 9576, 9577, 9578, 9579, 9580, 9581, 9582, 9583, 9584, 9585, 9586, 9587, 9588, 9589, 9590, 9591, 9592, 9593, 9594, 9595,
	9596, 9597, 9598, 9599, 9600, 9601, 9602, 9603, 9604, 9605, 9606, 9607, 9608, 9609, 9610, 9611, 9612, 9613, 9614, 9615, 9616,
	9617, 9618, 9619, 9620, 9621, 9622, 9623, 9624, 9625, 9626, 9627, 9628, 9629, 9630, 9631, 9632, 9633, 9634, 9635, 9636, 9637,
	9638, 9639, 9640, 9641, 9642, 9643, 9644, 9645, 9646, 9647, 9650, 9654, 9658, 9660, 9664, 9668, 9670, 9671, 9673, 9674, 9675,
	9678, 9679, 9680, 9681, 9682, 9683, 9685, 9686, 9687, 9689, 9690, 9691, 9692, 9693, 9694, 9695, 9696, 9697, 9698, 9699, 9700,
	9701, 9703, 9704, 9705, 9706, 9707, 9711, 9712, 9713, 9714, 9715, 9716, 9717, 9718, 9719, 9744, 9745, 9746, 9760, 9776, 9777,
	9778, 9779, 9780, 9781, 9782, 9783, 9785, 9786, 9787, 9788, 9792, 9794, 9824, 9827, 9829, 9830, 9834, 9835, 10003, 10096,
	10097, 10145, 10216, 10217, 10224, 10225, 10226, 10227, 10228, 10229, 10230, 10231, 10232, 10233, 10234, 10235, 10236, 10237,
	10238, 10239, 11013, 11014, 11015, 11834, 11835, 12300, 12301, 57344, 57345, 57346, 57347, 57504, 57505, 57506, 57520, 57521,
	57522, 57523, 60928, 60929, 60930, 60931, 60932, 60933, 60934, 60935, 60936, 60937, 60938, 60939, 64257, 64258, 65279, 65378,
	65379, 65533, 120121, 127245, 127246, 127247, 127341, 127342, 127343, 127405, 127760, 129904, 129905, 129906, 129907, 129908,
	129909, 129910, 129911, 129912, 129913, 129914, 129915, 129916, 129917, 129918, 129919, 129920, 129921, 129922, 129923,
	129924, 129925, 129926, 129927, 129928, 129929, 129930, 129931])

def updateMetadata(ttFont: TTFont, nameIDmetadata: dict[int, str]) -> None:
	ttFont['head'].fontRevision = settingsPackage.fontVersion  # ty:ignore[unresolved-attribute]
	ttFont['OS/2'].achVendID = settingsPackage.achVendID  # ty:ignore[unresolved-attribute]
	for nameID in nameIDmetadata:
		ttFont['name'].removeNames(nameID, name['platformID'], name['platEncID'], name['langID'])
		ttFont['name'].setName(nameIDmetadata[nameID], nameID, name['platformID'], name['platEncID'], name['langID'])

def archivistWritesCharacterSubsets(pathFilename: Path) -> list[Path]:
	def unicodesToInt(unicodeHexadecimalAsStr: str, /) -> int:
		return int(unicodeHexadecimalAsStr.strip('<>'), 16)

	listPathFilenames: list[Path] = []

	unicodeFiraCode: frozenset[int] = getUnicodeFiraCode()

	intMAPstr: dict[int, str] = keyfilter(complement(unicodeFiraCode.__contains__)
		, keymap(unicodesToInt, dict(map(compose(tuple[str, str], str.split), pathFilename.read_text('utf-8').splitlines()))))

	# gids: list[str] = sorted(frozenset(keyfilter((0xFFFF).__gt__, intMAPstr).values()))  # noqa: ERA001
	gids: list[str] = sorted({g for u, g in intMAPstr.items() if 0xFFFF < u}, key=int)  # ty:ignore[invalid-assignment]
	gids.append('')

	pathFilenameGids: Path = pathFilename.with_suffix('.gids')
	writeStringToHere('\n'.join(gids), pathFilenameGids)
	listPathFilenames.append(pathFilenameGids)

	unicodes: Iterator[str] = map(hex
		, filterfalse(between吗(0x1200, 0x2E7F)
		, filterfalse(between吗(0xFF01, 0xFF5E)
			, filter(between吗(0x1100, 0xFFFF), intMAPstr.keys())
	)))

	pathFilenameUnicodes: Path = pathFilename.with_suffix('.unicodes')
	writeStringToHere('\n'.join(unicodes) + '\n', pathFilenameUnicodes)
	listPathFilenames.append(pathFilenameUnicodes)

	return listPathFilenames

def Z0Z_doTheNeedful(fontFamilyCID: str = 'SourceHanMono', theLocales: Iterable[str] = frozenset(['Hong_Kong', 'Japan', 'Korea', 'Simplified_Chinese', 'Taiwan']), theStyles: Iterable[str | None] = frozenset(['Italic', None])) -> list[Path]:
	listPathFilenames: list[Path] = []

	pathMetadata: Path = settingsPackage.pathRoot / fontFamilyCID / 'metadata'
	dictionaryLocales: dict[str, LocaleIn] = getDictionaryLocales()

	for locale, style in CartesianProduct(theLocales, theStyles):
		filenameStem: identifierDotAttribute = getFilenameStem(fontFamilyCID, dictionaryLocales[locale].ascii, style)
		suffix: str = 'UTF32-map'
		pathFilename: Path = pathMetadata / f"{filenameStem}.{suffix}"
		listPathFilenames.extend(archivistWritesCharacterSubsets(pathFilename))

	return listPathFilenames

if __name__ == '__main__':
	Z0Z_doTheNeedful()
