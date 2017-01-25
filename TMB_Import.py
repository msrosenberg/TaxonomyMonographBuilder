"""
Functions to read data from files
"""

import codecs
import TMB_Classes
from TMB_Error import *


def read_simple_file(filename):
    """ read data from generic flatfile """
    with open(filename, "r") as infile:
        splist = []
        got_header = False
        for line in infile:
            if got_header:
                line = line.strip()
                line = line.replace("\"\"", "\"")
                spinfo = line.split("\t")
                for i, x in enumerate(spinfo):
                    if x.startswith("\"") and x.endswith("\""):
                        spinfo[i] = x[1:len(x)-1]
                splist.append(spinfo)
            else:
                got_header = True
    return splist


def read_citation_file(citation_filename):
    # citation info
    with open(citation_filename, "r") as reffile:
        citelist = []
        got_header = False
        for line in reffile:
            if not got_header:
                got_header = True
            else:
                line = line.replace("\"\"", "\"")
                cite = line.strip().split("\t")
                for i, x in enumerate(cite):
                    if x.startswith("\"") and x.endswith("\""):
                        cite[i] = x[1:len(x)-1]
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
                citelist.append(newcite)
                # cite_done[cite[0]][0] = True
    return citelist


def read_reference_data(ref_filename, formatref_filename, citation_filename, logfile):
    """ read reference data """
    reflist = []
    year_dat = {}
    cite_done = {}
    # reference citation data
    with codecs.open(ref_filename, "r", "utf-8") as reffile:
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
            # cite_done[ref[1]] = [False, y]
            cite_done[newref.cite_key] = [False, y]
            reflist.append(newref)

    # formatted references from html
    with codecs.open(formatref_filename, "r", "utf-8") as reffile:
        c = -1
        for line in reffile:
            line = line.strip()
            if line.endswith("<p>"):
                line = line[:line.find("<p>")]
                line = line.replace("<i>", "<em>")
                line = line.replace("</i>", "</em>")
                c += 1
                newref = reflist[c]
                newref.formatted_html = line
    refdict = {}
    for ref in reflist:
        if ref.cite_key in refdict and ref.cite_key != "<pending>":
            report_error(logfile, "Duplicate reference key:" + ref.cite_key)
        refdict[ref.cite_key] = ref
    # citation info
    citelist = read_citation_file(citation_filename)
    # with open(citation_filename, "r") as reffile:
    #     citelist = []
    #     got_header = False
    #     for line in reffile:
    #         if not got_header:
    #             got_header = True
    #         else:
    #             line = line.replace("\"\"", "\"")
    #             cite = line.strip().split("\t")
    #             for i, x in enumerate(cite):
    #                 if x.startswith("\"") and x.endswith("\""):
    #                     cite[i] = x[1:len(x)-1]
    #             newcite = TMB_Classes.CitationClass()
    #             newcite.cite_key = cite[0]
    #             newcite.name_key = cite[1]
    #             newcite.name = cite[2]
    #             newcite.common = cite[3]
    #             newcite.where = cite[4]
    #             newcite.context = cite[5]
    #             newcite.application = cite[6]
    #             newcite.cite_n = cite[7]
    #             newcite.actual = cite[8]
    #             newcite.source = cite[9]
    #             newcite.name_note = cite[10]
    #             newcite.general_note = cite[11]
    #             citelist.append(newcite)
    #             cite_done[cite[0]][0] = True
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
    return reflist, refdict, citelist, year_dat, cite_count


def read_species_data(filename):
    """ read data from species flatfile """
    tmplist = read_simple_file(filename)
    slist = []
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
        slist.append(newspecies)
    return slist


def read_photo_data(filename):
    """ read data from photo flatfile """
    tmplist = read_simple_file(filename)
    plist = []
    for p in tmplist:
        newphoto = TMB_Classes.PhotoClass()
        newphoto.species = p[0]
        newphoto.n = p[1]
        newphoto.caption = p[2]
        plist.append(newphoto)
    return plist


def read_video_data(filename):
    """ read data from video flatfile """
    tmplist = read_simple_file(filename)
    vlist = []
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
        vlist.append(newvideo)
    return vlist


def read_subgenera_data(filename):
    """ read subgenera data """
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


def read_specific_names_data(filename):
    """ read specific name data """
    tmplist = read_simple_file(filename)
    splist = []
    for s in tmplist:
        newname = TMB_Classes.SpecificNameClass()
        newname.name = s[0]
        newname.variations = s[1]
        newname.synonym = s[2]
        newname.original_binomial = s[3]
        newname.priority_source = s[4]
        newname.meaning = s[5]
        newname.notes = s[6]
        splist.append(newname)
    return splist


def read_art_data(filename):
    """ read art data """
    tmplist = read_simple_file(filename)
    artlist = []
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
        artlist.append(newart)
    return artlist


def read_morphology_data(filename):
    """ read morphology data """
    tmplist = read_simple_file(filename)
    morphlist = []
    for m in tmplist:
        newmorph = TMB_Classes.MorphologyClass()
        newmorph.character = m[0]
        newmorph.parent = m[1]
        newmorph.image = m[2]
        newmorph.caption = m[3]
        newmorph.description = m[4]
        morphlist.append(newmorph)
    return morphlist


def read_common_name_data(filename):
    with codecs.open(filename, "r", "utf-8") as infile:
        lines = infile.readlines()
    return lines
