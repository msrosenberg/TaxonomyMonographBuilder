"""
Module to cross-check location data
"""

# import TMB_Classes
import codecs
from TMB_Import import *
import TMB_Initialize

# def read_citations():
#     """ read citation data """
#     # citation info
#     citelist = []
#     gotheader = False
#     with open("citeinfo.txt", "r") as reffile:
#         for line in reffile:
#             if not gotheader:
#                 gotheader = True
#             else:
#                 line = line.replace("\"\"", "\"")
#                 cite = line.strip().split("\t")
#                 for i, x in enumerate(cite):
#                     if x.startswith("\"") and x.endswith("\""):
#                         cite[i] = x[1:len(x)-1]
#                 newcite = TMB_Classes.CitationClass()
#                 newcite.cite_key = cite[0]
#                 newcite.name_key = cite[1]
#                 newcite.name = cite[2]
#                 newcite.common = cite[3]
#                 newcite.where = cite[4]
#                 newcite.context = cite[5]
#                 newcite.application = cite[6]
#                 newcite.cite_n = cite[7]
#                 newcite.actual = cite[8]
#                 newcite.source = cite[9]
#                 newcite.name_note = cite[10]
#                 newcite.general_note = cite[11]
#                 citelist.append(newcite)
#     return citelist


def parse_data(citations):
    places = set()
    for c in citations:
        if (c.context == "location") or (c.context == "specimen"):
            p = c.application
            if p == ".":
                print(c.cite_key)
            elif p[0] != "[":
                if "[" in p:
                    p = p[:p.find("[")-1]
                places.add(p)
    place_list = sorted(list(places))
    return place_list


def read_location_data(filename):
    with codecs.open(filename, "r", "utf-8") as infile:
        dohead = True
        names = []
        full = {}
        for line in infile:
            if dohead:
                dohead = False
            else:
                d = line.strip().split("\t")
                n = d[0].replace("\"", "")
                names.append(n)
                full[n] = (d[1], d[2])
    return names, full


def location_map(species, citations, locations):
    with open("location checks/" + species + "_coords.txt", "w") as outfile:
        places = set()
        for c in citations:
            if (c.actual == species) and ((c.context == "location") or
                                          (c.context == "specimen")):
                p = c.application
                if p[0] != "[":
                    if "[" in p:
                        p = p[:p.find("[")-1]
                    places.add(p)
        place_list = sorted(list(places))
        for p in place_list:
            if p in locations:
                d = locations[p]
                outfile.write(p + "\t" + d[0] + "\t" + d[1] + "\n")


def unknown_map(citations, locations):
    with open("location checks/unknown_coords.txt", "w") as outfile:
        unknown = []
        for c in citations:
            if ((c.actual == "?") or (c.actual == ".")) and ((c.context == "location") or
                                                             (c.context == "specimen")):
                unknown.append(c)
        for u in unknown:
            p = u.application
            if p[0] != "[":
                if "[" in p:
                    p = p[:p.find("[")-1]
            if p in locations:
                d = locations[p]
            else:
                d = ("0", "0")
            outfile.write(u.cite_key + "\t" + u.name + "\t" + u.common + "\t" + p + "\t" + d[0] + "\t" + d[1] + "\n")


def main():
    init_data = TMB_Initialize.initialize()
    citation_data = read_citation_file(init_data.citation_info_file)
    location_set = parse_data(citation_data)
    with codecs.open("temp/location_all.txt", "w", "utf-8") as outfile:
        for l in location_set:
            outfile.write(l + "\n")

    loc_names, location_data = read_location_data("data/location_data.txt")
    with codecs.open("temp/location_clean.txt", "w", "utf-8") as outfile:
        for l in location_set:
            if l not in loc_names:
                outfile.write(l + "\n")

    # species = read_species_data(init_data.species_data_file)
    # for s in species:
    #     location_map(s.species, citation_data, location_data)
    # unknown_map(citation_data, location_data)


if __name__ == "__main__":
    main()