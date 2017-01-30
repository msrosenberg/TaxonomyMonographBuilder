
def name_to_filename(x):
    """ Convert a full species name into a valid file name """
    x = x.replace(" ", "_")
    x = x.replace("(", "")
    x = x.replace(")", "")
    x = x.replace(",", "")
    x = x.replace(".", "")
    x = x.replace("æ", "_ae_")
    x = x.replace("ö", "_o_")
    x = x.replace("œ", "_oe_")
    x = x.replace("ç", "_c_")
    x = x.replace("[", "_")
    x = x.replace("]", "_")
    return x
