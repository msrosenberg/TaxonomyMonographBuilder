"""
Import ArcInfo ShapeFile
"""

import struct
import TMB_Initialize
import TMB_Create_Maps
import matplotlib.pyplot as mplpy


VALIDSHAPES = {0, 1, 3, 5, 8, 11, 13, 15, 18, 21, 23, 25, 28, 31}


def read_double_value(x, fpos):
    dval = struct.unpack("d", x[fpos:fpos + 8])[0]
    fpos += 8
    return dval, fpos


def read_int_value(x, bo, fpos):
    lval = int.from_bytes(x[fpos:fpos + 4], byteorder=bo)
    fpos += 4
    return lval, fpos


def import_arcinfo_shp(filename: str) -> list:
    imported_data = []
    testout = False
    bn = 1
    # is_3d = False
    # is_line = False
    # is_poly = False
    try:
        with open(filename, "rb") as mapfile:
            mapdata = mapfile.read()

        fpos = 0
        lval, fpos = read_int_value(mapdata, "big", fpos)
        if testout:
            print("HEADER")  # for test purposes only
            print("1: " + str(lval))
        if lval == 9994:
            # read header
            for i in range(5):
                lval, fpos = read_int_value(mapdata, "big", fpos)  # unused bytes
                if testout:
                    bn += 1
                    print("{}: {}   (unused)".format(bn, lval))
            lval, fpos = read_int_value(mapdata, "big", fpos)  # file length
            if testout:
                bn += 1
                print("{}: {}   (file length)".format(bn, lval))
            lval, fpos = read_int_value(mapdata, "big", fpos)  # version
            if testout:
                bn += 1
                print("{}: {}   (version)".format(bn, lval))
            shp_type, fpos = read_int_value(mapdata, "little", fpos)  # shape type
            if testout:
                bn += 1
                print("{}: {}   (shape type)".format(bn, shp_type))
            if shp_type in VALIDSHAPES:
                for i in range(8):  # read boundaries
                    dval, fpos = read_double_value(mapdata, fpos)
                    if testout:
                        bn += 1
                        print("{}: {:1.8f}   (boundary)".format(bn, dval))
                # read records
                rcnt = - 1
                while fpos < len(mapdata):
                    lval, fpos = read_int_value(mapdata, "big", fpos)  # record number
                    rec_len, fpos = read_int_value(mapdata, "big", fpos)  # reord length
                    st, fpos = read_int_value(mapdata, "little", fpos)  # shape type
                    if testout:
                        print()
                        print("RECORD HEADER")
                        bn += 1
                        print("{}: {}   (record number)".format(bn, lval))
                        bn += 1
                        print("{}: {}   (content length)".format(bn, rec_len))
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
                        # if st in {3, 13, 23}:
                        #     is_line = True
                        # else:
                        #     is_poly = True
                        # if st in {13, 15}:
                        #     is_3d = True
                        # read x and y boundaries
                        for i in range(4):
                            dval, fpos = read_double_value(mapdata, fpos)
                            if testout:
                                bn += 1
                                print("{}: {:1.8f}   (boundary)".format(bn, dval))
                        nparts, fpos = read_int_value(mapdata, "little", fpos)
                        if testout:
                            bn += 1
                            print("{}: {}   (number of parts)".format(bn, nparts))
                        npoints, fpos = read_int_value(mapdata, "little", fpos)
                        if testout:
                            bn += 1
                            print("{}: {}   (number of points)".format(bn, npoints))
                        # read  number of points per part
                        pcnt = []
                        for i in range(nparts):
                            p, fpos = read_int_value(mapdata, "little", fpos)
                            pcnt.append(p)
                        if testout:
                            for i, p in enumerate(pcnt):
                                bn += 1
                                print("{}: {}   (first point for part {})".format(bn, p, i))
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
                                            print("{} {} {} {} {} {}".format(nparts, npoints, j, pcnt[cur_part-1],
                                                                             cur_part, npoints-pcnt[cur_part-1]))
                                        else:
                                            print("{} {} {} {} {} {}".format(nparts, npoints, j, pcnt[cur_part-1],
                                                                             cur_part, pcnt[cur_part]-pcnt[cur_part-1]))
                                    newpart = []
                                    imported_data.append(newpart)
                                    cur_part += 1
                                    """
                                    NewDat := TImportDataValue.Create;
                                    NewDat.row := rcnt;
                                    NewDat.col := 0;
                                    if (kk = nparts) then NewDat.Data := npnts - pcnt[kk-1]
                                    else NewDat.Data := pcnt[kk] - pcnt[kk-1]; //*****
                                    NewDat.IsEmpty := false;
                                    InDatList.Add(NewDat);
                                    inc(kk);
                                    """
                            point = TMB_Create_Maps.Point()
                            newpart.append(point)
                            # x value
                            point.lon, fpos = read_double_value(mapdata, fpos)
                            if testout:
                                bn += 1
                                # print("{}: {:1.8f}   (longitude)".format(bn, point.lon))
                            # NewDat: = TImportDataValue.Create;
                            # NewDat.row: = rcnt;
                            # NewDat.col: = 1;
                            # NewDat.Data: = dval;
                            # NewDat.IsEmpty: = false;
                            # InDatList.Add(NewDat);

                            # y value
                            point.lat, fpos = read_double_value(mapdata, fpos)
                            if testout:
                                bn += 1
                                # print("{}: {:1.8f}   (latitude)".format(bn, point.lat))
                            # NewDat: = TImportDataValue.Create;
                            # NewDat.row: = rcnt;
                            # NewDat.col: = 2;
                            # NewDat.Data: = dval;
                            # NewDat.IsEmpty: = false;
                            # InDatList.Add(NewDat);
                        if st in {13, 15}:  # get z values
                            dval, fpos = read_double_value(mapdata, fpos)  # min z
                            dval, fpos = read_double_value(mapdata, fpos)  # max z
                            for i in range(npoints):
                                z, fpos = read_double_value(mapdata, fpos)
                                #         NewDat := TImportDataValue.Create;
                                #         NewDat.row := rcnt - npnts + i;
                                #         NewDat.col := 3;
                                #         NewDat.Data := dval;
                                #         NewDat.IsEmpty := false;
                                #         InDatList.Add(NewDat);
                        if st not in {3, 5}:  # get m values
                            dval, fpos = read_double_value(mapdata, fpos)  # min m
                            dval, fpos = read_double_value(mapdata, fpos)  # max m
                            for i in range(npoints):
                                m, fpos = read_double_value(mapdata, fpos)

                    else:  # all other shape types are invalid at this time
                        fpos += (rec_len - 2) * 2

                # end of data read loop
                """

                 ImportDoRow := false;
                 ImportDoCol := false;
                 if Is3D then ImportND := 3
                 else ImportND := 2;
                 ImportNName := -1;
                 if IsLine then begin
                    ImportDataType := 7;
                    ImportNcnt := 0;
                    ImportXNum := 1;
                    ImportYNum := 2;
                    ImportZNum := 3;
                    if (rcnt < 0) then begin
                        result := false;
                        ReportPASSaGEError('Missing Data','No lines were found in '+trim(ExtractFilename(filen))+'.','',0);
                    end;
                 end else if IsPoly then begin
                    ImportDataType := 8;
                    ImportNcnt := 0;
                    ImportXNum := 1;
                    ImportYNum := 2;
                    ImportZNum := 3;
                    ImportPolyLastP := false;
                    ImportPolyCheckDir := true;
                    if (rcnt < 0) then begin
                        result := false;
                        ReportPASSaGEError('Missing Data','No polygons were found in '+trim(ExtractFilename(filen))+'.','',0);
                    end;
                 end else begin
                     ImportDataType := 1;
                     ImportCrdType := ctXY;
                     ImportXNum := 0;
                     ImportYNum := 1;
                     ImportZNum := 2;
                     if (rcnt < 0) then begin
                        result := false;
                        ReportPASSaGEError('Missing Data','No points were found in '+trim(ExtractFilename(filen))+'.','',0);
                     end;
                 end;
                """
            else:
                print(filename + " contains an unknown or unsupported shape type.")
        else:
            print(filename + " does not appear to be a shapefile.")
        if testout:
            # outputaddblankline;
            # for i := 0 to InDatList.Count - 1 do
            #     with TImportDataValue(InDatList[i]) do begin
            #          outputaddline('# ' + IntToStr(i) + ', Row ' + IntToStr(row) +
            #            ', Col ' + IntToStr(col) + ', Data ' + format('%1.8f',[Data]));
            # end;
            pass
    except:
        print("Input/Output Error")
        print("Error reading", filename)
    return imported_data


"""
function ImportArcInfoShapefile(InDatList : TObjectList; filen : string) : boolean;
var
   mapfile : file;
   ShpType,st,
   RecLen, lval : longword;
   wval : word;
   dval : double;
   IsShp : boolean;
   NewDat : TImportDataValue;
   i,j,kk,rcnt : integer;
   IsLine,IsPoly,Is3D : boolean;
   pcnt : array of integer;
   nparts,npnts : integer;

   // for test purposes only...
   bn : integer;
   testout : boolean;
begin
     testout := false;
     bn := 1;

     result := true;
     Is3D := false; IsLine := false; IsPoly := false;
     try
        IsShp := true;
        AssignFile(mapfile,FileN); Reset(mapfile,1);
        BlockRead(mapfile,lval,4);

        if testout then outputaddline('HEADER'); // for test purposes only
        if testout then outputaddline('1: ' +IntToStr(lval) + '   (swapped = ' + IntToStr(SwapBytes(lval))+')');
        if (SwapBytes(lval) = 9994) then begin // valid shape file
           // read header
           for i := 1 to 5 do begin
               BlockRead(mapfile,lval,4); // unused bytes
               if testout then begin
                  inc(bn);
                  outputaddline(IntToStr(bn)+': ' +IntToStr(lval) + '  (unused)');
               end;
           end;
           BlockRead(mapfile,lval,4); // file length (swapped)
           if testout then begin
              inc(bn);
              outputaddline(IntToStr(bn)+': ' +IntToStr(lval) + ' (file length)    (swapped = '
               + IntToStr(SwapBytes(lval))+' [1/2 the number of bytes])');
           end;
           BlockRead(mapfile,lval,4); // version
           if testout then begin
              inc(bn);
              outputaddline(IntToStr(bn)+': ' +IntToStr(lval) + ' (version)');
           end;
           BlockRead(mapfile,ShpType,4); // shape type
           if testout then begin
              inc(bn);
              outputaddline(IntToStr(bn)+': ' +IntToStr(ShpType) + ' (shape type)');
           end;

           if ShpType in ValidShapes then begin
              if (lval = 1000) then begin
                 for i := 1 to 8 do begin
                     BlockRead(mapfile,dval,8); // boundaries
                     if testout then begin
                        inc(bn);
                        outputaddline(IntTostr(bn)+': '+format('%1.8f',[dval])+ '   (boundary)');
                     end;
                 end;
                 // read records
                 rcnt := -1;
                 while not eof(mapfile) do begin
                       BlockRead(mapfile,lval,4); // record #
                       BlockRead(mapfile,RecLen,4); // record length
                       BlockRead(mapfile,st,4); // shape type
                       if testout then begin
                          outputaddblankline;
                          outputaddline('RECORD HEADER');
                          // the next two parts should not both be used
                          // the first is for lookint at the .shx file
                          // the second is for looking at the .shp file
                          // comment out whichever is not being examined

                          // the following block is for looking at the .shx file rather than the .shp file
                          {inc(bn);
                          outputaddline(IntToStr(bn)+': ' +IntToStr(lval) + ' (offset)    (swapped = '
                            + IntToStr(SwapBytes(lval))+')');
                          inc(bn);
                          outputaddline(IntToStr(bn)+': ' +IntToStr(RecLen) + ' (content length)    (swapped = '
                            + IntToStr(SwapBytes(RecLen))+')   [1/2 the number of bytes]');
                          outputaddblankline;}

                          // the next large section is for looking at the .shp file
                          inc(bn);
                          outputaddline(IntToStr(bn)+': ' +IntToStr(lval) + ' (record #)    (swapped = ' + IntToStr(SwapBytes(lval))+')');
                          inc(bn);
                          outputaddline(IntToStr(bn)+': ' +IntToStr(RecLen) + ' (content length)    (swapped = '  + IntToStr(SwapBytes(RecLen))+')   [1/2 the number of bytes]');
                          outputaddblankline;
                          outputaddline('RECORD');
                       end;

                       //if testout then begin
                          //inc(bn);
                          //outputaddline(IntToStr(bn)+': ' +IntToStr(st) + ' (shape type)');
                       //end;

                       case st of
                            0 : begin end; // Null Shape
                            1,11,21 : begin // Point, PointM, PointZ
                                      inc(rcnt);
                                      if (st = 11) then Is3D := true;
                                      // x value
                                      BlockRead(mapfile,dval,8);
                                      NewDat := TImportDataValue.Create;
                                      NewDat.row := rcnt;
                                      NewDat.col := 0;
                                      NewDat.Data := dval;
                                      NewDat.IsEmpty := false;
                                      InDatList.Add(NewDat);
                                      // y value
                                      BlockRead(mapfile,dval,8);
                                      NewDat := TImportDataValue.Create;
                                      NewDat.row := rcnt;
                                      NewDat.col := 1;
                                      NewDat.Data := dval;
                                      NewDat.IsEmpty := false;
                                      InDatList.Add(NewDat);
                                      if (st = 11) then begin
                                         // z value
                                         BlockRead(mapfile,dval,8);
                                         NewDat := TImportDataValue.Create;
                                         NewDat.row := rcnt;
                                         NewDat.col := 2;
                                         NewDat.Data := dval;
                                         NewDat.IsEmpty := false;
                                         InDatList.Add(NewDat);
                                      end;
                                      // associated measure
                                      if (st = 11) or (st = 21) then BlockRead(mapfile,dval,8);
                                end;
                            8,18,28 : begin // Multipoint, Multipoint M, Multipoint Z
                                      if (st = 18) then Is3D := true;
                                      // read x and y boundaries
                                      for i := 1 to 4 do BlockRead(mapfile,dval,8);
                                      BlockRead(mapfile,lval,4); // # points
                                      j := lval;
                                      for i := 1 to j do begin // each point
                                          inc(rcnt);
                                          // x value
                                          BlockRead(mapfile,dval,8);
                                          NewDat := TImportDataValue.Create;
                                          NewDat.row := rcnt;
                                          NewDat.col := 0;
                                          NewDat.Data := dval;
                                          NewDat.IsEmpty := false;
                                          InDatList.Add(NewDat);
                                          // y value
                                          BlockRead(mapfile,dval,8);
                                          NewDat := TImportDataValue.Create;
                                          NewDat.row := rcnt;
                                          NewDat.col := 1;
                                          NewDat.Data := dval;
                                          NewDat.IsEmpty := false;
                                          InDatList.Add(NewDat);
                                      end;
                                      if (st = 18) then begin
                                         BlockRead(mapfile,dval,8); // min Z
                                         BlockRead(mapfile,dval,8); // max Z
                                         for i := 1 to j do begin // Z for each point
                                             // z value
                                             BlockRead(mapfile,dval,8);
                                             NewDat := TImportDataValue.Create;
                                             NewDat.row := rcnt - j + i;
                                             NewDat.col := 2;
                                             NewDat.Data := dval;
                                             NewDat.IsEmpty := false;
                                             InDatList.Add(NewDat);
                                         end;
                                      end;
                                      if (st = 18) or (st = 28) then begin
                                         BlockRead(mapfile,dval,8); // min M
                                         BlockRead(mapfile,dval,8); // max M
                                         for i := 1 to lval do // M for each point
                                             BlockRead(mapfile,dval,8);
                                      end;
                                end;
                            3,13,23,
                            5,15,25 : begin // PolyLine(ZM), Polygon(ZM)
                                      case st of
                                          3,13,23 : IsLine := true;
                                          5,15,25 : IsPoly := true;
                                      end;
                                      //IsLine := true;
                                      if (st = 13) or (st  = 15) then Is3D := true;
                                      // read x and y boundaries
                                      for i := 1 to 4 do begin
                                          BlockRead(mapfile,dval,8);
                                          if testout then begin
                                             inc(bn);
                                             outputaddline(IntTostr(bn)+': '+format('%1.8f',[dval])+ '   (boundary)');
                                          end;
                                      end;
                                      BlockRead(mapfile,lval,4); // # parts
                                      nparts := lval;
                                      if testout then begin
                                         inc(bn);
                                         outputaddline(IntToStr(bn)+': ' +IntToStr(nparts) + ' (# of parts)');
                                      end;
                                      BlockRead(mapfile,lval,4); // total # points
                                      npnts := lval;
                                      if testout then begin
                                         inc(bn);
                                         outputaddline(IntToStr(bn)+': ' +IntToStr(npnts) + ' (# of points)');
                                      end;
                                      // read # points per part
                                      pcnt := nil;
                                      SetLength(pcnt,nparts);
                                      for i := 0 to nparts - 1 do begin
                                          BlockRead(mapfile,lval,4);
                                          pcnt[i] := lval;
                                          if testout then begin
                                             inc(bn);
                                             outputaddline(IntToStr(bn)+': ' +IntToStr(lval) + ' (first points for part '+IntToStr(i)+')');
                                          end;
                                      end;
                                      kk := 1;
                                      // read points
                                      for j := 0 to npnts - 1 do begin
                                          inc(rcnt);
                                          // first point in part
                                          if (kk <= nparts) then
                                             if (j = pcnt[kk-1]) then begin
                                                if testout then begin
                                                   if (kk = nparts) then
                                                      outputaddline(IntToStr(nparts)+' '+IntToStr(npnts)+' '+IntToStr(j)+' '+IntToStr(pcnt[kk-1])+' '+
                                                         IntToStr(kk)+ ' ' + IntToStr(npnts-pcnt[kk-1]))
                                                   else outputaddline(IntToStr(nparts)+' '+IntToStr(npnts)+' '+IntToStr(j)+' '+IntToStr(pcnt[kk-1])+' '+
                                                        IntToStr(kk)+ ' ' +
                                                        InttoStr(pcnt[kk] - pcnt[kk-1]));
                                                end;
                                                NewDat := TImportDataValue.Create;
                                                NewDat.row := rcnt;
                                                NewDat.col := 0;
                                                if (kk = nparts) then NewDat.Data := npnts - pcnt[kk-1]
                                                else NewDat.Data := pcnt[kk] - pcnt[kk-1]; //*****
                                                NewDat.IsEmpty := false;
                                                InDatList.Add(NewDat);
                                                inc(kk);
                                             end;
                                          // x value
                                          BlockRead(mapfile,dval,8);
                                          NewDat := TImportDataValue.Create;
                                          NewDat.row := rcnt;
                                          NewDat.col := 1;
                                          NewDat.Data := dval;
                                          NewDat.IsEmpty := false;
                                          InDatList.Add(NewDat);
                                          if testout then begin
                                             inc(bn);
                                             outputaddline(IntTostr(bn)+': '+format('%1.8f',[dval])+ '   (x value)');
                                          end;

                                          // y value
                                          BlockRead(mapfile,dval,8);
                                          NewDat := TImportDataValue.Create;
                                          NewDat.row := rcnt;
                                          NewDat.col := 2;
                                          NewDat.Data := dval;
                                          NewDat.IsEmpty := false;
                                          InDatList.Add(NewDat);
                                          if testout then begin
                                             inc(bn);
                                             outputaddline(IntTostr(bn)+': '+format('%1.8f',[dval])+ '   (y value)');
                                          end;
                                      end;
                                      if (st = 13) or (st = 15) then begin
                                         BlockRead(mapfile,dval,8); // min Z
                                         BlockRead(mapfile,dval,8); // max Z
                                         for i := 1 to npnts do begin // Z for each point
                                             // z value
                                             BlockRead(mapfile,dval,8);
                                             NewDat := TImportDataValue.Create;
                                             NewDat.row := rcnt - npnts + i;
                                             NewDat.col := 3;
                                             NewDat.Data := dval;
                                             NewDat.IsEmpty := false;
                                             InDatList.Add(NewDat);
                                         end;
                                      end;
                                      if (st <> 3) and (st <> 5) then begin
                                         BlockRead(mapfile,dval,8); // min M
                                         BlockRead(mapfile,dval,8); // max M
                                         for i := 1 to npnts do // M for each point
                                             BlockRead(mapfile,dval,8);
                                      end;
                                      pcnt := nil;
                                end;
                            // all other shape types are invalid at this time
                            else for i := 1 to SwapBytes(RecLen) - 2 do
                                     BlockRead(mapfile,wval,2);
                       end;
                 end;
                 ImportDoRow := false;
                 ImportDoCol := false;
                 if Is3D then ImportND := 3
                 else ImportND := 2;
                 ImportNName := -1;
                 if IsLine then begin
                    ImportDataType := 7;
                    ImportNcnt := 0;
                    ImportXNum := 1;
                    ImportYNum := 2;
                    ImportZNum := 3;
                    if (rcnt < 0) then begin
                        result := false;
                        ReportPASSaGEError('Missing Data','No lines were found in '+trim(ExtractFilename(filen))+'.','',0);
                    end;
                 end else if IsPoly then begin
                    ImportDataType := 8;
                    ImportNcnt := 0;
                    ImportXNum := 1;
                    ImportYNum := 2;
                    ImportZNum := 3;
                    ImportPolyLastP := false;
                    ImportPolyCheckDir := true;
                    if (rcnt < 0) then begin
                        result := false;
                        ReportPASSaGEError('Missing Data','No polygons were found in '+trim(ExtractFilename(filen))+'.','',0);
                    end;
                 end else begin
                     ImportDataType := 1;
                     ImportCrdType := ctXY;
                     ImportXNum := 0;
                     ImportYNum := 1;
                     ImportZNum := 2;
                     if (rcnt < 0) then begin
                        result := false;
                        ReportPASSaGEError('Missing Data','No points were found in '+trim(ExtractFilename(filen))+'.','',0);
                     end;
                 end;
              end else begin
                  result := false;
                  ReportPASSaGEError('Unknown Shape',trim(ExtractFilename(filen)) + ' contains a shape '
                    + 'type ('+IntToStr(ShpType)+') which PASSaGE does not recognize.','',0);
              end;
           end else IsShp := false;
        end else IsShp := false;
        Closefile(mapfile);

        if TestOut then begin
           outputaddblankline;
           for i := 0 to InDatList.Count - 1 do
               with TImportDataValue(InDatList[i]) do begin
                    outputaddline('# ' + IntToStr(i) + ', Row ' + IntToStr(row) +
                      ', Col ' + IntToStr(col) + ', Data ' + format('%1.8f',[Data]));
           end;
        end;

        if not IsShp then begin
            ReportPASSaGEError('Invalid File type',trim(ExtractFilename(filen)) + ' is not a valid '
              + 'Arc/Info shape file.','',0);
            result := false;
        end;
     except on EInOutError do begin
            result := false;
            ReportPASSaGEError('Input/Output Error','PASSaGE encountered an error while attempting to read '
              + trim(ExtractFilename(filen)) + '.','',0);
         end;
     end;
end;  
"""


def test_draw(data):
    fig, faxes = mplpy.subplots(figsize=[6, 3])
    for spine in faxes.spines:
        faxes.spines[spine].set_visible(False)
    for part in data:
        lons = []
        lats = []
        for p in part:
            lons.append(p.lon)
            lats.append(p.lat)
        faxes.plot(lons, lats, color="black", linewidth=0.5)

    mplpy.xlim(-180, 180)
    mplpy.ylim(-90, 90)
    faxes.axes.get_yaxis().set_visible(False)
    faxes.axes.get_xaxis().set_visible(False)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    mplpy.savefig("test_shp_import.png", format="png", dpi=600)
    mplpy.close("all")


if __name__ == "__main__":
    TMB_Initialize.initialize()
    data = import_arcinfo_shp(TMB_Initialize.INIT_DATA.shp_coastline)
    print("# of parts = {}".format(len(data)))
    data.extend(import_arcinfo_shp(TMB_Initialize.INIT_DATA.shp_islands))
    print("# of parts = {}".format(len(data)))
    test_draw(data)
