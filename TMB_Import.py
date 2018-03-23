"""
Functions to read data from files
"""

# import codecs
from typing import Tuple
import TMB_Classes
from TMB_Error import report_error


def read_simple_file(filename: str) -> list:
    """
    read data from generic flatfile
    """
    with open(filename, "r", encoding="utf-8") as infile:
        data_list = []
        got_header = False
        for line in infile:
            if got_header:
                line = line.strip()
                line = line.replace("\"\"", "\"")
                line_data = line.split("\t")
                for i, x in enumerate(line_data):
                    if x.startswith("\"") and x.endswith("\""):
                        line_data[i] = x[1:len(x)-1]
                data_list.append(line_data)
            else:
                got_header = True
    return data_list


def read_citation_file(filename: str) -> list:
    """
    read citation info
    """
    tmplist = read_simple_file(filename)
    cite_list = []
    for cite in tmplist:
        newcite = TMB_Classes.CitationClass()
        newcite.cite_key = cite[0]
        newcite.name_key = cite[1]
        newcite.name = cite[2]
        newcite.common = cite[3]
        newcite.where = cite[4]
        newcite.context = cite[5]
        newcite.application = cite[6]
        newcite.cite_n = cite[7]
        newcite.actual = cite[8]
        newcite.source = cite[9]
        newcite.name_note = cite[10]
        newcite.general_note = cite[11]
        cite_list.append(newcite)
    return cite_list


def read_reference_data(ref_filename: str, formatref_filename: str,
                        citation_filename: str) -> Tuple[list, dict, list, dict, int]:
    """
    read all reference data
    """
    ref_list = []
    year_dat = {}
    cite_done = {}

    # citation style data (Author, Year) and language for each reference
    with open(ref_filename, "r", encoding="utf-8") as reffile:
        for line in reffile:
            line = line.replace("et al.", "<em>et al.</em>")
            line = line.replace(" & ", " &amp; ")
            ref = line.strip().split("\t")
            while len(ref) < 3:
                ref.append("")
            newref = TMB_Classes.ReferenceClass()
            newref.citation = ref[0]
            newref.cite_key = ref[1]
            newref.language = ref[2]
            # calculate publishing trend
            y = newref.year()
            if y is not None:
                if y in year_dat:
                    year_dat[y] += 1
                else:
                    year_dat[y] = 1
            cite_done[newref.cite_key] = [False, y]
            ref_list.append(newref)

    # html formatted full references
    with open(formatref_filename, "r", encoding="utf-8") as reffile:
        c = -1
        for line in reffile:
            line = line.strip()
            if line.endswith("<p>"):
                line = line[:line.find("<p>")]
                line = line.replace("<i>", "<em>")
                line = line.replace("</i>", "</em>")
                c += 1
                newref = ref_list[c]
                newref.formatted_html = line
    refdict = {}
    for ref in ref_list:
        if ref.cite_key in refdict and ref.cite_key != "<pending>":
            report_error("Duplicate reference key:" + ref.cite_key)
        refdict[ref.cite_key] = ref

    # citation records information
    citelist = read_citation_file(citation_filename)
    for c in citelist:
        cite_done[c.cite_key][0] = True

    cite_count = 0
    for y in year_dat:
        year_dat[y] = [year_dat[y], 0]
    for x in cite_done:
        c = cite_done[x]
        if c[0]:
            cite_count += 1
            if c[1] in year_dat:
                year_dat[c[1]][1] += 1

    return ref_list, refdict, citelist, year_dat, cite_count


def read_species_data(filename: str) -> list:
    """
    read data from species flatfile
    """
    tmplist = read_simple_file(filename)
    species_list = []
    for s in tmplist:
        newspecies = TMB_Classes.SpeciesClass()
        newspecies.species = s[0]
        newspecies.subgenus = s[1]
        newspecies.type_species = s[2]
        newspecies.type_reference = s[3]
        newspecies.common = s[4]
        newspecies.commonext = s[5]
        newspecies.range = s[6]
        newspecies.range_references = s[7]
        newspecies.region = s[8]
        newspecies.status = s[9]
        newspecies.taxonid = s[10]
        newspecies.eolid = s[11]
        newspecies.inatid = s[12]
        newspecies.gbifid = s[13]
        species_list.append(newspecies)
    return species_list


def read_photo_data(filename: str) -> list:
    """
    read data from photo flatfile
    """
    tmplist = read_simple_file(filename)
    photo_list = []
    for p in tmplist:
        newphoto = TMB_Classes.PhotoClass()
        newphoto.species = p[0]
        newphoto.n = p[1]
        newphoto.caption = p[2]
        photo_list.append(newphoto)
    return photo_list


def read_video_data(filename: str) -> list:
    """
    read data from video flatfile
    """
    tmplist = read_simple_file(filename)
    video_list = []
    for v in tmplist:
        newvideo = TMB_Classes.VideoClass()
        newvideo.species = v[0]
        newvideo.n = v[1]
        newvideo.activity = v[2]
        newvideo.caption = v[3]
        newvideo.length = v[4]
        newvideo.size = v[5]
        newvideo.format = v[6]
        newvideo.date_location = v[7]
        newvideo.author = v[8]
        newvideo.notes = v[9]
        video_list.append(newvideo)
    return video_list


def read_subgenera_data(filename: str) -> list:
    """
    read subgenera data
    """
    tmplist = read_simple_file(filename)
    genlist = []
    for g in tmplist:
        newsubgenus = TMB_Classes.SubgenusClass()
        newsubgenus.subgenus = g[0]
        newsubgenus.author = g[1]
        newsubgenus.type_species = g[2]
        newsubgenus.notes = g[3]
        newsubgenus.taxonid = g[4]
        newsubgenus.eolid = g[5]
        genlist.append(newsubgenus)
    return genlist


def read_specific_names_data(filename: str) -> list:
    """
    read specific name data
    """
    tmplist = read_simple_file(filename)
    spec_name_list = []
    for s in tmplist:
        newname = TMB_Classes.SpecificNameClass()
        newname.name = s[0]
        newname.variations = s[1]
        newname.synonym = s[2]
        newname.original_binomial = s[3]
        newname.priority_source = s[4]
        newname.meaning = s[5]
        newname.notes = s[6]
        spec_name_list.append(newname)
    return spec_name_list


def read_art_data(filename: str) -> list:
    """
    read art data
    """
    tmplist = read_simple_file(filename)
    art_list = []
    for a in tmplist:
        newart = TMB_Classes.ArtClass()
        newart.art_type = a[0]
        newart.cite_key = a[1]
        newart.author = a[2]
        newart.year = a[3]
        newart.title = a[4]
        newart.image = a[5]
        newart.ext = a[6]
        newart.species = a[7]
        newart.notes = a[8]
        art_list.append(newart)
    return art_list


def read_morphology_data(filename: str) -> list:
    """
    read morphology data
    """
    tmplist = read_simple_file(filename)
    morph_list = []
    for m in tmplist:
        newmorph = TMB_Classes.MorphologyClass()
        newmorph.character = m[0]
        newmorph.parent = m[1]
        newmorph.image = m[2]
        newmorph.caption = m[3]
        newmorph.description = m[4]
        morph_list.append(newmorph)
    return morph_list


def read_common_name_data(filename: str) -> list:
    """
    read common name text info
    """
    with open(filename, "r", encoding="utf-8") as infile:
        lines = infile.readlines()
    return lines


def read_location_data(filename: str) -> dict:
    """
    read location data
    """
    tmplist = read_simple_file(filename)
    locdict = {}
    for loc in tmplist:
        newloc = TMB_Classes.LocationClass()
        newloc.name = loc[0]
        try:
            newloc.latitude = float(loc[1])
            newloc.longitude = float(loc[2])
        except ValueError:
            newloc.unknown = True
        if loc[3] != ".":
            newloc.notes = loc[3]
        # column 4 is for reference but not needed as data
        newloc.trimmed_name = loc[5]
        if loc[6] != ".":
            newloc.alternates = list(loc[6].split(";"))
        if loc[7] != ".":
            newloc.parent = loc[7]
        if loc[8] != ".":
            newloc.secondary_parents = list(loc[8].split(";"))
        newloc.validity = loc[9]
        # if loc[10] != ".":
        #     newloc.ne_lat = float(loc[10])
        #     newloc.ne_lon = float(loc[11])
        #     newloc.sw_lat = float(loc[12])
        #     newloc.sw_lon = float(loc[13])
        # else:  # set default boundaries if they are not loaded
        #     newloc.ne_lat = newloc.latitude + 7.5
        #     newloc.ne_lon = newloc.longitude + 15
        #     newloc.sw_lat = newloc.latitude - 7.5
        #     newloc.sw_lon = newloc.longitude - 15
        locdict[newloc.name] = newloc
    return locdict
