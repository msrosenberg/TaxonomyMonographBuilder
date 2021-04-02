from typing import Tuple
from collections import namedtuple
from math import sin, cos, acos
import datetime
import TMB_Create_Maps
import TMB_Initialize
import TMB_Import
import TMB_Create_Coastal_Ranges
from TMB_Classes import RangeCell


"""
{---Calculate the Spherical Distance between two points---}
{ Returns the geodesic distance along the globe in km, for
  two points represented by longitudes and latitudes }
function SphDist(Lon1,Lat1,Lon2,Lat2 : double) : double;
{function SphDist(x,y : TCoords) : double;}
const
        con1 = 24902.1483 * 1.60935;
        con2 = 57.29577951;
        conv = con2 / 360.0;
var
   angle, p : extended;
begin
     {if (abs(Lon1 - Lon2) > 180.0) then
        if (Lon1 < 0.0) then begin
           Lon1 := Lon1 + 180.0;
           Lon2 := Lon2 - 180.0;
        end else begin
            Lon1 := Lon1 - 180.0;
            Lon2 := Lon2 + 180.0;
        end;}
     Lon1 := Lon1 / con2; Lon2 := Lon2 / con2;
     Lat1 := Lat1 / con2; Lat2 := Lat2 / con2;
     p := abs(Lon1 - Lon2); // Difference in longitudes
     angle := sin(Lat1) * sin(Lat2) +
           cos(Lat1) * cos(Lat2) * cos(p);
     if (angle >= 1.0) then result := 0.0
     else result := arccos(angle) * con1 * conv;
     //else result := arctan(sqrt(1 - sqr(angle)) / angle) * con1 * conv;
end;
"""

CON1 = 24902.1483 * 1.60935
CON2 = 57.29577951
CONV = CON2 / 360.0


def spherical_distance(lon1, lat1, lon2, lat2) -> float:
    lon1 /= CON2
    lon2 /= CON2
    lat1 /= CON2
    lat2 /= CON2
    p = abs(lon1 - lon2)
    angle = sin(lat1)*sin(lat2) + cos(lat1)*cos(lat2)*cos(p)
    if angle >= 1:
        return 0
    else:
        return acos(angle)*CON1*CONV


def calculate_coastal_length(block_coast: list) -> float:
    length = 0
    for line in block_coast:
        for i, p2 in enumerate(line[1:]):
            p1 = line[i-1]
            length += spherical_distance(p1.lon, p1.lat, p2.lon, p2.lat)
    return length


def block_count(block: RangeCell, ranges: dict) -> Tuple[int, set]:
    cnt = 0
    species = set()
    for s in ranges:
        r = ranges[s]
        isin = False
        for line in r:
            for p in line:
                if block.inside(p.lat, p.lon):
                    isin = True
        if isin:
            cnt += 1
            species.add(s)
    return cnt, species


def block_calcluations(init_data: TMB_Initialize.INIT_DATA):
    start_time = datetime.datetime.now()
    print("......Start Time:", start_time)

    BlockData = namedtuple("BlockData", ["block", "block_coast", "length", "species_cnt", "species_set"])

    coastline_map = TMB_Create_Coastal_Ranges.import_coastline_data(init_data)
    print("Number of coastline elements:", len(coastline_map))

    species_blocks = TMB_Import.read_species_blocks(init_data.species_range_blocks)

    ranges = {}
    for species in species_blocks:
        print("Determining {} range".format(species))
        ranges[species] = TMB_Create_Maps.get_range_map_overlap(species_blocks[species], coastline_map)

    # all_blocks = []
    # for species in species_blocks:
    #     all_blocks.extend(species_blocks[species])
    # all_range = TMB_Create_Maps.get_range_map_overlap(all_blocks, coastline_map)

    with open("world_block_data.txt", "w") as outfile:
        world_blocks = []
        for lon in range(-180, 180):
            for lat in range(-45, 45):  # actual range is ~-38 to 43
                print("Working on cell {} {}".format(lat, lon))
                new_block = RangeCell(lat, lon, lat + 1, lon + 1)
                block_coast = TMB_Create_Maps.get_range_map_overlap([new_block], coastline_map)
                if len(block_coast) > 0:
                    coast_len = calculate_coastal_length(block_coast)
                    if coast_len > 0:
                        cnt, block_species = block_count(new_block, ranges)
                        b = BlockData(block=new_block, block_coast=block_coast, length=coast_len, species_cnt=cnt,
                                      species_set=block_species)
                        world_blocks.append(b)
                        outfile.write("{}\t{}\t{}\t{}\t{}\n".format(b.block.lower_left_lat,
                                                                    b.block.lower_left_lon,
                                                                    b.length,
                                                                    b.species_cnt,
                                                                    b.species_set))

    end_time = datetime.datetime.now()
    print("......End Time:", end_time)
    print("...TotalRun Time:", end_time - start_time)


def latitude_summary():
    with open("world_block_data.txt", "r") as infile:
        latspecies = {lat: set() for lat in range(-45, 45)}
        coastline = {lat: 0 for lat in range(-45, 45)}
        for line in infile:
            data = line.strip().split("\t")
            lat = eval(data[0])
            coastline[lat] += eval(data[2])
            if eval(data[3]) > 0:
                instr = data[4]
                instr = instr.replace("'", "")  # delete single quotes
                instr = instr.replace("{", "")  # delete {
                instr = instr.replace("}", "")  # delete }
                species = instr.split(",")
                species = set(s.strip() for s in species)
                latspecies[lat] |= species
    with open("lat_data.txt", "w") as outfile:
        for lat in sorted(latspecies.keys()):
            outfile.write("{}\t{}\t{}\t{}\n".format(lat, len(latspecies[lat]), latspecies[lat], coastline[lat]))


def calculate_species_extent(range_data: list) -> Tuple[float, float, float, float, float, float]:
    length = calculate_coastal_length(range_data)
    maxlon = -180
    minlon = 180
    maxlat = -90
    minlat = 90
    for line in range_data:
        for point in line:
            maxlon = max(maxlon, point.lon)
            minlon = min(minlon, point.lon)
            maxlat = max(maxlat, point.lat)
            minlat = min(minlat, point.lat)
    # input(str(minlon) + " " + str(maxlon))
    if (maxlon == 180) and (round(minlon) == -180):
        # print("entered")
        maxlon = -180
        minlon = 360
        for line in range_data:
            for point in line:
                if point.lon < 0:
                    lon = point.lon + 360
                else:
                    lon = point.lon
                maxlon = max(maxlon, lon)
                minlon = min(minlon, lon)
    dist = spherical_distance(maxlon, minlon, maxlat, minlat)
    return minlat, minlon, maxlat, maxlon, length, dist


def range_summary(init_data: TMB_Initialize.INIT_DATA):
    coastline_map = TMB_Create_Coastal_Ranges.import_coastline_data(init_data)
    print("Number of coastline elements:", len(coastline_map))

    species_blocks = TMB_Import.read_species_blocks(init_data.species_range_blocks)

    ranges = {}
    for species in species_blocks:
        print("Determining {} range".format(species))
        ranges[species] = TMB_Create_Maps.get_range_map_overlap(species_blocks[species], coastline_map)

    with open("species_extents.txt", "w") as outfile:
        outfile.write("species\tminlat\tminlon\tmaxlat\tmaxlon\tcoastline length\tdiagonal distance\n")
        for species in sorted(ranges.keys()):
            minlat, minlon, maxlat, maxlon, length, diagonal = calculate_species_extent(ranges[species])
            outfile.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(species, minlat, minlon, maxlat, maxlon, length,
                                                                diagonal))


def main():
    TMB_Initialize.initialize()
    init_data = TMB_Initialize.INIT_DATA
    # block_calcluations(init_data)
    # latitude_summary()
    range_summary(init_data)


if __name__ == "__main__":
    main()
