"""
Functions to read data from files
"""

# import codecs
import collections
from typing import Tuple
import urllib.request
import csv
import time
# from collections import namedtuple
from tqdm import tqdm
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
    year_dat = collections.Counter()
    cite_done = {}

    # citation style data (Author, Year), language, DOI, and Taxon Author for each reference
    with open(ref_filename, "r", encoding="utf-8") as reffile:
        for line in reffile:
            line = line.replace("et al.", "<em>et al.</em>")
            line = line.replace(" & ", " &amp; ")
            ref = line.strip().split("\t")
            while len(ref) < 5:
                ref.append("")
            newref = TMB_Classes.ReferenceClass()
            newref.citation = ref[0]
            newref.cite_key = ref[1]
            newref.language = ref[2]
            if ref[3] != "":
                newref.doi = ref[3]
            if ref[4] != "":
                newref.taxon_author = ref[4]

            # calculate publishing trend
            y = newref.year()
            if y is not None:
                year_dat.update([y])
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
        newspecies.genus = s[1]
        if s[2] != ".":
            newspecies.subgenus = s[2]
        # newspecies.subgenus = newspecies.genus  # this is temporary until other pieces are in place
        newspecies.type_species = s[3]
        newspecies.type_reference = s[4]
        newspecies.common = s[5]
        newspecies.commonext = s[6]
        newspecies.range = s[7]
        newspecies.range_references = s[8]
        newspecies.region = s[9]
        newspecies.status = s[10]
        newspecies.taxonid = s[11]
        newspecies.eolid = s[12]
        newspecies.inatid = s[13]
        newspecies.gbifid = s[14]
        species_list.append(newspecies)
    species_list.sort()  # sort into alphabetical order
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
        newvideo.width = int(v[5])
        newvideo.height = int(v[6])
        newvideo.format = v[7]
        newvideo.date_location = v[8]
        newvideo.author = v[9]
        newvideo.notes = v[10]
        video_list.append(newvideo)
    return video_list


def read_higher_taxa_data(filename: str) -> Tuple[list, dict]:
    """
    read data on taxa of ranks other than species
    """
    tmplist = read_simple_file(filename)
    taxon_list = []
    tmpdict = {}
    for g in tmplist:
        new_taxon = TMB_Classes.RankedTaxonClass()
        new_taxon.name = g[0]
        new_taxon.taxon_rank = g[1]
        if g[2] != ".":
            if g[2] in tmpdict:
                p = tmpdict[g[2]]
                new_taxon.parent = p
                p.children.append(new_taxon)
            else:
                report_error("Import Error: Taxon Parent Not Found: " + g[2])
        new_taxon.author = g[3]
        new_taxon.type_species = g[4]
        new_taxon.notes = g[5]
        new_taxon.taxonid = g[6]
        new_taxon.eolid = g[7]
        taxon_list.append(new_taxon)
        tmpdict[new_taxon.taxon_rank + new_taxon.name] = new_taxon
    return taxon_list, tmpdict


def read_taxon_rank_data(filename: str) -> list:
    """
    read data on type of taxonomic ranks
    """
    tmplist = read_simple_file(filename)
    rank_list = []
    for g in tmplist:
        new_rank = TMB_Classes.TaxonTypeClass()
        new_rank.rank = g[0]
        new_rank.plural = g[1]
        new_rank.notes = g[2]
        rank_list.append(new_rank)
    return rank_list


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
        locdict[newloc.name] = newloc
    return locdict


def get_webpage(url: str, encoding: str) -> list:
    """
    function to fetch the webpage specifed by url and return a list containing the contents of the page
    """
    webpage = urllib.request.urlopen(url)
    page = webpage.read()
    page = page.decode(encoding)
    lines = page.split('\n')
    return lines


def fetch_inat_data(species: list) -> dict:
    """
    function to fetch species observation data from iNaturalist
    """

    # INatData = namedtuple("INatData", ["coords", "url"])

    inat_data = {}
    print("...Importing iNaturalist Data...")
    for s in tqdm(species):
        time.sleep(5)
        if s.inatid != ".":
            coords = []
            page = 0
            next_page = True
            while next_page:
                page += 1
                raw_data = get_webpage("https://www.inaturalist.org/observations.csv?taxon_id=" + s.inatid +
                                       "&per_page=200&quality_grade=research&page=" + str(page), "utf-8")
                if len(raw_data) > 2:  # header plus the blank line at the end; data would require at least 3 lines
                    for data in csv.reader(raw_data[1:]):
                        if len(data) > 0:
                            try:
                                point = TMB_Classes.Point(eval(data[4]), eval(data[5]))
                                urlstr = data[8]
                                # coords.append(point)
                                coords.append(TMB_Classes.INatData(coords=point, url=urlstr))
                            except SyntaxError:
                                pass
                else:
                    next_page = False
            inat_data[s.species] = coords
    return inat_data


def read_species_blocks(filename: str) -> dict:
    blocks = {}
    with open(filename, "r") as infile:
        lines = infile.readlines()
    for line in lines[1:]:
        if line.strip() != "":
            species, startlat, startlon, endlat, endlon = line.strip().split("\t")
            blocks.setdefault(species, []).append(TMB_Classes.RangeBlock(eval(startlat), eval(startlon),
                                                                         eval(endlat), eval(endlon)))
    return blocks


def read_measurement_data(filename: str) -> list:
    data = []
    with open(filename, "r") as infile:
        dat = infile.readlines()
        for line in dat[2:]:
            d = line.strip().split("\t")
            if d[6] != "skip" and (d[9] != "." or d[10] != "."):  # used to skip redundant data or non-CW data
                new = TMB_Classes.Measurement()
                new.ref = d[0]
                new.location = d[1]
                new.id = d[2]
                new.species = d[3]
                new.sex = d[4]
                if d[5] != ".":
                    new.notes = d[5]
                new.type = d[7]
                if new.type == "individual":
                    new.value = eval(d[9])
                elif new.type == "range":
                    try:
                        new.n = int(d[8])
                    except ValueError:
                        new.n = 2  # a range requires a minimum of two individuals
                    new.value = TMB_Classes.MeasurementRange()
                    new.value.min_val = eval(d[10])
                    new.value.max_val = eval(d[11])
                elif "mean" in new.type:
                    try:
                        new.n = int(d[8])
                    except ValueError:
                        new.n = 1  # a mean requires a minimumof one individual
                    new.value = TMB_Classes.MeasurementMean()
                    new.value.mean = eval(d[9])
                    if new.type == "mean/sd":
                        new.value.sd = eval(d[12])
                    elif new.type == "mean/se":
                        new.value.se = eval(d[13])
                    elif new.type == "mean/sd/min/max":
                        new.value.sd = eval(d[12])
                        new.value.min_val = eval(d[10])
                        new.value.max_val = eval(d[11])
                elif "classcount" in new.type:
                    new.n = eval(d[8])  # allow for floating sample sizes due to averaging across samples
                    new.value = TMB_Classes.MeasurementRange()
                    new.value.min_val = eval(d[10])
                    new.value.max_val = eval(d[11])
                    new.class_id = d[6]
                data.append(new)
    return data


def read_abnormal_development_data(filename: str) -> list:
    """
    read abnormal development text info
    """
    with open(filename, "r", encoding="utf-8") as infile:
        lines = infile.readlines()
    return lines
