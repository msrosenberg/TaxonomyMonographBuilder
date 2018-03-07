"""
This program takes a single KML file with folders for each species, and
outputs cleaned-up KMZ files for each species, as well as a cleaned-up KMZ
file for all species combined. Formatting is standardized across the individual
species files and transparency automatically added to the combined output
file to reflect species density.

A temporary file called doc.kml is produced and not automatically deleted upon
completion of the code.
"""

# import codecs
import zipfile
import TMB_Initialize
from typing import Tuple, Union, Optional, TextIO
import matplotlib.pyplot as mplpy
from matplotlib.collections import PatchCollection
import matplotlib.patches as mplp
from TMB_Error import report_error
from TMB_Common import *

Number = Union[int, float]
__TMP_PATH__ = "temp/"
__OUTPUT_PATH__ = __TMP_PATH__ + "maps/"


class Point:
    def __init__(self, lat: Number = 0, lon: Number = 0):
        self.lat = lat
        self.lon = lon


class Polygon:
    def __init__(self):
        self.points = []

    def n(self) -> int:
        return len(self.points)


class BaseMap:
    def __init__(self):
        self.primary_polygons = []
        self.secondary_polygons = []

    def has_secondary(self) -> bool:
        if len(self.secondary_polygons) > 0:
            return True
        else:
            return False


def read_kml_placemark(infile: TextIO) -> list:
    namestr = infile.readline().strip()  # read name
    line = infile.readline().strip()
    while (not line.startswith("<LineString>") and not line.startswith("<Polygon>") and
           not line.startswith("<MultiGeometry>")):
        line = infile.readline().strip()
    typestr = line
    if typestr.startswith("<MultiGeometry>"):
        coords = []
        while not line.startswith("</Placemark>"):
            line = infile.readline().strip()
            if line.startswith("<coordinates>"):
                line = infile.readline().strip()
                coords.append(line)
        return [namestr, True, coords]
    else:
        line = infile.readline().strip()
        while not line.startswith("<coordinates>"):
            line = infile.readline().strip()
        coords = infile.readline().strip()
        line = infile.readline().strip()
        while not line.startswith("</Placemark>"):
            line = infile.readline().strip()
        return [namestr, False, coords]


def read_species_from_kml(infile: TextIO, namestr: str) -> list:
    line = infile.readline().strip()
    crabplaces = []
    while not line.startswith("</Folder>"):
        if line.startswith("<Placemark>"):
            newplace = read_kml_placemark(infile)
            crabplaces.append(newplace)
        line = infile.readline().strip()
    return [namestr, crabplaces]


def read_kml_folder(infile: TextIO) -> list:
    line = infile.readline().strip()
    crab = None
    while not line.startswith("</Folder>"):
        if line.startswith("<name>Uca"):
            crab = read_species_from_kml(infile, line)
            line = "</Folder>"
        else:
            line = infile.readline().strip()
    return crab


def read_raw_kml(filename: str) -> list:
    maplist = []
    with open(filename, "r", encoding="utf-8") as infile:
        line = infile.readline()
        while line != "":
            line = line.strip()
            if line.startswith("<Folder>"):
                new_map = read_kml_folder(infile)
                maplist.append(new_map)
            line = infile.readline()
    return maplist


def write_species_range_map_kml(species_map: list) -> None:
    name = species_map[0]
    locs = species_map[1]
    name = name[name.find("Uca")+4:name.find("</")]
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
        for loc in locs:
            if loc[1]:
                for x in loc[2]:
                    outfile.write("        <LineString>\n")
                    outfile.write("          <coordinates>\n")
                    outfile.write("            " + x + "\n")
                    outfile.write("          </coordinates>\n")
                    outfile.write("        </LineString>\n")
            else:
                outfile.write("        <LineString>\n")
                outfile.write("          <coordinates>\n")
                outfile.write("            " + loc[2] + "\n")
                outfile.write("          </coordinates>\n")
                outfile.write("        </LineString>\n")
        outfile.write("      </MultiGeometry>\n")
        outfile.write("    </Placemark>\n")
        outfile.write("  </Document>\n")
        outfile.write("</kml>\n")
    with zipfile.ZipFile(__OUTPUT_PATH__ + rangemap_name("u_" + name) + ".kmz", "w", zipfile.ZIP_DEFLATED) as myzip:
        myzip.write(__TMP_PATH__ + "doc.kml")
        myzip.close()


def write_all_range_map_kml(species_maps: list) -> None:
    with open(__TMP_PATH__ + "doc.kml", "w", encoding="UTF-8") as outfile:
        outfile.write("<?xml version=\"1.0\"?>\n")
        outfile.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
        outfile.write("  <Document>\n")
        for species in species_maps:
            name = species[0]
            name = name[name.find("Uca")+4:name.find("</")]
            outfile.write("    <Style id=\"" + name + "\">\n")
            outfile.write("      <LineStyle>\n")
            outfile.write("        <color>28FF78F0</color>\n")
            outfile.write("        <width>5</width>\n")
            outfile.write("      </LineStyle>\n")
            outfile.write("    </Style>\n")
        for species in species_maps:
            name = species[0]
            locs = species[1]
            name = name[name.find("Uca")+4:name.find("</")]
            outfile.write("    <Placemark>\n")
            outfile.write("      <name>Uca " + name + "</name>\n")
            outfile.write("      <description/>\n")
            outfile.write("      <styleUrl>\n")
            outfile.write("        #" + name + "\n")
            outfile.write("      </styleUrl>\n")
            outfile.write("      <MultiGeometry>\n")
            for loc in locs:
                if loc[1]:
                    for x in loc[2]:
                        outfile.write("        <LineString>\n")
                        outfile.write("          <coordinates>\n")
                        outfile.write("            " + x + "\n")
                        outfile.write("          </coordinates>\n")
                        outfile.write("        </LineString>\n")
                else:
                    outfile.write("        <LineString>\n")
                    outfile.write("          <coordinates>\n")
                    outfile.write("            " + loc[2] + "\n")
                    outfile.write("          </coordinates>\n")
                    outfile.write("        </LineString>\n")
            outfile.write("      </MultiGeometry>\n")
            outfile.write("    </Placemark>\n")
        outfile.write("  </Document>\n")
        outfile.write("</kml>\n")
    with zipfile.ZipFile(__OUTPUT_PATH__ + rangemap_name("uca_all") + ".kmz", "w", zipfile.ZIP_DEFLATED) as myzip:
        myzip.write(__TMP_PATH__ + "doc.kml")
        myzip.close()


def read_polygons_from_file(filename: str, outlist: list) -> None:
    with open(filename, "r") as infile:
        line = infile.readline()
        while line != "":
            if line.startswith("Polygon"):
                data = line.strip().split("\t")
                new_polygon = Polygon()
                outlist.append(new_polygon)
                n = abs(int(data[1]))
                new_point = Point(lat=float(data[3]), lon=float(data[2]))
                new_polygon.points.append(new_point)
                for i in range(n - 1):
                    line = infile.readline()
                    data = line.strip().split("\t")
                    new_point = Point(lat=float(data[1]), lon=float(data[0]))
                    new_polygon.points.append(new_point)
            else:
                line = infile.readline()


def read_base_map(primary_file: str, secondary_file: Optional[str] = None,
                  island_file: Optional[str] = None) -> BaseMap:
    basemap = BaseMap()
    read_polygons_from_file(primary_file, basemap.primary_polygons)
    if island_file is not None:
        read_polygons_from_file(island_file, basemap.primary_polygons)
    if secondary_file is not None:
        read_polygons_from_file(secondary_file, basemap.secondary_polygons)
    return basemap


def draw_base_map(faxes: mplpy.Axes, base_map: BaseMap, adj_lon: int=0) -> None:
    """
    Draw the background map of countries and islands
    """
    if base_map.has_secondary():
        # if data present, draw internal 1st level boundaries within countries (states, provinces, etc.)
        poly_list = []
        for polygon in base_map.secondary_polygons:
            plist = []
            for p in polygon.points:
                plist.append([p.lon + adj_lon, p.lat])
            newp = mplp.Polygon(plist, True)
            poly_list.append(newp)
        pc = PatchCollection(poly_list, alpha=1, facecolor="gainsboro", edgecolor="silver", zorder=1, linewidths=0.3)
        faxes.add_collection(pc)

    poly_list = []
    for polygon in base_map.primary_polygons:
        plist = []
        for p in polygon.points:
            plist.append([p.lon + adj_lon, p.lat])
        newp = mplp.Polygon(plist, True)
        poly_list.append(newp)
    if base_map.has_secondary():
        pc = PatchCollection(poly_list, alpha=1, facecolor="none", edgecolor="darkgrey", zorder=1, linewidths=0.5)
    else:
        pc = PatchCollection(poly_list, alpha=1, facecolor="gainsboro", edgecolor="darkgrey", zorder=1, linewidths=0.5)
    # pc = PatchCollection(poly_list, alpha=0.2, facecolor="silver", edgecolor="darkgray", zorder=1)
    # pc = PatchCollection(poly_list, alpha=0.2, facecolor="silver", edgecolor="darkgray", zorder=1, linewidths=0.5)
    # pc = PatchCollection(poly_list, alpha=0.2, facecolor="white", edgecolor="darkgray", zorder=1)
    faxes.add_collection(pc)


def adjust_map_boundaries(minlon: Number, maxlon: Number, minlat: Number, maxlat: Number) -> Tuple[Number, Number,
                                                                                                   Number, Number]:
    """
    Adjust ranges to keep map scale (2:1 ratio, lon to lat), with a 5 degree buffer
    Do not allow the boundaries to exceed 180/-180 in lon or 90/-90 in lat
    Force small areas to have a minimum size of 30x15 degrees
    """
    # min_width = 30  # mininmum width of map in degrees
    # min_height = min_width / 2
    # buffer = 5
    #
    # maxlon += buffer
    # minlon -= buffer
    # maxlat += buffer
    # minlat -= buffer
    # lon_range = maxlon - minlon
    # lat_range = maxlat - minlat
    # if lon_range < min_width:
    #     maxlon += min_width/2 - lon_range/2
    #     minlon -= min_width/2 - lon_range/2
    # if lat_range < min_height:
    #     maxlat += min_height/2 - lat_range/2
    #     minlat -= min_height/2 - lat_range/2
    # if lon_range > 2 * lat_range:
    #     d = lon_range - 2 * lat_range
    #     minlat -= d / 2
    #     maxlat += d / 2
    # else:
    #     d = 2 * lat_range - lon_range
    #     minlon -= d / 2
    #     maxlon += d / 2
    # if maxlon > 180:
    #     maxlon, minlon = 180, minlon - (maxlon-180)
    # if minlon < -180:
    #     maxlon, minlon = maxlon + (-180 - minlon), -180
    # if maxlat > 90:
    #     maxlat, minlat = 90, minlat - (maxlat-90)
    # if minlat < -90:
    #     maxlat, minlat = maxlat + (-90 - minlat), -90
    # if (maxlon > 180) or (minlon < -180) or (maxlat > 90) or (minlat < -90):
    #     return -180, 180, -90, 90
    # else:
    #     return minlon, maxlon, minlat, maxlat

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
    # if maxlon > 180:
    #     maxlon, minlon = 180, minlon - (maxlon-180)
    # if minlon < -180:
    #     maxlon, minlon = maxlon + (-180 - minlon), -180
    if maxlat > 90:
        maxlat, minlat = 90, minlat - (maxlat-90)
    if minlat < -90:
        maxlat, minlat = maxlat + (-90 - minlat), -90
    if (maxlon - minlon > 360) or (maxlat - minlat > 180):
        return -180, 180, -90, 90
    else:
        return minlon, maxlon, minlat, maxlat


def add_line_to_map(faxes: mplpy.Axes, points: str, minlon: Number, maxlon: Number, minlat: Number, maxlat: Number,
                    lw: int, a: Number) -> Tuple[Number, Number, Number, Number]:
    lons = []
    lats = []
    points = points.split(" ")
    for p in points:
        coords = p.split(",")
        lon = float(coords[0])
        lat = float(coords[1])
        lons.append(lon)
        lats.append(lat)
        maxlon = max(maxlon, lon)
        minlon = min(minlon, lon)
        maxlat = max(maxlat, lat)
        minlat = min(minlat, lat)
    faxes.plot(lons, lats, color="red", linewidth=lw, alpha=a)
    return minlon, maxlon, minlat, maxlat


def write_species_range_map(base_map: BaseMap, species_map: list) -> None:
    fig, faxes = mplpy.subplots(figsize=[6.5, 3.25])
    draw_base_map(faxes, base_map)
    for spine in faxes.spines:
        faxes.spines[spine].set_visible(False)
    maxlat = -90
    minlat = 90
    maxlon = -180
    minlon = 180
    name = species_map[0]
    name = name[name.find("Uca")+4:name.find("</")]
    locs = species_map[1]
    for loc in locs:
        if loc[1]:
            for x in loc[2]:
                minlon, maxlon, minlat, maxlat = add_line_to_map(faxes, x, minlon, maxlon, minlat, maxlat, 1, 1)
        else:
            minlon, maxlon, minlat, maxlat = add_line_to_map(faxes, loc[2], minlon, maxlon, minlat, maxlat, 1, 1)

    minlon, maxlon, minlat, maxlat = adjust_map_boundaries(minlon, maxlon, minlat, maxlat)
    mplpy.xlim(minlon, maxlon)
    mplpy.ylim(minlat, maxlat)
    mplpy.xlabel("longitude")
    mplpy.ylabel("latitude")
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    # mplpy.savefig(__OUTPUT_PATH__ + rangemap_name("u_" + name) + ".svg", format="svg")
    mplpy.savefig(__OUTPUT_PATH__ + rangemap_name("u_" + name) + ".png", format="png", dpi=600)
    mplpy.close("all")


def write_all_range_map(base_map: BaseMap, species_maps: list) -> None:
    fig, faxes = mplpy.subplots(figsize=[6.5, 3.25])
    draw_base_map(faxes, base_map)
    for spine in faxes.spines:
        faxes.spines[spine].set_visible(False)
    maxlat = -90
    minlat = 90
    maxlon = -180
    minlon = 180
    for species in species_maps:
        locs = species[1]
        for loc in locs:
            if loc[1]:
                for x in loc[2]:
                    minlon, maxlon, minlat, maxlat = add_line_to_map(faxes, x, minlon, maxlon, minlat, maxlat,
                                                                     2, 0.1)
            else:
                minlon, maxlon, minlat, maxlat = add_line_to_map(faxes, loc[2], minlon, maxlon, minlat, maxlat,
                                                                 2, 0.1)

    mplpy.xlim(-180, 180)
    mplpy.ylim(-90, 90)
    # mplpy.xlabel("longitude")
    # mplpy.ylabel("latitude")
    faxes.axes.get_yaxis().set_visible(False)
    faxes.axes.get_xaxis().set_visible(False)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    # mplpy.savefig(__OUTPUT_PATH__ + rangemap_name("uca_all") + ".svg", format="svg")
    mplpy.savefig(__OUTPUT_PATH__ + rangemap_name("uca_all") + ".png", format="png", dpi=600)
    mplpy.close("all")


def write_point_map_kml(title: str, place_list: list, point_locations: dict, invalid_places: Optional[set],
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
        faxes.set_xticklabels(xlabels)


def write_point_map(title: str, place_list: list, point_locations: dict, invalid_places: Optional[set],
                    base_map: BaseMap, skip_axes: bool, set_bounds: bool, sub_locations: Optional[list]) -> None:
    fig, faxes = mplpy.subplots(figsize=[6.5, 3.25])
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
                is_sub = False
                if sub_locations is not None:
                    if point in sub_locations:
                        is_sub = True
                lats.append(point.latitude)
                lons.append(point.longitude)
                if is_invalid:
                    colors.append("blue")
                    edges.append("darkblue")
                elif is_fossil:
                    colors.append("mediumpurple")
                    edges.append("indigo")
                elif is_sub:
                    colors.append("yellow")
                    edges.append("goldenrod")
                else:
                    colors.append("red")
                    edges.append("darkred")
                maxlon = max(maxlon, point.longitude)
                minlon = min(minlon, point.longitude)
                maxlat = max(maxlat, point.latitude)
                minlat = min(minlat, point.latitude)
                if 0 > point.longitude > -50:
                    mid_atlantic = True

    # if set_bounds:
    #     place = place_list[0]
    #     if place in point_locations:
    #         point = point_locations[place]
    #         if point.sw_lon is None:
    #             minlon = point.longitude - 15
    #             maxlon = point.longitude + 15
    #             minlat = point.latitude - 7.5
    #             maxlat = point.latitude + 7.5
    #         else:
    #             minlon = point.sw_lon
    #             maxlon = point.ne_lon
    #             minlat = point.sw_lat
    #             maxlat = point.ne_lat
    minlon, maxlon, minlat, maxlat = adjust_map_boundaries(minlon, maxlon, minlat, maxlat)
    draw_base_map(faxes, base_map)
    if (not mid_atlantic) and (maxlon == 180) and (minlon == -180):
        # shift map focus so default center is international date line rather than Greenwich
        draw_base_map(faxes, base_map, 360)
        # adjust longitude of points and recalculate boundaries
        maxlat = -90
        minlat = 90
        maxlon = 0
        minlon = 360
        for i in range(len(lons)):
            if lons[i] < 0:
                lons[i] += 360
            maxlon = max(maxlon, lons[i])
            minlon = min(minlon, lons[i])
            maxlat = max(maxlat, lats[i])
            minlat = min(minlat, lats[i])
        minlon, maxlon, minlat, maxlat = adjust_map_boundaries(minlon, maxlon, minlat, maxlat)
    else:  # if necessary, wrap map across international date line
        if maxlon > 180:
            draw_base_map(faxes, base_map, 360)
        if minlon < -180:
            draw_base_map(faxes, base_map, -360)

    # faxes.scatter(lons, lats, s=20, color=colors, edgecolors=edges, alpha=1, zorder=2, clip_on=False)
    faxes.scatter(lons, lats, s=20, color=colors, edgecolors=edges, alpha=1, zorder=2, clip_on=False, linewidth=0.5)

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
        mplpy.xlabel("longitude")
        mplpy.ylabel("latitude")
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    adjust_longitude_tick_values(faxes)

    # mplpy.savefig(__OUTPUT_PATH__ + pointmap_name(title) + ".svg", format="svg")
    mplpy.savefig(__OUTPUT_PATH__ + pointmap_name(title) + ".png", format="png", dpi=600)
    mplpy.close("all")


def create_all_point_maps(species: list, point_locations: dict, species_plot_locations: dict,
                          invalid_species_locations: dict, base_map: BaseMap,
                          init_data: TMB_Initialize.InitializationData) -> None:
    all_places = set()
    total = len(species)
    report = total / 20
    j = 0
    print(".........Point Maps.........")
    for i, s in enumerate(species):
        if i >= report:
            j += 1
            print("............{}%".format(j*5))
            report += total / 20
        if s.status != "fossil":
            places = species_plot_locations[s]
            invalid_places = invalid_species_locations[s]
            write_point_map("u_" + s.species, places, point_locations, invalid_places, base_map, False, False, None)
            write_point_map_kml("u_" + s.species, places, point_locations, invalid_places, init_data, None)
            all_places |= set(places)
    all_list = sorted(list(all_places))
    write_point_map("uca_all", all_list, point_locations, None, base_map, True, False, None)
    write_point_map_kml("uca_all", all_list, point_locations, None, init_data, None)


def create_all_species_maps(base_map: BaseMap, init_data: TMB_Initialize.InitializationData, species: list,
                            point_locations: dict, species_plot_locations: dict,
                            invalid_species_locations: dict) -> None:
    # create range maps
    species_maps = read_raw_kml(init_data.map_kml_file)
    total = len(species_maps)
    report = total / 20
    j = 0
    print(".........Range Maps.........")
    for i, m in enumerate(species_maps):
        if i >= report:
            j += 1
            print("............{}%".format(j*5))
            report += total / 20
        write_species_range_map_kml(m)
        write_species_range_map(base_map, m)
    write_all_range_map_kml(species_maps)
    write_all_range_map(base_map, species_maps)

    # create point maps
    create_all_point_maps(species, point_locations, species_plot_locations, invalid_species_locations, base_map,
                          init_data)


def create_all_name_maps(base_map: BaseMap, all_names: list, specific_names: list, point_locations: dict,
                         specific_plot_locations: dict, binomial_plot_locations: dict,
                         init_data: TMB_Initialize.InitializationData) -> None:
    total = len(all_names) + len(specific_names)
    report = total / 20
    j = 0
    for i, name in enumerate(all_names):
        if i >= report:
            j += 1
            print(".........{}%".format(j*5))
            report += total / 20
        namefile = "name_" + name_to_filename(name)
        place_list = binomial_plot_locations[name]
        write_point_map(namefile, place_list, point_locations, None, base_map, False, False, None)
        write_point_map_kml(namefile, place_list, point_locations, None, init_data, None)
    for i, name in enumerate(specific_names):
        if i + len(all_names) >= report:
            j += 1
            print("...{}%".format(j*5), end="")
            report += total / 20
        namefile = "sn_" + name.name
        place_list = specific_plot_locations[name]
        write_point_map(namefile, place_list, point_locations, None, base_map, False, False, None)
        write_point_map_kml(namefile, place_list, point_locations, None, init_data, None)


def create_all_location_maps(base_map: BaseMap, point_locations: dict,
                             init_data: TMB_Initialize.InitializationData) -> None:
    total = len(point_locations)
    report = total / 20
    j = 0
    for i, loc in enumerate(point_locations):
        if i >= report:
            j += 1
            print(".........{}%".format(j*5))
            report += total / 20
        point = point_locations[loc]
        if not point.unknown and (("Pacific" in loc) or
                                  ("Europe" in loc) or
                                  ("Samoa" in loc) or
                                  ("Fiji" in loc) or
                                  ("Kiribati" in loc)):  # for testing purposes
        # if not point.unknown:
            place_list = []
            try:
                sub_list = point.all_children()
            except RecursionError:
                report_error("Recursion Error on location: " + loc)
                quit()
            for p in sub_list:
                place_list.append(p.name)
            place_list.append(loc)  # put the primary location at end so it is drawn above children
            namefile = "location_" + place_to_filename(loc)
            write_point_map(namefile, place_list, point_locations, None, base_map, False, True, sub_list)
            write_point_map_kml(namefile, place_list, point_locations, None, init_data, sub_list)


def create_all_maps(init_data: TMB_Initialize.InitializationData, point_locations: dict, species: Optional[list] = None,
                    species_plot_locations: Optional[dict] = None, invalid_species_locations: Optional[dict] = None,
                    all_names: Optional[list] = None, binomial_plot_locations: Optional[dict] = None,
                    specific_names: Optional[list] = None, specific_plot_locations: Optional[dict] = None) -> None:
    # base_map = read_base_map("resources/ne_10m_admin_1_states_provinces.txt", "resources/ne_10m_minor_islands.txt")
    base_map = read_base_map("resources/ne_10m_admin_0_countries.txt", "resources/ne_10m_admin_1_states_provinces.txt",
                             "resources/ne_10m_minor_islands.txt")
    # base_map = read_base_map("resources/ne_50m_admin_0_countries.txt")
    if species is not None:
        print("......Creating Species Maps......")
        create_all_species_maps(base_map, init_data, species, point_locations, species_plot_locations,
                                invalid_species_locations)
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
