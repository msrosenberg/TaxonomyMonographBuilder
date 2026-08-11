"""
Import ArcInfo ShapeFile

Notes:
This is very minimalistic at this point. It only can successfully read polygon or polyline shape files and ignores
both z and m elements if present.
"""

import struct
from typing import Tuple, Literal
import matplotlib.pyplot as mplpy  # only for testing
import TMB_Initialize
from TMB_Classes import Point


VALIDSHAPES = {0, 1, 3, 5, 8, 11, 13, 15, 18, 21, 23, 25, 28, 31}


def read_double_value(x: bytes, fpos: int) -> Tuple[float, int]:
    """
    extract an 8-byte floating point number from bytestream and increase position counter by 8
    """
    dval = struct.unpack("d", x[fpos:fpos + 8])[0]
    fpos += 8
    return dval, fpos


def read_int_value(x: bytes, byteorder: Literal["little", "big"], fpos: int) -> Tuple[int, int]:
    """
    extract a 4-byte integer from bytestream and increase position counter by 4
    """
    lval = int.from_bytes(x[fpos:fpos + 4], byteorder=byteorder)
    fpos += 4
    return lval, fpos


def import_arcinfo_shp(filename: str, testout: bool = False) -> list:
    """
    testout allows for the printing of values as they are read from the file
    """

    imported_data = []
    bn = 1
    with open(filename, "rb") as mapfile:
        mapdata = mapfile.read()

    fpos = 0
    lval, fpos = read_int_value(mapdata, "big", fpos)
    if testout:
        print("HEADER")  # for test purposes only
        print(f"1: {lval}")
    if lval == 9994:
        # read header
        for i in range(5):
            lval, fpos = read_int_value(mapdata, "big", fpos)  # unused bytes
            if testout:
                bn += 1
                print(f"{bn}: {lval}   (unused)")
        lval, fpos = read_int_value(mapdata, "big", fpos)  # file length
        if testout:
            bn += 1
            print(f"{bn}: {lval}   (file length)")
        lval, fpos = read_int_value(mapdata, "big", fpos)  # version
        if testout:
            bn += 1
            print(f"{bn}: {lval}   (version)")
        shp_type, fpos = read_int_value(mapdata, "little", fpos)  # shape type
        if testout:
            bn += 1
            print(f"{bn}: {shp_type}   (shape type)")
        if shp_type in VALIDSHAPES:
            for i in range(8):  # read boundaries
                dval, fpos = read_double_value(mapdata, fpos)
                if testout:
                    bn += 1
                    print(f"{bn}: {dval:1.8f}   (boundary)")
            # read records
            rcnt = - 1
            while fpos < len(mapdata):
                lval, fpos = read_int_value(mapdata, "big", fpos)  # record number
                rec_len, fpos = read_int_value(mapdata, "big", fpos)  # record length
                st, fpos = read_int_value(mapdata, "little", fpos)  # shape type
                if testout:
                    print()
                    print("RECORD HEADER")
                    bn += 1
                    print(f"{bn}: {lval}   (record number)")
                    bn += 1
                    print(f"{bn}: {rec_len}   (content length)")
                    print()
                    print("RECORD")
                if st == 0:
                    pass  # null shape
                # elif st in {1, 11, 21}:  # point, pointm, pointz
                #     pass
                #     """
                #       inc(rcnt);
                #       if (st = 11) then Is3D := true;
                #       // x value
                #       BlockRead(mapfile,dval,8);
                #       NewDat := TImportDataValue.Create;
                #       NewDat.row := rcnt;
                #       NewDat.col := 0;
                #       NewDat.Data := dval;
                #       NewDat.IsEmpty := false;
                #       InDatList.Add(NewDat);
                #       // y value
                #       BlockRead(mapfile,dval,8);
                #       NewDat := TImportDataValue.Create;
                #       NewDat.row := rcnt;
                #       NewDat.col := 1;
                #       NewDat.Data := dval;
                #       NewDat.IsEmpty := false;
                #       InDatList.Add(NewDat);
                #       if (st = 11) then begin
                #          // z value
                #          BlockRead(mapfile,dval,8);
                #          NewDat := TImportDataValue.Create;
                #          NewDat.row := rcnt;
                #          NewDat.col := 2;
                #          NewDat.Data := dval;
                #          NewDat.IsEmpty := false;
                #          InDatList.Add(NewDat);
                #       end;
                #       // associated measure
                #       if (st = 11) or (st = 21) then BlockRead(mapfile,dval,8);
                #     """
                # elif st in {8, 18, 28}:  # multipoint, multipoint m, multipoint z
                #     pass
                #     """
                #               if (st = 18) then Is3D := true;
                #               // read x and y boundaries
                #               for i := 1 to 4 do BlockRead(mapfile,dval,8);
                #               BlockRead(mapfile,lval,4); // # points
                #               j := lval;
                #               for i := 1 to j do begin // each point
                #                   inc(rcnt);
                #                   // x value
                #                   BlockRead(mapfile,dval,8);
                #                   NewDat := TImportDataValue.Create;
                #                   NewDat.row := rcnt;
                #                   NewDat.col := 0;
                #                   NewDat.Data := dval;
                #                   NewDat.IsEmpty := false;
                #                   InDatList.Add(NewDat);
                #                   // y value
                #                   BlockRead(mapfile,dval,8);
                #                   NewDat := TImportDataValue.Create;
                #                   NewDat.row := rcnt;
                #                   NewDat.col := 1;
                #                   NewDat.Data := dval;
                #                   NewDat.IsEmpty := false;
                #                   InDatList.Add(NewDat);
                #               end;
                #               if (st = 18) then begin
                #                  BlockRead(mapfile,dval,8); // min Z
                #                  BlockRead(mapfile,dval,8); // max Z
                #                  for i := 1 to j do begin // Z for each point
                #                      // z value
                #                      BlockRead(mapfile,dval,8);
                #                      NewDat := TImportDataValue.Create;
                #                      NewDat.row := rcnt - j + i;
                #                      NewDat.col := 2;
                #                      NewDat.Data := dval;
                #                      NewDat.IsEmpty := false;
                #                      InDatList.Add(NewDat);
                #                  end;
                #               end;
                #               if (st = 18) or (st = 28) then begin
                #                  BlockRead(mapfile,dval,8); // min M
                #                  BlockRead(mapfile,dval,8); // max M
                #                  for i := 1 to lval do // M for each point
                #                      BlockRead(mapfile,dval,8);
                #               end;
                #     """

                elif st in {3, 13, 23, 5, 15, 25}:  # polyline(zm), polygon (zm)
                    # read x and y boundaries
                    for i in range(4):
                        dval, fpos = read_double_value(mapdata, fpos)
                        if testout:
                            bn += 1
                            print(f"{bn}: {dval:1.8f}   (boundary)")
                    nparts, fpos = read_int_value(mapdata, "little", fpos)
                    if testout:
                        bn += 1
                        print(f"{bn}: {nparts}   (number of parts)")
                    npoints, fpos = read_int_value(mapdata, "little", fpos)
                    if testout:
                        bn += 1
                        print(f"{bn}: {npoints}   (number of points)")
                    # read  number of points per part
                    pcnt = []
                    for i in range(nparts):
                        p, fpos = read_int_value(mapdata, "little", fpos)
                        pcnt.append(p)
                    if testout:
                        for i, p in enumerate(pcnt):
                            bn += 1
                            print(f"{bn}: {p}   (first point for part {i})")
                    cur_part = 1
                    # read points
                    newpart = []
                    for j in range(npoints):
                        rcnt += 1
                        # first point in part
                        if cur_part <= nparts:
                            if j == pcnt[cur_part-1]:
                                if testout:
                                    if cur_part == nparts:
                                        print(f"{nparts} {npoints} {j} {pcnt[cur_part-1]} {cur_part} "
                                              f"{npoints-pcnt[cur_part-1]}")
                                    else:
                                        print(f"{nparts} {npoints} {j} {pcnt[cur_part-1]} {cur_part} "
                                              f"{pcnt[cur_part]-pcnt[cur_part-1]}")
                                newpart = []
                                imported_data.append(newpart)
                                cur_part += 1
                        point = Point()
                        newpart.append(point)
                        # x value
                        point.lon, fpos = read_double_value(mapdata, fpos)
                        if testout:
                            bn += 1
                            print(f"{bn}: {point.lon:1.8f}   (longitude)")
                        # y value
                        point.lat, fpos = read_double_value(mapdata, fpos)
                        if testout:
                            bn += 1
                            print(f"{bn}: {point.lat:1.8f}   (latitude)")

                    if st in {13, 15}:  # get z values
                        dval, fpos = read_double_value(mapdata, fpos)  # min z
                        dval, fpos = read_double_value(mapdata, fpos)  # max z
                        for i in range(npoints):
                            z, fpos = read_double_value(mapdata, fpos)
                    if st not in {3, 5}:  # get m values
                        dval, fpos = read_double_value(mapdata, fpos)  # min m
                        dval, fpos = read_double_value(mapdata, fpos)  # max m
                        for i in range(npoints):
                            m, fpos = read_double_value(mapdata, fpos)

                else:  # all other shape types are invalid at this time; skip
                    fpos += (rec_len - 2) * 2
            # end of data read loop
        else:
            print(f"{filename} contains an unknown or unsupported shape type.")
    else:
        print(f"{filename} does not appear to be a shapefile.")
    return imported_data


def test_draw(map_data: list) -> None:
    """
    Only meant to be used internally to test whether the maps are importing correctly. Creates a PNG
    of the imported line segments
    """
    fig, faxes = mplpy.subplots(figsize=[6, 3])
    for spine in faxes.spines:
        faxes.spines[spine].set_visible(False)
    for part in map_data:
        lons = []
        lats = []
        for p in part:
            lons.append(p.lon)
            lats.append(p.lat)
        faxes.plot(lons, lats, color="black", linewidth=0.5)

    mplpy.xlim(-180, 180)
    mplpy.ylim(-90, 90)
    faxes.yaxis.set_visible(False)
    faxes.xaxis.set_visible(False)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    mplpy.savefig("test_shp_import.png", format="png", dpi=600)
    mplpy.close("all")


if __name__ == "__main__":
    # for testing purposes
    TMB_Initialize.initialize()
    data = import_arcinfo_shp(TMB_Initialize.INIT_DATA.map_coastline)
    print("# of parts = {}".format(len(data)))
    data.extend(import_arcinfo_shp(TMB_Initialize.INIT_DATA.map_islands))
    print("# of parts = {}".format(len(data)))
    test_draw(data)
