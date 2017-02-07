
def rangemap_name(name):
    return name + "_range_map"


def pointmap_name(name):
    return name + "_point_map"


def name_to_filename(x):
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


def place_to_filename(x):
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
