"""
Create Species Range Maps from the intersection of rectangular bounds and coastlines
"""

import TMB_Create_Maps
import TMB_Initialize
import TMB_ImportShape
import matplotlib.pyplot as mplpy


class Rectangle:
    def __init__(self, startlat=0, startlon=0, endlat=0, endlon=0):
        self.lower_left_lat = startlat
        self.lower_left_lon = startlon
        self.upper_right_lat = endlat
        self.upper_right_lon = endlon

    def __str__(self):
        return "{}, {}, {}, {}".format(self.lower_left_lat, self.lower_left_lon, self.upper_right_lat,
                                       self.upper_right_lon)

    def inside(self, lat, lon) -> bool:
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


def in_blocks(p, blocks: list) -> bool:
    """
    test whether the point is in any of the blocks
    """
    result = False
    for b in blocks:
        if not result:
            result = b.inside(p.lat, p.lon)
    return result


def get_overlap(blocks: list, coastline: list):
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


"""
    species_range = []
    for polygon in base_map.primary_polygons:
        p1 = polygon.points[0]
        p1in = in_blocks(p1, blocks)
        startline = True
        newline = []
        for p2 in polygon.points[1:]:
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
"""


def test_draw(species, ranges, base_map):
    fig, faxes = mplpy.subplots(figsize=[6, 3])
    for spine in faxes.spines:
        faxes.spines[spine].set_visible(False)
    TMB_Create_Maps.draw_base_map(faxes, base_map)

    for line in ranges:
        lons = []
        lats = []
        for p in line:
            lons.append(p.lon)
            lats.append(p.lat)
        # p1, p2 = pair[0], pair[1]
        # lons = [p1.lon, p2.lon]
        # lats = [p1.lat, p2.lat]
        faxes.plot(lons, lats, color="red", linewidth=0.5)

    mplpy.xlim(-180, 180)
    mplpy.ylim(-90, 90)
    faxes.axes.get_yaxis().set_visible(False)
    faxes.axes.get_xaxis().set_visible(False)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    # mplpy.savefig(__OUTPUT_PATH__ + rangemap_name("uca_all") + ".svg", format="svg")
    mplpy.savefig(species + "_test.png", format="png", dpi=600)
    mplpy.close("all")


def calculate_ranges(init_data: TMB_Initialize.InitializationData):
    base_map = TMB_Create_Maps.read_base_map(init_data.map_primary, None, init_data.map_islands)
    coastline_map = TMB_ImportShape.import_arcinfo_shp(TMB_Initialize.INIT_DATA.shp_coastline)
    coastline_map.extend(TMB_ImportShape.import_arcinfo_shp(TMB_Initialize.INIT_DATA.shp_islands))
    print("Number of coastline elements:", len(coastline_map))

    species_blocks = import_species_blocks(init_data.species_range_blocks)
    # for species in species_blocks:
    #     print(species)
    #     for rect in species_blocks[species]:
    #         print(rect)
    ranges = {}
    for species in species_blocks:
        print("Determining {} range".format(species))
        ranges[species] = get_overlap(species_blocks[species], coastline_map)

    # for species in ranges:
    #     print(species)
    #     for r in ranges[species]:
    #         print(len(r))

    for species in ranges:
        test_draw(species, ranges[species], base_map)


if __name__ == "__main__":
    TMB_Initialize.initialize()
    init_data = TMB_Initialize.INIT_DATA
    calculate_ranges(init_data)
