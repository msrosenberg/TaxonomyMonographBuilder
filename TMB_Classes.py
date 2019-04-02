"""
General Data Classes for the Taxonomy Manuscript Builder
"""

from typing import Optional
from TMB_Common import Number


# ----classes----
class ReferenceClass:
    """ A class to hold references """
    def __init__(self):
        self.formatted_html = ""
        self.citation = ""
        self.cite_key = ""
        self.language = ""

    def year(self) -> Optional[int]:
        y = self.citation
        y = y[y.find("(") + 1:y.find(")")]
        if (y != "?") and (y.lower() != "in press"):
            if y[0] == "~":
                y = y[1:]
            if len(y) > 4:
                y = y[:4]
            y = int(y)
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
    """ a class to hold subgenera """
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
        self.type_reference = ""
        self.common = ""
        self.commonext = ""
        self.range = ""
        self.range_references = ""
        self.region = ""
        self.status = ""
        self.taxonid = ""
        self.eolid = ""
        self.inatid = ""
        self.gbifid = ""

    def __lt__(self, x):
        # return self.species < x.species
        return self.fullname() < x.fullname()

    def fullname(self) -> str:
        return self.genus + " " + self.species


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
        # self.ne_lat = None
        # self.ne_lon = None
        # self.sw_lat = None
        # self.sw_lon = None
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
