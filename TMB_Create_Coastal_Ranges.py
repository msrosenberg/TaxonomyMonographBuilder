"""
Create Species Range Maps from the intersection of rectangular bounds and coastlines
"""

import TMB_Create_Maps
import TMB_Initialize
import TMB_ImportShape
from TMB_Classes import Point
from TMB_Common import Number
import matplotlib.pyplot as mplpy


__TMP_PATH__ = "temp/"
__OUTPUT_PATH__ = __TMP_PATH__ + "maps/"


class Rectangle:
    def __init__(self, startlat=0, startlon=0, endlat=0, endlon=0):
        self.lower_left_lat = startlat
        self.lower_left_lon = startlon
        self.upper_right_lat = endlat
        self.upper_right_lon = endlon

    def __str__(self):
        return "{}, {}, {}, {}".format(self.lower_left_lat, self.lower_left_lon, self.upper_right_lat,
                                       self.upper_right_lon)

    def inside(self, lat: Number, lon: Number) -> bool:
        if (self.lower_left_lat <= lat <= self.upper_right_lat) and \
                (self.lower_left_lon <= lon <= self.upper_right_lon):
            return True
        else:
            return False


def import_species_blocks(filename: str) -> dict:
    blocks = {}
    with open(filename, "r") as infile:
        for line in infile:
            if line.strip() != "":
                species, startlat, startlon, endlat, endlon = line.strip().split("\t")
                if species in blocks:
                    block_data = blocks[species]
                else:
                    block_data = []
                    blocks[species] = block_data
                block_data.append(Rectangle(eval(startlat), eval(startlon), eval(endlat), eval(endlon)))
    return blocks


def in_blocks(p: Point, blocks: list) -> bool:
    """
    test whether the point is in any of the blocks
    """
    result = False
    for b in blocks:
        if not result:
            result = b.inside(p.lat, p.lon)
    return result


def get_overlap(blocks: list, coastline: list) -> list:
    species_range = []
    for part in coastline:
        p1 = part[0]
        p1in = in_blocks(p1, blocks)
        startline = True
        newline = []
        for p2 in part[1:]:
            p2in = in_blocks(p2, blocks)
            if p1in and p2in:
                if startline:
                    newline = [p1, p2]
                    startline = False
                else:
                    newline.append(p2)
            else:
                startline = True
                if len(newline) > 0:
                    species_range.append(newline)
                newline = []
            p1, p1in = p2, p2in
        if len(newline) > 0:
            species_range.append(newline)
    return species_range


def test_draw_ranges(species: str, ranges: list, base_map: TMB_Create_Maps.BaseMap) -> None:
    """
    only for testing purposes
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

    for line in ranges:
        lons = []
        lats = []
        for p in line:
            lon = p.lon
            if wrap_lons and lon < 0:
                lon += 360
            lons.append(lon)
            lats.append(p.lat)
        faxes.plot(lons, lats, color="red", linewidth=0.5)

    mplpy.xlim(minlon, maxlon)
    mplpy.ylim(minlat, maxlat)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    mplpy.savefig(species + "_test_range.png", format="png", dpi=600)
    mplpy.close("all")


def test_draw_blocks(species: str, blocks: list, base_map: TMB_Create_Maps.BaseMap) -> None:
    """
    only for cross-checking purposes
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

    for block in blocks:
        ll = block.lower_left_lon
        ur = block.upper_right_lon
        if wrap_lons and ll < 0:
            ll += 360
        if wrap_lons and ur < 0:
            ur += 360
        lons = [ll, ur, ur, ll, ll]
        lats = [block.lower_left_lat, block.lower_left_lat, block.upper_right_lat, block.upper_right_lat,
                block.lower_left_lat]
        faxes.plot(lons, lats, color="red", linewidth=0.3)

    mplpy.xlim(minlon, maxlon)
    mplpy.ylim(minlat, maxlat)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    mplpy.savefig(__OUTPUT_PATH__ + "blocks_" + species + ".png", format="png", dpi=600)
    mplpy.close("all")


def calculate_ranges(init_data: TMB_Initialize.InitializationData) -> None:
    base_map = TMB_Create_Maps.read_base_map(init_data.map_primary, None, init_data.map_islands)
    coastline_map = TMB_ImportShape.import_arcinfo_shp(TMB_Initialize.INIT_DATA.map_coastline)
    coastline_map.extend(TMB_ImportShape.import_arcinfo_shp(TMB_Initialize.INIT_DATA.map_islands))
    print("Number of coastline elements:", len(coastline_map))

    species_blocks = import_species_blocks(init_data.species_range_blocks)
    for species in species_blocks:
        test_draw_blocks(species, species_blocks[species], base_map)

    ranges = {}
    for species in species_blocks:
        print("Determining {} range".format(species))
        ranges[species] = get_overlap(species_blocks[species], coastline_map)
    for species in ranges:
        test_draw_ranges(species, ranges[species], base_map)


if __name__ == "__main__":
    TMB_Initialize.initialize()
    t_init_data = TMB_Initialize.INIT_DATA
    calculate_ranges(t_init_data)
