class CitationClass:
    def __init__(self):
        self.__citeKey = ""
        self.__nameKey = ""
        self.__name = ""
        self.__common = ""
        self.__where = ""
        self.__context = ""
        self.__application = ""
        self.__citeN = ""
        self.__actual = ""
        self.__source = ""
        self.__nameNote = ""
        self.__generalNote = ""
    def citeKey(self):
        return self.__citeKey
    def setCiteKey(self,x):
        self.__citeKey = x
    def nameKey(self):
        return self.__nameKey
    def setNameKey(self,x):
        self.__nameKey = x
    def name(self):
        return self.__name
    def setName(self,x):
        self.__name = x
    def common(self):
        return self.__common
    def setCommon(self,x):
        self.__common = x
    def where(self):
        return self.__where
    def setWhere(self,x):
        self.__where = x
    def context(self):
        return self.__context
    def setContext(self,x):
        self.__context = x
    def application(self):
        return self.__application
    def setApplication(self,x):
        self.__application = x
    def citeN(self):
        return self.__citeN
    def setCiteN(self,x):
        self.__citeN = x
    def actual(self):
        return self.__actual
    def setActual(self,x):
        self.__actual = x
    def source(self):
        return self.__source
    def setSource(self,x):
        self.__source = x
    def nameNote(self):
        return self.__nameNote
    def setNameNote(self,x):
        self.__nameNote = x
    def generalNote(self):
        return self.__generalNote
    def setGeneralNote(self, x):
        self.__generalNote = x
    def __lt__(self, x):
        if self.name() == x.name():
            if self.context() == x.context():
                return self.application() < x.application()
            else:
                return self.context() < x.context()
        else:
            return self.name() < x.name()


class SpeciesClass:
    def __init__(self):
        self.__species = ""
        self.__subgenus = ""
        self.__typeSpecies = ""
        self.__typeRef = ""
        self.__common = ""
        self.__commonext = ""
        self.__range = ""
        self.__rangeRefs = ""
        self.__region = ""
        self.__status = ""
        self.__taxonid = ""
        self.__EOLid = ""
        self.__iNatid = ""
        self.__gbifid = ""
    def species(self):
        return self.__species
    def setSpecies(self, x):
        self.__species = x
    def subgenus(self):
        return self.__subgenus
    def setSubgenus(self, x):
        self.__subgenus = x
    def typeSpecies(self):
        return self.__typeSpecies
    def setTypeSpecies(self, x):
        self.__typeSpecies = x
    def typeRef(self):
        return self.__typeRef
    def setTypeRef(self, x):
        self.__typeRef = x
    def common(self):
        return self.__common
    def setCommon(self, x):
        self.__common = x
    def commonext(self):
        return self.__commonext
    def setCommonext(self, x):
        self.__commonext = x
    def range(self):
        return self.__range
    def setRange(self, x):
        self.__range = x
    def rangeRefs(self):
        return self.__rangeRefs
    def setRangeRefs(self, x):
        self.__rangeRefs = x
    def region(self):
        return self.__region
    def setRegion(self, x):
        self.__region = x
    def status(self):
        return self.__status
    def setStatus(self, x):
        self.__status = x
    def taxonid(self):
        return self.__taxonid
    def setTaxonid(self, x):
        self.__taxonid = x
    def EOLid(self):
        return self.__EOLid
    def setEOLid(self, x):
        self.__EOLid = x
    def iNatid(self):
        return self.__iNatid
    def setiNatid(self, x):
        self.__iNatid = x
    def gbifid(self):
        return self.__gbifid
    def setgbifid(self, x):
        self.__gbifid = x


def read_citations():
    """ read citation data """
    # citation info
    citelist = []
    gotheader = False
    with open("citeinfo.txt", "r") as reffile:
        for line in reffile:
            if not gotheader:
                gotheader = True
            else:
                line = line.replace("\"\"", "\"")
                cite = line.strip().split("\t")
                for i, x in enumerate(cite):
                    if x.startswith("\"") and x.endswith("\""):
                        cite[i] = x[1:len(x)-1]
                newcite = CitationClass()
                newcite.setCiteKey(cite[0])
                newcite.setNameKey(cite[1])
                newcite.setName(cite[2])
                newcite.setCommon(cite[3])
                newcite.setWhere(cite[4])
                newcite.setContext(cite[5])
                newcite.setApplication(cite[6])
                newcite.setCiteN(cite[7])
                newcite.setActual(cite[8])
                newcite.setSource(cite[9])
                newcite.setNameNote(cite[10])
                newcite.setGeneralNote(cite[11])
                citelist.append(newcite)
    return citelist


def read_simple_file(fname):
    """ read data from generic flatfile """
    infile = open(fname, "r")
    # infile = codecs.open(fname,"r")
    splist = []
    gotheader = False
    for line in infile:
        if gotheader:
            line = line.strip()
            line = line.replace("\"\"", "\"")
            spinfo = line.split("\t")
            for i, x in enumerate(spinfo):
                if x.startswith("\"") and x.endswith("\""):
                    spinfo[i] = x[1:len(x)-1]
            splist.append(spinfo)
        else:
            gotheader = True
    infile.close()
    return splist


def get_species():
    """ read data from species flatfile """
    tmplist = read_simple_file("species_info.txt")
    slist = []
    for s in tmplist:
        newspecies = SpeciesClass()
        newspecies.setSpecies(s[0])
        newspecies.setSubgenus(s[1])
        newspecies.setTypeSpecies(s[2])
        newspecies.setTypeRef(s[3])
        newspecies.setCommon(s[4])
        newspecies.setCommonext(s[5])
        newspecies.setRange(s[6])
        newspecies.setRangeRefs(s[7])
        newspecies.setRegion(s[8])
        newspecies.setStatus(s[9])
        newspecies.setTaxonid(s[10])
        newspecies.setEOLid(s[11])
        newspecies.setiNatid(s[12])
        newspecies.setgbifid(s[13])
        slist.append(newspecies)
    return slist


def parse_data(citations):
    places = set()
    for c in citations:
        if (c.context() == "location") or (c.context() == "specimen"):
            p = c.application()
            if p == ".":
                print(c.citeKey())
            elif p[0] != "[":
                if "[" in p:
                    p = p[:p.find("[")-1]
                places.add(p)
    place_list = sorted(list(places))
    return place_list


def read_location_data():
    with open("location_data.txt", "r") as infile:
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
            if (c.actual() == species) and ((c.context() == "location") or
                                            (c.context() == "specimen")):                                    
                p = c.application()
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
            if ((c.actual() == "?") or (c.actual() == ".")) and ((c.context() == "location") or
                                                                 (c.context() == "specimen")):
                unknown.append(c)
        for u in unknown:        
            p = u.application()
            if p[0] != "[":
                if "[" in p:
                    p = p[:p.find("[")-1]
            if p in locations:
                d = locations[p]
            else:
                d = ("0", "0")
            outfile.write(u.citeKey() + "\t" + u.name() + "\t" + u.common() + "\t" + p + "\t" + d[0] + "\t" + d[1] +
                          "\n")


def main():
    citation_data = read_citations()
    location_set = parse_data(citation_data)
    with open("location_all.txt", "w") as outfile:
        for l in location_set:
            outfile.write(l + "\n")

    loc_names, location_data = read_location_data()
    with open("location_clean.txt", "w") as outfile:
        for l in location_set:
            if l not in loc_names:
                outfile.write(l + "\n")

    species = get_species()
    for s in species:
        location_map(s.species(), citation_data, location_data)
    unknown_map(citation_data, location_data)


if __name__ == "__main__":
    main()
