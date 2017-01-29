"""
Module to cross-check location data
"""

# from TMB_Import import *
import TMB_Import
import TMB_Initialize
import os
import codecs


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
    citation_data = TMB_Import.read_citation_file(init_data.citation_info_file)
    location_set = parse_data(citation_data)
    # create path for temp files
    if not os.path.exists("temp/"):
        os.makedirs("temp/")

    with codecs.open("temp/location_all.txt", "w", "utf-8") as outfile:
        for l in location_set:
            outfile.write(l + "\n")

    location_data = TMB_Import.read_location_data(init_data.location_file)
    location_names = list(location_data.keys())
    with codecs.open("temp/location_clean.txt", "w", "utf-8") as outfile:
        for loc in location_set:
            if loc not in location_names:
                outfile.write(loc + "\n")

    # species = read_species_data(init_data.species_data_file)
    # for s in species:
    #     location_map(s.species, citation_data, location_data)
    # unknown_map(citation_data, location_data)


if __name__ == "__main__":
    main()
