"""
Initialization of Paths and File Names
"""

import os


class InitializationData:
    def __init__(self):
        self.main_path = "fiddlercrab.info"

        # input file names and paths
        self.reference_ciation_file = "data/references_cites.txt"
        self.reference_file = "data/references.html"
        self.citation_info_file = "data/citeinfo.txt"
        self.species_data_file = "data/species_info.txt"
        self.specific_names_file = "data/specific_names.txt"
        self.common_names_file = "data/common_names.txt"
        self.subgenera_file = "data/subgenera.txt"
        self.photo_file = "data/photos.txt"
        self.video_file = "data/videos.txt"
        self.art_file = "data/art.txt"
        self.morphology_file = "data/morphology.txt"
        self.map_kml_file = "data/Fiddler Crabs.kml"
        self.location_file = "data/location_data.txt"

        self.error_log = "errorlog.txt"

        # site information
        self.site_title = "Fiddler Crabs"
        self.site_subtitle = "A Comprehensive Compendium and Guide to the Fiddler Crabs of the World"
        self.site_author = "Michael S. Rosenberg"
        self.site_address = "www.fiddlercrab.info"
        self.site_http = "http://"  # this leaves open the option of quick switching to https

    def site_url(self):
        return self.site_http + self.site_address


def initialize():
    init_data = InitializationData()
    os.chdir(init_data.main_path)
    return init_data
