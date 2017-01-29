"""
General Data Classes for the Taxonomy Manuscript Builder
"""


# ----classes----
class ReferenceClass:
    """ A class to hold references """
    def __init__(self):
        self.formatted_html = ""
        self.citation = ""
        self.cite_key = ""
        self.language = ""

    def year(self):
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

    def author(self):
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


class SubgenusClass:
    """ a class to hold subgenera """
    def __init__(self):
        self.subgenus = ""
        self.author = ""
        self.type_species = ""
        self.notes = ""
        self.taxonid = ""
        self.eolid = ""


class VideoClass:
    """ a class to hold video information """
    def __init__(self):
        self.species = ""
        self.n = 0
        self.activity = ""
        self.caption = ""
        self.length = ""
        self.size = ""
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
    def __init__(self):
        self.character = ""
        self.parent = ""
        self.image = ""
        self.description = ""
        self.caption = ""


class SpeciesClass:
    def __init__(self):
        self.species = ""
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


class CitationClass:
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

    def __lt__(self, x):
        if self.name == x.name:
            if self.context == x.context:
                return self.application < x.application
            else:
                return self.context < x.context
        else:
            return self.name < x.name


class LocationClass:
    def __init__(self):
        self.name = ""
        self.trimmed_name = ""
        self.latitude = 0
        self.longitude = 0
        self.parent = None
        self.notes = ""
        self.children = []
        self.alternates = []

    def n_children(self):
        return len(self.children)

    def n_alternates(self):
        return len(self.alternates)
