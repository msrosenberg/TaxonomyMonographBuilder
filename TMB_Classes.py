"""
General Data Classes for the Taxonomy Manuscript Builder
"""

from typing import Optional
from TMB_Common import Number
from TMB_Error import report_error


# ----classes----
class ReferenceClass:
    """ A class to hold references """
    def __init__(self):
        self.formatted_html = ""
        self.citation = ""
        self.cite_key = ""
        self.language = ""
        self.doi = None
        self.taxon_author = None

    def year(self) -> Optional[int]:
        y = self.citation
        y = y[y.find("(") + 1:y.find(")")]
        if (y != "?") and (y.lower() != "in press"):
            if y[0] == "~":
                y = y[1:]
            if len(y) > 4:
                y = y[:4]
            try:
                y = int(y)
            except ValueError:
                report_error("Error finding year in reference citation info: " + self.citation)
            return y
        else:
            return None

    def author(self) -> str:
        return self.citation[:self.citation.find("(")].strip()


class SpecificNameClass:
    """ a class to hold specific names """
    def __init__(self):
        self.name = ""
        self.variations = ""
        self.synonym = ""
        self.original_binomial = ""
        self.priority_source = ""
        self.meaning = ""
        self.notes = ""

    def __lt__(self, x):
        return self.name < x.name


class RankedTaxonClass:
    """ a class to hold ranked taxa """
    def __init__(self):
        self.name = ""
        self.author = ""
        self.type_species = ""
        self.notes = ""
        self.taxonid = ""
        self.eolid = ""
        self.parent = None
        self.taxon_rank = ""
        self.children = []

    def __lt__(self, x):
        return self.name < x.name

    def n_children(self):
        return len(self.children)


class TaxonTypeClass:
    """ a class to hold info about types of taxonomic ranks """
    def __init__(self):
        self.rank = ""
        self.plural = ""
        self.notes = ""


class VideoClass:
    """ a class to hold video information """
    def __init__(self):
        self.species = ""
        self.n = 0
        self.activity = ""
        self.caption = ""
        self.length = ""
        self.height = 0
        self.width = 0
        self.format = ""
        self.date_location = ""
        self.author = ""
        self.notes = ""


class PhotoClass:
    """ a class to hold photo information """
    def __init__(self):
        self.species = ""
        self.n = 0
        self.caption = ""


class ArtClass:
    """ a class to hold art information """
    def __init__(self):
        self.art_type = ""
        self.author = ""
        self.year = ""
        self.title = ""
        self.image = ""
        self.ext = ""
        self.species = ""
        self.notes = ""
        self.cite_key = ""


class MorphologyClass:
    """ a class to hold morphology information """
    def __init__(self):
        self.character = ""
        self.parent = ""
        self.image = ""
        self.description = ""
        self.caption = ""


class SpeciesClass:
    """ a class to hold species information """
    def __init__(self):
        self.species = ""
        self.genus = ""
        self.subgenus = ""
        self.type_species = ""
        self.type_reference = None
        self.common = ""
        self.commonext = ""
        self.range = ""
        self.range_references = ""
        self.realm = ""
        self.status = ""
        self.taxonid = ""
        self.eolid = ""
        self.inatid = ""
        self.gbifid = ""

    def __lt__(self, x):
        # return self.species < x.species
        return self.binomial() < x.binomial()

    def binomial(self) -> str:
        return self.genus + " " + self.species

    def fullname(self) -> str:
        if self.subgenus == "":
            return self.binomial()
        else:
            return self.genus + " (" + self.subgenus + ") " + self.species

    def authority(self) -> str:
        ogenus = self.type_species[:self.type_species.find(" ")].strip()
        author = self.type_reference.author() + ", " + str(self.type_reference.year())
        if ogenus == self.genus:
            return author
        else:
            return "(" + author + ")"


class CitationClass:
    """ a class to hold citation data """
    def __init__(self):
        self.cite_key = ""
        self.name_key = ""
        self.name = ""
        self.common = ""
        self.where = ""
        self.context = ""
        self.application = ""
        self.cite_n = ""
        self.actual = ""
        self.source = ""
        self.name_note = ""
        self.general_note = ""
        self.applied_cites = set()

    def __lt__(self, x):
        if self.name == x.name:
            if self.context == x.context:
                return self.application < x.application
            else:
                return self.context < x.context
        else:
            return self.name < x.name


class LocationClass:
    """ a class to hold location data """
    def __init__(self):
        self.name = ""
        self.trimmed_name = ""
        self.latitude = 0
        self.longitude = 0
        self.parent = None
        self.secondary_parents = []
        self.notes = None
        self.children = []
        self.secondary_children = []
        self.alternates = []
        self.validity = ""
        self.unknown = False

    def n_children(self) -> int:
        return len(self.children)

    def n_alternates(self) -> int:
        return len(self.alternates)

    def all_children(self) -> list:
        result = []
        result.extend(self.direct_children())
        for c in self.direct_children():
            result.extend(c.all_children())
        return list(set(result))

    def n_secondary_parents(self) -> int:
        return len(self.secondary_parents)

    def n_secondary_children(self) -> int:
        return len(self.secondary_children)

    def direct_children(self) -> list:
        return self.children + self.secondary_children

    def n_direct_children(self) -> int:
        return self.n_children() + self.n_secondary_children()

    def n_parents(self) -> int:
        if self.parent is None:
            cnt = 0
        else:
            cnt = 1
        return cnt + self.n_secondary_parents()


class Point:
    def __init__(self, lat: Number = 0, lon: Number = 0):
        self.lat = lat
        self.lon = lon


class RangeCell:
    def __init__(self, startlat=0, startlon=0, endlat=0, endlon=0):
        self.lower_left_lat = startlat
        self.lower_left_lon = startlon
        self.upper_right_lat = endlat
        self.upper_right_lon = endlon
        if endlon < startlon:
            self.wrap = True
        else:
            self.wrap = False

    def __repr__(self):
        return "{}, {}, {}, {}".format(self.lower_left_lat, self.lower_left_lon, self.upper_right_lat,
                                       self.upper_right_lon)

    def inside(self, lat: Number, lon: Number) -> bool:
        if (self.lower_left_lat <= lat <= self.upper_right_lat) and \
                (self.lower_left_lon <= lon <= self.upper_right_lon):
            return True
        elif self.wrap:
            if lon < 0:
                lon += 360
            if (self.lower_left_lat <= lat <= self.upper_right_lat) and \
                    (self.lower_left_lon <= lon <= self.upper_right_lon + 360):
                return True
            else:
                return False
        else:
            return False


class INatData:
    def __init__(self, coords: Point = None, url: str = ""):
        self.coords = coords
        self.url = url


class MeasurementRange:
    def __init__(self):
        self.min_val = 0
        self.max_val = 0

    def midpoint(self):
        return self.min_val + (self.max_val - self.min_val)/2


class MeasurementMean:
    def __init__(self):
        self.mean = 0
        self.sd = None
        self.se = None
        self.min_val = None
        self.max_val = None


class Measurement:
    def __init__(self):
        self.ref = ""
        self.location = ""
        self.id = ""
        self.species = ""
        self.sex = ""
        self.notes = ""
        self.type = ""
        self.n = 0
        self.value = None
        self.class_id = None


class SpeciesMeasurements:
    def __init__(self):
        self.other = {}
        self.male = {}
        self.female = {}
        self.all = {}


class Handedness:
    def __init__(self):
        self.ref = ""
        self.species = ""
        self.total_cnt = 0
        self.right_cnt = 0
        self.left_cnt = 0
        self.right_p = 0
        self.left_p = 0
        self.notes = ""
