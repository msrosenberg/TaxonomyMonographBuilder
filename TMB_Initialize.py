"""
Initialization of Paths and File Names
"""

import os
import datetime


INIT_DATA = None


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
        self.higher_taxa_file = "data/higher_taxa.txt"
        self.taxon_ranks_file = "data/taxon_ranks.txt"
        self.photo_file = "data/photos.txt"
        self.video_file = "data/videos.txt"
        self.art_file = "data/art.txt"
        self.morphology_file = "data/morphology.txt"
        self.map_kml_file = "data/Fiddler Crabs.kml"
        self.location_file = "data/location_data.txt"
        self.species_changes_new = "data/species_changes_new.txt"
        self.species_changes_spelling = "data/species_changes_spelling.txt"
        self.species_changes_synonyms = "data/species_changes_synonyms.txt"
        self.species_range_blocks = "data/species_range_blocks.txt"
        self.measurement_file = "data/measurement_data.txt"
        self.unusual_development_file = "data/unusual_development.txt"
        self.handedness_file = "data/handedness.txt"

        # taxonomic key data
        self.tax_key_trait_file = "data/tax_key_trait_data.txt"
        self.tax_key_trait_var_file = "data/tax_key_variant_data.txt"
        self.tax_key_generic_file = "data/tax_key_generic_notes.txt"
        self.tax_key_taxa_file = "data/tax_key_taxa_data.txt"

        self.error_log = "errorlog.txt"

        # map data
        self.map_primary = "resources/ne_10m_admin_0_countries.shp"
        self.map_secondary = "resources/ne_10m_admin_1_states_provinces.shp"
        self.map_islands = "resources/ne_10m_minor_islands.shp"
        self.map_coastline = "resources/ne_10m_coastline.shp"

        # site information
        self.site_title = "Fiddler Crabs"
        self.site_subtitle = "A Comprehensive Compendium and Guide to the Fiddler Crabs of the World"
        self.site_author = "Michael S. Rosenberg"
        self.site_address = "www.fiddlercrab.info"
        self.site_http = "https://"  # this leaves open the option of quick switching between http and https
        self.site_author_email = "msrosenberg@vcu.edu"

        # major web output file names
        self.species_url = "uca_species.html"
        self.ref_url = "uca_references.html"
        self.ref_sum_url = "uca_refsummary.html"
        self.syst_url = "uca_systematics.html"
        self.common_url = "uca_common_names.html"
        self.photo_url = "uca_photos.html"
        self.video_url = "uca_videos.html"
        self.map_url = "uca_ranges.html"
        self.lifecycle_url = "uca_lifecycle.html"
        self.unsuual_dev_url = "uca_unusual_development.html"
        self.tree_url = "uca_phylogeny.html"
        self.art_sci_url = "uca_art_science.html"
        self.art_stamp_url = "uca_art_stamps.html"
        self.art_craft_url = "uca_art_crafts.html"
        self.morph_url = "uca_morphology.html"
        self.cite_url = "citation.html"
        self.name_sum_url = "name_graphs.html"
        self.synonyms_genera = "synonymys_uca.html"

        # customization of fonts on graphs and charts
        self.graph_font = "Noto Serif"  # font to use for PNG versions of graphs
        self.wc_font_path = r"C:\Windows\Fonts\NotoSerif-regular.ttf"  # wordcloud requires a path to the font

        # general data
        self.version = datetime.datetime.now().strftime("%Y.%m.%d.%H.%M")
        self.start_year = 1758  # Start with Linnean taxonomy
        self.current_year = datetime.date.today().year

    def site_url(self) -> str:
        return self.site_http + self.site_address


def initialize() -> None:
    global INIT_DATA
    INIT_DATA = InitializationData()
    os.chdir(INIT_DATA.main_path)
