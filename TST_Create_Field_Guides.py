"""
This module is simply for testing the field guide creation without having to run the entirety of the main code
"""

import TMB_Initialize, Build_Website, TMB_Import, TMB_Create_Maps
from TMB_SpeciesXRef import init_species_crossref


def test_guides():
    TMB_Initialize.initialize()
    t_init_data = TMB_Initialize.INIT_DATA

    species = TMB_Import.read_species_data(t_init_data.species_data_file)
    init_species_crossref(species)

    field_guide_list = TMB_Import.read_field_guide_list(t_init_data.field_guide_file)
    field_guide_data = TMB_Import.read_field_guide_data(field_guide_list, t_init_data.field_guide_data_path)
    field_guide_map_data = TMB_Import.read_species_blocks(t_init_data.field_guide_map_file)
    fg_images = Build_Website.write_field_guides(field_guide_list, field_guide_data, field_guide_map_data)

    print("drawing maps")
    # TMB_Create_Maps.draw_field_guide_maps(t_init_data, field_guide_map_data)

    print("copying files")
    Build_Website.copy_field_guide_files(field_guide_list, fg_images)


if __name__ == "__main__":
    test_guides()
    # import matplotlib.font_manager
    # for x in matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf'):
    #     print(x)
