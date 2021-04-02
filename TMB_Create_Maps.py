"""
This program takes a single KML file with folders for each species, and
outputs cleaned-up KMZ files for each species, as well as a cleaned-up KMZ
file for all species combined. Formatting is standardized across the individual
species files and transparency automatically added to the combined output
file to reflect species density.

A temporary file called doc.kml is produced and not automatically deleted upon
completion of the code.
"""

import zipfile
import multiprocessing
from typing import Tuple, Optional
import matplotlib.pyplot as mplpy
import matplotlib.ticker
from matplotlib.collections import PatchCollection
import matplotlib.patches as mplp
from tqdm import tqdm
import TMB_Initialize
from TMB_Error import report_error
from TMB_Common import *
from TMB_Classes import Point
import TMB_ImportShape
import numpy
# import TMB_Create_Coastal_Ranges


__TMP_PATH__ = "temp/"
__OUTPUT_PATH__ = __TMP_PATH__ + "maps/"
FIG_WIDTH = 6.5
FIG_HEIGHT = 3.25
MAX_PROCESSOR_COUNT = 2  # maximum number of processors which can be used for map creation; set to 1 to skip


class BaseMap:
    def __init__(self):
        self.primary_parts = []
        self.secondary_parts = []

    def has_secondary(self) -> bool:
        if len(self.secondary_parts) > 0:
            return True
        else:
            return False


def point_in_blocks(p: Point, blocks: list) -> bool:
    """
    test whether the point is in any of the blocks
    """
    # result = False
    for b in blocks:
        # if not result:
        #     result = b.inside(p.lat, p.lon)
        if b.inside(p.lat, p.lon):
            return True
    return False


def get_range_map_overlap(blocks: list, coastline: list) -> list:
    species_range = []
    for part in coastline:
        p1 = part[0]
        p1in = point_in_blocks(p1, blocks)
        startline = True
        newline = []
        for p2 in part[1:]:
            p2in = point_in_blocks(p2, blocks)
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


# def read_kml_placemark(infile: TextIO) -> list:
#     namestr = infile.readline().strip()  # read name
#     line = infile.readline().strip()
#     while (not line.startswith("<LineString>") and not line.startswith("<Polygon>") and
#            not line.startswith("<MultiGeometry>")):
#         line = infile.readline().strip()
#     typestr = line
#     if typestr.startswith("<MultiGeometry>"):
#         coords = []
#         while not line.startswith("</Placemark>"):
#             line = infile.readline().strip()
#             if line.startswith("<coordinates>"):
#                 line = infile.readline().strip()
#                 coords.append(line)
#         return [namestr, True, coords]
#     else:
#         line = infile.readline().strip()
#         while not line.startswith("<coordinates>"):
#             line = infile.readline().strip()
#         coords = infile.readline().strip()
#         line = infile.readline().strip()
#         while not line.startswith("</Placemark>"):
#             line = infile.readline().strip()
#         return [namestr, False, coords]


# def read_species_from_kml(infile: TextIO, namestr: str) -> list:
#     line = infile.readline().strip()
#     crabplaces = []
#     while not line.startswith("</Folder>"):
#         if line.startswith("<Placemark>"):
#             newplace = read_kml_placemark(infile)
#             crabplaces.append(newplace)
#         line = infile.readline().strip()
#     return [namestr, crabplaces]


# def read_kml_folder(infile: TextIO) -> list:
#     line = infile.readline().strip()
#     crab = None
#     while not line.startswith("</Folder>"):
#         if line.startswith("<name>Uca"):
#             crab = read_species_from_kml(infile, line)
#             line = "</Folder>"
#         else:
#             line = infile.readline().strip()
#     return crab


# def read_raw_kml(filename: str) -> list:
#     maplist = []
#     with open(filename, "r", encoding="utf-8") as infile:
#         line = infile.readline()
#         while line != "":
#             line = line.strip()
#             if line.startswith("<Folder>"):
#                 new_map = read_kml_folder(infile)
#                 maplist.append(new_map)
#             line = infile.readline()
#     return maplist


def write_species_range_map_kml(name, species_range: list) -> None:
    with open(__TMP_PATH__ + "doc.kml", "w", encoding="UTF-8") as outfile:
        outfile.write("<?xml version=\"1.0\"?>\n")
        outfile.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
        outfile.write("  <Document>\n")
        outfile.write("    <Style id=\"species_range\">\n")
        outfile.write("      <LineStyle>\n")
        outfile.write("        <color>FFFF55FF</color>\n")
        outfile.write("        <width>5</width>\n")
        outfile.write("      </LineStyle>\n")
        outfile.write("    </Style>\n")
        outfile.write("    <Placemark>\n")
        outfile.write("      <name/>\n")
        outfile.write("      <description/>\n")
        outfile.write("      <styleUrl>\n")
        outfile.write("        #species_range\n")
        outfile.write("      </styleUrl>\n")
        outfile.write("      <MultiGeometry>\n")
        for line in species_range:
            outfile.write("        <LineString>\n")
            outfile.write("          <coordinates>\n")
            for p in line:
                outfile.write("            {},{},0\n".format(p.lon, p.lat))
            outfile.write("          </coordinates>\n")
            outfile.write("        </LineString>\n")
        outfile.write("      </MultiGeometry>\n")
        outfile.write("    </Placemark>\n")
        outfile.write("  </Document>\n")
        outfile.write("</kml>\n")
    with zipfile.ZipFile(__OUTPUT_PATH__ + rangemap_name("u_" + name) + ".kmz", "w", zipfile.ZIP_DEFLATED) as myzip:
        myzip.write(__TMP_PATH__ + "doc.kml")
        myzip.close()


def write_all_range_map_kml(species_maps: dict) -> None:
    with open(__TMP_PATH__ + "doc.kml", "w", encoding="UTF-8") as outfile:
        outfile.write("<?xml version=\"1.0\"?>\n")
        outfile.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
        outfile.write("  <Document>\n")
        for species in species_maps:
            outfile.write("    <Style id=\"" + species + "\">\n")
            outfile.write("      <LineStyle>\n")
            outfile.write("        <color>28FF78F0</color>\n")
            outfile.write("        <width>5</width>\n")
            outfile.write("      </LineStyle>\n")
            outfile.write("    </Style>\n")
        for species in species_maps:
            species_range = species_maps[species]
            outfile.write("    <Placemark>\n")
            outfile.write("      <name>Uca " + species + "</name>\n")
            outfile.write("      <description/>\n")
            outfile.write("      <styleUrl>\n")
            outfile.write("        #" + species + "\n")
            outfile.write("      </styleUrl>\n")
            outfile.write("      <MultiGeometry>\n")
            for line in species_range:
                outfile.write("        <LineString>\n")
                outfile.write("          <coordinates>\n")
                for p in line:
                    outfile.write("            {},{},0\n".format(p.lon, p.lat))
                outfile.write("          </coordinates>\n")
                outfile.write("        </LineString>\n")
            outfile.write("      </MultiGeometry>\n")
            outfile.write("    </Placemark>\n")
        outfile.write("  </Document>\n")
        outfile.write("</kml>\n")
    with zipfile.ZipFile(__OUTPUT_PATH__ + rangemap_name("fiddlers_all") + ".kmz", "w", zipfile.ZIP_DEFLATED) as myzip:
        myzip.write(__TMP_PATH__ + "doc.kml")
        myzip.close()


def read_base_map(primary_file: str, secondary_file: Optional[str] = None,
                  island_file: Optional[str] = None) -> BaseMap:
    basemap = BaseMap()
    basemap.primary_parts = TMB_ImportShape.import_arcinfo_shp(primary_file)
    if island_file is not None:
        basemap.primary_parts.extend(TMB_ImportShape.import_arcinfo_shp(island_file))
    if secondary_file is not None:
        basemap.secondary_parts = TMB_ImportShape.import_arcinfo_shp(secondary_file)
    return basemap


def draw_base_map(faxes: mplpy.Axes, base_map: BaseMap, adj_lon: int = 0) -> None:
    """
    Draw the background map of countries and islands
    """
    if base_map.has_secondary():
        # if data present, draw internal 1st level boundaries within countries (states, provinces, etc.)
        parts_list = []
        for part in base_map.secondary_parts:
            plist = []
            for p in part:
                plist.append([p.lon + adj_lon, p.lat])
            newp = mplp.Polygon(plist, True)
            parts_list.append(newp)
        pc = PatchCollection(parts_list, alpha=1, facecolor="gainsboro", edgecolor="silver", zorder=1, linewidths=0.3)
        faxes.add_collection(pc)

    parts_list = []
    for part in base_map.primary_parts:
        plist = []
        for p in part:
            plist.append([p.lon + adj_lon, p.lat])
        newp = mplp.Polygon(plist, True)
        parts_list.append(newp)
    if base_map.has_secondary():
        pc = PatchCollection(parts_list, alpha=1, facecolor="none", edgecolor="darkgrey", zorder=1, linewidths=0.5)
    else:
        pc = PatchCollection(parts_list, alpha=1, facecolor="gainsboro", edgecolor="darkgrey", zorder=1, linewidths=0.5)
    faxes.add_collection(pc)


def adjust_map_boundaries(minlon: Number, maxlon: Number, minlat: Number, maxlat: Number) -> Tuple[Number, Number,
                                                                                                   Number, Number]:
    """
    Adjust ranges to keep map scale (2:1 ratio, lon to lat), with a 5 degree buffer
    Do not allow the boundaries to exceed 180/-180 in lon or 90/-90 in lat
    Force small areas to have a minimum size of 30x15 degrees
    """
    min_width = 10  # mininmum width of map in degrees
    min_height = min_width / 2
    buffer = 2  # buffer around points in degrees

    maxlon += buffer
    minlon -= buffer
    maxlat += buffer
    minlat -= buffer
    lon_range = maxlon - minlon
    lat_range = maxlat - minlat
    if lon_range < min_width:
        maxlon += min_width/2 - lon_range/2
        minlon -= min_width/2 - lon_range/2
    if lat_range < min_height:
        maxlat += min_height/2 - lat_range/2
        minlat -= min_height/2 - lat_range/2
    if lon_range > 2 * lat_range:
        d = lon_range - 2 * lat_range
        minlat -= d / 2
        maxlat += d / 2
    else:
        d = 2 * lat_range - lon_range
        minlon -= d / 2
        maxlon += d / 2
    if maxlat > 90:
        maxlat, minlat = 90, minlat - (maxlat-90)
    if minlat < -90:
        maxlat, minlat = maxlat + (-90 - minlat), -90
    if (maxlon - minlon > 360) or (maxlat - minlat > 180):
        return -180, 180, -90, 90
    else:
        return minlon, maxlon, minlat, maxlat


def add_line_to_map(faxes: mplpy.Axes, points: list, wrap_lons: bool = False, lw: int = 1, a: Number = 1) -> None:
    lons = []
    lats = []
    for p in points:
        if wrap_lons and p.lon < 0:
            p.lon += 360
        lons.append(p.lon)
        lats.append(p.lat)
    faxes.plot(lons, lats, color="red", linewidth=lw, alpha=a)


# def check_line_boundaries(points: str, minlon: Number, maxlon: Number, minlat: Number, maxlat: Number,
#                           mid_atlantic: bool, lons, lats: list) -> Tuple[Number, Number, Number, Number, bool,
#                                                                          list, list]:
#     points = points.split(" ")
#     for p in points:
#         coords = p.split(",")
#         lon = float(coords[0])
#         lat = float(coords[1])
#         maxlon = max(maxlon, lon)
#         minlon = min(minlon, lon)
#         maxlat = max(maxlat, lat)
#         minlat = min(minlat, lat)
#         if 0 > lon > -50:
#             mid_atlantic = True
#         lons.append(lon)
#         lats.append(lat)
#     return minlon, maxlon, minlat, maxlat, mid_atlantic, lons, lats


def draw_and_adjust_basemap(faxes: mplpy.Axes, base_map: BaseMap, mid_atlantic: bool, minlon: float, maxlon: float,
                            minlat: float, maxlat: float, all_lons: list, all_lats: list) -> Tuple[float, float, float,
                                                                                                   float, bool]:
    draw_base_map(faxes, base_map)
    wrap_lons = False
    if (not mid_atlantic) and (maxlon == 180) and (minlon == -180):
        # shift map focus so default center is international date line rather than Greenwich
        draw_base_map(faxes, base_map, 360)
        # adjust longitude of points and recalculate boundaries
        maxlat = -90
        minlat = 90
        maxlon = 0
        minlon = 360
        for i in range(len(all_lons)):
            if all_lons[i] < 0:
                all_lons[i] += 360
            maxlon = max(maxlon, all_lons[i])
            minlon = min(minlon, all_lons[i])
            maxlat = max(maxlat, all_lats[i])
            minlat = min(minlat, all_lats[i])
        minlon, maxlon, minlat, maxlat = adjust_map_boundaries(minlon, maxlon, minlat, maxlat)
        wrap_lons = True
    else:  # if necessary, wrap map across international date line
        if maxlon > 180:
            draw_base_map(faxes, base_map, 360)
        if minlon < -180:
            draw_base_map(faxes, base_map, -360)
    return minlon, maxlon, minlat, maxlat, wrap_lons


# def write_species_range_map(base_map: BaseMap, species_map: list, graph_font: Optional[str] = None) -> None:
def write_species_range_map(base_map: BaseMap, species, species_map: list, graph_font: Optional[str] = None) -> None:
    fig, faxes = mplpy.subplots(figsize=[FIG_WIDTH, FIG_HEIGHT])
    for spine in faxes.spines:
        faxes.spines[spine].set_visible(False)
    maxlat = -90
    minlat = 90
    maxlon = -180
    minlon = 180
    mid_atlantic = False
    # find boundaries from range lines
    all_lons = []
    all_lats = []
    for line in species_map:
        for p in line:
            maxlon = max(maxlon, p.lon)
            maxlat = max(maxlat, p.lat)
            minlon = min(minlon, p.lon)
            minlat = min(minlat, p.lat)
            if 0 > p.lon > -50:
                mid_atlantic = True
            all_lons.append(p.lon)
            all_lats.append(p.lat)
    minlon, maxlon, minlat, maxlat = adjust_map_boundaries(minlon, maxlon, minlat, maxlat)
    (minlon, maxlon, minlat, maxlat, wrap_lons) = draw_and_adjust_basemap(faxes, base_map, mid_atlantic, minlon,
                                                                          maxlon, minlat, maxlat, all_lons, all_lats)

    # draw range lines
    for line in species_map:
        add_line_to_map(faxes, line, wrap_lons)

    mplpy.xlim(minlon, maxlon)
    mplpy.ylim(minlat, maxlat)
    mplpy.xlabel("longitude", fontname=graph_font)
    mplpy.ylabel("latitude", fontname=graph_font)
    # temporarily disabled because the font I want to use is missing the negative symbol ?!?
    # mplpy.xticks(fontname=graph_font)
    # mplpy.yticks(fontname=graph_font)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    adjust_longitude_tick_values(faxes)
    # mplpy.savefig(__OUTPUT_PATH__ + rangemap_name("u_" + name) + ".svg", format="svg")
    mplpy.savefig(__OUTPUT_PATH__ + rangemap_name("u_" + species) + ".png", format="png", dpi=600)
    mplpy.close("all")


def write_all_range_map(base_map: BaseMap, species_maps: dict) -> None:
    fig, faxes = mplpy.subplots(figsize=[FIG_WIDTH, FIG_HEIGHT])
    for spine in faxes.spines:
        faxes.spines[spine].set_visible(False)
    draw_base_map(faxes, base_map)
    for species in species_maps:
        species_range = species_maps[species]
        for line in species_range:
            add_line_to_map(faxes, line, lw=2, a=0.1)

    mplpy.xlim(-180, 180)
    mplpy.ylim(-90, 90)
    faxes.axes.get_yaxis().set_visible(False)
    faxes.axes.get_xaxis().set_visible(False)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    mplpy.savefig(__OUTPUT_PATH__ + rangemap_name("fiddlers_all") + ".png", format="png", dpi=600)
    mplpy.close("all")


def write_point_map_kml(title: str, place_list: list, point_locations: dict, invalid_places: Optional[set],
                        questionable_ids: Optional[set], inat_locations: Optional[list],
                        init_data: TMB_Initialize.InitializationData, sub_locations: Optional[list]) -> None:
    with open(__TMP_PATH__ + "doc.kml", "w", encoding="utf-8") as outfile:
        outfile.write("<?xml version=\"1.0\"?>\n")
        outfile.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
        outfile.write("  <Document>\n")
        outfile.write("    <Style id=\"good_location\">\n")
        outfile.write("      <IconStyle>\n")
        outfile.write("        <Icon>\n")
        outfile.write("          <href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href>\n")
        outfile.write("        </Icon >\n")
        outfile.write("      </IconStyle>\n")
        outfile.write("    </Style>\n")
        outfile.write("    <Style id=\"bad_location\">\n")
        outfile.write("      <IconStyle>\n")
        outfile.write("        <Icon>\n")
        outfile.write("          <href>http://maps.google.com/mapfiles/kml/paddle/blu-circle.png</href>\n")
        outfile.write("        </Icon >\n")
        outfile.write("      </IconStyle>\n")
        outfile.write("    </Style>\n")
        outfile.write("    <Style id=\"questionable_id\">\n")
        outfile.write("      <IconStyle>\n")
        outfile.write("        <Icon>\n")
        outfile.write("          <href>http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png</href>\n")
        outfile.write("        </Icon >\n")
        outfile.write("      </IconStyle>\n")
        outfile.write("    </Style>\n")
        outfile.write("    <Style id=\"sub_location\">\n")
        outfile.write("      <IconStyle>\n")
        outfile.write("        <Icon>\n")
        outfile.write("          <href>http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png</href>\n")
        outfile.write("        </Icon >\n")
        outfile.write("      </IconStyle>\n")
        outfile.write("    </Style>\n")
        outfile.write("    <Style id=\"fossil_location\">\n")
        outfile.write("      <IconStyle>\n")
        outfile.write("        <Icon>\n")
        outfile.write("          <href>http://maps.google.com/mapfiles/kml/paddle/purple-circle.png</href>\n")
        outfile.write("        </Icon >\n")
        outfile.write("      </IconStyle>\n")
        outfile.write("    </Style>\n")
        outfile.write("    <Style id=\"inat_location\">\n")
        outfile.write("      <IconStyle>\n")
        outfile.write("        <Icon>\n")
        outfile.write("          <href>http://maps.google.com/mapfiles/kml/paddle/grn-circle.png</href>\n")
        outfile.write("        </Icon >\n")
        outfile.write("        <scale>\n")
        outfile.write("          0.75\n")
        outfile.write("        </scale >\n")
        outfile.write("      </IconStyle>\n")
        outfile.write("    </Style>\n")

        if inat_locations is not None:
            # for point in inat_locations:
            for p in inat_locations:
                point = p.coords
                outfile.write("    <Placemark>\n")
                outfile.write("      <name>iNaturalist import</name>\n")
                outfile.write("      <description>" + p.url + "</description>\n")
                outfile.write("      <styleUrl>\n")
                outfile.write("        #inat_location\n")
                outfile.write("      </styleUrl>\n")
                outfile.write("      <Point>\n")
                outfile.write("       <coordinates>\n")
                outfile.write("          " + str(point.lon) + "," + str(point.lat) + "\n")
                outfile.write("       </coordinates>\n")
                outfile.write("      </Point>\n")
                outfile.write("    </Placemark>\n")

        for place in place_list:
            pnt = point_locations[place]
            if not pnt.unknown:
                is_invalid = False
                is_fossil = False
                if invalid_places is not None:
                    if place in invalid_places:
                        is_invalid = True
                if pnt.validity == "X":
                    is_invalid = True
                elif pnt.validity == "FOSSIL":
                    is_fossil = True
                is_question = False
                if questionable_ids is not None:
                    if place in questionable_ids:
                        is_question = True
                is_sub = False
                if sub_locations is not None:
                    if pnt in sub_locations:
                        is_sub = True
                outfile.write("    <Placemark>\n")
                outfile.write("      <name>" + unicode_to_html_encoding(place) + "</name>\n")
                outfile.write("      <description>" + init_data.site_url() + "/locations/" + place_to_filename(place) +
                              ".html</description>\n")
                outfile.write("      <styleUrl>\n")
                if is_invalid:
                    outfile.write("        #bad_location\n")
                elif is_question:
                    outfile.write("        #questionable_id\n")
                elif is_fossil:
                    outfile.write("        #fossil_location\n")
                elif is_sub:
                    outfile.write("        #sub_location\n")
                else:
                    outfile.write("        #good_location\n")
                outfile.write("      </styleUrl>\n")
                outfile.write("      <Point>\n")
                outfile.write("       <coordinates>\n")
                outfile.write("          " + str(pnt.longitude) + "," + str(pnt.latitude) + "\n")
                outfile.write("       </coordinates>\n")
                outfile.write("      </Point>\n")
                outfile.write("    </Placemark>\n")
        outfile.write("  </Document>\n")
        outfile.write("</kml>\n")
    with zipfile.ZipFile(__OUTPUT_PATH__ + pointmap_name(title) + ".kmz", "w", zipfile.ZIP_DEFLATED) as myzip:
        myzip.write(__TMP_PATH__ + "doc.kml")
        myzip.close()


def adjust_longitude_tick_values(faxes: mplpy.Axes) -> None:
    """
    This function adjusts the labels on the longitudinal axis when they wrap across the international date
    line.
    """
    xlabels = list(faxes.get_xticks())
    adj_labels = False
    all_ints = True
    for i, x in enumerate(xlabels):
        if x > 180:
            xlabels[i] = x - 360
            adj_labels = True
        elif x < -180:
            xlabels[i] = x + 360
            adj_labels = True
        if not x.is_integer():
            all_ints = False
    if adj_labels:
        if all_ints:  # if all of the values are integers, force to display as integers
            for i, x in enumerate(xlabels):
                xlabels[i] = int(x)
        ticks_loc = faxes.get_xticks().tolist()
        faxes.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(ticks_loc))
        faxes.set_xticklabels(xlabels)


def write_point_map(title: str, place_list: list, point_locations: dict, invalid_places: Optional[set],
                    questionable_ids: Optional[set], inat_locations: Optional[list], base_map: BaseMap,
                    skip_axes: bool, sub_locations: Optional[list], graph_font: Optional[str] = None) -> None:
    fig, faxes = mplpy.subplots(figsize=[FIG_WIDTH, FIG_HEIGHT])
    for spine in faxes.spines:
        faxes.spines[spine].set_visible(False)
    maxlat = -90
    minlat = 90
    maxlon = -180
    minlon = 180
    mid_atlantic = False
    lats = []
    lons = []
    colors = []
    edges = []
    sizes = []
    if inat_locations is not None:
        # for point in inat_locations:
        for p in inat_locations:
            point = p.coords
            lats.append(point.lat)
            lons.append(point.lon)
            colors.append("green")
            edges.append("darkgreen")
            sizes.append(10)
            maxlon = max(maxlon, point.lon)
            minlon = min(minlon, point.lon)
            maxlat = max(maxlat, point.lat)
            minlat = min(minlat, point.lat)
            if 0 > point.lon > -50:
                mid_atlantic = True

    for place in place_list:
        if place in point_locations:
            point = point_locations[place]
            if not point.unknown:
                is_invalid = False
                is_fossil = False
                if invalid_places is not None:
                    if place in invalid_places:
                        is_invalid = True
                if point.validity == "X":
                    is_invalid = True
                elif point.validity == "FOSSIL":
                    is_fossil = True
                is_question = False
                if questionable_ids is not None:
                    if place in questionable_ids:
                        is_question = True
                is_sub = False
                if sub_locations is not None:
                    if point in sub_locations:
                        is_sub = True
                lats.append(point.latitude)
                lons.append(point.longitude)
                if is_invalid:
                    colors.append("blue")
                    edges.append("darkblue")
                elif is_question:
                    colors.append("yellow")
                    edges.append("goldenrod")
                elif is_fossil:
                    colors.append("mediumpurple")
                    edges.append("indigo")
                elif is_sub:
                    colors.append("yellow")
                    edges.append("goldenrod")
                else:
                    colors.append("red")
                    edges.append("darkred")
                sizes.append(20)
                maxlon = max(maxlon, point.longitude)
                minlon = min(minlon, point.longitude)
                maxlat = max(maxlat, point.latitude)
                minlat = min(minlat, point.latitude)
                if 0 > point.longitude > -50:
                    mid_atlantic = True

    minlon, maxlon, minlat, maxlat = adjust_map_boundaries(minlon, maxlon, minlat, maxlat)

    (minlon, maxlon, minlat, maxlat, _) = draw_and_adjust_basemap(faxes, base_map, mid_atlantic, minlon, maxlon,
                                                                  minlat, maxlat, lons, lats)

    # faxes.scatter(lons, lats, s=20, color=colors, edgecolors=edges, alpha=1, zorder=2, clip_on=False)
    faxes.scatter(lons, lats, s=sizes, color=colors, edgecolors=edges, alpha=1, zorder=2, clip_on=False, linewidth=0.5)

    # uncomment to force full world map
    # maxlat = 90
    # minlat = -90
    # maxlon = 180
    # minlon = -180
    mplpy.xlim(minlon, maxlon)
    mplpy.ylim(minlat, maxlat)
    if skip_axes:
        faxes.axes.get_yaxis().set_visible(False)
        faxes.axes.get_xaxis().set_visible(False)
    else:
        mplpy.xlabel("longitude", fontname=graph_font)
        mplpy.ylabel("latitude", fontname=graph_font)
    # temporarily disabled because the font I want to use is missing the negative symbol ?!?
    # mplpy.xticks(fontname=graph_font)
    # mplpy.yticks(fontname=graph_font)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    adjust_longitude_tick_values(faxes)

    # mplpy.savefig(__OUTPUT_PATH__ + pointmap_name(title) + ".svg", format="svg")
    mplpy.savefig(__OUTPUT_PATH__ + pointmap_name(title) + ".png", format="png", dpi=600)
    mplpy.close("all")


def create_cell_density_map(latitudes, longitudes, cell_counts, title: str, base_map: BaseMap, skip_axes: bool = True,
                            graph_font: Optional[str] = None) -> None:
    fig, faxes = mplpy.subplots(figsize=[FIG_WIDTH, FIG_HEIGHT])
    for spine in faxes.spines:
        faxes.spines[spine].set_visible(False)
    # maxlat = -90
    # minlat = 90
    # maxlon = -180
    # minlon = 180
    # mid_atlantic = False
    # lats = []
    # lons = []
    # _ = draw_and_adjust_basemap(faxes, base_map, mid_atlantic, minlon, maxlon, minlat, maxlat, lons, lats)
    draw_base_map(faxes, base_map)

    x, y = numpy.meshgrid(longitudes, latitudes)
    mesh = faxes.pcolormesh(x, y, cell_counts, cmap="plasma")
    fig.colorbar(mesh)

    maxlat = 90
    minlat = -90
    maxlon = 180
    minlon = -180
    mplpy.xlim(minlon, maxlon)
    mplpy.ylim(minlat, maxlat)
    if skip_axes:
        faxes.axes.get_yaxis().set_visible(False)
        faxes.axes.get_xaxis().set_visible(False)
    else:
        mplpy.xlabel("longitude", fontname=graph_font)
        mplpy.ylabel("latitude", fontname=graph_font)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    adjust_longitude_tick_values(faxes)

    mplpy.savefig(__OUTPUT_PATH__ + "density_map.png", format="png", dpi=600)
    mplpy.close("all")


def create_all_species_point_maps(species: list, point_locations: dict, species_plot_locations: dict,
                                  invalid_species_locations: dict, base_map: BaseMap,
                                  init_data: TMB_Initialize.InitializationData,
                                  inat_species_locations: Optional[dict] = None,
                                  questionable_id_locations: Optional[dict] = None) -> None:
    all_places = set()
    print(".........Species Point Maps.........")
    if MAX_PROCESSOR_COUNT > 1:
        pool = multiprocessing.Pool(MAX_PROCESSOR_COUNT)
    else:
        pool = None
    png_inputs = []
    for s in species:
        if s.status != "fossil":
            places = species_plot_locations[s]
            invalid_places = invalid_species_locations[s]
            questionable_ids = questionable_id_locations[s]
            if inat_species_locations is None:
                inat_data = None
            elif s.species in inat_species_locations:
                inat_data = inat_species_locations[s.species]
            else:
                inat_data = None
            if MAX_PROCESSOR_COUNT > 1:
                png_inputs.append(("u_" + s.species, places, point_locations, invalid_places, questionable_ids,
                                   inat_data, base_map, False, None, init_data.graph_font))
            else:
                write_point_map("u_" + s.species, places, point_locations, invalid_places, questionable_ids, inat_data,
                                base_map, False, None, init_data.graph_font)
            write_point_map_kml("u_" + s.species, places, point_locations, invalid_places, questionable_ids, inat_data,
                                init_data, None)
            all_places |= set(places)
    if MAX_PROCESSOR_COUNT > 1:
        pool.starmap(write_point_map, png_inputs)
        pool.close()
        pool.join()
    all_list = sorted(list(all_places))
    write_point_map("fiddlers_all", all_list, point_locations, None, None, None, base_map, True, None,
                    init_data.graph_font)
    write_point_map_kml("fiddlers_all", all_list, point_locations, None, None, None, init_data, None)


def create_all_species_maps(base_map: BaseMap, init_data: TMB_Initialize.InitializationData, species: list,
                            species_ranges: dict, point_locations: dict, species_plot_locations: dict,
                            invalid_species_locations: dict, inat_species_locations: Optional[dict] = None,
                            questionable_id_locations: Optional[dict] = None) -> None:
    # create range maps
    print(".........Species Range Maps.........")
    if MAX_PROCESSOR_COUNT > 1:
        pool = multiprocessing.Pool(MAX_PROCESSOR_COUNT)
    else:
        pool = None
    inputs = []
    for s in species_ranges:
        write_species_range_map_kml(s, species_ranges[s])
        if MAX_PROCESSOR_COUNT > 1:
            inputs.append((base_map, s, species_ranges[s], init_data.graph_font))
        else:
            write_species_range_map(base_map, s, species_ranges[s], init_data.graph_font)
    if MAX_PROCESSOR_COUNT > 1:
        pool.starmap(write_species_range_map, inputs)
        pool.close()
        pool.join()
    write_all_range_map_kml(species_ranges)
    write_all_range_map(base_map, species_ranges)

    # create point maps
    create_all_species_point_maps(species, point_locations, species_plot_locations, invalid_species_locations, base_map,
                                  init_data, inat_species_locations, questionable_id_locations)


def create_all_name_maps(base_map: BaseMap, all_names: list, specific_names: list, point_locations: dict,
                         specific_plot_locations: dict, binomial_plot_locations: dict,
                         init_data: TMB_Initialize.InitializationData) -> None:
    if MAX_PROCESSOR_COUNT > 1:
        pool = multiprocessing.Pool(MAX_PROCESSOR_COUNT)
    else:
        pool = None
    bi_inputs_png = []
    sp_inputs_png = []
    for i, name in enumerate(all_names):
        print("......." + name)
        namefile = "name_" + name_to_filename(name)
        place_list = binomial_plot_locations[name]
        if MAX_PROCESSOR_COUNT > 1:
            bi_inputs_png.append((namefile, place_list, point_locations, None, None, None, base_map, False, None,
                                  init_data.graph_font))
        else:
            write_point_map(namefile, place_list, point_locations, None, None, None, base_map, False, None,
                            init_data.graph_font)
        write_point_map_kml(namefile, place_list, point_locations, None, None, None, init_data, None)
    for i, name in enumerate(specific_names):
        namefile = "sn_" + name.name
        place_list = specific_plot_locations[name]
        if MAX_PROCESSOR_COUNT > 1:
            sp_inputs_png.append((namefile, place_list, point_locations, None, None, None, base_map, False, None,
                                  init_data.graph_font))
        else:
            write_point_map(namefile, place_list, point_locations, None, None, None, base_map, False, None,
                            init_data.graph_font)
        write_point_map_kml(namefile, place_list, point_locations, None, None, None, init_data, None)
    if MAX_PROCESSOR_COUNT > 1:
        pool.starmap(write_point_map, bi_inputs_png)
        pool.starmap(write_point_map, sp_inputs_png)
        pool.close()
        pool.join()


def create_all_location_maps(base_map: BaseMap, point_locations: dict,
                             init_data: TMB_Initialize.InitializationData) -> None:
    if MAX_PROCESSOR_COUNT > 1:
        pool = multiprocessing.Pool(MAX_PROCESSOR_COUNT)
    else:
        pool = None
    png_inputs = []
    for i, loc in enumerate(point_locations):
        point = point_locations[loc]
        if not point.unknown:
            place_list = []
            sub_list = []
            try:
                sub_list = point.all_children()
            except RecursionError:
                report_error("Recursion Error on location: " + loc)
                quit()
            for p in sub_list:
                place_list.append(p.name)
            place_list.append(loc)  # put the primary location at end so it is drawn above children
            namefile = "location_" + place_to_filename(loc)
            if MAX_PROCESSOR_COUNT > 1:
                png_inputs.append((namefile, place_list, point_locations, None, None, None, base_map, False, sub_list,
                                   init_data.graph_font))
            else:
                write_point_map(namefile, place_list, point_locations, None, None, None, base_map, False, sub_list,
                                init_data.graph_font)
            write_point_map_kml(namefile, place_list, point_locations, None, None, None, init_data, sub_list)
    if MAX_PROCESSOR_COUNT > 1:
        pool.starmap(write_point_map, png_inputs)
        pool.close()
        pool.join()


def create_all_maps(init_data: TMB_Initialize.InitializationData, point_locations: dict, species: Optional[list] = None,
                    species_plot_locations: Optional[dict] = None, invalid_species_locations: Optional[dict] = None,
                    all_names: Optional[list] = None, binomial_plot_locations: Optional[dict] = None,
                    specific_names: Optional[list] = None, specific_plot_locations: Optional[dict] = None,
                    inat_locations: Optional[dict] = None, questionable_id_locations: Optional[dict] = None,
                    species_blocks: Optional[dict] = None) -> None:
    base_map = read_base_map(init_data.map_primary, init_data.map_secondary, init_data.map_islands)
    if species is not None:
        print("......Creating Species Maps......")
        print(".........Determining Species Ranges.........")
        coastline_map = TMB_ImportShape.import_arcinfo_shp(TMB_Initialize.INIT_DATA.map_coastline)
        coastline_map.extend(TMB_ImportShape.import_arcinfo_shp(TMB_Initialize.INIT_DATA.map_islands))
        species_ranges = {}
        for s in tqdm(species_blocks):
            species_ranges[s] = get_range_map_overlap(species_blocks[s], coastline_map)

        print(".........Drawing Species Maps.........")
        create_all_species_maps(base_map, init_data, species, species_ranges, point_locations, species_plot_locations,
                                invalid_species_locations, inat_locations, questionable_id_locations)
    if specific_names is not None:
        print("......Creating Name Maps......")
        create_all_name_maps(base_map, all_names, specific_names, point_locations, specific_plot_locations,
                             binomial_plot_locations, init_data)
    print("......Creating Location Maps......")
    create_all_location_maps(base_map, point_locations, init_data)


def main():
    pass
    # temp code to produce a blank map
    # base_map = read_base_map("fiddlercrab.info/private/ne_50m_land.txt", None)
    # write_point_map_svg("blank", [], [], None, base_map, True, False)


if __name__ == "__main__":
    main()
