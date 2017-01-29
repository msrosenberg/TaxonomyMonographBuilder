"""
shared functions dealing with drawing maps
"""


class Point:
    def __init__(self, lat=0.0, lon=0.0):
        self.lat = lat
        self.lon = lon


class Polygon:
    def __init__(self):
        self.points = []

    def n(self):
        return len(self.points)


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
    return polygon_list


def draw_base_map(faxes, base_map):
    for polygon in base_map:
        lons = [p.lon for p in polygon.points]
        lats = [p.lat for p in polygon.points]
        faxes.plot(lons, lats, "silver", linewidth=0.5, zorder=1)


def adjust_map_boundaries(minlon, maxlon, minlat, maxlat):
    # adjust ranges to keep map scale (2:1 ratio, lon to lat), with a 5 degree buffer
    # lon_range = maxlon - minlon + 10
    # lat_range = maxlat - minlat + 10
    # if (lon_range >= 350) or (lat_range >= 170):
    #     return -180, 180, -90, 90
    # else:
    #     if lon_range > 2 * lat_range:
    #         d = lon_range - 2 * lat_range
    #         minlat -= d/2
    #         maxlat += d/2
    #     else:
    #         d = 2 * lat_range - lon_range
    #         minlon -= d/2
    #         maxlon += d/2
    #     if maxlon > 175:
    #         d = maxlon - 175
    #         maxlon = 175
    #         minlon -= d
    #     if minlon < -175:
    #         d = -175 - minlon
    #         minlon = -175
    #         maxlon += d
    #     if maxlat > 85:
    #         d = maxlat - 85
    #         maxlat = 85
    #         minlat -= d
    #     if minlat < -85:
    #         d = -85 - minlat
    #         minlat = -85
    #         maxlat += d
    #     return minlon-5, maxlon+5, minlat-5, maxlat+5

    # alternate approach
    maxlon += 5
    minlon -=5
    maxlat += 5
    minlat -=5
    lon_range = maxlon - minlon
    lat_range = maxlat - minlat
    if lon_range > 2 * lat_range:
        d = lon_range - 2 * lat_range
        minlat -= d / 2
        maxlat += d / 2
    else:
        d = 2 * lat_range - lon_range
        minlon -= d / 2
        maxlon += d / 2
    if maxlon > 180:
        maxlon, minlon = 180, minlon - (maxlon-180)
    if minlon < -180:
        maxlon, minlon = maxlon + (-180 - minlon), -180
    if maxlat > 90:
        maxlat, minlat = 90, minlat - (maxlat-90)
    if minlat < -90:
        maxlat, minlat = maxlat + (-90 - minlat), -90
    if (maxlon > 180) or (minlon < -180) or (maxlat > 90) or (minlat < -90):
        return -180, 180, -90, 90
    else:
        return minlon, maxlon, minlat, maxlat
