
def indent(n: int) -> str:
    return n * " "


def rangemap_name(name: str) -> str:
    return name + "_range_map"


def pointmap_name(name: str) -> str:
    return name + "_point_map"


def name_to_filename(x: str) -> str:
    """ Convert a full species name into a valid file name """
    name_replace_list = [
        [" ", "_"],
        ["(", ""],
        [")", ""],
        [",", ""],
        [".", ""],
        ["æ", "_ae_"],
        ["ö", "_o_"],
        ["œ", "_oe_"],
        ["ç", "_c_"],
        ["[", "_"],
        ["]", "_"]
    ]
    for r in name_replace_list:
        x = x.replace(r[0], r[1])
    return x


def place_to_filename(x: str) -> str:
    """ Convert a location name into a valid file name """
    place_replace_list = [
        [", ", "_-_"],
        [" (", "_-_"],
        [")", ""],
        ["/", "-"],
        [" ", "_"],
        ["\"", ""],
        ["'", ""],
        ["ç", "c"],
        ["ñ", "n"],
        ["ã", "a"],
        ["á", "a"],
        ["é", "e"],
        ["í", "i"],
        ["ó", "o"],
        ["ơ", "o"],
        ["ú", "u"],
        ["ū", "u"]
    ]
    for r in place_replace_list:
        x = x.replace(r[0], r[1])
    return x


def unicode_to_html_encoding(x: str) -> str:
    unicode_replace_list = [
        ["ç", "&#x00E7;"],  # 231
        ["ñ", "&#x00F1;"],  # 241
        ["ã", "&#x00E3;"],  # 227
        ["á", "&#x00E1;"],  # 225
        ["é", "&#x00E9;"],  # 233
        ["í", "&#x00ED;"],  # 237
        ["ó", "&#x00F3;"],  # 243
        ["ơ", "&#x01A1;"],  # 417
        ["ú", "&#x00FA;"],  # 250
        ["ū", "&#x016B;"]   # 363
    ]
    for r in unicode_replace_list:
        x = x.replace(r[0], r[1])
    return x
