import TMB_Initialize
import TMB_Create_Maps
import TMB_ImportShape
import TMB_Import
from tqdm import tqdm
from typing import Optional
import matplotlib.pyplot as mplpy


class FocalSpecies:
    def __init__(self, color="red", maxlat=90, minlat=-90, maxlon=180, minlon=-180):
        self.color = color
        self.maxlat = maxlat
        self.minlat = minlat
        self.maxlon = maxlon
        self.minlon = minlon


def write_multi_species_range_map(base_map, name: str, species_maps: dict, focal_species: dict,
                                  graph_font: Optional[str] = None,
                                  fig_width: float = TMB_Create_Maps.FIG_WIDTH,
                                  fig_height: float = TMB_Create_Maps.FIG_HEIGHT,
                                  fminlat: Optional[float] = None, fmaxlat: Optional[float] = None,
                                  fminlon: Optional[float] = None, fmaxlon: Optional[float] = None) -> None:

    fig, faxes = mplpy.subplots(figsize=[fig_width, fig_height])
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
    for species in species_maps:
        species_map = species_maps[species]
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
    minlon, maxlon, minlat, maxlat = TMB_Create_Maps.adjust_map_boundaries(minlon, maxlon, minlat, maxlat)
    (minlon, maxlon, minlat, maxlat, wrap_lons) = TMB_Create_Maps.draw_and_adjust_basemap(faxes, base_map, mid_atlantic, minlon,
                                                                          maxlon, minlat, maxlat, all_lons, all_lats)

    if fminlon is not None:
        minlon = fminlon
    if fmaxlon is not None:
        maxlon = fmaxlon
    if fminlat is not None:
        minlat = fminlat
    if fmaxlat is not None:
        maxlat = fmaxlat

    # draw range lines
    for c, species in enumerate(species_maps):
        species_map = species_maps[species]
        for line in species_map:
            TMB_Create_Maps.add_line_to_map(faxes, line, wrap_lons, lw=2, color=focal_species[species].color)

    mplpy.xlim(minlon, maxlon)
    mplpy.ylim(minlat, maxlat)
    mplpy.xlabel("longitude", fontname=graph_font)
    mplpy.ylabel("latitude", fontname=graph_font)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    TMB_Create_Maps.adjust_longitude_tick_values(faxes)
    mplpy.savefig(TMB_Create_Maps.__OUTPUT_PATH__ + name + ".png", format="png", dpi=600)
    mplpy.close("all")


def main():
    focal_species = {"tangeri": FocalSpecies(color="blue", maxlat=43, minlat=35.95, maxlon=2, minlon=-12),
                     "princeps": FocalSpecies(color="gold", maxlat=35, minlat=22, maxlon=-100, minlon=-126),
                     "pugnax": FocalSpecies(color="red", maxlat=44, minlat=41, maxlon=-69, minlon=-75),
                     "occidentalis": FocalSpecies(color="purple", maxlat=-27, minlat=-35, maxlon=31, minlon=15),
                     "uruguayensis": FocalSpecies(color="green", maxlat=-33, minlat=-42, maxlon=-50, minlon=-68)}

    TMB_Initialize.initialize()
    init_data = TMB_Initialize.INIT_DATA
    base_map = TMB_Create_Maps.read_base_map(init_data.map_primary, init_data.map_secondary, init_data.map_islands)

    species_blocks = TMB_Import.read_species_blocks(init_data.species_range_blocks)

    print(".........Determining Species Ranges.........")
    coastline_map = TMB_ImportShape.import_arcinfo_shp(TMB_Initialize.INIT_DATA.map_coastline)
    coastline_map.extend(TMB_ImportShape.import_arcinfo_shp(TMB_Initialize.INIT_DATA.map_islands))
    species_ranges = {}
    for s in tqdm(species_blocks):
        # if I want to do the density map
        species_ranges[s] = TMB_Create_Maps.get_range_map_overlap(species_blocks[s], coastline_map)

        # if only doing limited species
        # if s in focal_species:
        #     species_ranges[s] = TMB_Create_Maps.get_range_map_overlap(species_blocks[s], coastline_map)

    # blank map, whole world
    # TMB_Create_Maps.write_species_range_map(base_map, "test", [], fig_width=10, fig_height=5)

    # blank map, reduced latitudes
    # TMB_Create_Maps.write_species_range_map(base_map, "test", [], fig_width=18, fig_height=5.5, fminlat=-50, fmaxlat=60,
    #                                         fminlon=-180, fmaxlon=180)

    # blank map, reduced latitudes and longitudes
    # TMB_Create_Maps.write_species_range_map(base_map, "test", [], fig_width=19, fig_height=11, fminlat=-50, fmaxlat=60,
    #                                         fminlon=-130, fmaxlon=60)

    for s in species_ranges:
        if s in focal_species:
            fs = focal_species[s]
            fw = fs.maxlon - fs.minlon
            fh = fs.maxlat - fs.minlat
            while fw > 10:
                fw /= 2
                fh /= 2
            TMB_Create_Maps.write_species_range_map(base_map, "test" + s, species_ranges[s], fig_width=fw,
                                                    fig_height=fh, fminlat=fs.minlat, fmaxlat=fs.maxlat,
                                                    fminlon=fs.minlon, fmaxlon=fs.maxlon, color=fs.color)

    # reduced latitude and longitudes
    filtered_ranges = {x: species_ranges[x] for x in species_ranges if x in focal_species}
    write_multi_species_range_map(base_map, "test_combined_red", filtered_ranges, focal_species, fig_width=19,
                                  fig_height=11, fminlat=-50, fmaxlat=60, fminlon=-130, fmaxlon=60)

    # no antarctica
    write_multi_species_range_map(base_map, "test_combined_noant", filtered_ranges, focal_species, fig_width=18,
                                  fig_height=7.4, fminlat=-58, fmaxlat=90, fminlon=-180, fmaxlon=180)


    cell_lats, cell_lons, cell_cnts = TMB_Create_Maps.count_species_in_coastal_cells(species_ranges, 4)
    # density map without antarctica
    TMB_Create_Maps.create_cell_density_map(cell_lats, cell_lons, cell_cnts, base_map, name="testdensity",
                                            fig_width=18, fig_height=7.4, minlat=-58)


if __name__ == "__main__":
    main()
