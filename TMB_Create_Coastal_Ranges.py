"""
Create Species Range Maps from the intersection of rectangular bounds and coastlines

This module is for creating and testing species range maps outside of the normal program pipeline.
In addition to calculating and drawing the range maps, it will also draw the maps of the blocks from
which the ranges are derived.

The code in this module does not make up part of the regular pipeline and is not used in regular site updates
"""

# from typing import Tuple, Optional
# import bisect
import matplotlib.pyplot as mplpy
import TMB_Create_Maps
import TMB_Initialize
import TMB_ImportShape
import TMB_Import
# import numpy
# from tqdm import tqdm


__TMP_PATH__ = "temp/"
__OUTPUT_PATH__ = __TMP_PATH__ + "maps/"


def test_draw_ranges(species: str, ranges: list, base_map: TMB_Create_Maps.BaseMap, draw_blank: bool = False,
                     do_bw: bool = False) -> None:
    """
    only for testing purposes
    """
    if do_bw:
        fig, faxes = mplpy.subplots(figsize=[3.75, 1.875])
        # fig, faxes = mplpy.subplots(figsize=[7.5, 3.75])
    else:
        fig, faxes = mplpy.subplots(figsize=[9, 4.5])
    for spine in faxes.spines:
        faxes.spines[spine].set_visible(False)
    maxlat = -90
    minlat = 90
    maxlon = -180
    minlon = 180

    mid_atlantic = False
    all_lons = []
    all_lats = []
    for line in ranges:
        for p in line:
            maxlon = max(maxlon, p.lon)
            maxlat = max(maxlat, p.lat)
            minlon = min(minlon, p.lon)
            minlat = min(minlat, p.lat)
            if 0 > p.lon > -50:
                mid_atlantic = True
            all_lons.append(p.lon)
            all_lats.append(p.lat)
    minlon, maxlon, minlat, maxlat = TMB_Create_Maps.adjust_map_boundaries(minlon, maxlon, minlat, maxlat)

    (minlon, maxlon, minlat, maxlat,
     wrap_lons) = TMB_Create_Maps.draw_and_adjust_basemap(faxes, base_map, mid_atlantic, minlon, maxlon, minlat,
                                                          maxlat, all_lons, all_lats)

    if draw_blank:
        mplpy.xlim(minlon, maxlon)
        mplpy.ylim(minlat, maxlat)
        # mplpy.xlabel("longitude")
        # mplpy.ylabel("latitude")
        mplpy.rcParams["svg.fonttype"] = "none"
        mplpy.tight_layout()
        TMB_Create_Maps.adjust_longitude_tick_values(faxes)
        mplpy.savefig(__OUTPUT_PATH__ + "blocks_blank_test_range.png", format="png", dpi=1200)
        mplpy.savefig(__OUTPUT_PATH__ + "blocks_blank_test_range.svg", format="svg", dpi=1200)

    for line in ranges:
        lons = []
        lats = []
        for p in line:
            lon = p.lon
            if wrap_lons and lon < 0:
                lon += 360
            lons.append(lon)
            lats.append(p.lat)
        if do_bw:
            faxes.plot(lons, lats, color="black", linewidth=1)
        else:
            faxes.plot(lons, lats, color="red", linewidth=1)

    if do_bw:
        mplpy.rcParams.update({"font.size": 8})
    mplpy.xlim(minlon, maxlon)
    mplpy.ylim(minlat, maxlat)
    # mplpy.xlabel("longitude")
    # mplpy.ylabel("latitude")
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    TMB_Create_Maps.adjust_longitude_tick_values(faxes)
    mplpy.savefig(__OUTPUT_PATH__ + "blocks_" + species + "_test_range.png", format="png", dpi=1200)
    mplpy.savefig(__OUTPUT_PATH__ + "blocks_" + species + "_test_range.svg", format="svg", dpi=1200)
    mplpy.close("all")


# def test_draw_provinces(provinces: dict, base_map: TMB_Create_Maps.BaseMap) -> None:
#     """
#     only for testing purposes
#     """
#     colors = ("red", "blue", "green", "yellow", "magenta", "cyan", "salmon")
#
#     fig, faxes = mplpy.subplots(figsize=[9, 4.5])
#     for spine in faxes.spines:
#         faxes.spines[spine].set_visible(False)
#     maxlat = -90
#     minlat = 90
#     maxlon = -180
#     minlon = 180
#
#     mid_atlantic = False
#     all_lons = []
#     all_lats = []
#     for province in provinces:
#         ranges = provinces[province]
#         for line in ranges:
#             for p in line:
#                 maxlon = max(maxlon, p.lon)
#                 maxlat = max(maxlat, p.lat)
#                 minlon = min(minlon, p.lon)
#                 minlat = min(minlat, p.lat)
#                 if 0 > p.lon > -50:
#                     mid_atlantic = True
#                 all_lons.append(p.lon)
#                 all_lats.append(p.lat)
#     minlon, maxlon, minlat, maxlat = TMB_Create_Maps.adjust_map_boundaries(minlon, maxlon, minlat, maxlat)
#
#     (minlon, maxlon, minlat, maxlat,
#      wrap_lons) = TMB_Create_Maps.draw_and_adjust_basemap(faxes, base_map, mid_atlantic, minlon, maxlon, minlat,
#                                                           maxlat, all_lons, all_lats)
#
#     for i, province in enumerate(provinces):
#         ranges = provinces[province]
#         if i < 7:
#             c = colors[i]
#         else:
#             c = "black"
#         for line in ranges:
#             lons = []
#             lats = []
#             for p in line:
#                 lon = p.lon
#                 if wrap_lons and lon < 0:
#                     lon += 360
#                 lons.append(lon)
#                 lats.append(p.lat)
#             faxes.plot(lons, lats, color=c, linewidth=3)
#
#     mplpy.xlim(minlon, maxlon)
#     mplpy.ylim(minlat, maxlat)
#     mplpy.xlabel("longitude")
#     mplpy.ylabel("latitude")
#     mplpy.rcParams["svg.fonttype"] = "none"
#     mplpy.tight_layout()
#     TMB_Create_Maps.adjust_longitude_tick_values(faxes)
#     mplpy.savefig(__OUTPUT_PATH__ + "blocks_provinces_test_range.png", format="png", dpi=1200)
#     mplpy.savefig(__OUTPUT_PATH__ + "blocks_provinces_test_range.svg", format="svg", dpi=1200)
#     mplpy.close("all")


def test_draw_blocks(species: str, blocks: list, base_map: TMB_Create_Maps.BaseMap) -> None:
    """
    only for cross-checking purposes

    this function draws the defined rectangles on the map, and labels them by number, to aid in
    evaluating that they cover the correct regions
    """
    fig, faxes = mplpy.subplots(figsize=[TMB_Create_Maps.FIG_WIDTH, TMB_Create_Maps.FIG_HEIGHT])
    for spine in faxes.spines:
        faxes.spines[spine].set_visible(False)

    maxlat = -90
    minlat = 90
    maxlon = -180
    minlon = 180
    mid_atlantic = False
    all_lons = []
    all_lats = []
    for block in blocks:
        maxlon = max(maxlon, block.lower_left_lon, block.upper_right_lon)
        maxlat = max(maxlat, block.lower_left_lat, block.upper_right_lat)
        minlon = min(minlon, block.lower_left_lon, block.upper_right_lon)
        minlat = min(minlat, block.lower_left_lat, block.upper_right_lat)
        if 0 > block.lower_left_lon > -50:
            mid_atlantic = True
        all_lons.extend([block.lower_left_lon, block.upper_right_lon])
        all_lats.extend([block.lower_left_lat, block.upper_right_lat])
    minlon, maxlon, minlat, maxlat = TMB_Create_Maps.adjust_map_boundaries(minlon, maxlon, minlat, maxlat)
    (minlon, maxlon, minlat, maxlat,
     wrap_lons) = TMB_Create_Maps.draw_and_adjust_basemap(faxes, base_map, mid_atlantic, minlon, maxlon, minlat,
                                                          maxlat, all_lons, all_lats)

    for i, block in enumerate(blocks):
        ll = block.lower_left_lon
        ur = block.upper_right_lon
        if wrap_lons and ll < 0:
            ll += 360
        if wrap_lons and ur < 0:
            ur += 360
        lons = [ll, ur, ur, ll, ll]
        midx = ll + (ur - ll)/2
        midy = block.lower_left_lat + (block.upper_right_lat - block.lower_left_lat)/2
        lats = [block.lower_left_lat, block.lower_left_lat, block.upper_right_lat, block.upper_right_lat,
                block.lower_left_lat]
        faxes.plot(lons, lats, color="red", linewidth=0.3)
        faxes.text(midx, midy, str(i+1), fontsize=6, color="blue")

    mplpy.xlim(minlon, maxlon)
    mplpy.ylim(minlat, maxlat)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    mplpy.savefig(__OUTPUT_PATH__ + "blocks_" + species + ".png", format="png", dpi=600)
    mplpy.close("all")


def test_draw_all_ranges(base_map: TMB_Create_Maps.BaseMap, species_maps: dict) -> None:
    fig, faxes = mplpy.subplots(figsize=[9, 4.5])
    for spine in faxes.spines:
        faxes.spines[spine].set_visible(False)
    TMB_Create_Maps.draw_base_map(faxes, base_map)
    for species in species_maps:
        species_range = species_maps[species]
        for line in species_range:
            TMB_Create_Maps.add_line_to_map(faxes, line, lw=2)

    mplpy.xlim(-180, 180)
    mplpy.ylim(-90, 90)
    faxes.axes.get_yaxis().set_visible(False)
    faxes.axes.get_xaxis().set_visible(False)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    mplpy.savefig(__OUTPUT_PATH__ + "blocks_all_test_range.png", format="png", dpi=600)
    mplpy.close("all")


def import_coastline_data(init_data: TMB_Initialize.InitializationData) -> list:
    coastline_map = TMB_ImportShape.import_arcinfo_shp(init_data.map_coastline)
    coastline_map.extend(TMB_ImportShape.import_arcinfo_shp(init_data.map_islands))
    return coastline_map


def calculate_ranges(init_data: TMB_Initialize.InitializationData, verbose: bool = False) -> None:
    base_map = TMB_Create_Maps.read_base_map(init_data.map_primary, None, init_data.map_islands)
    # coastline_map = TMB_ImportShape.import_arcinfo_shp(init_data.map_coastline)
    # coastline_map.extend(TMB_ImportShape.import_arcinfo_shp(init_data.map_islands))
    coastline_map = import_coastline_data(init_data)
    if verbose:
        print("Number of coastline elements:", len(coastline_map))

    species_blocks = TMB_Import.read_species_blocks(init_data.species_range_blocks)
    for species in species_blocks:
        test_draw_blocks(species, species_blocks[species], base_map)

    ranges = {}
    for species in species_blocks:
        if verbose:
            print("Determining {} range".format(species))
        ranges[species] = TMB_Create_Maps.get_range_map_overlap(species_blocks[species], coastline_map)
    for species in ranges:
        test_draw_ranges(species, ranges[species], base_map)

    # test_draw_all_ranges(base_map, ranges)
    # all_blocks = []
    # for species in species_blocks:
    #     all_blocks.extend(species_blocks[species])
    # all_range = TMB_Create_Maps.get_range_map_overlap(all_blocks, coastline_map)
    # test_draw_ranges("all_combined", all_range, base_map, draw_blank=True, do_bw=True)


def draw_provinces(init_data: TMB_Initialize.InitializationData) -> None:
    base_map = TMB_Create_Maps.read_base_map(init_data.map_primary, None, init_data.map_islands)
    coastline_map = import_coastline_data(init_data)
    print("Number of coastline elements:", len(coastline_map))
    provinces = TMB_Import.read_species_blocks("data/provinces.txt")
    for province in provinces:
        test_draw_blocks(province, provinces[province], base_map)
    ranges = {}
    for province in provinces:
        print("Determining {} range".format(province))
        ranges[province] = TMB_Create_Maps.get_range_map_overlap(provinces[province], coastline_map)
    for species in ranges:
        test_draw_ranges(species, ranges[species], base_map, do_bw=True)
    # test_draw_provinces(ranges, base_map)


# def range_in_cell(cell, species_range):
#     for line in species_range:
#         for p in line:
#             if cell.inside(p.lat, p.lon):
#                 return True
#     return False
#
#
# def count_species_in_cell(cell: RangeCell, ranges: dict) -> Tuple[int, set]:
#     species = set()
#     for s in ranges:
#         if range_in_cell(cell, ranges[s]):
#             species.add(s)
#     return len(species), species
#
#
# def count_species_in_grid(init_data: TMB_Initialize.InitializationData, coastal_cells: list, cells_per_degree=4,
#                           species_ranges: Optional[dict] = None):
#     print()
#     print("Determining Global Grid Cell Species Count")
#     latitudes = [-90 + x/cells_per_degree for x in range(180*cells_per_degree)]
#     longitudes = [-180 + x/cells_per_degree for x in range(360*cells_per_degree)]
#     nlats = len(latitudes)
#     nlons = len(longitudes)
#     # create empty matrix of counts; we use nan rather than 0 because we do not want to color empty cells
#     counts = numpy.full((nlats, nlons), numpy.nan)
#     x_ref = {}
#
#     coastline_map = import_coastline_data(init_data)
#
#     for i, lat in enumerate(latitudes):
#         for j, lon in enumerate(longitudes):
#             x_ref[lat, lon] = (i, j)
#
#     if species_ranges is None:  # calculate if not directly input
#         species_range_blocks = TMB_Import.read_species_blocks(init_data.species_range_blocks)
#         species_ranges = {}
#         for s in species_range_blocks:
#             species_ranges[s] = TMB_Create_Maps.get_range_map_overlap(species_range_blocks[s], coastline_map)
#
#     for coords in tqdm(coastal_cells):
#         lat, lon = coords[0], coords[1]
#         # print("...Working on cell {:0.2f}°, {:0.2f}°".format(lat, lon))
#         new_cell = RangeCell(lat, lon, lat + 1/cells_per_degree, lon + 1/cells_per_degree)
#         cnt, block_species = count_species_in_cell(new_cell, species_ranges)
#         if cnt > 0:
#             i, j = x_ref[lat, lon]
#             counts[i, j] = cnt
#
#     # for i, lat in enumerate(latitudes):
#     #     if abs(lat) < 45:  # do not bother checking for any cell above 45 degrees (north or south)
#     #         for j, lon in enumerate(longitudes):
#     #             print("...Working on cell {:0.2f}°, {:0.2f}°".format(lat, lon))
#     #             new_cell = RangeCell(lat, lon, lat + 1/cells_per_degree, lon + 1/cells_per_degree)
#     #             # cell_coast = TMB_Create_Maps.get_range_map_overlap([new_cell], coastline_map)
#     #             # if len(cell_coast) > 0:
#     #             cnt, block_species = count_species_in_cell(new_cell, species_ranges)
#     #             if cnt > 0:
#     #                 counts[i, j] = cnt
#     print()
#     return latitudes, longitudes, counts
#
#
# # def coast_in_cell(cell: RangeCell, coastline: list) -> bool:
# #     for part in coastline:
# #         for p in part:
# #             if cell.inside(p.lat, p.lon):
# #                 return True
# #     return False
#
#
# def identify_coastal_cells(coastline_map, cells_per_degree=4) -> list:
#     # coastal_cells = []
#     # latitudes = [-90 + x/cells_per_degree for x in range(180*cells_per_degree)]
#     # longitudes = [-180 + x/cells_per_degree for x in range(360*cells_per_degree)]
#     # for lat in latitudes:
#     #     if abs(lat) < 45:  # do not bother checking for any cell above 45 degrees (north or south)
#     #         print("working on lat {:0.2f}".format(lat))
#     #         for lon in longitudes:
#     #             new_cell = RangeCell(lat, lon, lat + 1/cells_per_degree, lon + 1/cells_per_degree)
#     #             if coast_in_cell(new_cell, coastline_map):
#     #                 coastal_cells.append((lat, lon))
#     # return coastal_cells
#
#     latitudes = [-90 + x/cells_per_degree for x in range(180*cells_per_degree)]
#     longitudes = [-180 + x/cells_per_degree for x in range(360*cells_per_degree)]
#     world_cells = {}
#     for lat in latitudes:
#         for lon in longitudes:
#             world_cells[lat, lon] = False
#     for part in tqdm(coastline_map):
#         for p in part:
#             lat = latitudes[bisect.bisect(latitudes, p.lat)-1]
#             lon = longitudes[bisect.bisect(latitudes, p.lon)-1]
#             world_cells[lat, lon] = True
#     coastal_cells = []
#     for lat in latitudes:
#         if abs(lat) < 45:
#             for lon in longitudes:
#                 if world_cells[lat, lon]:
#                     coastal_cells.append((lat, lon))
#     return coastal_cells
#
#
# def pre_calculate_coastal_cells(init_data: TMB_Initialize.InitializationData, filename: str, cells_per_degree=4):
#     coastline_map = import_coastline_data(init_data)
#     coastal_cells = identify_coastal_cells(coastline_map, cells_per_degree)
#     with open(filename, "w") as outfile:
#         for c in coastal_cells:
#             outfile.write("{:0.4f}\t{:0.4f}\n".format(c[0], c[1]))
#
#
# def load_coastal_cells(filename: str) -> list:
#     coastal_cells = []
#     with open(filename, "r") as infile:
#         for line in infile:
#             lat, lon = line.strip().split("\t")
#             coastal_cells.append((eval(lat), eval(lon)))
#     return coastal_cells


# def identify_species_coastal_cells(species_range, cells_per_degree=4) -> list:
#     latitudes = [-90 + x/cells_per_degree for x in range(180*cells_per_degree)]
#     longitudes = [-180 + x/cells_per_degree for x in range(360*cells_per_degree)]
#     world_cells = {}
#     for lat in latitudes:
#         for lon in longitudes:
#             world_cells[lat, lon] = False
#     for part in species_range:
#         for p in part:
#             lat = latitudes[bisect.bisect(latitudes, p.lat)-1]
#             lon = longitudes[bisect.bisect(longitudes, p.lon)-1]
#             world_cells[lat, lon] = True
#     species_cells = []
#     for lat in latitudes:
#         if abs(lat) < 45:
#             for lon in longitudes:
#                 if world_cells[lat, lon]:
#                     species_cells.append((lat, lon))
#     return species_cells
#
#
# def count_species_in_coastal_cells(init_data: TMB_Initialize.InitializationData, cells_per_degree=4,
#                                    species_ranges: Optional[dict] = None):
#         latitudes = [-90 + x / cells_per_degree for x in range(180 * cells_per_degree)]
#         longitudes = [-180 + x / cells_per_degree for x in range(360 * cells_per_degree)]
#         nlats = len(latitudes)
#         nlons = len(longitudes)
#         counts = numpy.zeros((nlats, nlons))
#
#         x_ref = {}
#         for i, lat in enumerate(latitudes):
#             for j, lon in enumerate(longitudes):
#                 x_ref[lat, lon] = (i, j)
#
#         if species_ranges is None:  # calculate if not directly input
#             print("...Determining Species Coastlines...")
#             coastline_map = import_coastline_data(init_data)
#             species_range_blocks = TMB_Import.read_species_blocks(init_data.species_range_blocks)
#             species_ranges = {}
#             for s in tqdm(species_range_blocks):
#                 species_ranges[s] = TMB_Create_Maps.get_range_map_overlap(species_range_blocks[s], coastline_map)
#
#         print("...Determining Species Cells...")
#         for species in tqdm(species_ranges):
#             species_cells = identify_species_coastal_cells(species_ranges[species], cells_per_degree)
#             for cell in species_cells:
#                 i, j = x_ref[cell[0], cell[1]]
#                 counts[i, j] = counts[i, j] + 1
#
#         for i in range(nlats):
#             for j in range(nlons):
#                 if counts[i, j] == 0:
#                     counts[i, j] = numpy.nan
#
#         # need these to complete the colormesh grid
#         latitudes.append(90)
#         longitudes.append(180)
#         return latitudes, longitudes, counts


def test_range_density_map():
    TMB_Initialize.initialize()
    # t_init_data = TMB_Initialize.INIT_DATA

    # cell_per_degree = 1
    # coastal_file = "coastal_cells_1_degree.txt"

    # cell_per_degree = 2
    # coastal_file = "coastal_cells_1-2_degree.txt"

    # only need to include this if background map has been modified; otherwise run once and comment out
    # pre_calculate_coastal_cells(t_init_data, coastal_file, cells_per_degree=cell_per_degree)

    # coastal_cells = load_coastal_cells(coastal_file)
    #
    # lats, lons, cnts = count_species_in_grid(t_init_data, coastal_cells, cells_per_degree=cell_per_degree)

    # cell_per_degree = 4
    # lats, lons, cnts = count_species_in_coastal_cells(t_init_data, cells_per_degree=cell_per_degree)
    #
    # base_map = TMB_Create_Maps.read_base_map(t_init_data.map_primary, t_init_data.map_secondary,
    #                                          t_init_data.map_islands)
    # TMB_Create_Maps.create_cell_density_map(lats, lons, cnts, "", base_map)


if __name__ == "__main__":
    TMB_Initialize.initialize()
    t_init_data = TMB_Initialize.INIT_DATA
    calculate_ranges(t_init_data, True)
    # draw_provinces(t_init_data)
    # test_range_density_map()
