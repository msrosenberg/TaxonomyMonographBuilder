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
import os
import matplotlib.pyplot as mplpy

TMP_PATH = "temp/"
OUTPUT_PATH = "media/maps/"


class Point():
    def __init__(self, lat=0.0, lon=0.0):
        self.lat = lat
        self.lon = lon


class Polygon():
    def __init__(self):
        self.points = []

    def n(self):
        return len(self.points)


def read_placemark(infile):
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


def read_crab(infile, namestr):
    line = infile.readline().strip()
    crabplaces = []
    while not line.startswith("</Folder>"):
        if line.startswith("<Placemark>"):
            newplace = read_placemark(infile)
            crabplaces.append(newplace)
        line = infile.readline().strip()
    return [namestr, crabplaces]


def read_folder(infile):
    line = infile.readline().strip()
    crab = None
    while not line.startswith("</Folder>"):
        if line.startswith("<name>Uca"):
            crab = read_crab(infile, line)
            line = "</Folder>"
        else:
            line = infile.readline().strip()
    return crab


def read_raw(filename):
    maplist = []
    with open(filename, "r") as infile:
        line = infile.readline()
        while line != "":
            line = line.strip()
            if line.startswith("<Folder>"):
                new_map = read_folder(infile)
                maplist.append(new_map)
            line = infile.readline()
    return maplist


def output_species_kml(crab):
    name = crab[0]
    locs = crab[1]
    name = name[name.find("Uca")+4:name.find("</")]
    with open(TMP_PATH + "doc.kml", "w") as outfile:
        outfile.write("<?xml version=\"1.0\"?>\n")
        outfile.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
        outfile.write(" <Document>\n")
        outfile.write("  <Style id=\"species_range\">\n")
        outfile.write("    <LineStyle>\n")
        outfile.write("      <color>FFFF55FF</color>\n")
        outfile.write("      <width>5</width>\n")
        outfile.write("    </LineStyle>\n")
        outfile.write("  </Style>\n")
        outfile.write("  <Placemark>\n")
        outfile.write("    <name/>\n")
        outfile.write("    <description/>\n")
        outfile.write("    <styleUrl>\n")
        outfile.write("      #species_range\n")
        outfile.write("    </styleUrl>\n")
        outfile.write("    <MultiGeometry>\n")
        for loc in locs:
            if loc[1]:
                for x in loc[2]:
                    outfile.write("      <LineString>\n")
                    outfile.write("        <coordinates>\n")
                    outfile.write("          " + x + "\n")
                    outfile.write("        </coordinates>\n")
                    outfile.write("      </LineString>\n")
            else:
                outfile.write("      <LineString>\n")
                outfile.write("        <coordinates>\n")
                outfile.write("          " + loc[2] + "\n")
                outfile.write("        </coordinates>\n")
                outfile.write("      </LineString>\n")
        outfile.write("    </MultiGeometry>\n")
        outfile.write("  </Placemark>\n")
        outfile.write(" </Document>\n")
        outfile.write("</kml>\n")
    with zipfile.ZipFile(OUTPUT_PATH + "u_" + name + ".kmz", "w", zipfile.ZIP_DEFLATED) as myzip:
        myzip.write(TMP_PATH + "doc.kml")
        myzip.close()


def output_all_kml(crabs):
    with open(TMP_PATH + "doc.kml", "w") as outfile:
        outfile.write("<?xml version=\"1.0\"?>\n")
        outfile.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
        outfile.write(" <Document>\n")
        for crab in crabs:
            name = crab[0]
            name = name[name.find("Uca")+4:name.find("</")]
            outfile.write("  <Style id=\"" + name + "\">\n")
            outfile.write("    <LineStyle>\n")
            outfile.write("      <color>28FF78F0</color>\n")
            outfile.write("      <width>5</width>\n")
            outfile.write("    </LineStyle>\n")
            outfile.write("  </Style>\n")
        for crab in crabs:
            name = crab[0]
            locs = crab[1]
            name = name[name.find("Uca")+4:name.find("</")]
            outfile.write("  <Placemark>\n")
            outfile.write("    <name>Uca " + name + "</name>\n")
            outfile.write("    <description/>\n")
            outfile.write("    <styleUrl>\n")
            outfile.write("      #" + name + "\n")
            outfile.write("    </styleUrl>\n")
            outfile.write("    <MultiGeometry>\n")
            for loc in locs:
                if loc[1]:
                    for x in loc[2]:
                        outfile.write("      <LineString>\n")
                        outfile.write("        <coordinates>\n")
                        outfile.write("          " + x + "\n")
                        outfile.write("        </coordinates>\n")
                        outfile.write("      </LineString>\n")
                else:
                    outfile.write("      <LineString>\n")
                    outfile.write("        <coordinates>\n")
                    outfile.write("          " + loc[2] + "\n")
                    outfile.write("        </coordinates>\n")
                    outfile.write("      </LineString>\n")
            outfile.write("    </MultiGeometry>\n")
            outfile.write("  </Placemark>\n")
        outfile.write(" </Document>\n")
        outfile.write("</kml>\n")
    with zipfile.ZipFile(OUTPUT_PATH + "uca.kmz", "w", zipfile.ZIP_DEFLATED) as myzip:
        myzip.write(TMP_PATH + "doc.kml")
        myzip.close()


def read_base_map(filename):
    polygon_list = []
    with open(filename, "r") as infile:
        line = infile.readline()
        while line != "":
            if line.startswith("Polygon"):
                data = line.strip().split("\t")
                new_polygon = Polygon()
                polygon_list.append(new_polygon)
                n = abs(int(data[1]))  # wtf??? why is one of the # of points negative?
                new_point = Point(lat=float(data[3]), lon=float(data[2]))
                new_polygon.points.append(new_point)
                for i in range(n-1):
                    line = infile.readline()
                    data = line.strip().split("\t")
                    new_point = Point(lat=float(data[1]), lon=float(data[0]))
                    new_polygon.points.append(new_point)
            else:
                line = infile.readline()
            # print(line)
    # test
    # for p in polygon_list:
    #     print("# points =", p.n())
    return polygon_list


def add_line_to_map(faxes, points, minlon, maxlon, minlat, maxlat, lw, a):
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
    # faxes.plot(lons, lats, color="red", linewidth=5, alpha=0.4)
    faxes.plot(lons, lats, color="red", linewidth=lw, alpha=a)
    return minlon, maxlon, minlat, maxlat


def draw_base_map(faxes, base_map):
    for polygon in base_map:
        lons = [p.lon for p in polygon.points]
        lats = [p.lat for p in polygon.points]
        faxes.plot(lons, lats, "silver", linewidth=0.5)


def adjust_map_boundaries(minlon, maxlon, minlat, maxlat):
    # adjust ranges to keep map scale (2:1 ratio, lon to lat), with a 5 degree buffer
    lon_range = maxlon - minlon + 10
    lat_range = maxlat - minlat + 10
    if lon_range > 2 * lat_range:
        d = lon_range - 2 * lat_range
        minlat -= d/2
        maxlat += d/2
    else:
        d = 2 * lat_range - lon_range
        minlon -= d/2
        maxlon += d/2
    return minlon-5, maxlon+5, minlat-5, maxlat+5


def write_single_species_map_figure(base_map, species_map):
    fig, faxes = mplpy.subplots(figsize=[6.5, 3.25])
    draw_base_map(faxes, base_map)
    # for polygon in base_map:
    #     lons = [p.lon for p in polygon.points]
    #     lats = [p.lat for p in polygon.points]
    #     faxes.plot(lons, lats, "silver", linewidth=0.5)
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
    mplpy.savefig("media/maps/u_" + name + "_map.svg", format="svg")
    mplpy.close()


def write_all_species_map_figure(base_map, species_maps):
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
                    minlon, maxlon, minlat, maxlat = add_line_to_map(faxes, x, minlon, maxlon, minlat, maxlat, 2, 0.1)
            else:
                minlon, maxlon, minlat, maxlat = add_line_to_map(faxes, loc[2], minlon, maxlon, minlat, maxlat, 2, 0.1)

    # minlon, maxlon, minlat, maxlat = adjust_map_boundaries(minlon, maxlon, minlat, maxlat)
    mplpy.xlim(-180, 180)
    mplpy.ylim(-90, 90)
    # mplpy.xlabel("longitude")
    # mplpy.ylabel("latitude")
    faxes.axes.get_yaxis().set_visible(False)
    faxes.axes.get_xaxis().set_visible(False)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    mplpy.savefig("media/maps/uca_map.svg", format="svg")
    mplpy.close()


def main():
    # will eventually need to put options here for choosing different paths, etc.
    main_path = "fiddlercrab.info"
    os.chdir(main_path)

    input_file_name = "data/Fiddler Crabs.kml"
    species_maps = read_raw(input_file_name)
    base_map = read_base_map("resources/world_map.txt")
    # for m in species_maps:
        # output_species_kml(m)
        # write_single_species_map_figure(base_map, m)
    # output_all_kml(bas_map, species_maps)
    write_all_species_map_figure(base_map, species_maps)

if __name__ == "__main__":
    main()
