"""
Taxonomy Monograph Builder
"""

import codecs
import datetime
import random
import os
import shutil
import re
# local dependencies
import TMB_Import
import TMB_Create_Maps
from TMB_Error import report_error
from TMB_Common import name_to_filename
import TMB_Initialize
# external dependencies
import matplotlib.pyplot as mplpy

WEBOUT_PATH = "webout/"
MEDIA_PATH = "media/"
TMP_PATH = "temp/"
MAP_PATH = TMP_PATH + "maps/"

SPECIES_URL = "uca_species.html"
REF_URL = "uca_references.html"
REF_SUM_URL = "uca_refsummary.html"
SYST_URL = "uca_systematics.html"
COMMON_URL = "uca_common_names.html"
PHOTO_URL = "uca_photos.html"
VIDEO_URL = "uca_videos.html"
MAP_URL = "uca_ranges.html"
LIFECYCLE_URL = "uca_lifecycle.html"
TREE_URL = "uca_phylogeny.html"
ART_SCI_URL = "uca_art_science.html"
ART_STAMP_URL = "uca_art_stamps.html"
ART_CRAFT_URL = "uca_art_crafts.html"
MORPH_URL = "uca_morphology.html"
CITE_URL = "citation.html"
NAME_SUM_URL = "name_graphs.html"
# fossilImage = "<img class=\"fossilImg\" src=\"images/fossil.png\" alt=\" (fossil)\" title=\" (fossil)\" />"
FOSSIL_IMAGE = " <span class=\"fossil-img\">&#9760;</span>"
START_YEAR = 1758
CURRENT_YEAR = datetime.date.today().year
VERSION = datetime.datetime.now().strftime("%Y.%m.%d.%H.%M")

AUTHOR_NOPAREN = 0
AUTHOR_PAREN = 1
AUTHOR_NOPCOMMA = 2

# this flag is to hide/display new materials still in progress from the general release
SHOW_NEW = True

randSeed = random.randint(0, 10000)


def remove_html(x):
    """ remove any stray html tags from string before using as title of html documemnt """
    regex = r"<.+?>"
    return re.sub(regex, "", x)
    # x = x.replace("<em>", "")
    # x = x.replace("</em>","")


# -----End input code---- #
def common_header_part1(outfile, title, indexpath):
    """ part 1 of the header for all html """
    outfile.write("<!DOCTYPE HTML>\n")
    outfile.write("<html lang=\"en\">\n")
    outfile.write("  <head>\n")
    outfile.write("    <meta charset=\"utf-8\" />\n")
    outfile.write("    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n")
    outfile.write("    <title>" + remove_html(title) + "</title>\n")
    outfile.write("    <meta name=\"description\" content=\"Fiddler Crabs\" />\n")
    outfile.write("    <link rel=\"icon\" sizes=\"128x128\" href=\"" + indexpath +
                  "favicon128.png\" type=\"image/png\" />\n")
    outfile.write("    <link rel=\"icon\" sizes=\"96x96\" href=\"" + indexpath +
                  "favicon96.png\" type=\"image/png\" />\n")
    outfile.write("    <link rel=\"icon\" sizes=\"72x72\" href=\"" + indexpath +
                  "favicon72.png\" type=\"image/png\" />\n")
    outfile.write("    <link rel=\"icon\" sizes=\"48x48\" href=\"" + indexpath +
                  "favicon48.png\" type=\"image/png\" />\n")
    outfile.write("    <link rel=\"icon\" sizes=\"32x32\" href=\"" + indexpath +
                  "favicon32.png\" type=\"image/png\" />\n")
    outfile.write("    <link rel=\"icon\" sizes=\"24x24\" href=\"" + indexpath +
                  "favicon24.png\" type=\"image/png\" />\n")
    outfile.write("    <link rel=\"icon\" sizes=\"16x16\" href=\"" + indexpath +
                  "favicon16.png\" type=\"image/png\" />\n")
    outfile.write("    <link rel=\"apple-touch-icon-precomposed\" href=\"" + indexpath +
                  "apple-touch-icon-precomposed.png\">\n")
    outfile.write("    <link rel=\"apple-touch-icon-precomposed\" sizes=\"72x72\" "
                  "href=\"" + indexpath + "apple-touch-icon-72x72-precomposed.png\">\n")
    outfile.write("    <link rel=\"apple-touch-icon-precomposed\" sizes=\"114x114\" "
                  "href=\"" + indexpath + "apple-touch-icon-114x114-precomposed.png\">\n")
    outfile.write("    <link rel=\"apple-touch-icon-precomposed\" sizes=\"144x144\" "
                  "href=\"" + indexpath + "apple-touch-icon-144x144-precomposed.png\">\n")
    outfile.write("    <link rel=\"stylesheet\" href=\"http://fonts.googleapis.com/css?family=Merienda+One|"
                  "Lora:400,700,400italic,700italic\" />\n")
    outfile.write("    <link rel=\"stylesheet\" href=\"" + indexpath + "uca_style.css\" />\n")
    outfile.write("    <script src=\"https://use.fontawesome.com/3669ad7c2b.js\"></script>\n")
    # outfile.write("    <link rel=\"stylesheet\" href=\"" + indexpath +
    #               "images/font-awesome/css/font-awesome.min.css\" />\n")
    outfile.write("    <link rel=\"author\" href=\"mailto:msr@asu.edu\" />\n")


def common_header_part2(outfile, indexpath, include_map):
    """ part 2 of the header for all html """
    outfile.write("  </head>\n")
    outfile.write("\n")
    if include_map:
        outfile.write("  <body onload=\"initialize()\">\n")
    else:
        outfile.write("  <body>\n")
    outfile.write("    <div id=\"home\">\n")
    outfile.write("      <a href=\"" + indexpath + "index.html\">Fiddler Crabs</a>\n")
    outfile.write("    </div>\n")


def common_species_html_header(outfile, title, indexpath, species):
    """ for species pages, insert the map scripts """
    common_header_part1(outfile, title, indexpath)
    outfile.write("    <script type=\"text/javascript\"\n")
    outfile.write("      src=\"http://maps.googleapis.com/maps/api/js?"
                  "key=AIzaSyAaITaFdh_own-ULkURNKtyeh2ZR_cpR74&sensor=false\">\n")
    outfile.write("    </script>\n")
    outfile.write("    <script type=\"text/javascript\">\n")
    outfile.write("      function initialize() {\n")
    outfile.write("        var mapOptions = {\n")
    outfile.write("          center: new google.maps.LatLng(0,0),\n")
    outfile.write("          zoom: 1,\n")
    outfile.write("          disableDefaultUI: true,\n")
    outfile.write("          panControl: false,\n")
    outfile.write("          zoomControl: true,\n")
    outfile.write("          mapTypeControl: true,\n")
    outfile.write("          scaleControl: false,\n")
    outfile.write("          streetViewControl: false,\n")
    outfile.write("          overviewMapControl: false,\n")
    outfile.write("          mapTypeId: google.maps.MapTypeId.TERRAIN\n")
    outfile.write("        };\n")
    if species == "":
        # range map
        outfile.write("        var map = new google.maps.Map(document.getElementById(\"map_canvas\"),mapOptions);\n")
        outfile.write("        var ctaLayer = new google.maps.KmlLayer(\"http://www.fiddlercrab.info/maps/uca.kmz\","
                      "{suppressInfoWindows: true});\n")
        # point map
        if SHOW_NEW:
            outfile.write("        var map2 = new google.maps.Map(document.getElementById(\"map2_canvas\"),"
                          "mapOptions);\n")
            outfile.write("        var ctaLayer2 = "
                          "new google.maps.KmlLayer(\"http://www.fiddlercrab.info/maps/uca_points.kmz\","
                          "{suppressInfoWindows: false});\n")
    else:
        # range map
        outfile.write("        var map = new google.maps.Map(document.getElementById(\"map_canvas_sp\"),mapOptions);\n")
        outfile.write("        var ctaLayer = new google.maps.KmlLayer(\"http://www.fiddlercrab.info/maps/u_" +
                      species + ".kmz\",{suppressInfoWindows: true});\n")
        if SHOW_NEW:
            # point map
            outfile.write("        var map2 = new google.maps.Map(document.getElementById(\"map2_canvas_sp\"),"
                          "mapOptions);\n")
            outfile.write("        var ctaLayer2 = new google.maps.KmlLayer(\"http://www.fiddlercrab.info/maps/u_" +
                          species + "_points.kmz\",{suppressInfoWindows: false});\n")
    outfile.write("        ctaLayer.setMap(map);\n")
    if SHOW_NEW:
        outfile.write("        ctaLayer2.setMap(map2);\n")
    outfile.write("      }\n")
    outfile.write("    </script>\n")
    common_header_part2(outfile, indexpath, True)


def common_html_header(outfile, title, indexpath):
    common_header_part1(outfile, title, indexpath)
    common_header_part2(outfile, indexpath, False)


def common_html_footer(outfile, indexpath):
    outfile.write("\n")
    outfile.write("    <footer>\n")
    outfile.write("       <figure id=\"footmap\"><script type=\"text/javascript\" "
                  "src=\"http://jf.revolvermaps.com/p.js\"></script><script type=\"text/javascript\">rm2d_ki101('0',"
                  "'150','75','5f9t1sywiez','ff0000',20);</script><figcaption>Visitors</figcaption></figure>\n")
    outfile.write("       <p id=\"citation\"><a href=\"" + indexpath + CITE_URL +
                  "\"><span class=\"fa fa-pencil\"></span> How to cite this site</a></p>\n")
    outfile.write("       <p id=\"contact\">Questions or comments about the site? Contact "
                  "<a href=\"mailto:msr@asu.edu\"><span class=\"fa fa-envelope-o\"></span> "
                  "Dr. Michael S. Rosenberg</a></p>\n")
    outfile.write("       <p id=\"copyright\">Release: " + VERSION + " &mdash; Copyright &copy; 2003&ndash;" +
                  str(CURRENT_YEAR) + " All Rights Reserved</p>\n")
    outfile.write("    </footer>\n")
    outfile.write("  </body>\n")
    outfile.write("</html>\n")


def start_page_division(outfile, page_class):
    outfile.write("  <div class=\"" + page_class + "\">\n")


def end_page_division(outfile):
    outfile.write("  </div>\n")


def create_blank_index(fname):
    with open(fname, "w") as outfile:
        outfile.write("<!DOCTYPE HTML>\n")
        outfile.write("<html lang=\"en\">\n")
        outfile.write(" <head>\n")
        outfile.write("  <meta charset=\"utf-8\" />\n")
        outfile.write("  <title>n/a</title>\n")
        outfile.write("  <meta name=\"description\" content=\"n/a\" />\n")
        outfile.write(" </head>\n")
        outfile.write(" <body>\n")
        outfile.write(" </body>\n")
        outfile.write("</html>\n")


def rel_link_prefix(do_print, prefix):
    if do_print:
        return "#"
    else:
        return prefix


def abs_link_prefix(do_absolute):
    if do_absolute:
        return "http://www.fiddlercrab.info/"
    else:
        return ""


def format_reference_full(ref, do_print, logfile):
    if ref.cite_key == "<pending>":
        return ref.formatted_html
    else:
        try:
            return ("<a href=\"" + rel_link_prefix(do_print, "references/") + ref.cite_key + ".html\">" +
                    ref.formatted_html + "</a>")
        except LookupError:
            report_error(logfile, "missing label: " + ref.cite_key)


def format_reference_cite(ref, do_print, author_style, logfile):
    if author_style == AUTHOR_PAREN:
        outstr = ref.citation
    elif author_style == AUTHOR_NOPAREN:
        outstr = ref.author() + " " + str(ref.year())
    elif author_style == AUTHOR_NOPCOMMA:
        outstr = ref.author() + ", " + str(ref.year())
    else:
        outstr = ref.citaiton
    if ref.cite_key == "<pending>":
        return outstr
    else:
        try:
            return ("<a href=\"" + rel_link_prefix(do_print, "references/") + ref.cite_key +
                    ".html\">" + outstr + "</a>")
        except LookupError:
            report_error(logfile, "missing label: " + ref.cite_key)


def replace_reference_in_string(instr, refdict, do_print, logfile):
    search_str = r"\[\[(?P<key>.+?),(?P<format>.+?)\]\]"
    # for every citation reference in the string
    for match in re.finditer(search_str, instr):
        # create the new link text
        ref = refdict[match.group("key")]
        if match.group("format") == ".out":
            link_str = format_reference_cite(ref, do_print, AUTHOR_PAREN, logfile)
        elif match.group("format") == ".in":
            link_str = format_reference_cite(ref, do_print, AUTHOR_NOPAREN, logfile)
        else:
            link_str = "<a href=\"" + rel_link_prefix(do_print, "references/") + ref.cite_key + ".html\">" + \
                       match.group("format") + "</a>"
        # replace the cross-reference with the correct text
        instr = re.sub(search_str, link_str, instr, 1)
    return instr


def replace_references(in_list, refdict, do_print, logfile):
    out_list = []
    for line in in_list:
        out_list.append(replace_reference_in_string(line, refdict, do_print, logfile))
    return out_list


def clean_reference_html(ref):
    """ add slightly better formatting to html formatted references """
    # replace hyphens with an n-dash in page ranges
    sstr = r"((?:Pp\. |:)[\d]+)(-)([\d]+)"
    ref = re.sub(sstr, r"\1&ndash;\3", ref)
    # print(re.sub(sstr, r"\1&ndash;\3", ref))

    # replace hyphens with an n-dash in volume ranges
    sstr = r"(\([\d]+)(-)([\d]+\))"
    ref = re.sub(sstr, r"\1&ndash;\3", ref)
    # print(re.sub(sstr, r"\1&ndash;\3", ref))
    return ref


def clean_references(references):
    for ref in references:
        ref.formatted_html = clean_reference_html(ref.formatted_html)


# def chart_style():
#     custom_style = pygal.style.DefaultStyle
#     custom_style.background = "transparent"
#     custom_style.plot_background = "transparent"
#     custom_style.label_font_size = 15
#     custom_style.major_label_font_size = 15
#     return custom_style


def create_pie_chart_file(filename, data):
    datalist = list(data.keys())
    datalist.sort()
    sizes = []
    for d in datalist:
        sizes.append(data[d])
    fig, faxes = mplpy.subplots(figsize=[6, 3])
    # cl = [i for i in range(len(data))]
    # faxes.pie(sizes, labels=datalist, autopct="%1.1f%%")
    # color_list = mplpy.cm.Vega20(cl)
    # my approximation of the pygal color scheme
    color_list = ["salmon", "royalblue", "lightseagreen", "gold", "darkorange", "mediumorchid", "deepskyblue",
                  "lightgreen", "sandybrown", "palevioletred", "lightskyblue", "mediumaquamarine", "lemonchiffon"]
    # tol14rainbow
    # color_list = ["#882E72", "#B178A6", "#D6C1DE", "#1965B0", "#5289C7", "#7BAFDE", "#4EB265", "#90C987", "#CAE0AB",
    #                  "#F7EE55", "#F6C141", "#F1932D", "#E8601C", "#DC050C"]
    # color brewer paired (12)
    # color_list = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6',
    #               '#6a3d9a', '#ffff99', '#b15928']
    # color brewer set3 (12)
    # color_list = ['#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3', '#fdb462', '#b3de69', '#fccde5', '#d9d9d9',
    #               '#bc80bd', '#ccebc5', '#ffed6f']
    faxes.pie(sizes, colors=color_list, startangle=90, counterclock=False)
    faxes.axis("equal")
    faxes.legend(datalist, loc="upper left", frameon=False)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    mplpy.savefig(TMP_PATH + filename)
    mplpy.close()


def create_bar_chart_file(filename, data, minx, maxx, y):
    x_list = [x for x in range(minx, maxx+1)]
    y_list = [d[y] for d in data]
    fig, faxes = mplpy.subplots(figsize=[6.5, 2])
    faxes.bar(x_list, y_list, color="blue", edgecolor="darkblue")
    faxes.spines["right"].set_visible(False)
    faxes.spines["top"].set_visible(False)
    if maxx-minx > 200:
        tick_step = 40
    else:
        tick_step = 20
    mplpy.xticks([i for i in range(minx, maxx + 1, tick_step)])
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    mplpy.savefig(TMP_PATH + filename)
    mplpy.close()


def create_stacked_bar_chart_file(filename, data, minx, maxx, cols):
    # currently assumes only two stacked bars
    x_list = [x for x in range(minx, maxx+1)]
    fig, faxes = mplpy.subplots(figsize=[6.5, 2])
    col_names = [c[0] for c in cols]
    y_list1 = [d[cols[0][1]] for d in data]
    y_list2 = [d[cols[1][1]] for d in data]
    faxes.bar(x_list, y_list1, color="blue", edgecolor="darkblue")
    # faxes.bar(x_list, y_list1, fc=(0,0,1,0.8), edgecolor="darkblue")
    faxes.bar(x_list, y_list2, bottom=y_list1, color="red", edgecolor="darkred")
    faxes.spines["right"].set_visible(False)
    faxes.spines["top"].set_visible(False)
    faxes.legend(col_names, loc="upper left", frameon=False)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    mplpy.savefig(TMP_PATH + filename)
    mplpy.close()


def create_qual_bar_chart_file(filename, label_list, data_dict):
    x_list = [x for x in range(len(label_list))]
    y_list = [data_dict[x] for x in label_list]
    fig, faxes = mplpy.subplots(figsize=[6.5, 3])
    faxes.bar(x_list, y_list, color="blue", edgecolor="darkblue")
    mplpy.xticks(rotation="vertical", style="italic")
    tick_list = x_list[::4]
    tick_labels = label_list[::4]
    faxes.set_xticks(tick_list)
    faxes.set_xticklabels(tick_labels)
    # faxes.set_xticks(x_list)
    # faxes.set_xticklabels(label_list)
    faxes.spines["right"].set_visible(False)
    faxes.spines["top"].set_visible(False)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    mplpy.savefig(TMP_PATH + filename)
    mplpy.close()


def create_line_chart_file(filename, data, minx, maxx, y):
    x_list = [x for x in range(minx, maxx+1)]
    y_list = [d[y] for d in data]
    fig, faxes = mplpy.subplots(figsize=[6.5, 2])
    faxes.plot(x_list, y_list, "blue")
    faxes.spines["right"].set_visible(False)
    faxes.spines["top"].set_visible(False)
    if maxx-minx > 200:
        tick_step = 40
    else:
        tick_step = 20
    mplpy.xticks([i for i in range(minx, maxx + 1, tick_step)])
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    mplpy.savefig(TMP_PATH + filename, format="svg")
    mplpy.close()


def create_chronology_chart_file(filename, miny, maxy, maxcnt, yearly_data):
    y_list = []
    for y in range(miny, maxy + 1):
        if yearly_data[y] != 0:
            y_list.append(yearly_data[y])
        else:
            do_null = True
            if miny < y < maxy:
                if (yearly_data[y + 1] != 0) or (yearly_data[y - 1] != 0):
                    do_null = False
            elif y > miny:
                if yearly_data[y-1] != 0:
                    do_null = False
            elif y < maxy:
                if yearly_data[y+1] != 0:
                    do_null = False
            if do_null:
                y_list.append(None)
            else:
                y_list.append(0)
    y2_list = []
    for x in y_list:
        if x is None:
            y2_list.append(None)
        else:
            y2_list.append(-x)

    x = [y for y in range(miny, maxy+1)]
    fig, faxes = mplpy.subplots(figsize=[6.5, 1.5])
    mplpy.ylim(-maxcnt, maxcnt)
    mplpy.xlim(miny, maxy)
    faxes.fill(x, y_list, "black")
    faxes.fill(x, y2_list, "black")
    for spine in faxes.spines:
        faxes.spines[spine].set_visible(False)
    cur_axes = mplpy.gca()
    cur_axes.axes.get_yaxis().set_visible(False)
    mplpy.xticks([i for i in range(miny, maxy+1, 20)])
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    mplpy.savefig(TMP_PATH + filename)
    mplpy.close()


def write_reference_summary(nrefs, year_data, year_data_1900, cite_count, languages, do_print, outfile):
    if do_print:
        start_page_division(outfile, "")
    else:
        common_header_part1(outfile, "Fiddler Crab Reference Summary", "")
        outfile.write("    <script type=\"text/javascript\" src=\"https://www.google.com/jsapi\"></script>\n")
        outfile.write("    <script type=\"text/javascript\">\n")
        outfile.write("      google.load(\"visualization\", \"1\", {packages:[\"corechart\"]});\n")
        outfile.write("      google.setOnLoadCallback(drawChart);\n")
        outfile.write("      function drawChart() {\n")
        outfile.write("        var data1 = google.visualization.arrayToDataTable([\n")
        outfile.write("          ['Year', 'Cumulative Publications'],\n")
        for y in year_data:
            outfile.write("          ['" + str(y[0]) + "', " + str(y[2]) + "],\n")
        outfile.write("        ]);\n")
        outfile.write("\n")
        outfile.write("        var data2 = google.visualization.arrayToDataTable([\n")
        outfile.write("          ['Year', 'Publications'],\n")
        for y in year_data:
            outfile.write("          ['" + str(y[0]) + "', " + str(y[1]) + "],\n")
        outfile.write("        ]);\n")
        outfile.write("\n")
        """
        outfile.write("        var data3 = google.visualization.arrayToDataTable([\n")
        outfile.write("          ['Year', 'Citations in DB', 'Pending'],\n")
        for y in yearData:
            outfile.write("          ['"+str(y[0])+"', "+str(y[3])+", "+str(y[1]-y[3])+"],\n")
        outfile.write("        ]);\n")
        outfile.write("\n")
        """
        outfile.write("        var data4 = google.visualization.arrayToDataTable([\n")
        outfile.write("          ['Year', 'Publications'],\n")
        for y in year_data_1900:
            outfile.write("          ['" + str(y[0]) + "', " + str(y[1]) + "],\n")
        outfile.write("        ]);\n")
        outfile.write("\n")
        outfile.write("        var data5 = google.visualization.arrayToDataTable([\n")
        outfile.write("          ['Year', 'Citations in DB', 'Pending'],\n")
        for y in year_data_1900:
            outfile.write("          ['" + str(y[0]) + "', " + str(y[2]) + ", " + str(y[1]-y[2]) + "],\n")
        outfile.write("        ]);\n")

        outfile.write("        var data6 = google.visualization.arrayToDataTable([\n")
        outfile.write("          ['Language', 'Count'],\n")
        langlist = list(languages.keys())
        langlist.sort()
        for l in langlist:
            outfile.write("          ['" + l + "', " + str(languages[l]) + "],\n")
        outfile.write("        ]);\n")

        outfile.write("\n")
        outfile.write("        var options1 = {\n")
        outfile.write("          title: \"Cumulative References by Year\", \n")
        outfile.write("          legend: { position: 'none' }\n")
        outfile.write("        };\n")
        outfile.write("\n")
        outfile.write("        var options2 = {\n")
        outfile.write("          title: \"References by Year\", \n")
        outfile.write("          legend: { position: 'none' }\n")
        outfile.write("        };\n")
        outfile.write("\n")
        """
        outfile.write("        var options3 = {\n")
        outfile.write("          title: \"References with Citation Data in Database\", \n")
        outfile.write("          legend: { position: 'bottom' },\n")
        outfile.write("          isStacked: true\n")
        outfile.write("        };\n")
        outfile.write("\n")
        """
        outfile.write("        var options4 = {\n")
        outfile.write("          title: \"References by Year (since 1900)\", \n")
        outfile.write("          legend: { position: 'none' },\n")
        outfile.write("          bar: { groupWidth: '80%' }\n")
        outfile.write("        };\n")
        outfile.write("\n")
        outfile.write("        var options5 = {\n")
        outfile.write("          title: \"References with Citation Data in Database (since 1900; all pre-1900 "
                      "literature is complete)\", \n")
        outfile.write("          legend: { position: 'bottom' },\n")
        outfile.write("          isStacked: true,\n")
        outfile.write("          bar: { groupWidth: '80%' }\n")
        outfile.write("        };\n")
        outfile.write("\n")

        outfile.write("        var options6 = {\n")
        outfile.write("          title: \"Primary Language of References\", \n")
        outfile.write("          titleTextStle: { fontSize: '16' },\n")
        # outfile.write("          isStacked: true,\n")
        # outfile.write("          bar: { groupWidth: '80%' }\n")
        outfile.write("        };\n")
        outfile.write("\n")

        outfile.write("        var chart = new google.visualization.LineChart"
                      "(document.getElementById('chart_div'));\n")
        outfile.write("        chart.draw(data1, options1);\n")
        outfile.write("        var chart2 = new google.visualization.ColumnChart"
                      "(document.getElementById('chart2_div'));\n")
        outfile.write("        chart2.draw(data2, options2);\n")
        # outfile.write("        var chart3 = new google.visualization.ColumnChart
        #               "(document.getElementById('chart3_div'));\n")
        # outfile.write("        chart3.draw(data3, options3);\n")
        outfile.write("        var chart4 = new google.visualization.ColumnChart"
                      "(document.getElementById('chart4_div'));\n")
        outfile.write("        chart4.draw(data4, options4);\n")
        outfile.write("        var chart5 = new google.visualization.ColumnChart"
                      "(document.getElementById('chart5_div'));\n")
        outfile.write("        chart5.draw(data5, options5);\n")
        outfile.write("        var chart6 = new google.visualization.PieChart"
                      "(document.getElementById('chart6_div'));\n")
        outfile.write("        chart6.draw(data6, options6);\n")
        outfile.write("      }\n")
        outfile.write("    </script>\n")
        common_header_part2(outfile, "", False)

    outfile.write("    <header id=\"" + REF_SUM_URL + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Summary of References</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "") + REF_URL +
                      "\"><span class=\"fa fa-list\"></span> Full Reference List</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <p>\n")
    outfile.write("      A summary of the references  in the database (last updated {}).\n".
                  format(datetime.date.isoformat(datetime.date.today())))
    outfile.write("      " + str(cite_count) + " of " + str(nrefs) +
                  " references  have had citation data recorded.\n")
    outfile.write("      See also the <a href=\"" + rel_link_prefix(do_print, "names/") + NAME_SUM_URL +
                  "\">name summary page</a> for information on reference patterns to specific species.\n")
    outfile.write("    </p>\n")
    if do_print:
        # pie chart of languages
        filename = "language_pie.svg"
        create_pie_chart_file(filename, languages)
        outfile.write("    <h3 class=\"nobookmark\">Primary Language of References</h3>\n")
        outfile.write("    <figure class=\"graph\">\n")
        outfile.write("      <img src=\"" + TMP_PATH + filename + "\" class=\"pie_chart\" />\n")
        outfile.write("    </figure>\n")

        # pubs per year bar chart
        miny = CURRENT_YEAR
        maxy = START_YEAR
        for y in year_data:
            miny = min(miny, y[0])
            maxy = max(maxy, y[0])

        filename = "pubs_per_year_bar.svg"
        create_bar_chart_file(filename, year_data, miny, maxy, 1)
        outfile.write("    <h3 class=\"nobookmark\">References by Year</h3>\n")
        outfile.write("    <figure class=\"graph\">\n")
        outfile.write("      <img src=\"" + TMP_PATH + filename + "\" class=\"bar_chart\" />\n")
        outfile.write("    </figure>\n")

        # pubs per year since 1900 bar chart
        filename = "pubs_per_year_1900_bar.svg"
        create_bar_chart_file(filename, year_data_1900, 1900, maxy, 1)
        outfile.write("    <h3 class=\"nobookmark\">References by Year (since 1900)</h3>\n")
        outfile.write("    <figure class=\"graph\">\n")
        outfile.write("      <img src=\"" + TMP_PATH + filename + "\" class=\"bar_chart\" />\n")
        outfile.write("    </figure>\n")

        # citation data in database
        filename = "pubs_per_year_1900_complete_bar.svg"
        tmp_dat = []
        for y in year_data_1900:
            tmp_dat.append([y[2], y[1] - y[2]])
        dat_info = [["Citations in DB", 0], ["Pending", 1]]
        create_stacked_bar_chart_file(filename, tmp_dat, 1900, maxy, dat_info)
        outfile.write("    <h3 class=\"nobookmark\">References with Citation Data in Database (since 1900; all "
                      "pre-1900 literature is complete)</h3>\n")
        outfile.write("    <figure class=\"graph\">\n")
        outfile.write("      <img src=\"" + TMP_PATH + filename + "\" class=\"bar_chart\" />\n")
        outfile.write("    </figure>\n")

        # cumulative publications line chart
        filename = "cumulative_pubs_line.svg"
        create_line_chart_file(filename, year_data, miny, maxy, 2)
        outfile.write("    <h3 class=\"nobookmark\">Cumulative References by Year</h3>\n")
        outfile.write("    <figure class=\"graph\">\n")
        outfile.write("      <img src=\"" + TMP_PATH + filename + "\" class=\"line_chart\" />\n")
        outfile.write("    </figure>\n")

        end_page_division(outfile)
    else:
        outfile.write("    <div id=\"chart6_div\"></div>\n")
        outfile.write("    <div id=\"chart2_div\"></div>\n")
        outfile.write("    <div id=\"chart4_div\"></div>\n")
        # outfile.write("    <div id=\"chart3_div\"></div>\n")
        outfile.write("    <div id=\"chart5_div\"></div>\n")
        outfile.write("    <div id=\"chart_div\"></div>\n")
        common_html_footer(outfile, "")


def write_reference_bibliography(reflist, do_print, outfile, logfile):
    if do_print:
        start_page_division(outfile, "index_page")
    else:
        common_html_header(outfile, "Fiddler Crab Publications", "")
    outfile.write("    <header id=\"" + REF_URL + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Full Reference List</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "") + REF_SUM_URL +
                      "\"><span class=\"fa fa-line-chart\"></span> Reference/Citation Summary</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <p>\n")
    outfile.write("      Following is a fairly comprehensive list of papers, books, and theses that deal or refer "
                  "to fiddler crabs. The list currently contains {:0,} references (last updated {}). Many of these "
                  "papers (particularly the older ones) are primarily "
                  "taxonomic lists.\n".format(len(reflist), datetime.date.isoformat(datetime.date.today())))
    outfile.write("    </p>\n")
    outfile.write("    <p>\n")
    outfile.write("      The references can also be downloaded as "
                  "<a href=\"" + abs_link_prefix(do_print) + "references/Uca_references.enlx\">compressed Endnote</a>, "
                  "<a href=\"" + abs_link_prefix(do_print) + "references/Uca_references_RIS.txt\">RIS (text)</a>, or "
                  "<a href=\"" + abs_link_prefix(do_print) + "references/Uca_references_RIS.xml\">RIS (XML)</a>.\n")
    outfile.write("    </p>\n")
    outfile.write("    <p>\n")
    outfile.write("      Linked references contain information on every name applied to fiddler crabs within "
                  "the publication, including context and the correct name as we currently understand it. These "
                  "data are in the process of being compiled (chronologically for all publications I have access "
                  "to a copy of), with most references still incomplete.\n")
    outfile.write("    </p>\n")
    outfile.write("    <p>\n")
    outfile.write("      In a list of this size, there are bound to be errors, omissions, and mistaken "
                  "inclusions. Please feel free to send me corrections.\n")
    outfile.write("    </p>\n")
    outfile.write("\n")
    outfile.write("    <section class=\"spsection\">\n")
    outfile.write("      <div class=\"reference_list\">\n")
    outfile.write("        <ul>\n")
    for ref in reflist:
        outfile.write("          <li>" + format_reference_full(ref, do_print, logfile) + "</li>\n")
    outfile.write("        </ul>\n")
    outfile.write("      </div>\n")
    outfile.write("    </section>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "")


def create_name_table(citelist):
    name_refs = {}
    for c in citelist:
        nstr = c.name_key
        if "." in nstr:
            nstr = nstr[:nstr.find(".")]
        i = int(nstr)
        if c.cite_key in name_refs:
            namelist = name_refs[c.cite_key]
        else:
            namelist = {}
        namelist[i] = c.name
        if "." in c.name_key:
            namelist[c.name_key] = [c.name, c.application]
        name_refs[c.cite_key] = namelist
    return name_refs


def match_num_ref(x, y):
    if (("." in x) and ("." in y)) or (("." not in x) and ("." not in y)):
        return x == y
    elif "." in x:
        return x[:x.find(".")] == y
    else:
        return y[:y.find(".")] == x


def compute_applied_name_contexts(citelist):
    """ function to gather list of primary contexts referred to by other citation entries  """
    for i, cite in enumerate(citelist):
        if (cite.context == "specimen") or (cite.context == "location"):
            cite.applied_cites = {cite}
        elif cite.context == "citation":
            for j in range(i):  # only look at entries up to the current one
                tmp = citelist[j]
                if (tmp.cite_key == cite.application) and match_num_ref(tmp.name_key, cite.cite_n):
                    if (tmp.context == "specimen") or (tmp.context == "location"):
                        cite.applied_cites |= {tmp}
        if len(cite.applied_cites) == 0:
            cite.applied_cites = None

        # for testing purposes only
        # if cite.applied_cites is None:
        #     print(cite.cite_key, cite.name_key, cite.context, "No application")
        # else:
        #     for c in cite.applied_cites:
        #         print(cite.cite_key, cite.name_key, cite.context, c.cite_key, c.name_key, c.context)
        # input()


def compute_species_from_citation_linking(citelist):
    """ function to update correct species citations through cross-references to earlier works """
    for i, cite in enumerate(citelist):
        if cite.actual == "=":
            crossnames = {}
            for j in range(i):  # only look at entries up to the current one
                tmp = citelist[j]
                if (tmp.cite_key == cite.application) and match_num_ref(tmp.name_key, cite.cite_n):
                    cname = tmp.name
                    if tmp.actual in crossnames:
                        crossnames[tmp.actual] += 1
                    else:
                        crossnames[tmp.actual] = 1
            if len(crossnames) == 0:
                pass
            elif len(crossnames) == 1:
                for tmp in crossnames:
                    cite.actual = tmp
            else:
                mcnt = max(crossnames.values())

                keylist = []
                for key in crossnames:
                    if crossnames[key] == mcnt:
                        keylist.append(key)

                if len(keylist) == 1:
                    cite.actual = keylist[0]
                else:
                    cite_name = cite.name.lower()
                    while cite_name.find(" ") > -1:
                        cite_name = cite_name[cite_name.find(" ")+1:]
                    while cname.find(" ") > -1:
                        cname = cname[cname.find(" ")+1:]

                    if cite_name in keylist:
                        cite.actual = cite_name
                    elif cname in keylist:
                        cite.actual = cname
                    else:
                        cite.actual = keylist[0]

                if cite.name_note == ".":
                    cite.name_note = "in part"
                else:
                    cite.name_note = "in part; " + cite.name_note


def create_species_link(species, status, path, do_print):
    if status == "fossil":
        sc = FOSSIL_IMAGE
    else:
        sc = ""
    return ("<a href=\"" + rel_link_prefix(do_print, path) + "u_" + species + ".html\"><em class=\"species\">Uca " +
            species + "</em>" + sc + "</a>")


def format_name_string(x):
    """ properly emphasize species names, but not non-name signifiers """
    # get rid of [#] when present
    if "{" in x:
        x = x[:x.find("{")-1]
    if "var." in x.lower():
        p = x.lower().find("var.")
        return "<em class=\"species\">" + x[:p] + "</em> " + x[p:p+4] + " <em class=\"species\">" + x[p+4:] + "</em>"
    elif " var " in x.lower():
        p = x.lower().find(" var ")
        return "<em class=\"species\">" + x[:p] + "</em> " + x[p:p+4] + " <em class=\"species\">" + x[p+4:] + "</em>"
    elif "subsp." in x.lower():
        p = x.lower().find("subsp.")
        return "<em class=\"species\">" + x[:p] + "</em> " + x[p:p+6] + " <em class=\"species\">" + x[p+6:] + "</em>"
    elif " forme " in x.lower():
        p = x.lower().find(" forme ")
        return "<em class=\"species\">" + x[:p] + "</em> " + x[p:p+6] + " <em class=\"species\">" + x[p+6:] + "</em>"
    elif " f. " in x.lower():
        p = x.lower().find(" f. ")
        return "<em class=\"species\">" + x[:p] + "</em> " + x[p:p+3] + " <em class=\"species\">" + x[p+3:] + "</em>"
    else:
        return "<em class=\"species\">" + x + "</em>"


def clean_specific_name(x):
    """
    function to extract the specific names from binomials

    this is a list of terms that are not actual species names or specific names that have never been part of
    a fiddler genus
    """
    skip_list = ("sp.",
                 "spp.",
                 "var.",
                 "a",
                 "ete",
                 "panema",
                 "pagurus",
                 "quadratus",
                 "albidus",
                 "vociferans",
                 "(gelasimus)",
                 "raniformis",
                 "nigra",
                 "albicans",
                 "arenarius",
                 "raninus",
                 "serratus",
                 "cordimana",
                 "spec.")

    if " " not in x:
        return ""
    else:
        if "{" in x:
            x = x[:x.find("{")-1]        
        y = x.split(" ")
        x = y[len(y)-1].lower()
        if x in skip_list or ("gruppe" in x):
            return ""
        else:
            return x.lower()


def output_name_table(is_name, outfile, itemlist, uniquelist, notecnt, comcnt, refdict, name_table, logfile, do_print):
    first_name = True
    ncols = 5
    if notecnt > 0:
        ncols += 1
    if comcnt > 0:
        ncols += 1

    for n in itemlist:
        outfile.write("    <tr>\n")
        if is_name:
            nref = n.cite_key
        else:
            nref = n.name
        if nref in uniquelist:
            if first_name:
                first_name = False
            else:
                outfile.write("      <td class=\"rowspacer\" colspan=\"" + str(ncols) + "\">&nbsp;</td>\n")
                outfile.write("    </tr>\n")
                outfile.write("    <tr>\n")

            if nref == ".":
                outfile.write("      <td>&nbsp;</td>\n")
            elif is_name:  # output citation
                crossref = refdict[nref]
                outfile.write("      <td><a href=\"" + rel_link_prefix(do_print, "../references/") +
                              crossref.cite_key + ".html\">" + crossref.citation + "</a></td>\n")
            else:  # output species name
                outfile.write("      <td><a href=\"" + rel_link_prefix(do_print, "../names/") +
                              name_to_filename(nref) + ".html\">" + format_name_string(nref) + "</a></td>\n")

            # common names
            if comcnt > 0:
                if n.common == ".":
                    outfile.write("      <td>&nbsp;</td>\n")
                else:
                    outfile.write("      <td>" + n.common + "</td>\n")
            outfile.write("      <td>" + n.where + "</td>\n")
            uniquelist -= {nref}
        else:
            outfile.write("      <td>&nbsp;</td>\n")
            if comcnt > 0:
                outfile.write("      <td>&nbsp;</td>\n")
            outfile.write("      <td>&nbsp;</td>\n")
        # applies to...
        if n.context == "location":
            outfile.write("      <td><span class=\"fa fa-map-marker\"></span> location: " + n.application + "</td>\n")
        elif n.context == "citation":
            if n.application in refdict:
                crossref = refdict[n.application]
                if n.application in name_table:
                    nstr = n.cite_n
                    if nstr == "0":
                        outfile.write("      <td><span class=\"fa fa-pencil-square-o\"></span> citation: "
                                      "<a href=\"" + rel_link_prefix(do_print, "../references/") + crossref.cite_key +
                                      ".html\">" + crossref.citation + "</a></td>\n")
                    else:
                        if "." in nstr:
                            try:
                                extraref = " [" + name_table[n.application][nstr][1] + "]"
                                refname = name_table[n.application][nstr][0]
                            except LookupError:
                                if is_name:  # only print errors on one pass
                                    report_error(logfile, "Error in citation: " +
                                                 n.cite_key + " cites" + nstr +
                                                 " in " + n.application)
                                extraref = ""
                                refname = ""
                        else:
                            extraref = ""                                
                            try:
                                refname = name_table[n.application][int(nstr)]
                            except ValueError:
                                report_error(logfile, "Citation " + n.cite_key + " tried to cite " + n.application +
                                             " #" + nstr)
                                refname = ""
                        outfile.write("      <td><span class=\"fa fa-pencil-square-o\"></span> citation: "
                                      "<a href=\"" + rel_link_prefix(do_print, "../references/") + crossref.cite_key +
                                      ".html\">" + crossref.citation + "</a> → " + format_name_string(refname) +
                                      extraref + "</td>\n")
                else:
                    outfile.write("      <td><span class=\"fa fa-pencil-square-o\"></span> citation: "
                                  "<a href=\"" + rel_link_prefix(do_print, "../references/") + crossref.cite_key +
                                  ".html\">" + crossref.citation + "</a></td>\n")
            else:
                outfile.write("      <td><span class=\"fa fa-pencil-square-o\"></span> citation: " + n.application +
                              "</td>\n")
                if is_name and not do_print:  # only print on one pass
                    report_error(logfile, "Citation not in DB: " +
                                 n.cite_key + " cites " + n.application)
        elif n.context == "specimen":
            if n.application == "?":
                outfile.write("      <td><span class=\"fa fa-flask\"></span> specimen: unknown locality</td>\n")
            else:
                outfile.write("      <td><span class=\"fa fa-flask\"></span> specimen: " + n.application +
                              "</td>\n")
        elif n.context == "unpublished":
            outfile.write("      <td>unpublished name <em class=\"species\">" +
                          n.application + "</em></td>\n")
        else:  # "n/a"
            outfile.write("      <td>&nbsp;</td>\n")

        # accepted species name                                
        if n.actual == "?":
            outfile.write("      <td>?</td>\n")
        elif n.actual in {".", "="}:
            outfile.write("      <td>TBD</td>\n")
        elif n.actual == "n/a":
            outfile.write("      <td>&nbsp;</td>\n")                    
        elif n.actual[0] == ">":
            outfile.write("      <td><em class=\"species\">" + n.actual[1:] +
                          "</em></td>\n")
        else:
            outfile.write("      <td><a href=\"" + rel_link_prefix(do_print, "../") + "u_" + n.actual +
                          ".html\"><em class=\"species\">Uca " + n.actual +
                          "</em></a></td>\n")

        # source of accepted species
        if n.source == ".":  # currently not listed
            outfile.write("      <td>&nbsp;</td>\n")                   
        elif n.source == "<":  # original name retained
            outfile.write("      <td><span class=\"fa fa-arrow-left\"></span> Original</td>\n")
        elif n.source == "=":  # automatically computer
            outfile.write("      <td><span class=\"fa fa-gears\"></span> Computed</td>\n")
        else:
            if ";" in n.source:
                source_list = n.source.split(";")
            else:
                source_list = [n.source]
            source_strs = []
            for source in source_list:
                if source in refdict:  # another reference
                    crossref = refdict[source]
                    source_strs.append("<a href=\"" + rel_link_prefix(do_print, "../references/") +
                                       crossref.cite_key + ".html\">" + crossref.citation + "</a>")
                else:  # should start with a >
                    tmpsource = source[1:]
                    tmpsource = tmpsource.replace("MSR:", "")
                    tmpsource = tmpsource.replace("/", "/<br />")
                    tmpsource = tmpsource.replace("geography", "<span class=\"fa fa-map-o\"></span> Geography")
                    tmpsource = tmpsource.replace("synonymy", "<span class=\"fa fa-exchange\"></span> Synonymy")
                    source_strs.append(tmpsource)
            outfile.write("      <td>" + ", ".join(source_strs) + "</td>\n")

        # notes
        if notecnt > 0:
            if n.name_note == ".":
                outfile.write("      <td>&nbsp;</td>\n")
            else:
                outfile.write("      <td>" + n.name_note + "</td>\n")
        outfile.write("    </tr>\n")
    outfile.write("    </table>\n")


def write_reference_page(outfile, do_print, ref, citelist, refdict, name_table, logfile):
    if do_print:
        start_page_division(outfile, "ref_page")
    else:
        common_html_header(outfile, ref.citation, "../")
    outfile.write("    <header id=\"" + ref.cite_key + ".html\">\n")
    if not do_print:
        outfile.write("      <h1 class=\"nobookmark\">" + ref.citation + "</h1>\n")
    outfile.write("      <h2 class=\"nobookmark\">" + ref.formatted_html + "</h2>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"../" + REF_URL +
                      "\"><span class=\"fa fa-list\"></span> Full Reference List</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    # find names for this citation
    names = []
    cites_to = []
    for c in citelist:
        if c.cite_key == ref.cite_key:
            names.append(c)
        if c.application == ref.cite_key:
            cites_to.append(c)
    started_note = False
    comcnt = 0
    notecnt = 0
    uniquenames = set()
    for n in names:
        if n.general_note != ".":
            if not started_note:
                outfile.write("    <p>\n")
                started_note = True
            outfile.write("      " + n.general_note + "\n")
        if n.common != ".":
            comcnt += 1
        if n.name_note != ".":
            notecnt += 1
        uniquenames |= {n.name}
    if started_note:
        outfile.write("    </p>\n")

    # write name table
    outfile.write("    <h3 class=\"nobookmark\">Names Appearing in this Publication</h3>\n")
    if len(names) > 0:
        outfile.write("    <table class=\"citetable\">\n")
        outfile.write("      <tr>\n")
        outfile.write("        <th class=\"name_col\">Name Used</th>\n")
        if comcnt > 0:
            outfile.write("        <th class=\"common_col\">Common Name(s)</th>\n")
        outfile.write("        <th class=\"where_col\">Where</th>\n")
        outfile.write("        <th class=\"applied_col\">Applied to...</th>\n")
        outfile.write("        <th class=\"accepted_col\">Accepted Name</th>\n")
        outfile.write("        <th class=\"source_col\">Source of Accepted</th>\n")
        if notecnt > 0:
            outfile.write("        <th class=\"notes_col\">Note(s)</th>\n")
        outfile.write("      </tr>\n")
        names.sort()
        output_name_table(False, outfile, names, uniquenames, notecnt, comcnt, refdict, name_table,
                          logfile, do_print)
    else:
        outfile.write("    <p>\n")
        outfile.write("      Data not yet available.\n")
        outfile.write("    </p>\n")

    if len(cites_to) > 0:
        outfile.write("    <h3 class=\"nobookmark\">This Publication is Cited By</h3>\n")
        outfile.write("    <p>\n")
        cs = set()
        for c in cites_to:
            if c.cite_key in refdict:
                crossref = refdict[c.cite_key]
                cs |= {"<a href=\"" + rel_link_prefix(do_print, "") + crossref.cite_key +
                       ".html\">" + crossref.citation + "</a>"}
            else:
                cs |= {c.cite_key}
        cl = []
        for x in cs:
            cl.append(x)
        cl.sort()
        outfile.write("     " + "\n, ".join(cl) + "\n")
        outfile.write("    </p>\n")

    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "../")


def write_reference_pages(reflist, refdict, citelist, do_print, printfile, logfile, name_table):
    """ control function to loop through creating a page for every reference """
    # name_table = create_name_table(citelist)
    # update_cite_list(citelist)  # moving this outside of write loop so as not to have it run twice
    for ref in reflist:
        if ref.cite_key != "<pending>":
            if do_print:
                write_reference_page(printfile, do_print, ref, citelist, refdict, name_table, logfile)
            else:
                with codecs.open(WEBOUT_PATH + "references/" + ref.cite_key + ".html", "w", "utf-8") as outfile:
                    write_reference_page(outfile, do_print, ref, citelist, refdict, name_table, logfile)


def clean_name(x):
    """ function to clean up names so that variation such as punctuation does not prevent a match """
    x = x.replace(", var.", " var.")
    if "{" in x:
        x = x[:x.find("{")-1]
    return x


def calculate_binomial_yearly_cnts(name, refdict, citelist):
    miny = START_YEAR
    maxy = CURRENT_YEAR
    # find citations for this name
    cites = []
    for c in citelist:
        clean = clean_name(c.name)
        if clean.lower() == name.lower():
            cites.append(c)
    uniquecites = set()
    for c in cites:
        uniquecites |= {c.cite_key}
    name_by_year = {y: 0 for y in range(miny, maxy+1)}
    for c in uniquecites:
        y = refdict[c].year()
        if y is not None:
            if miny <= y <= maxy:
                name_by_year[y] += 1
    return name_by_year


def write_binomial_name_page(name, namefile, name_by_year, refdict, citelist, name_table, species_name, logfile,
                             outfile, do_print):
    """ create a page listing all citations using a specific binomial """
    # find citations for this name
    cites = []
    for c in citelist:
        clean = clean_name(c.name)
        if clean.lower() == name.lower():
            cites.append(c)
    comcnt = 0
    notecnt = 0
    uniquecites = set()
    for c in cites:
        if c.common != ".":
            comcnt += 1
        if c.name_note != ".":
            notecnt += 1
        uniquecites |= {c.cite_key}

    miny = START_YEAR
    maxy = CURRENT_YEAR
    maxcnt = max(name_by_year.values())
    image_name = ""
    if do_print:
        start_page_division(outfile, "name_page")
        if maxcnt > 0:
            image_name = name_to_filename(name) + "_chronology.svg"
            create_chronology_chart_file(image_name,  miny, maxy, maxcnt, name_by_year)
    else:
        common_header_part1(outfile, name, "../")
        if maxcnt > 0:
            outfile.write("    <script type=\"text/javascript\" src=\"https://www.google.com/jsapi\"></script>\n")
            outfile.write("    <script type=\"text/javascript\">\n")
            outfile.write("      google.load(\"visualization\", \"1\", {packages:[\"corechart\"]});\n")
            outfile.write("      google.setOnLoadCallback(drawChart);\n")
            outfile.write("      function drawChart() {\n")
            image_name = 0
            setup_chronology_chart(image_name, miny, maxy, maxcnt, name_by_year, outfile)
            outfile.write("      }\n")
            outfile.write("    </script>\n")
        common_header_part2(outfile, "", False)

    outfile.write("    <header id=\"" + namefile + ".html\" class=\"tabular_page\">\n")
    outfile.write("      <h1 class=\"nobookmark\">" + format_name_string(name) + "</h1>\n")
    outfile.write("      <nav>\n")
    outfile.write("        <ul>\n")
    if species_name != "":
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "") + "sn_" + species_name +
                      ".html\"><span class=\"fa fa-window-minimize\"></span> " + format_name_string(species_name) +
                      "</a></li>\n")
        if not do_print:
            outfile.write("          <li><a href=\"index.html\"><span class=\"fa fa-list\"></span> Full Name "
                          "Index</a></li>\n")
    outfile.write("        </ul>\n")
    outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")

    if SHOW_NEW:
        if maxcnt > 0:
            write_chronology_chart_div(image_name, outfile, None, "Number of Uses of Name per Year", False, do_print,
                                       False)
            outfile.write("\n")

    # write name table
    outfile.write("    <h3 class=\"nobookmark\">Publications Using this Name</h3>\n")
    outfile.write("    <table class=\"citetable\">\n")
    outfile.write("      <tr>\n")
    outfile.write("        <th class=\"citation_col\">Citation</th>\n")
    if comcnt > 0:
        outfile.write("        <th class=\"common_col\">Common Name(s)</th>\n")
    outfile.write("        <th class=\"where_col\">Where</th>\n")
    outfile.write("        <th class=\"applied_col\">Applied to...</th>\n")
    outfile.write("        <th class=\"accepted_col\">Accepted Name</th>\n")
    outfile.write("        <th class=\"source_col\">Source of Accepted</th>\n")
    if notecnt > 0:
        outfile.write("        <th class=\"notes_col\">Note(s)</th>\n")
    outfile.write("      </tr>\n")
    output_name_table(True, outfile, cites, uniquecites, notecnt, comcnt, refdict, name_table, logfile, do_print)
    outfile.write("    <p>\n")
    outfile.write("    </p>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "../")


def calculate_specific_name_yearly_cnts(specific_name, binomial_names, binomial_cnts):
    miny = START_YEAR
    maxy = CURRENT_YEAR
    year_cnts = {y: 0 for y in range(miny, maxy+1)}
    for n in binomial_names:
        sp_name = clean_specific_name(n)
        tmpnamelist = specific_name.variations.split(";")
        if (sp_name != "") and (sp_name in tmpnamelist):
            cnts = binomial_cnts[clean_name(n)]
            for y in cnts:
                if miny <= y <= maxy:
                    year_cnts[y] += cnts[y]
    return year_cnts


def calculate_specific_locations(specific_name, binomial_names, binomial_locations):
    locs = {}
    for n in binomial_names:
        sp_name = clean_specific_name(n)
        tmpnamelist = specific_name.variations.split(";")
        if (sp_name != "") and (sp_name in tmpnamelist):
            locs |= binomial_locations[clean_name(n)]
    return locs


def write_specific_name_page(specific_name, binomial_names, refdict, binomial_cnts, logfile, outfile, do_print):
    """ create a page with the history of a specific name """
    miny = START_YEAR
    maxy = CURRENT_YEAR
    byears = {y: 0 for y in range(miny, maxy + 1)}
    for n in binomial_names:
        sp_name = clean_specific_name(n)
        tmpnamelist = specific_name.variations.split(";")
        if (sp_name != "") and (sp_name in tmpnamelist):
            cnts = binomial_cnts[clean_name(n)]
            for y in cnts:
                if miny <= y <= maxy:
                    byears[y] += cnts[y]
    maxcnt = max(byears.values())
    image_name = ""
    if do_print:
        start_page_division(outfile, "base_page")
        if maxcnt > 0:
            image_name = name_to_filename(specific_name.name) + "_chronology.svg"
            create_chronology_chart_file(image_name,  miny, maxy, maxcnt, byears)
    else:
        common_header_part1(outfile, specific_name.name, "../")
        if maxcnt > 0:
            outfile.write("    <script type=\"text/javascript\" src=\"https://www.google.com/jsapi\"></script>\n")
            outfile.write("    <script type=\"text/javascript\">\n")
            outfile.write("      google.load(\"visualization\", \"1\", {packages:[\"corechart\"]});\n")
            outfile.write("      google.setOnLoadCallback(drawChart);\n")
            outfile.write("      function drawChart() {\n")
            image_name = 0
            setup_chronology_chart(image_name, miny, maxy, maxcnt, byears, outfile)
            outfile.write("      }\n")
            outfile.write("    </script>\n")
        common_header_part2(outfile, "", False)

    outfile.write("    <header id=\"sn_" + specific_name.name + ".html\" class=\"tabular_page\">\n")
    outfile.write("      <h1 class=\"nobookmark\">" + format_name_string(specific_name.name) + "</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"index.html\"><span class=\"fa fa-list\"></span> "
                      "Full Name Index</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <section class=\"topspsection\">\n")
    outfile.write("      <h3 class=\"nobookmark\">History</h3>\n")
    outfile.write("      <dl>\n")
    if specific_name.synonym != ".":
        if specific_name.synonym in specific_name.variations:
            outfile.write("        <dt>Species</dt>\n")
        else:
            outfile.write("        <dt>Primary Senior Synonym</dt>\n")
        if specific_name.synonym == "?":
            outfile.write("          <dd>Unknown</dd>\n")
        elif specific_name.synonym.startswith(">"):
            outfile.write("          <dd><em class=\"species\">" +
                          specific_name.synonym[1:] + "</em></dd>\n")
        else:
            outfile.write("          <dd>" + create_species_link(specific_name.synonym, "", "../", do_print) +
                          "</dd>\n")
    outfile.write("        <dt>Original Usage</dt>\n")
    outfile.write("          <dd>" + format_name_string(specific_name.original_binomial) + "</dd>\n")
    outfile.write("        <dt>Original Source with Priority</dt>\n")
    refname = ""
    if specific_name.priority_source != ".":
        try:
            ref = refdict[specific_name.priority_source]
            refname = ref.formatted_html
        except LookupError:
            # print(name.priority_source)
            report_error(logfile, specific_name.priority_source)
    else:
        refname = "unknown"
    outfile.write("          <dd>" + refname + "</dd>\n")
    outfile.write("        <dt>Derivation</dt>\n")
    if specific_name.meaning == ".":
        outfile.write("          <dd>unknown</dd>\n")
    else:
        outfile.write("          <dd>" + specific_name.meaning + "</dd>\n")
    outfile.write("      </dl>\n")
    outfile.write("    </section>\n")
    outfile.write("\n")

    if SHOW_NEW:
        if maxcnt > 0:
            write_chronology_chart_div(image_name, outfile, None, "Number of Uses of Name per Year", False, do_print,
                                       False)
            outfile.write("\n")

    if specific_name.notes != ".":
        outfile.write("    <section class=\"spsection\" style=\"clear: both\">\n")
        outfile.write("      <h3 class=\"nobookmark\">Notes/Comments</h3>\n")
        outfile.write("      <p>\n")
        outfile.write("        " + specific_name.notes + "\n")
        outfile.write("      </p>\n")
        outfile.write("    </section>\n")
    outfile.write("    <section class=\"spsection\" style=\"clear: both\">\n")
    outfile.write("      <h3 class=\"nobookmark\">Binomials Using this Specific Name</h3>\n")
    outfile.write("      <ul>\n")
    for n in binomial_names:
        x = clean_specific_name(n)
        tmpnamelist = specific_name.variations.split(";")
        if (x != "") and (x in tmpnamelist):
            namefile = name_to_filename(n)
            outfile.write("      <li><a href=\"" + rel_link_prefix(do_print, "") + namefile + ".html\">" +
                          format_name_string(n) + "</a></li>\n")
    outfile.write("      </ul>\n")
    outfile.write("    </section>\n")

    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "../")


def setup_chronology_chart(n, miny, maxy, maxcnt, yearly_data, outfile):
    nstr = str(n)
    outfile.write("        var data" + nstr + " = google.visualization.arrayToDataTable([\n")
    outfile.write("          ['Year', 'Number of Uses', 'Number of Uses'],\n")
    for y in range(miny, maxy + 1):
        if yearly_data[y] != 0:
            outfile.write("          ['" + str(y) + "', " + str(yearly_data[y]) + ", " + str(yearly_data[y]) + "],\n")
        else:
            do_null = True
            if miny < y < maxy:
                if (yearly_data[y + 1] != 0) or (yearly_data[y - 1] != 0):
                    do_null = False
            elif y > miny:
                if yearly_data[y-1] != 0:
                    do_null = False
            elif y < maxy:
                if yearly_data[y+1] != 0:
                    do_null = False
            if do_null:
                outfile.write("          ['" + str(y) + "', null, null],\n")
            else:
                outfile.write("          ['" + str(y) + "', 0, 0],\n")
    outfile.write("        ]);\n")
    outfile.write("\n")
    outfile.write("        var options" + nstr + " = {\n")
    outfile.write("          legend: { position: 'none' },\n")
    outfile.write("          lineWidth: 1,\n")
    outfile.write("          areaOpacity: 1.0,\n")
    outfile.write("          series: { 0: { color: 'black'},\n")
    outfile.write("                    1: { color: 'black', targetAxisIndex: 1}\n")
    outfile.write("                  },\n")
    outfile.write("          vAxes: { 1: { direction: -1}},\n")
    outfile.write("          vAxis: { gridlines: {count: 0},\n")
    outfile.write("                   baselineColor: 'none',\n")
    outfile.write("                   minValue: -" + str(maxcnt) + ",\n")
    outfile.write("                   maxValue: " + str(maxcnt) + "\n")
    outfile.write("                 },\n")
    outfile.write("          hAxis: { showTextEvery: 20},\n")
    outfile.write("          chartArea: { left:50,\n")
    outfile.write("                       top:10,\n")
    outfile.write("                       width:\"95%\",\n")
    outfile.write("                       height:\"80%\"\n")
    outfile.write("                 }\n")
    outfile.write("        };\n")
    outfile.write("\n")
    outfile.write("        var chart" + nstr + " = new google.visualization.AreaChart(document.getElementById"
                                               "('chronchart" + nstr + "_div'));\n")
    outfile.write("        chart" + nstr + ".draw(data" + nstr + ", options" + nstr + ");\n")
    outfile.write("\n")


def write_chronology_chart_div(n, outfile, linkfile, title, is_species, do_print, do_multi):
    # n can be either the file name (print) or the chart # on the page (web)
    if is_species:
        if linkfile is not None:
            fn = rel_link_prefix(do_print, "") + name_to_filename(linkfile) + ".html"
            title_str = "<a href=\"" + fn + "\"><em class=\"species\">" + title + "</em></a>"
        else:
            title_str = "<em class=\"species\">" + title + "</em>"
    else:
        title_str = title
    outfile.write("    <div class=\"chron_div\">\n")
    if do_multi:
        position = "left"
    else:
        position = "top"
    outfile.write("      <div class=\"chronchart_title_" + position + "\">" + title_str + "</div>\n")
    if do_print:
        outfile.write("      <div class=\"chronchart_" + position + "\"><img src=\"" + TMP_PATH + n +
                      "\" alt=\"chronology chart\" /></div>\n")
    else:
        outfile.write("      <div id=\"chronchart" + str(n) + "_div\" class=\"chronchart_" + position + "\"></div>\n")
    outfile.write("    </div>\n")


def create_synonym_chronology(species, binomial_synlist, binomial_name_counts, specific_synlist, specific_name_counts,
                              do_print, outfile):
    """ create a page with the chronological history of a specific name and its synonyms """
    miny = START_YEAR
    maxy = CURRENT_YEAR
    # --all totals and specific names--
    # find max count across all synonyms
    name_cnts = []
    total_cnts = {y: 0 for y in range(miny, maxy + 1)}
    for name in specific_synlist:
        cnts = specific_name_counts[name]
        for y in cnts:
            total_cnts[y] += cnts[y]
        total = sum(cnts.values())
        name_cnts.append([total, name])
    maxcnt = max(total_cnts.values())
    name_cnts.sort(reverse=True)
    # put accepted name first, followed by the rest in decreasing frequency
    sp_order = [species]
    for x in name_cnts:
        if x[1] != species:
            sp_order.append(x[1])

    # --binomials--
    # find max count across all binomial synonyms
    bmaxcnt = 0
    name_cnts = []
    for name in binomial_synlist:
        cnts = binomial_name_counts[clean_name(name)]
        tmpmax = max(cnts.values())
        bmaxcnt = max(bmaxcnt, tmpmax)
        total = sum(cnts.values())
        name_cnts.append([total, name])
    name_cnts.sort(reverse=True)
    # put accepted name first, followed by the rest in decreasing frequency
    if ("Uca " + species) in binomial_synlist:
        bi_order = ["Uca " + species]
    else:
        bi_order = []
    for x in name_cnts:
        if x[1] != "Uca " + species:
            bi_order.append(x[1])

    if do_print:
        start_page_division(outfile, "synonym_page")
        image_name = "synonym_" + name_to_filename(species) + "_total_chronology.svg"
        create_chronology_chart_file(image_name,  miny, maxy, maxcnt, total_cnts)
        for name in sp_order:
            image_name = "synonym_" + name_to_filename(name) + "_chronology.svg"
            create_chronology_chart_file(image_name, miny, maxy, maxcnt, specific_name_counts[name])
        for name in bi_order:
            image_name = "synonym_" + name_to_filename(name) + "_chronology.svg"
            create_chronology_chart_file(image_name, miny, maxy, maxcnt, binomial_name_counts[clean_name(name)])
    else:
        common_header_part1(outfile, species, "../")
        outfile.write("    <script type=\"text/javascript\" src=\"https://www.google.com/jsapi\"></script>\n")
        outfile.write("    <script type=\"text/javascript\">\n")
        outfile.write("      google.load(\"visualization\", \"1\", {packages:[\"corechart\"]});\n")
        outfile.write("      google.setOnLoadCallback(drawChart);\n")
        outfile.write("      function drawChart() {\n")
        image_name = 0
        setup_chronology_chart(image_name, miny, maxy, maxcnt, total_cnts, outfile)
        adjust = 1
        for i, name in enumerate(sp_order):
            setup_chronology_chart(i + adjust, miny, maxy, maxcnt, specific_name_counts[name], outfile)
        adjust += len(specific_synlist)
        for i, name in enumerate(bi_order):
            setup_chronology_chart(i + adjust, miny, maxy, bmaxcnt, binomial_name_counts[clean_name(name)], outfile)
        outfile.write("      }\n")
        outfile.write("    </script>\n")
        common_header_part2(outfile, "", False)

    outfile.write("    <header>\n")
    outfile.write("      <h1 class=\"nobookmark\">Synonym Chronology of " + format_name_string("Uca " + species) +
                  "</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "../") + "u_" + species +
                      ".html\"><span class=\"fa fa-info-circle\"></span> Species page</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    if do_print:
        image_name = "synonym_" + name_to_filename(species) + "_total_chronology.svg"
    else:
        image_name = 0
    write_chronology_chart_div(image_name, outfile, None, "All Names", False, do_print, True)
    adjust = 1
    outfile.write("    <p style=\"clear: both\">Accepted name is listed first, followed by synonyms in decreasing "
                  "order of use.</p>\n")
    outfile.write("    <h2 class=\"nobookmark\">Specific Synonyms</h2>\n")
    for i, name in enumerate(sp_order):
        if do_print:
            image_name = "synonym_" + name_to_filename(name) + "_chronology.svg"
        else:
            image_name = i + adjust
        write_chronology_chart_div(image_name, outfile, "sn_"+name, name, True, do_print, True)
    adjust += len(specific_synlist)
    outfile.write("    <h2  class=\"nobookmark\" style=\"clear: both\">Binomial Synonyms</h2>\n")
    for i, name in enumerate(bi_order):
        if do_print:
            image_name = "synonym_" + name_to_filename(name) + "_chronology.svg"
        else:
            image_name = i + adjust
        write_chronology_chart_div(image_name, outfile, name, name, True, do_print, True)

    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "../")


def match_specific_name(name, specific_names):
    """ match the specific name from a binomial to the list of accepted specific names """
    c = clean_specific_name(name)
    if c == "":
        return c
    else:
        y = ""
        for x in specific_names:
            matchlist = x.variations.split(";")
            if c in matchlist:
                y = x.name
        return y


def create_name_summary(binomial_year_cnts, specific_year_cnts, species_refs, do_print, outfile):
    miny = START_YEAR
    maxy = CURRENT_YEAR
    byears = []
    c = 0
    for y in range(miny, maxy+1):
        if y in binomial_year_cnts:
            c = c + binomial_year_cnts[y]
            byears.append([y, binomial_year_cnts[y], c])
        else:
            byears.append([y, 0, c])

    miny = 1758
    maxy = CURRENT_YEAR
    syears = []
    c = 0
    for y in range(miny, maxy+1):
        if y in specific_year_cnts:
            c = c + specific_year_cnts[y]
            syears.append([y, specific_year_cnts[y], c])
        else:
            syears.append([y, 0, c])
    tmpslist = list(species_refs.keys())
    tmpslist.sort()
    ref_cnts = {s: len(species_refs[s]) for s in tmpslist}

    if do_print:
        start_page_division(outfile, "base_page")
    else:
        common_header_part1(outfile, "Fiddler Crab Name Summary", "../")
        outfile.write("    <script type=\"text/javascript\" src=\"https://www.google.com/jsapi\"></script>\n")
        outfile.write("    <script type=\"text/javascript\">\n")
        outfile.write("      google.load(\"visualization\", \"1\", {packages:[\"corechart\"]});\n")
        outfile.write("      google.setOnLoadCallback(drawChart);\n")
        outfile.write("      function drawChart() {\n")
        outfile.write("        var data1 = google.visualization.arrayToDataTable([\n")
        outfile.write("          ['Year', 'Cumulative Unique Binomial/Compound Names'],\n")
        for y in byears:
            outfile.write("          ['" + str(y[0]) + "', " + str(y[2]) + "],\n")
        outfile.write("        ]);\n")
        outfile.write("\n")
        outfile.write("        var data2 = google.visualization.arrayToDataTable([\n")
        outfile.write("          ['Year', 'New Unique Binomial/Compound Names'],\n")
        for y in byears:
            outfile.write("          ['" + str(y[0]) + "', " + str(y[1]) + "],\n")
        outfile.write("        ]);\n")
        outfile.write("\n")
        outfile.write("        var data3 = google.visualization.arrayToDataTable([\n")
        outfile.write("          ['Year', 'Cumulative Unique Specific Names'],\n")
        for y in syears:
            outfile.write("          ['" + str(y[0]) + "', " + str(y[2]) + "],\n")
        outfile.write("        ]);\n")
        outfile.write("\n")
        outfile.write("        var data4 = google.visualization.arrayToDataTable([\n")
        outfile.write("          ['Year', 'New Unique Specific Names'],\n")
        for y in syears:
            outfile.write("          ['" + str(y[0]) + "', " + str(y[1]) + "],\n")
        outfile.write("        ]);\n")
        outfile.write("\n")
        outfile.write("        var data5 = google.visualization.arrayToDataTable([\n")
        outfile.write("          ['Species', 'Referring References'],\n")
        for s in tmpslist:
            outfile.write("          ['" + s + "', " + str(ref_cnts[s]) + "],\n")
        outfile.write("        ]);\n")
        outfile.write("\n")
        outfile.write("        var options1 = {\n")
        outfile.write("          title: \"Cumulative Unique Binomial/Compound Names by Year\", \n")
        outfile.write("          legend: { position: 'none' }\n")
        outfile.write("        };\n")
        outfile.write("\n")
        outfile.write("        var options2 = {\n")
        outfile.write("          title: \"Unique Binomial/Compound Names by Year\", \n")
        outfile.write("          legend: { position: 'none' },\n")
        outfile.write("          bar: { groupWidth: '80%' }\n")
        outfile.write("        };\n")
        outfile.write("\n")
        outfile.write("        var options3 = {\n")
        outfile.write("          title: \"Cumulative Unique Specific Names by Year\", \n")
        outfile.write("          legend: { position: 'none' }\n")
        outfile.write("        };\n")
        outfile.write("\n")
        outfile.write("        var options4 = {\n")
        outfile.write("          title: \"Unique Specific Names by Year\", \n")
        outfile.write("          legend: { position: 'none' },\n")
        outfile.write("          bar: { groupWidth: '80%' }\n")
        outfile.write("        };\n")
        outfile.write("\n")
        outfile.write("        var options5 = {\n")
        outfile.write("          title: \"Number of References Referring to Accepted Species\", \n")
        outfile.write("          legend: { position: 'none' },\n")
        outfile.write("          bar: { groupWidth: '80%' }\n")
        outfile.write("        };\n")
        outfile.write("\n")
        outfile.write("        var chart1 = new google.visualization.LineChart(document.getElementById"
                      "('namechart1_div'));\n")
        outfile.write("        chart1.draw(data1, options1);\n")
        outfile.write("        var chart2 = new google.visualization.ColumnChart(document.getElementById"
                      "('namechart2_div'));\n")
        outfile.write("        chart2.draw(data2, options2);\n")
        outfile.write("        var chart3 = new google.visualization.LineChart(document.getElementById"
                      "('namechart3_div'));\n")
        outfile.write("        chart3.draw(data3, options3);\n")
        outfile.write("        var chart4 = new google.visualization.ColumnChart(document.getElementById"
                      "('namechart4_div'));\n")
        outfile.write("        chart4.draw(data4, options4);\n")
        outfile.write("        var chart5 = new google.visualization.ColumnChart(document.getElementById"
                      "('namechart5_div'));\n")
        outfile.write("        chart5.draw(data5, options5);\n")
        outfile.write("      }\n")
        outfile.write("    </script>\n")
        common_header_part2(outfile, "", False)

    outfile.write("    <header>\n")
    outfile.write("      <h1 id=\"" + NAME_SUM_URL + "\" class=\"bookmark2\">Summary of Names</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\".\"><span class=\"fa fa-list\"></span> Name Index</a></li>\n")
        outfile.write("          <li><a href=\"../" + SPECIES_URL +
                      "\"><span class=\"fa fa-check-circle\"></span> Accepted Species</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <p>\n")
    outfile.write("      A summary of the names in the database (last updated {}).\n".
                  format(datetime.date.isoformat(datetime.date.today())))
    outfile.write("      Most of these data are only based on <a href=\"../" + REF_SUM_URL +
                  "\">references whose citation data is already included in the database</a>.\n")
    outfile.write("    </p>\n")

    if do_print:
        filename = "cumulative_binames_line.svg"
        create_line_chart_file(filename, byears, START_YEAR, CURRENT_YEAR, 2)
        outfile.write("    <h3 class=\"nobookmark\">Cumulative Unique Binomial/Compound Names by Year</h3>\n")
        outfile.write("    <figure class=\"graph\">\n")
        outfile.write("      <img src=\"" + TMP_PATH + filename + "\" class=\"line_chart\" />\n")
        outfile.write("    </figure>\n")

        filename = "binames_per_year.svg_bar.svg"
        create_bar_chart_file(filename, byears, START_YEAR, CURRENT_YEAR, 1)
        outfile.write("    <h3 class=\"nobookmark\">Unique Binomial/Compound Names by Year</h3>\n")
        outfile.write("    <figure class=\"graph\">\n")
        outfile.write("      <img src=\"" + TMP_PATH + filename + "\" class=\"bar_chart\" />\n")
        outfile.write("    </figure>\n")

        filename = "cumulative_spnames_line.svg"
        create_line_chart_file(filename, syears, 1758, CURRENT_YEAR, 2)
        outfile.write("    <h3 class=\"nobookmark\">Cumulative Unique Specific Names by Year</h3>\n")
        outfile.write("    <figure class=\"graph\">\n")
        outfile.write("      <img src=\"" + TMP_PATH + filename + "\" class=\"line_chart\" />\n")
        outfile.write("    </figure>\n")

        filename = "spnames_per_year_bar.svg"
        create_bar_chart_file(filename, syears, 1758, CURRENT_YEAR, 1)
        outfile.write("    <h3 class=\"nobookmark\">Unique Specific Names by Year</h3>\n")
        outfile.write("    <figure class=\"graph\">\n")
        outfile.write("      <img src=\"" + TMP_PATH + filename + "\" class=\"bar_chart\" />\n")
        outfile.write("    </figure>\n")

        filename = "refs_per_species_bar.svg"
        create_qual_bar_chart_file(filename, tmpslist, ref_cnts)
        outfile.write("    <h3 class=\"nobookmark\">Number of References Referring to Accepted Species</h3>\n")
        outfile.write("    <figure class=\"graph\">\n")
        outfile.write("      <img src=\"" + TMP_PATH + filename + "\" class=\"bar_chart\" />\n")
        outfile.write("    </figure>\n")

        end_page_division(outfile)
    else:
        outfile.write("    <div id=\"namechart1_div\"></div>\n")
        outfile.write("    <div id=\"namechart2_div\"></div>\n")
        outfile.write("    <div id=\"namechart3_div\"></div>\n")
        outfile.write("    <div id=\"namechart4_div\"></div>\n")
        outfile.write("    <div id=\"namechart5_div\"></div>\n")
        common_html_footer(outfile, "../")


def extract_genus(name):
    if " " in name:
        return name[:name.find(" ")]
    else:
        return name


def create_genus_chronology(genus_cnts, do_print, outfile):
    """ create a page with the chronological history of the genera """
    miny = START_YEAR
    maxy = CURRENT_YEAR
    # --all totals and specific names--
    # find max count across all synonyms
    maxcnt = 0
    name_cnts = []
    total_cnts = {y: 0 for y in range(miny, maxy + 1)}
    for name in genus_cnts:
        cnts = genus_cnts[name]
        for y in cnts:
            total_cnts[y] += cnts[y]
        tmpmax = max(cnts.values())
        maxcnt = max(maxcnt, tmpmax)
        total = sum(cnts.values())
        name_cnts.append([total, name])
    maxcnt = max(total_cnts.values())
    name_cnts.sort(reverse=True)
    # put accepted name first, followed by the rest in decreasing frequency
    order = ["Uca"]
    for x in name_cnts:
        if x[1] != "Uca":
            order.append(x[1])
    if do_print:
        start_page_division(outfile, "synonym_page")
        filename = "Genus_total_chronology.svg"
        create_chronology_chart_file(filename, miny, maxy, maxcnt, total_cnts)
        for name in order:
            filename = "Genus_" + name + "_chronology.svg"
            create_chronology_chart_file(filename, miny, maxy, maxcnt, genus_cnts[name])
    else:
        common_header_part1(outfile, "Uca", "../")
        outfile.write("    <script type=\"text/javascript\" src=\"https://www.google.com/jsapi\"></script>\n")
        outfile.write("    <script type=\"text/javascript\">\n")
        outfile.write("      google.load(\"visualization\", \"1\", {packages:[\"corechart\"]});\n")
        outfile.write("      google.setOnLoadCallback(drawChart);\n")
        outfile.write("      function drawChart() {\n")
        setup_chronology_chart(0, miny, maxy, maxcnt, total_cnts, outfile)
        adjust = 1
        for i, name in enumerate(order):
            setup_chronology_chart(i + adjust, miny, maxy, maxcnt, genus_cnts[name], outfile)
        outfile.write("      }\n")
        outfile.write("    </script>\n")
        common_header_part2(outfile, "", False)

    outfile.write("    <header>\n")
    outfile.write("      <h1 class=\"bookmark2\">Synonym Chronology of the genus " + format_name_string("Uca") +
                  "</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "") +
                      "index.html\"><span class=\"fa fa-list\"></span> Full Name Index</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    if do_print:
        filename = "Genus_total_chronology.svg"
    else:
        filename = 0
    outfile.write("    <p>Chronological charts of different generic names for fiddler crabs. Strictly speaking"
                  "not all of these are synonyms; the charts include instances when fiddler crabs were placed in "
                  "other, valid, genera (<em>e.g.,</em> <em class=\"species\">Cancer</em>) as well as cases in the "
                  "19th century when the genus <em class=\"species\">Uca</em> was used for non-fiddler crabs.</p>\n")
    write_chronology_chart_div(filename, outfile, None, "All Genera", False, do_print, True)
    adjust = 1
    outfile.write("    <p style=\"clear: both\">Accepted name is listed first, followed by synonyms in decreasing "
                  "order of use.</p>\n")
    outfile.write("    <h2 class=\"nobookmark\">Genus Synonyms</h2>\n")
    for i, name in enumerate(order):
        if do_print:
            filename = "Genus_" + name + "_chronology.svg"
        else:
            filename = i + adjust
        write_chronology_chart_div(filename, outfile, None, name, True, do_print, True)

    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "../")


def calculate_binomial_locations(name, citelist):
    # find locations this name is applied to
    locs = set()
    for c in citelist:
        clean = clean_name(c.name)
        if clean.lower() == name.lower():
            if c.applied_cites is not None:
                for a in c.applied_cites:
                    p = a.application
                    if (p != ".") and (p[0] != "[") and (p != "?"):
                        if "[" in p:
                            p = p[:p.find("[") - 1]
                        locs |= {p}
    return locs


def clean_genus(genus):
    # fix alternate genus spellings when performing summaries
    if genus in {"Galasimus", "Gelasimes", "Gelasius", "Gelasmus", "Gelsimus", "Gelassimus", "Gelasima"}:
        return "Gelasimus"
    elif genus in {"Uka", "Uça"}:
        return "Uca"
    elif genus in {"Goneplax"}:
        return "Gonoplax"
    elif genus in {"Ocypoda"}:
        return "Ocypode"
    elif genus in {"Ciecie"}:
        return ""
    else:
        return genus


def calculate_name_index_data(refdict, citelist, specific_names):
    """ calculate all the data associated with binomials and specific names """
    name_table = create_name_table(citelist)
    unique_names = list()
    nameset = set()
    total_binomial_year_cnts = {}
    for c in citelist:
        if c.name != ".":
            clean = clean_name(c.name)
            if not clean.lower() in nameset:
                nameset |= {clean.lower()}
                unique_names.append(clean)
                y = refdict[c.cite_key].year()
                if y is not None:
                    if y in total_binomial_year_cnts:
                        total_binomial_year_cnts[y] += 1
                    else:
                        total_binomial_year_cnts[y] = 1
    unique_names.sort(key=lambda s: s.lower())

    # identify genera used per paper
    genera_per_paper = {}
    for c in citelist:
        if c.name != ".":
            if c.cite_key not in genera_per_paper:
                genera_per_paper[c.cite_key] = set()
            genera_set = genera_per_paper[c.cite_key]
            genera_set |= {extract_genus(clean_name(c.name))}
    genus_cnts = {}
    for c in genera_per_paper:
        y = refdict[c].year()
        if y is not None:
            if START_YEAR <= y <= CURRENT_YEAR:
                genera_set = genera_per_paper[c]
                for genus in genera_set:
                    genus = clean_genus(genus)
                    if genus != "":
                        if genus not in genus_cnts:
                            genus_cnts[genus] = {y: 0 for y in range(START_YEAR, CURRENT_YEAR + 1)}
                        gcnts = genus_cnts[genus]
                        gcnts[y] += 1

    binomial_usage_cnts_by_year = {}
    binomial_location_applications = {}
    for name in unique_names:
        binomial_usage_cnts_by_year[name] = calculate_binomial_yearly_cnts(name, refdict, citelist)
        binomial_location_applications[name] = calculate_binomial_locations(name, citelist)
        # test
        # print(name)
        # for x in binomial_location_applications[name]:
        #     print("  ", x)
        # print()

    specific_year_cnts = {}
    specific_usage_cnts_by_year = {}
    specific_location_applications = {}
    for name in specific_names:
        specific_usage_cnts_by_year[name.name] = calculate_specific_name_yearly_cnts(name, unique_names,
                                                                                     binomial_usage_cnts_by_year)
        specific_location_applications[name] = calculate_specific_locations(name, unique_names,
                                                                            binomial_location_applications)
        tmpkey = name.priority_source
        if tmpkey != ".":
            y = refdict[tmpkey].year()
            if y is not None:
                if y in specific_year_cnts:
                    specific_year_cnts[y] += 1
                else:
                    specific_year_cnts[y] = 1
    return (unique_names, binomial_usage_cnts_by_year, specific_usage_cnts_by_year, genus_cnts,
            total_binomial_year_cnts, name_table, specific_location_applications, binomial_location_applications)


def write_all_name_pages(refdict, citelist, unique_names, specific_names, name_table, species_refs, genus_cnts,
                         binomial_usage_cnts_by_year, total_binomial_year_cnts, outfile, do_print, logfile):
    """ create an index of binomials and specific names """
    if do_print:
        start_page_division(outfile, "index_page")
    else:
        common_html_header(outfile, "Name Index", "../")
    outfile.write("    <header id=\"name_index\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Name Index</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "") + NAME_SUM_URL +
                      "\"><span class=\"fa fa-line-chart\"></span> Name Summary</a></li>\n")
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "../") + SPECIES_URL +
                      "\"><span class=\"fa fa-check-circle\"></span> Accepted Species</a></li>\n")
        if SHOW_NEW:
            outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "") +
                          "synonyms_uca.html\">Synonyms of <em class=\"species\">Uca</em></a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("    <p>\n")
    outfile.write("      This is an index of every scientific name (including all alternate spellings) which have "
                  "been applied to fiddler crabs or placed in the fiddler crab genus.\n")
    outfile.write("    </p>\n")
    outfile.write("    <p>\n")
    outfile.write("      For the binomials, every publication which used that name is provided, as well as the "
                  "best estimate as to which species, as we understand them today, the author was actually "
                  "referring.\n")
    outfile.write("    </p>\n")
    outfile.write("    <p>\n")
    outfile.write("      For the specific names, only the primary spelling is listed below, but all alternate "
                  "spellings and inclusive binomials are included on the linked page, as well as general "
                  "information on the status of each specific name.\n")
    outfile.write("    </p>\n")
    outfile.write("    <div class=\"namecol\">\n")
    outfile.write("      <h3 id=\"binomials\" class=\"bookmark2\">Binomials (and other Compound Names)</h3>\n")
    outfile.write("      <ul class=\"namelist\">\n")
    # outfile.write("\n")
    for name in unique_names:
        namefile = name_to_filename(name)
        outfile.write("        <li><a href=\"" + rel_link_prefix(do_print, "") + namefile + ".html\">" +
                      format_name_string(name) + "</a></li>\n")

    outfile.write("      </ul>\n")
    outfile.write("    </div>\n")
    outfile.write("    <div class=\"namecol pagebreak\">\n")
    outfile.write("      <h3 id=\"specificnames\" class=\"bookmark2\">Specific Names</h3>\n")
    outfile.write("      <ul class=\"spnamelist\">\n")
    # outfile.write("\n")
    specific_year_cnts = {}
    for name in specific_names:
        outfile.write("        <li><a href=\"" + rel_link_prefix(do_print, "") + "sn_" + name.name + ".html\">" +
                      format_name_string(name.name) + "</a></li>\n")
        tmpkey = name.priority_source
        if tmpkey != ".":
            y = refdict[tmpkey].year()
            if y is not None:
                if y in specific_year_cnts:
                    specific_year_cnts[y] += 1
                else:
                    specific_year_cnts[y] = 1
    outfile.write("      </ul>\n")
    outfile.write("    </div>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "../")

    if do_print:
        create_name_summary(total_binomial_year_cnts, specific_year_cnts, species_refs, do_print, outfile)
        create_genus_chronology(genus_cnts, do_print, outfile)
    else:
        with codecs.open(WEBOUT_PATH + "names/" + NAME_SUM_URL, "w", "utf-8") as suboutfile:
            create_name_summary(total_binomial_year_cnts, specific_year_cnts, species_refs, do_print, suboutfile)
        with codecs.open(WEBOUT_PATH + "names/synonyms_uca.html", "w", "utf-8") as suboutfile:
            create_genus_chronology(genus_cnts, do_print, suboutfile)

    # write out individual pages for each binomial name and specific name
    for name in unique_names:
        sname = match_specific_name(name, specific_names)
        namefile = name_to_filename(name)
        if do_print:
            write_binomial_name_page(name, namefile, binomial_usage_cnts_by_year[name], refdict, citelist, name_table,
                                     sname, logfile, outfile, True)
        else:
            with codecs.open(WEBOUT_PATH + "names/" + namefile + ".html", "w", "utf-8") as suboutfile:
                write_binomial_name_page(name, namefile, binomial_usage_cnts_by_year[name], refdict, citelist,
                                         name_table, sname, logfile, suboutfile, False)
    for name in specific_names:
        if do_print:
            write_specific_name_page(name, unique_names, refdict, binomial_usage_cnts_by_year, logfile, outfile,
                                     True)
        else:
            with codecs.open(WEBOUT_PATH + "names/sn_" + name.name + ".html", "w", "utf-8") as suboutfile:
                write_specific_name_page(name, unique_names, refdict, binomial_usage_cnts_by_year, logfile, suboutfile,
                                         False)


def check_specific_names(citelist, specific_names, logfile):
    """ checks all specific names used to confirm they are accounted for in the full synonymy list """
    unique_names = list()
    nameset = set()
    for c in citelist:
        if c.name != ".":
            clean = clean_specific_name(c.name)
            if (not (clean in nameset)) and (clean != ""):
                nameset |= {clean}
                unique_names.append(clean)
    unique_names.sort()
    for n in unique_names:
        is_found = False
        for s in specific_names:
            if n in s.variations:
                is_found = True
        if not is_found:
            report_error(logfile, "Missing specific name: " + n)


def write_geography_page(species, outfile, do_print):
    """ output geographic ranges to HTML """
    regions = ("Eastern Atlantic",
               "Western Atlantic",
               "Eastern Pacific",
               "Indo-West Pacific")
    if do_print:
        start_page_division(outfile, "index_page")
    else:
        common_species_html_header(outfile, "Fiddler Crab Geographic Ranges", "", "")
    outfile.write("    <header id=\"" + MAP_URL + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Geographic Ranges</h1>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <section class=\"topspsection\">\n")
    outfile.write("      <div class=\"map_section\">\n")
    if do_print:
        outfile.write("      <figure>\n")
        outfile.write("        <img src=\"" + MAP_PATH + "uca_map.svg\" alt=\"Map\" "
                      "title=\"Map of fiddler crab distribution\" />\n")
        outfile.write("      </figure>\n")
        outfile.write("      <figure>\n")
        outfile.write("        <img src=\"" + MAP_PATH + "uca_point_map.svg\" alt=\"Point Map\" "
                      "title=\"Point map of fiddler crab distribution\" />\n")
        outfile.write("      </figure>\n")
    else:
        outfile.write("        <div id=\"map_canvas\"></div>\n")
        if SHOW_NEW:
            outfile.write("        <div id=\"map2_canvas\"></div>\n")
        outfile.write("        <div class=\"map_download\">\n")
        outfile.write("          <a href=\"maps/uca_map.svg\"><span class=\"fa fa-download\"></span> "
                      "Download SVG line map of ranges.</a> \n")
        if SHOW_NEW:
            outfile.write("          <a href=\"maps/uca_point_map.svg\"><span class=\"fa fa-download\"></span> "
                          "Download SVG line map of point locations.</a>\n")
        outfile.write("        </div>\n")
    outfile.write("      </div>\n")
    outfile.write("      <p>\n")
    outfile.write("        The first map shows the approximate density of species richness, with denser color "
                  "where more species are found. ")
    if SHOW_NEW:
        outfile.write("The second map shows approximate point locations where fiddler crabs "
                      "have been recorded in the scientific record.")
    outfile.write("\n      </p>\n")
    outfile.write("      <p>\n")
    outfile.write("        Specific ranges for a species or name can be found on its associated pages. "
                  "The list below sorts the species by major geographic region.\n")
    outfile.write("      </p>\n")

    outfile.write("    </section>\n")
    for r in regions:
        outfile.write("\n")
        outfile.write("    <section class=\"spsection\">\n")
        outfile.write("      <h2>" + r + "</h2>\n")
        outfile.write("      <ul class=\"splist\">\n")
        for s in species:
            if s.region == r:
                if s.status != "fossil":
                    outfile.write("        <li>" +
                                  create_species_link(s.species, "", "", do_print) +
                                  "</li>\n")
        outfile.write("      </ul>\n")
        outfile.write("    </section>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "")


def create_location_hierarchy(point_locations, logfile):
    """ got through all locations and add children to the parent locations """
    loc_dict = {}
    for p in point_locations:
        loc = point_locations[p]
        if loc.parent is not None:
            if loc.parent in point_locations:
                ploc = point_locations[loc.parent]
                ploc.children.append(loc)
            else:
                report_error(logfile, "Location missing: " + loc.parent)
        if loc.trimmed_name in loc_dict:
            report_error(logfile, "Duplicate trimmed location name: " + loc.trimmed_name)
        else:
            loc_dict[loc.trimmed_name] = loc
        for a in loc.alternates:
            if a in loc_dict:
                report_error(logfile, "Duplicate trimmed location name: " + a)
            else:
                loc_dict[a] = loc
    return loc_dict


# def write_location(loc, point_locations, indent):
#     """ print a location and its child locations """
#     print(indent + loc.trimmed_name)
#     if loc.n_children() > 0:
#         child_list = []
#         for child in loc.children:
#             child_list.append(child.name)
#         child_list.sort()
#         for child in child_list:
#             write_location(point_locations[child], point_locations, indent + "  ")
#
#
# def write_all_locations(point_locations):
#     """ create a indented list of all point locations """
#     top_list = []
#     for p in point_locations:
#         loc = point_locations[p]
#         if loc.parent is None:
#             top_list.append(loc.name)
#     top_list.sort()
#     for p in top_list:
#         loc = point_locations[p]
#         write_location(loc, point_locations, "")


def write_location(outfile, loc, point_locations):
    """ print a location and its child locations """
    outfile.write("<li>" + loc.trimmed_name)
    if loc.n_children() > 0:
        child_list = []
        for child in loc.children:
            child_list.append(child.name)
        child_list.sort()
        outfile.write("\n <ul>\n")
        for child in child_list:
            write_location(outfile, point_locations[child], point_locations)
        outfile.write(" </ul>\n")
    outfile.write("</li>\n")


def write_location_pages(outfile, do_print, point_locations, location_dict):
    """ output observation location index to HTML """
    if do_print:
        start_page_division(outfile, "index_page")
    else:
        common_html_header(outfile, "Fiddler Crab Observation Locations", "../")
    outfile.write("    <header id=\"location_index\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Location Index</h1>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <p>")
    outfile.write("      The following indices include all locations extracted from the literature in the database "
                  "where fiddler crabs have been reported. The first list includes all modern names in a rough,"
                  "hierarchical framework, mostly by country and subregions within country. Bodies of water which "
                  "cannot be associated with a single country are listed independently. The hierarchy is imperfect "
                  "because some observations were general enough to cross political or other structural boundaries.\n")
    outfile.write("    </p>")
    outfile.write("    <p>")
    outfile.write("      The second list is strictly alphabetical and includes archaic and older place names.\n")
    outfile.write("    </p>")
    outfile.write("    <p>")
    outfile.write("    Each location is expressed as a single pair of coordinates, so all plotted points "
                  "should only be viewed as an approximate location. Generally, a point on the shore was chosen to "
                  "represent each locality, but occasionally an interior land point may have been chosen when no "
                  "single shore point made sense, for example, in the case of a record on an island.\n")
    outfile.write("    </p>")
    outfile.write("\n")
    outfile.write("    <h2 class=\"nobookmark\">Hierarchical List of Modern Location Names</h2>\n")
    top_list = []
    # full_list = []
    for p in point_locations:
        loc = point_locations[p]
        if loc.parent is None:
            top_list.append(loc.name)
        # full_list.append(loc.trimmed_name)
        # for a in loc.alternates:
        #     full_list.append(a)
    top_list.sort()
    outfile.write("    <ul>\n")
    for p in top_list:
        loc = point_locations[p]
        write_location(outfile, loc, point_locations)
    outfile.write("    </ul>\n")
    outfile.write("    <h2 class=\"nobookmark\">Alphabetical List of All Location Names</h2>\n")
    full_list = list(location_dict.keys())
    full_list.sort()
    outfile.write("    <ul>\n")
    for p in full_list:
        outfile.write("   <li>" + p + "</li>\n")
    outfile.write("    </ul>\n")

    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "")


# def create_point_map_kml(title, place_list, point_locations):
#     with codecs.open(TMP_PATH + "doc.kml", "w", "utf-8") as outfile:
#         outfile.write("<?xml version=\"1.0\"?>\n")
#         outfile.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
#         outfile.write(" <Document>\n")
#         outfile.write("  <Style id=\"species_observations\">\n")
#         # outfile.write("    <LineStyle>\n")
#         # outfile.write("      <color>FFFF55FF</color>\n")
#         # outfile.write("      <width>5</width>\n")
#         # outfile.write("    </LineStyle>\n")
#         outfile.write("  </Style>\n")
#         for p in place_list:
#             pnt = point_locations[p]
#             outfile.write("  <Placemark>\n")
#             outfile.write("    <name>" + p + "</name>\n")
#             outfile.write("    <description/>\n")
#             outfile.write("    <styleUrl>\n")
#             outfile.write("      #species_observations\n")
#             outfile.write("    </styleUrl>\n")
#             outfile.write("    <Point>\n")
#             outfile.write("     <coordinates>\n")
#             outfile.write("          " + str(pnt.longitude) + "," + str(pnt.latitude) + "\n")
#             outfile.write("     </coordinates>\n")
#             outfile.write("    </Point>\n")
#             outfile.write("  </Placemark>\n")
#         outfile.write(" </Document>\n")
#         outfile.write("</kml>\n")
#     with zipfile.ZipFile("media/maps/" + title + "_points.kmz", "w", zipfile.ZIP_DEFLATED) as myzip:
#         myzip.write(TMP_PATH + "doc.kml")
#         myzip.close()
#
#
# def create_point_map_svg(title, place_list, point_locations, base_map, skip_axes):
#     fig, faxes = mplpy.subplots(figsize=[6.5, 3.25])
#     TMB_Common_Maps.draw_base_map(faxes, base_map)
#     for spine in faxes.spines:
#         faxes.spines[spine].set_visible(False)
#     maxlat = -90
#     minlat = 90
#     maxlon = -180
#     minlon = 180
#     lats = []
#     lons = []
#     for p in place_list:
#         if p in point_locations:
#             point = point_locations[p]
#             lats.append(point.latitude)
#             lons.append(point.longitude)
#             maxlon = max(maxlon, point.longitude)
#             minlon = min(minlon, point.longitude)
#             maxlat = max(maxlat, point.latitude)
#             minlat = min(minlat, point.latitude)
#
#     faxes.scatter(lons, lats, s=20, color="red", edgecolors="darkred", alpha=1, zorder=2)
#     minlon, maxlon, minlat, maxlat = TMB_Common_Maps.adjust_map_boundaries(minlon, maxlon, minlat, maxlat)
#     mplpy.xlim(minlon, maxlon)
#     mplpy.ylim(minlat, maxlat)
#     if skip_axes:
#         faxes.axes.get_yaxis().set_visible(False)
#         faxes.axes.get_xaxis().set_visible(False)
#     else:
#         mplpy.xlabel("longitude")
#         mplpy.ylabel("latitude")
#     mplpy.rcParams["svg.fonttype"] = "none"
#     mplpy.tight_layout()
#     mplpy.savefig("media/maps/" + title + "_point_map.svg", format="svg")
#     mplpy.close()
#
#
# def create_point_map(species, point_locations, citelist, base_map, logfile):
#     places = set()
#     for c in citelist:
#         if (c.actual == species) and ((c.context == "location") or
#                                       (c.context == "specimen")):
#             p = c.application
#             if p[0] != "[":
#                 if "[" in p:
#                     p = p[:p.find("[")-1]
#                 if p in point_locations:
#                     places.add(p)
#                 elif p != "?":
#                     report_error(logfile, "Missing point location: " + p)
#     place_list = sorted(list(places))
#     create_point_map_svg("u_" + species, place_list, point_locations, base_map, False)
#     create_point_map_kml("u_" + species, place_list, point_locations)
#     return place_list
#
#
# def create_all_point_maps(species, point_locations, citelist, base_map, logfile):
#     all_places = set()
#     for s in species:
#         new_places = create_point_map(s.species, point_locations, citelist, base_map, logfile)
#         all_places |= set(new_places)
#     all_list = sorted(list(all_places))
#     create_point_map_svg("uca", all_list, point_locations, base_map, True)
#     create_point_map_kml("uca", all_list, point_locations)


def write_common_names_pages(outfile, common_name_data, do_print):
    """ output common names to HTML """
    if do_print:
        start_page_division(outfile, "base_page")
    else:
        common_html_header(outfile, "Common Names of Fiddler Crabs", "")
    outfile.write("    <header id=\"" + COMMON_URL + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Common Names of Fiddler Crabs</h1>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <p>\n")
    outfile.write("      Following is a summary of common names for crabs in the genus "
                  "<em class=\"species\">Uca</em>. See <a href=\"" + rel_link_prefix(do_print, "") + SPECIES_URL +
                  "\">individual species</a> for more information on the common names of a particular species.\n")
    outfile.write("    </p>\n")
    outfile.write("    <dl class=\"common\">\n")
    first_level = True
    for line in common_name_data[1:]:
        line = line.strip()
        if line != "":
            text_level, text = line.split("\t")
            if text_level == "T":
                if not first_level:
                    outfile.write("        </dd>\n")
                else:
                    first_level = False
                outfile.write("      <dt>" + text + "</dt>\n")
                outfile.write("        <dd>\n")
            elif text_level == "P":
                outfile.write("          <p>\n")
                outfile.write("            " + text + "\n")
                outfile.write("          </p>\n")
            elif text_level == "B":
                outfile.write("          <blockquote>\n")
                outfile.write("            " + text + "\n")
                outfile.write("          </blockquote>\n")
    outfile.write("        </dd>\n")
    outfile.write("    </dl>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "")


def connect_refs_to_species(species, citelist):
    """ create list of references for each species """
    # create dictionary with empty reference lists
    # species_refs = {}
    # for s in species:
    #     reflist = set()
    #     species_refs[s.species] = reflist
    species_refs = {s.species: set() for s in species}
    # go through all citations
    for c in citelist:
        if c.actual in species_refs:
            reflist = species_refs[c.actual]
            reflist |= {c.cite_key}
            # species_refs[c.actual] = reflist  # note: this line is probably not necessary
    return species_refs


def write_species_list(specieslist, outfile, do_print):
    """ output species index HTML """
    if do_print:
        start_page_division(outfile, "index_page")
        link_str = "#name_index"
    else:
        common_html_header(outfile, "Fiddler Crab Species", "")
        link_str = "names/"
    outfile.write("    <header id=\"" + SPECIES_URL + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Species</h1>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <p>")
    nf = 0
    for s in specieslist:
        if s.status == "fossil":
            nf += 1
    tstr = ("      The following lists all {} of the currently recognized species of fiddler crab, as well as "
            "{} fossil species (marked with" + FOSSIL_IMAGE + ").\n")
    outfile.write(tstr.format(len(specieslist) - nf, nf))
    outfile.write("      See the <a href=\"" + link_str + "\">complete name index</a> for alternate species names "
                  "and spellings.\n")
    outfile.write("    </p>")
    outfile.write("\n")
    outfile.write("    <ul class=\"splist\">\n")
    for species in specieslist:
        outfile.write("      <li>" + create_species_link(species.species, species.status, "", do_print) + "</li>\n")
    outfile.write("    </ul>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "")


def write_species_photo_page(outfile, fname, species, common_name, caption, pn, pspecies, do_print):
    """ create page for a specific photo """
    if ";" in pspecies:
        spname = pspecies.replace(";", "_")
        ptitle = "Uca " + pspecies.replace(";", " & Uca ")
        is_multi = True
    else:
        spname = species
        ptitle = "Uca " + species
        is_multi = False
    if do_print:
        start_page_division(outfile, "photo_page")
        media_path = MEDIA_PATH + "photos/"
    else:
        common_html_header(outfile, ptitle + " Photo", "../")
        media_path = ""
    outfile.write("    <header id=\"" + fname + "\">\n")
    outfile.write("      <h1 class=\"nobookmark\"><em class=\"species\">" + ptitle + "</em> Photo</h1>\n")
    if not is_multi:
        if common_name != "#":
            outfile.write("      <h2 class=\"nobookmark\">" + common_name + "</h2>\n")
    outfile.write("      <nav>\n")
    outfile.write("        <ul>\n")
    if is_multi:
        splist = pspecies.split(";")
        for s in splist:
            outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "../") + "u_" + s +
                          ".html\"><span class=\"fa fa-info-circle\"></span> <em class=\"species\">Uca " + s +
                          "</em> page</a></li>\n")
    else:
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "../") + "u_" + species +
                      ".html\"><span class=\"fa fa-info-circle\"></span> Species page</a></li>\n")
    if not do_print:
        outfile.write("          <li><a href=\"../" + PHOTO_URL +
                      "\"><span class=\"fa fa-camera\"></span> All species photos</a></li>\n")
    outfile.write("        </ul>\n")
    outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <figure class=\"fullpic\">\n")
    outfile.write("      <img src=\"" + media_path + "U_" + spname + format(pn, "0>2") + ".jpg\" alt=\"Uca " +
                  species + " photo\" title=\"Uca " + species + "\" />\n")
    outfile.write("      <figcaption>" + caption + "</figcaption>\n")
    outfile.write("    </figure>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "../")


# def write_species_video_page(fname, species, common_name, video, vn):
def write_species_video_page(fname, video, vn):
    """ create page for a specific video """
    with codecs.open(fname, "w", "utf-8") as outfile:
        if ";" in video.species:
            spname = video.species.replace(";", "_")
            vtitle = "Uca " + video.species.replace(";", " & Uca ")
            is_multi = True
        else:
            # spname = species
            spname = video.species
            vtitle = "Uca " + video.species
            is_multi = False
        common_html_header(outfile, vtitle + " Video", "../")
        outfile.write("    <header>\n")
        outfile.write("      <h1 class=\"nobookmark\"><em class=\"species\">" + vtitle + "</em> Video</h1>\n")
        # if not is_multi:
        #     outfile.write("      <h2>" + common_name + "</h2>\n")
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        if is_multi:
            splist = video.species.split(";")
            for s in splist:
                outfile.write("          <li><a href=\"../u_" + s +
                              ".html\"><span class=\"fa fa-info-circle\"></span> <em class=\"species\">Uca " + s +
                              "</em> page</a></li>\n")
        else:
            outfile.write("          <li><a href=\"../u_" + video.species +
                          ".html\"><span class=\"fa fa-info-circle\"></span> Species page</a></li>\n")
        outfile.write("          <li><a href=\"../" + VIDEO_URL +
                      "\"><span class=\"fa fa-video-camera\"></span> All species videos</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
        outfile.write("    </header>\n")
        outfile.write("\n")
        outfile.write("    <h2>" + video.caption + "</h2>\n")
        outfile.write("    <video width=\"352\" height=\"240\" controls>\n")
        outfile.write("      <source src=\"U_" + spname + format(vn, "0>2") + "." + video.format.lower() +
                      "\" type=\"video/mp4\">\n")
        outfile.write("      Your browser does not support the video tag.\n")
        outfile.write("    </video>\n")
        outfile.write("    <p class=\"vidcaption\">\n")
        outfile.write("      " + video.date_location + "<br />\n")
        outfile.write("      " + video.author + "<br />\n")
        outfile.write("    </p>\n")
        outfile.write("    <dl class=\"viddetails\">\n")
        outfile.write("      <dt>Length</dt>\n")
        outfile.write("        <dd>" + video.length + "</dd>\n")
        outfile.write("      <dt>Size</dt>\n")
        outfile.write("        <dd>" + video.size + "</dd>\n")
        outfile.write("      <dt>Format</dt>\n")
        outfile.write("        <dd>" + video.format + "</dd>\n")
        if video.notes != "#":
            outfile.write("      <dt>Notes</dt>\n")
            outfile.write("        <dd>" + video.notes + "</dd>\n")
        outfile.write("    </dl>\n")
        common_html_footer(outfile, "../")


def write_species_page(species, references, specific_names, all_names, photos, videos, artlist, sprefs, refdict,
                       binomial_name_counts, specific_name_cnts, logfile, outfile, do_print):
    """ create the master page for a species """
    if do_print:
        media_path = MEDIA_PATH
    else:
        media_path = ""
    if species.status == "fossil":
        is_fossil = True
    else:
        is_fossil = False
    if do_print:
        start_page_division(outfile, "species_page")
    else:
        if is_fossil:
            common_html_header(outfile, "Uca " + species.species + " / Fossil", "")
        else:
            common_species_html_header(outfile, "Uca " + species.species + " / " + species.common, "",
                                       species.species)
    outfile.write("    <header id=\"u_" + species.species + ".html\">\n")
    if is_fossil:
        sc = FOSSIL_IMAGE
    else:
        sc = ""
    outfile.write("      <h1 class=\"species bookmark2\">Uca " + species.species + sc + "</h1>\n")
    if is_fossil:
        outfile.write("      <h2 class=\"nobookmark\">Fossil</h2>\n")
    else:
        outfile.write("      <h2 class=\"nobookmark\">" + species.common + "</h2>\n")
    # the species page navigation links only make sense on a webpage, not the printed version
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"#type\">Type</a></li>\n")
        outfile.write("          <li><a href=\"#info\"><span class=\"fa fa-info-circle\"></span> "
                      "Information</a></li>\n")
        outfile.write("          <li><a href=\"#pics\"><span class=\"fa fa-camera\"></span> Photos</a></li>\n")
        if not is_fossil:
            outfile.write("          <li><a href=\"#video\"><span class=\"fa fa-video-camera\"></span> "
                          "Video</a></li>\n")
            outfile.write("          <li><a href=\"#art\"><span class=\"fa fa-paint-brush\"></span> Art</a></li>\n")
        outfile.write("          <li><a href=\"#references\"><span class=\"fa fa-book\"></span> References</a></li>\n")
        outfile.write("          <li><a href=\"uca_species.html\"><span class=\"fa fa-list\"></span> "
                      "Species List</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <section class=\"topspsection\">\n")
    if do_print:
        outfile.write("      <h2 class=\"nobookmark\">Type Description</h2>\n")
    else:
        outfile.write("      <h2 id=\"type\" class=\"nobookmark\">Type Description</h2>\n")
    outfile.write("      <dl>\n")
    outfile.write("        <dt><em class=\"species\">" + species.type_species + "</em></dt>\n")
    tref = refdict[species.type_reference]
    outfile.write("        <dd>" + tref.formatted_html + "</dd>\n")
    outfile.write("      </dl>\n")
    outfile.write("    </section>\n")
    outfile.write("\n")
    outfile.write("    <section class=\"spsection\">\n")
    if do_print:
        outfile.write("      <h2 class=\"nobookmark\"><span class=\"fa fa-info-circle\"></span> Information</h2>\n")
    else:
        outfile.write("      <h2 id=\"info\" class=\"nobookmark\"><span class=\"fa fa-info-circle\"></span> "
                      "Information</h2>\n")
    outfile.write("      <dl>\n")
    outfile.write("       <dt>Subgenus</dt>\n")
    outfile.write("         <dd><a href=\"" + rel_link_prefix(do_print, "") + SYST_URL + "#" + species.subgenus +
                  "\"><em class=\"species\">" + species.subgenus + "</em></a></dd>\n")
    if not is_fossil:
        outfile.write("       <dt>Common Names</dt>\n")
        outfile.write("         <dd>" + species.commonext + "</dd>\n")

    # Synonyms
    binomial_synlist = []
    specific_synlist = []
    for spname in specific_names:
        if spname.synonym == species.species:
            varlist = spname.variations.split(";")
            for varname in varlist:
                for uname in all_names:
                    cleanname = clean_specific_name(uname)
                    if varname == cleanname:
                        binomial_synlist.append(uname)
            specific_synlist.append(spname.name)
    if len(binomial_synlist) > 0:
        binomial_synlist.sort(key=lambda s: s.lower())
        llist = []
        for n in binomial_synlist:
            namefile = name_to_filename(n)
            llist.append("<a href=\"" + rel_link_prefix(do_print, "names/") + namefile + ".html\">" +
                         format_name_string(n) + "</a>")

        tmpstr = "Synonyms, Alternate Spellings, &amp; Name Forms"
        if SHOW_NEW:
            tmpstr += "(<a href=\"" + rel_link_prefix(do_print, "names/") + "synonyms_" + species.species + \
                      ".html\">Chronology</a>n"
        outfile.write("       <dt>" + tmpstr + "</dt>\n")
        # outfile.write("       <dt>Synonyms, Alternate Spellings, &amp; Name Forms (<a href=\"" +
        #               rel_link_prefix(do_print, "names/") + "synonyms_" + species.species +
        #               ".html\">Chronology</a>)</dt>\n")
        outfile.write("         <dd><em class=\"species\">" + ", ".join(llist) + "</em></dd>\n")

    # Geographic Range
    outfile.write("       <dt class=\"pagebreak\">Geographic Range</dt>\n")
    outfile.write("         <dd>" + species.region + ": " + species.range + "</dd>\n")
    if not is_fossil:
        outfile.write("         <dd>\n")
        if do_print:
            outfile.write("           <img src=\"" + MAP_PATH + "u_" + species.species + "_map.svg\" alt=\"Map\" />\n")
            outfile.write("           <img src=\"" + MAP_PATH + "u_" + species.species + "_point_map.svg\" "
                          "alt=\"Map\" />\n")
        else:
            outfile.write("           <div id=\"map_canvas_sp\"></div>\n")
            if SHOW_NEW:
                outfile.write("           <div id=\"map2_canvas_sp\"></div>\n")
            outfile.write("           <div class=\"map_download\">\n")
            outfile.write("             <a href=\"maps/u_" + species.species + "_map.svg\">"
                          "<span class=\"fa fa-download\"></span> Download SVG line map of ranges.</a> \n")
            if SHOW_NEW:
                outfile.write("             <a href=\"maps/u_" + species.species + "_point_map.svg\">"
                              "<span class=\"fa fa-download\"></span> Download SVG line map of point locations.</a>\n")
            outfile.write("           </div>\n")
        outfile.write("         </dd>\n")
        outfile.write("         <dd class=\"map_data\">\n")
        maprefkeylist = species.range_references.split(";")
        maprefkeylist.sort(key=lambda s: s.lower())
        mapcitelist = []
        for m in maprefkeylist:
            if m in refdict:
                mref = refdict[m]
                mapcitelist.append("<a href=\"" + rel_link_prefix(do_print, "references/") + mref.cite_key +
                                   ".html\">" + mref.citation+"</a>")
            else:
                mapcitelist.append(m)
        outfile.write("           Map data derived from: " + "; ".join(mapcitelist) + "\n")
        outfile.write("         </dd>\n")

    # External links
    outfile.write("       <dt>External Links</dt>\n")
    if species.eolid != ".":
        outfile.write("         <dd><a href=\"http://eol.org/pages/" + species.eolid +
                      "/overview\">Encyclopedia of Life</a></dd>\n")
    outfile.write("         <dd><a href=\"http://en.wikipedia.org/wiki/Uca_" + species.species +
                  "\">Wikipedia</a></dd>\n")
    if species.inatid != ".":
        outfile.write("         <dd><a href=\"http://www.inaturalist.org/taxa/" + species.inatid +
                      "\">iNaturalist</a></dd>\n")
    if species.taxonid != ".":
        outfile.write("         <dd><a href=\"http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=" +
                      species.taxonid + "\">NCBI Taxonomy Browser/Genbank</a></dd>\n")
    if species.gbifid != ".":
        outfile.write("         <dd><a href=\"http://www.gbif.org/species/" + species.gbifid +
                      "\">GBIF</a></dd>\n")

    outfile.write("      </dl>\n")
    outfile.write("    </section>\n")
    outfile.write("\n")
    outfile.write("    <section class=\"spsection\">\n")
    if do_print:
        outfile.write("      <h2 class=\"nobookmark\"><span class=\"fa fa-camera\"></span> Photos</h2>\n")
    else:
        outfile.write("      <h2 id=\"pics\" class=\"nobookmark\"><span class=\"fa fa-camera\"></span> Photos</h2>\n")
    photo_n = 0
    for photo in photos:
        slist = photo.species.split(";")
        if species.species in slist:
            pn = int(photo.n)
            if ";" in photo.species:
                nl = photo.species.replace(";", "_")
                # pfname = WEBOUT_PATH + "photos/u_" + nl + format(pn, "0>2") + ".html"
                pfname = "photo_u_" + nl + format(pn, "0>2") + ".html"
                tname = nl
            else:
                pfname = "photo_u_" + species.species + format(pn, "0>2") + ".html"
                tname = species.species
            outfile.write("      <figure class=\"sppic\">\n")
            outfile.write("        <a href=\"" + rel_link_prefix(do_print, "photos/") + pfname +
                          "\"><img class=\"thumbnail\" src=\"" + media_path + "photos/U_" + tname +
                          format(pn, "0>2") + "tn.jpg\" alt=\"Uca " + species.species + " thumbnail\" title=\"Uca " +
                          species.species + "\" /></a>\n")
            outfile.write("      </figure>\n")
            photo_n += 1
    if photo_n == 0:
        outfile.write("      <p>\n")
        outfile.write("        <em>No pictures available at this time.</em>\n")
        outfile.write("      </p>\n")
    outfile.write("    </section>\n")

    outfile.write("\n")
    if not is_fossil:
        outfile.write("    <section class=\"spsection\">\n")
        if do_print:
            outfile.write("      <h2 class=\"nobookmark\"><span class=\"fa fa-video-camera\"></span> Video</h2>\n")
        else:
            outfile.write("      <h2 id=\"video\" class=\"nobookmark\"><span class=\"fa fa-video-camera\"></span> "
                          "Video</h2>\n")
        video_n = 0
        for video in videos:
            slist = video.species.split(";")
            if species.species in slist:
                vn = int(video.n)
                if ";" in video.species:
                    nl = video.species.replace(";", "_")
                    vfname = "video/video_u_" + nl + format(vn, "0>2") + ".html"
                else:
                    vfname = "video/video_u_" + species.species + format(vn, "0>2") + ".html"
                video_n += 1
                if video_n == 1:
                    if do_print:
                        outfile.write("    <p>\n")
                        outfile.write("      Videos are available on the web at "
                                      "<a href=\"http://www.fiddlercrab.info/uca_videos.html\">"
                                      "http://www.fiddlercrab.info/uca_videos.html</a> or by following the embedded "
                                      "links.")
                        outfile.write("    </p>\n")
                    outfile.write("      <dl class=\"vidlist\">\n")
                outfile.write("            <dt><a class=\"vidlink\" href=\"" + abs_link_prefix(do_print) + vfname +
                              "\">" + video.caption + "</a></dt>\n")
                outfile.write("              <dd>" + video.length + ", " + video.size + ", " +
                              video.format + "</dd>\n")
        if video_n == 0:
            outfile.write("      <p>\n")
            outfile.write("        <em>No videos available at this time.</em>\n")
            outfile.write("      </p>\n")
        else:
            outfile.write("      </dl>\n")
        outfile.write("    </section>\n")
        outfile.write("\n")

        outfile.write("    <section class=\"spsection\">\n")
        if do_print:
            outfile.write("      <h2 class=\"nobookmark\"><span class=\"fa fa-paint-brush\"></span> Art</h2>\n")
        else:
            outfile.write("      <h2 id=\"art\" class=\"nobookmark\"><span class=\"fa fa-paint-brush\"></span> "
                          "Art</h2>\n")
        artn = 0
        for art in artlist:
            slist = art.species.split(";")
            if species.species in slist:
                # pfname = "art/" + art.image + ".html"
                outfile.write("      <figure class=\"sppic\">\n")
                outfile.write("        <a href=\"" + rel_link_prefix(do_print, "art/") + art.image +
                              ".html\"><img class=\"thumbnail\" src=\"" + media_path + "art/" + art.image +
                              "_tn." + art.ext + "\" alt=\"" + art.title + " thumbnail\" title=\"" + art.title +
                              "\" /></a>\n")
                outfile.write("      </figure>\n")
                artn += 1
        if artn == 0:
            outfile.write("      <p>\n")
            outfile.write("        <em>No art available at this time.</em>\n")
            outfile.write("      </p>\n")
        outfile.write("    </section>\n")
        outfile.write("\n")

    outfile.write("    <section class=\"spsection\">\n")
    if do_print:
        outfile.write("      <h2 class=\"nobookmark\"><span class=\"fa fa-book\"></span> References</h2>\n")
    else:
        outfile.write("      <h2 id=\"references\" class=\"nobookmark\"><span class=\"fa fa-book\"></span> "
                      "References</h2>\n")
    outfile.write("      <div class=\"reference_list\">\n")
    outfile.write("        <ul>\n")
    for ref in references:
        if ref.cite_key in sprefs:
            outfile.write("          <li>" + format_reference_full(ref, do_print, logfile) + "</li>\n")
    outfile.write("        </ul>\n")
    outfile.write("      </div>\n")
    outfile.write("    </section>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "")

    if len(binomial_synlist) > 0:
        if do_print:
            create_synonym_chronology(species.species, binomial_synlist, binomial_name_counts, specific_synlist,
                                      specific_name_cnts, do_print, outfile)
        else:
            with codecs.open(WEBOUT_PATH + "names/synonyms_" + species.species + ".html", "w", "utf-8") as suboutfile:
                create_synonym_chronology(species.species, binomial_synlist, binomial_name_counts, specific_synlist,
                                          specific_name_cnts, do_print, suboutfile)


def write_photo_index(specieslist, photos, do_print, outfile, logfile):
    """ create the photos index page """
    if do_print:
        start_page_division(outfile, "index_page")
        media_path = MEDIA_PATH
    else:
        common_html_header(outfile, "Fiddler Crab Photos", "")
        media_path = ""
    outfile.write("    <header id=\"" + PHOTO_URL + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Photo Index</h1>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <p>\n")
    outfile.write("      Note: many photos of supposed fiddler crabs on the web are actually from other genera "
                  "(ghost crabs are a common error). Lay-people often assume any crab with asymmetric claws is a "
                  "fiddler crab.\n")
    outfile.write("    </p>\n")
    outfile.write("    <p>\n")
    outfile.write("      Total photo count is " + str(len(photos)) + ".\n")
    outfile.write("    </p>\n")
    for sp in specieslist:
        species = sp.species
        status = sp.status
        outfile.write("    <section class=\"photosection\">\n")
        outfile.write("      <h2 class=\"nobookmark\">" + create_species_link(species, status, "", do_print) +
                      "</h2>\n")
        photo_n = 0
        for photo in photos:
            splist = photo.species.split(";")
            if species in splist:
                pn = int(photo.n)
                if ";" in photo.species:
                    spname = photo.species.replace(";", "_")
                else:
                    spname = photo.species
                # pfname = "photos/u_" + spname + format(pn, "0>2") + ".html"
                pfname = "photo_u_" + spname + format(pn, "0>2") + ".html"
                outfile.write("      <figure class=\"sppic\">\n")
                outfile.write("        <a href=\"" + rel_link_prefix(do_print, "photos/") + pfname +
                              "\"><img class=\"thumbnail\" src=\"" + media_path + "photos/U_" + spname +
                              format(pn, "0>2") + "tn.jpg\" alt=\"Uca " + spname + " thumbnail\" title=\"Uca " +
                              spname + "\" /></a>\n")
                outfile.write("      </figure>\n")
                photo_n += 1
        if photo_n == 0:
            outfile.write("      <p>\n")
            outfile.write("        <em>No pictures available at this time.</em>\n")
            outfile.write("      </p>\n")
        outfile.write("    </section>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "")

    # output individual photo pages
    for sp in specieslist:
        species = sp.species
        for photo in photos:
            splist = photo.species.split(";")
            if species == splist[0]:  # only output one time
                pn = int(photo.n)
                if ";" in photo.species:
                    spname = photo.species.replace(";", "_")
                else:
                    spname = photo.species
                # pfname = "photos/u_" + spname + format(pn, "0>2") + ".html"
                pfname = "photo_u_" + spname + format(pn, "0>2") + ".html"
                if do_print:
                    # if species[0] in "ab":
                    write_species_photo_page(outfile, pfname, species, sp.common, photo.caption, pn,
                                             photo.species, True)
                else:
                    # copy photos and thumbnails to web output directory
                    tmp_name = "photos/U_" + spname + format(pn, "0>2")
                    try:
                        shutil.copy2(MEDIA_PATH + tmp_name + ".jpg",  WEBOUT_PATH + "photos/")
                    except FileNotFoundError:
                        report_error(logfile, "Missing file: " + tmp_name + ".jpg")
                    try:
                        shutil.copy2(MEDIA_PATH + tmp_name + "tn.jpg", WEBOUT_PATH + "photos/")
                    except FileNotFoundError:
                        report_error(logfile, "Missing file: " + tmp_name + "tn.jpg")
                    with open(WEBOUT_PATH + "photos/" + pfname, "w") as suboutfile:
                        write_species_photo_page(suboutfile, pfname, species, sp.common, photo.caption, pn,
                                                 photo.species, False)


def write_video_index(videos, do_print, outfile, logfile):
    """ create the videos page """
    sectitle = ("Feeding", "Male Waving and Other Displays", "Female Display", "Fighting", "Mating", "Miscellaneous")
    secshort = ("Feeding", "Male Display", "Female Display", "Fighting", "Mating", "Miscellaneous")
    secanchor = ("video_feeding", "video_display", "video_female", "video_fighting", "video_mating", "video_misc")
    if do_print:
        start_page_division(outfile, "index_page")
    else:
        common_html_header(outfile, "Fiddler Crab Videos", "")
    outfile.write("    <header id=\"" + VIDEO_URL + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Video Index</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        for i, x in enumerate(secshort):
            outfile.write("          <li><a href=\"#" + secanchor[i] + "\">" + x + "</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    if do_print:
        outfile.write("    <p>\n")
        outfile.write("      Videos are available on the web at "
                      "<a href=\"http://www.fiddlercrab.info/uca_videos.html\">"
                      "http://www.fiddlercrab.info/uca_videos.html</a> or by following the embedded links.")
        outfile.write("    </p>\n")
    outfile.write("    <p>\n")
    if do_print:
        linktxt = "individual species' page"
    else:
        linktxt = "<a href=\"" + rel_link_prefix(do_print, "") + SPECIES_URL + "\">individual species' page</a>"
    outfile.write("      Most of these videos predate digital video (let alone HD) and were recorded on Hi8 tape. "
                  "Hopefully they will eventually be replaced by higher quality video. These are grouped by "
                  "activity. Videos for specific species can be found on the " + linktxt + ".\n")
    outfile.write("    </p>\n")
    outfile.write("    <p>\n")
    outfile.write("      Total video count is " + str(len(videos)) + "\n")
    outfile.write("    </p>\n")
    for i, x in enumerate(sectitle):
        outfile.write("\n")
        outfile.write("    <section class=\"spsection\">\n")
        outfile.write("      <h2 id=\"" + secanchor[i] + "\" class=\"nobookmark\">" + x + "</h2>\n")
        outfile.write("      <dl class=\"vidlist\">\n")
        for video in videos:
            if "video_" + video.activity == secanchor[i]:
                vn = int(video.n)
                if ";" in video.species:
                    spname = video.species.replace(";", "_")
                else:
                    spname = video.species
                vfname = "video/video_u_" + spname + format(vn, "0>2") + ".html"
                outfile.write("            <dt><a class=\"vidlink\" href=\"" + abs_link_prefix(do_print) + vfname +
                              "\">" + video.caption + "</a></dt>\n")
                outfile.write("              <dd>" + video.length + ", " + video.size + ", " + video.format +
                              "</dd>\n")
        outfile.write("      </dl>\n")
        outfile.write("    </section>\n")
    # write individual video pages
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "")
        for video in videos:
            vn = int(video.n)
            if ";" in video.species:
                spname = video.species.replace(";", "_")
            else:
                spname = video.species
            vfname = WEBOUT_PATH + "video/video_u_" + spname + format(vn, "0>2") + ".html"
            # write_species_video_page(vfname, species.species, species.common, video, vn)
            write_species_video_page(vfname, video, vn)
            # copy video to web output directory
            tmp_name = "video/U_" + spname + format(vn, "0>2") + "." + video.format.lower()
            try:
                shutil.copy2(MEDIA_PATH + tmp_name, WEBOUT_PATH + "video/")
            except FileNotFoundError:
                report_error(logfile, "Missing file: " + tmp_name)


def write_specific_art_page(outfile, art, backurl, backtext, do_print):
    """ create the individual page for each piece of art """
    ptitle = art.title + " (" + art.author + " " + art.year + ")"
    if do_print:
        start_page_division(outfile, "art_page")
        media_path = MEDIA_PATH + "art/"
    else:
        common_html_header(outfile, ptitle, "../")
        media_path = ""
    outfile.write("    <header id=\"" + art.image + ".html\">\n")
    outfile.write("      <h1 class=\"nobookmark\"><em class=\"species\">" + art.title + "</em></h1>\n")
    outfile.write("      <h2 class=\"nobookmark\">" + art.author + " (" + art.year + ")</h2>\n")
    # if do_print and (art.cite_key != "n/a"):
    #     outfile.write("      <h2 class=\"nobookmark\">" + format_reference_cite(refdict[art.cite_key], do_print,
    #                                                                             AUTHOR_OUT, logfile) + "</h2>\n")
    # else:
    #     outfile.write("      <h2 class=\"nobookmark\">" + art.author + " (" + art.year + ")</h2>\n")
    if (art.species != "n/a") or (art.cite_key != "n/a") or (not do_print):
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        if art.species != "n/a":
            outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "../") + "u_" + art.species +
                          ".html\">Species page</a></li>\n")
        if art.cite_key != "n/a":
            outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "../references/") + art.cite_key +
                          ".html\">Reference</a></li>\n")
        if not do_print:
            outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "../") + backurl + "\">" + backtext +
                          "</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <figure class=\"fullpic\">\n")
    outfile.write("      <img src=\"" + media_path + art.image + "." + art.ext + "\" alt=\"" + ptitle +
                  " image\" title=\"" + ptitle + "\" />\n")
    outfile.write("      <figcaption>" + art.notes + "</figcaption>\n")
    outfile.write("    </figure>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "../")


def write_art_science_pages(artlist, do_print, outfile):
    """ create the art science index """
    if do_print:
        start_page_division(outfile, "index_page")
        media_path = MEDIA_PATH
    else:
        common_html_header(outfile, "Fiddler Crab Art - Scientific", "")
        media_path = ""
    outfile.write("    <header id=\"" + ART_SCI_URL + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Scientific Drawings</h1>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    artsource = []
    cnt = 0
    for art in artlist:
        if art.art_type == "science":
            cnt += 1
            artist = art.author + " (" + art.year + ")"
            try:
                artsource.index(artist)
            except ValueError:
                artsource.append(artist)
    outfile.write("      <p>\n")
    outfile.write("        Formal scientific drawings are often works of art as well as scientific illustration. "
                  "These are ordered chronologically.\n")
    outfile.write("      </p>\n")
    outfile.write("      <p>\n")
    outfile.write("        Total scientific drawing count is " + str(cnt) + ".\n")
    outfile.write("      </p>\n")
    for a in artsource:
        outfile.write("      <h3 class=\"nobookmark\">" + a + "</h3>\n")
        for art in artlist:
            if art.art_type == "science":
                artist = art.author + " (" + art.year + ")"
                if artist == a:
                    # pfname = "art/" + art.image + ".html"
                    outfile.write("      <figure class=\"sppic\">\n")
                    outfile.write("        <a href=\"" + rel_link_prefix(do_print, "art/") + art.image +
                                  ".html\"><img class=\"thumbnail\" src=\"" + media_path + "art/" +
                                  art.image + "_tn." + art.ext + "\" alt=\"" + art.title + " thumbnail\" title=\"" +
                                  art.title + "\" /></a>\n")
                    outfile.write("      </figure>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "")
    for a in artsource:
        for art in artlist:
            if art.art_type == "science":
                artist = art.author + " (" + art.year + ")"
                if artist == a:
                    if do_print:
                        write_specific_art_page(outfile, art, ART_SCI_URL, "All Scientific Drawings", do_print)
                    else:
                        with codecs.open(WEBOUT_PATH + "art/" + art.image + ".html", "w", "utf-8") as suboutfile:
                            write_specific_art_page(suboutfile, art, ART_SCI_URL, "All Scientific Drawings", do_print)


def write_art_stamps_pages(artlist, do_print, outfile):
    """ create the art stamps index """
    if do_print:
        start_page_division(outfile, "index_page")
        media_path = MEDIA_PATH
    else:
        common_html_header(outfile, "Fiddler Crab Stamps", "")
        media_path = ""
    outfile.write("    <header id=\"" + ART_STAMP_URL + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Postage Stamps</h1>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    artsource = []
    cnt = 0
    for art in artlist:
        if art.art_type == "stamp":
            cnt += 1
            try:
                artsource.index(art.author)
            except ValueError:
                artsource.append(art.author)
    outfile.write("      <p>\n")
    outfile.write("        Fiddler crabs have been featured on postage stamps surprisingly often. Quality "
                  "control leaves something to be desired, however, as misidentifications are common "
                  "(<em>e.g.</em>, see The Gambia and the Solomon Islands). Omori &amp; Holthuis (2000, 2005) "
                  "have actually written papers about crustacea on postage stamps.\n")
    outfile.write("      </p>\n")
    outfile.write("      <p>\n")
    outfile.write("        Total fiddler crab stamps is " + str(cnt) + ".\n")
    outfile.write("      </p>\n")
    for a in artsource:
        outfile.write("      <h3 class=\"nobookmark\">" + a + "</h3>\n")
        for art in artlist:
            if art.art_type == "stamp":
                if art.author == a:
                    # pfname = "art/" + art.image + ".html"
                    outfile.write("      <figure class=\"sppic\">\n")
                    outfile.write("        <a href=\"" + rel_link_prefix(do_print, "art/") + art.image +
                                  ".html\"><img class=\"thumbnail\" src=\"" + media_path + "art/" +
                                  art.image + "_tn." + art.ext + "\" alt=\"" + art.title + " thumbnail\" title=\"" +
                                  art.title + "\" /></a>\n")
                    outfile.write("      </figure>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "")
    for a in artsource:
        for art in artlist:
            if art.art_type == "stamp":
                if art.author == a:
                    if do_print:
                        write_specific_art_page(outfile, art, ART_STAMP_URL, "All Stamps", do_print)
                    else:
                        with codecs.open(WEBOUT_PATH + "art/" + art.image + ".html", "w", "utf-8") as suboutfile:
                            write_specific_art_page(suboutfile, art, ART_STAMP_URL, "All Stamps", do_print)

    
def write_art_crafts_pages(artlist, do_print, outfile):
    """ create the art craft index """
    if do_print:
        start_page_division(outfile, "index_page")
        media_path = MEDIA_PATH
    else:
        common_html_header(outfile, "Fiddler Crab Crafts", "")
        media_path = ""
    outfile.write("    <header id=\"" + ART_CRAFT_URL + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Arts &amp; Crafts</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"#origami\">Origami</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("      <h2 id=\"origami\" class=\"nobookmark\">Origami</h2>\n")
    artsource = []
    cnt = 0
    for art in artlist:
        if art.art_type == "origami":
            cnt += 1
            try:
                artsource.index(art.author)
            except ValueError:
                artsource.append(art.author)
    outfile.write("      <p>\n")
    outfile.write("        Male fiddler crabs are a particular challenge for origami because of the asymmetry, "
                  "but a number of origami experts have developed fiddler crab models.\n")
    outfile.write("      </p>\n")
    outfile.write("      <p>\n")
    outfile.write("        Total fiddler crab origami models is " + str(cnt) + ".\n")
    outfile.write("      </p>\n")
    for a in artsource:
        outfile.write("      <h3 class=\"nobookmark\">" + a + "</h3>\n")
        for art in artlist:
            if art.art_type == "origami":
                if art.author == a:
                    outfile.write("      <figure class=\"sppic\">\n")
                    outfile.write("        <a href=\"" + rel_link_prefix(do_print, "art/") + art.image +
                                  ".html\"><img class=\"thumbnail\" src=\"" + media_path + "art/" +
                                  art.image + "_tn." + art.ext + "\" alt=\"" + art.title + " thumbnail\" title=\"" +
                                  art.title + "\" /></a>\n")
                    outfile.write("      </figure>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "")
    for a in artsource:
        for art in artlist:
            if art.art_type == "origami":
                if art.author == a:
                    if do_print:
                        write_specific_art_page(outfile, art, ART_CRAFT_URL, "All Crafts", do_print)
                    else:
                        with codecs.open(WEBOUT_PATH + "art/" + art.image + ".html", "w", "utf-8") as suboutfile:
                            write_specific_art_page(suboutfile, art, ART_CRAFT_URL, "All Crafts", do_print)


def write_all_art_pages(artlist, do_print, outfile, logfile):
    """ create the art pages """
    if do_print:
        write_art_science_pages(artlist, do_print, outfile)
        write_art_stamps_pages(artlist, do_print, outfile)
        write_art_crafts_pages(artlist, do_print, outfile)
    else:
        with codecs.open(WEBOUT_PATH + ART_CRAFT_URL, "w", "utf-8") as suboutfile:
            write_art_crafts_pages(artlist, do_print, suboutfile)
        with codecs.open(WEBOUT_PATH + ART_STAMP_URL, "w", "utf-8") as suboutfile:
            write_art_stamps_pages(artlist, do_print, suboutfile)
        with codecs.open(WEBOUT_PATH + ART_SCI_URL, "w", "utf-8") as suboutfile:
            write_art_science_pages(artlist, do_print, suboutfile)
    # copy art files
    if not do_print:
        for art in artlist:
            try:
                shutil.copy2(MEDIA_PATH + "art/" + art.image + "." + art.ext, WEBOUT_PATH + "art/")
            except FileNotFoundError:
                report_error(logfile, "Missing file: " + MEDIA_PATH + "art/" + art.image + "." + art.ext)
            try:
                shutil.copy2(MEDIA_PATH + "art/" + art.image + "_tn." + art.ext, WEBOUT_PATH + "art/")
            except FileNotFoundError:
                report_error(logfile, "Missing file: " + MEDIA_PATH + "art/" + art.image + "_tn." + art.ext)


def write_species_info_pages(specieslist, references, specific_names, all_names, photos, videos, art, species_refs,
                             refdict, binomial_name_cnts, specific_name_cnts, logfile, outfile, do_print):
    """ output species list and individual species pages """
    if do_print:
        write_species_list(specieslist, outfile, True)
    else:
        with codecs.open(WEBOUT_PATH + SPECIES_URL, "w", "utf-8") as suboutfile:
            write_species_list(specieslist, suboutfile, False)
    for species in specieslist:
        sprefs = species_refs[species.species]
        if do_print:
            write_species_page(species, references, specific_names, all_names, photos, videos, art, sprefs, refdict,
                               binomial_name_cnts, specific_name_cnts, logfile, outfile, True)
        else:
            with codecs.open(WEBOUT_PATH + "u_" + species.species + ".html", "w", "utf-8") as suboutfile:
                write_species_page(species, references, specific_names, all_names, photos, videos, art, sprefs, refdict,
                                   binomial_name_cnts, specific_name_cnts, logfile, suboutfile, False)


def write_systematics_overview(subgenlist, specieslist, refdict, outfile, do_print, logfile):
    """ create the systematics page """
    if do_print:
        start_page_division(outfile, "base_page")
        media_path = MEDIA_PATH
    else:
        common_html_header(outfile, "Fiddler Crab Systematics", "")
        media_path = ""
    outfile.write("    <header id=\"" + SYST_URL + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Systematics</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"#genus\">Genus</a></li>\n")
        outfile.write("          <li><a href=\"#subgenera\">Subgenera</a></li>\n")
        outfile.write("          <li><a href=\"#species\">Species</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <div class=\"topsection\">\n")
    outfile.write("    <p>The following information is an expansion and update of that found in:</p>\n")
    outfile.write("    <blockquote>\n")
    outfile.write("      Rosenberg, M.S. 2001. The systematics and taxonomy of fiddler crabs: A phylogeny of the "
                  "genus <em class=\"species\">Uca.</em> <em>Journal of Crustacean Biology</em> 21(3):839-869.\n")
    outfile.write("    </blockquote>\n")
    outfile.write("    <p>Additional references for updated information will be detailed below.</p>")
    outfile.write("    </div>\n")
    outfile.write("\n")

    # genus section
    outfile.write("    <section class=\"spsection\">\n")
    outfile.write("      <h2 id=\"genus\" class=\"bookmark2\">Genus <em class=\"species\">Uca</em> Leach, 1814</h2>\n")
    outfile.write("      <h3 class=\"nobookmark\">Type species: <em class=\"species\">Cancer vocans major</em> "
                  "Herbst, 1782</h3>\n")
    outfile.write("      <p>\n")
    outfile.write("         The earliest description of the type species of <em class=\"species\">Uca</em> is from "
                  "a drawing in " + format_reference_cite(refdict["Seba1758"], do_print, AUTHOR_PAREN, logfile) +
                  ", which he called <em class=\"species\">Cancer uka una, Brasiliensibus</em> (shown below).\n")
    outfile.write("      </p>\n")
    outfile.write("      <figure>\n")
    outfile.write("        <img src=\"" + media_path + "art/Seba_Uca_una.jpg\" "
                  "style=\"padding-left: 0; padding-right: 0; "
                  "margin-left: 0; margin-right: 0; text-align: center\" alt=\"Seba's fiddler crab image\" "
                  "title=\"Seba's fiddler crab\" />\n")
    outfile.write("      </figure>\n")
    outfile.write("      <p>\n")
    outfile.write("        A number of authors subsequently used this same picture as a basis for naming the "
                  "species (" +
                  format_reference_cite(refdict["Manning1981"], do_print, AUTHOR_NOPAREN, logfile) + ").  "
                  "<em class=\"species\">Cancer vocans major</em> Herbst, 1782; "
                  "<em class=\"species\">Ocypode heterochelos</em> Lamarck, 1801; "
                  "<em class=\"species\">Cancer uka</em> Shaw and Nodder, 1802; and "
                  "<em class=\"species\">Uca una</em> Leach, 1814, are  all objective synonyms, because they are "
                  "all based on the picture and  description from Seba. Because of this, the official type "
                  "specimen of the  genus <em class=\"species\">Uca</em> is <em class=\"species\">Cancer vocans "
                  "major.</em>  The earliest description of  this species based on actual specimens and not on "
                  "Seba's drawing was <em class=\"species\"> Gelasimus platydactylus</em> Milne-Edwards, 1837.\n")
    outfile.write("      </p>\n")
    outfile.write("      <blockquote>\n")
    outfile.write("        As an aside, Seba's name, <em class=\"species\">Cancer uka una</em> comes from the "
                  "nomenclature of " +
                  format_reference_cite(refdict["Marcgrave1648"], do_print, AUTHOR_PAREN, logfile) +
                  ", who mispelled &ldquo;u&ccedil;a una&rdquo; as &ldquo;uca una&rdquo;. Not only did Seba copy the "
                  "mispelling, but he applied it to the fiddler crab instead of the mangrove crab (which is today "
                  "called <em class=\"species\">Ucides</em>) to which Marcgrave applied the name (see below). "
                  "<a href=\"references/Latreille1817.2.html\">Latreille's (1817)</a> proposal of the generic "
                  "name <em class=\"species\">Gelasimus</em> for fiddler crabs was so that "
                  "<em class=\"species\">Uca</em> could be applied to mangrove crabs; as this was an invalid "
                  "proposal, <em class=\"species\">Uca</em> is retained for fiddlers, despite being due to a pair of "
                  "errors (" +
                  format_reference_cite(refdict["Tavares1993"], do_print, AUTHOR_NOPAREN, logfile) + ").\n")
    outfile.write("        <figure class=\"syspic\">\n")
    outfile.write("          <img src=\"" + media_path + "art/Marcgrave_Maracoani.png\" "
                  "alt=\"Marcgrave's Maracoani image\" title=\"Marcgrave's Maracoani\">\n")
    outfile.write("          <figcaption>Oldest known drawing of a fiddler crab "
                  "(" + format_reference_cite(refdict["Marcgrave1648"], do_print, AUTHOR_NOPAREN, logfile) + "). "
                  "He labeled it &ldquo;Maracoani&rdquo;, and it represents the namesake of the species "
                  "<em class=\"species\">Uca maracoani.</em></figcaption>\n")
    outfile.write("        </figure>\n")
    outfile.write("        <figure class=\"syspic\">\n")
    outfile.write("          <img src=\"" + media_path + "art/Marcgrave_Uca_una.png\" "
                  "alt=\"Marcgrave's Uca una image\" title=\"Marcgrave's Uca una\">\n")
    outfile.write("          <figcaption>The drawing actually labeled &ldquo;Uca Una&rdquo; by "
                  + format_reference_cite(refdict["Marcgrave1648"], do_print, AUTHOR_PAREN, logfile) +
                  " is not a fiddler crab. Today this species is known as the mangrove crab "
                  "<em class=\"species\">Ucides cordatus.</em></figcaption>\n")
    outfile.write("        </figure>\n")
    outfile.write("        <figure class=\"syspic\">\n")
    outfile.write("          <img src=\"" + media_path + "art/Marcgrave_Ciecie_Ete.png\" "
                  "alt=\"Marcgrave's Ciecie Ete image\" title=\"Marcgrave's Ciecie Ete\">\n")
    outfile.write("          <figcaption>The other fiddler crab drawing found in "
                  + format_reference_cite(refdict["Marcgrave1648"], do_print, AUTHOR_PAREN, logfile) + ", labeled "
                  "&ldquo;Ciecie Ete&rdquo; (he also refers to a very similar species called "
                  "&ldquo;Ciecie Panema&rdquo;). This figure is believed to most likely represent "
                  "<em class=\"species\">Uca thayeri.</em></figcaption>\n")
    outfile.write("        </figure>\n")
    outfile.write("      </blockquote>\n")
    outfile.write("      <p>\n")
    outfile.write("        For about 60 years, the genus was known as <em class=\"species\">Gelasimus,</em> "
                  "until " + format_reference_cite(refdict["Rathbun1897.1"], do_print, AUTHOR_PAREN, logfile)
                  + " showed that the abandonment of the older name <em class=\"species\">Uca</em> did not conform to "
                  "zoological naming conventions. The type species of <em class=\"species\">Uca</em> was known as both "
                  "<em class=\"species\">Uca heterochelos</em> and <em class=\"species\">U. platydactylus,</em> "
                  "until " + format_reference_cite(refdict["Rathbun1918.2"], do_print, AUTHOR_PAREN, logfile) +
                  " suggested the adoption of "
                  "<em class=\"species\">U. heterochelos</em> as the valid name. Almost 50 years later, "
                  + format_reference_cite(refdict["Holthuis1962"], do_print, AUTHOR_PAREN, logfile) +
                  " pointed out that "
                  "<em class=\"species\">U. heterochelos</em> was an objective junior synonym of "
                  "<em class=\"species\">U. major,</em> thus the type species has been referred to as "
                  "<em class=\"species\">U. major</em> ever since.\n")
    outfile.write("      </p>\n")
    outfile.write("      <p>\n")
    outfile.write("        However, " +
                  format_reference_cite(refdict["Bott1973.1"], do_print, AUTHOR_PAREN, logfile) +
                  " discovered that there "
                  "has been a universal  misinterpretation of the type species; the species pictured by Seba is "
                  "not the American species commonly referred to as "
                  "<em class=\"species\">U. major,</em> but rather the West African/Portuguese species called "
                  "<em class=\"species\">U. tangeri</em> (Eydoux, 1835). Correcting this error would have caused "
                  "a somewhat painful change of names (" +
                  format_reference_cite(refdict["Holthuis1979"], do_print, AUTHOR_NOPAREN, logfile) + "; " +
                  format_reference_cite(refdict["Manning1981"], do_print, AUTHOR_NOPAREN, logfile) +
                  "). The type species would still be called <em class=\"species\">U. major</em>, but would refer to "
                  "the West African/European species rather than the American one; the American species, "
                  "which has been called <em class=\"species\">U. major</em> since 1962, would be called "
                  "<em class=\"species\">U. platydactylus,</em> a name not used since 1918.\n")
    outfile.write("      </p>\n")
    outfile.write("      <p>\n")
    outfile.write("         To deal with this dilemma, the Society of Zoological Nomenclature officially "
                  "designated the holotype of <em class=\"species\">Gelasimus platydactylus</em> as a neotype "
                  "of <em class=\"species\">Cancer vocans major</em> (" +
                  format_reference_cite(refdict["Holthuis1979"], do_print, AUTHOR_NOPAREN, logfile) + "; " +
                  format_reference_cite(refdict["ICZN1983"], do_print, AUTHOR_NOPAREN, logfile) + "). "
                  "The result of this decision is "
                  "that we retain the names <em class=\"species\">U. major</em> for the American species and "
                  "<em class=\"species\">U. tangeri</em> for the West African/European species. It also means "
                  "that although <em class=\"species\">U. tangeri</em> is technically the species upon which "
                  "the genus is named, <em class=\"species\">U. major</em> "
                  "(<em class=\"species\">Cancer vocans major</em>) is still the official type species of the "
                  "genus <em class=\"species\">Uca.</em>\n")
    outfile.write("      </p>\n")
    outfile.write("    </section>\n")
    outfile.write("\n")

    # subgenera section
    outfile.write("    <section class=\"spsection\">\n")
    outfile.write("      <h2 id=\"subgenera\" class=\"bookmark2\">Subgenera</h2>\n")
    outfile.write("      <p>\n")
    outfile.write("       There have been two major proposals for splitting up the genus, one by " +
                  format_reference_cite(refdict["Bott1973.2"], do_print, AUTHOR_PAREN, logfile) +
                  " and the other by " +
                  format_reference_cite(refdict["Crane1975"], do_print, AUTHOR_PAREN, logfile) + ". "
                  "Neither is based on a numerical "
                  "phylogeny. Crane's descriptions are very complete. Bott's descriptions are poor, but have "
                  "priority. For a long time, scientists actively ignored both subdivisions and when there "
                  "was a reference in the literature, it almost always used Crane's names and not Bott's. "
                  "Bott also split the genus into multiple genera rather than subgenera, an unnecessary "
                  "complication in most researcher's minds.\n")
    outfile.write("      </p>\n")
    outfile.write("      <p>\n")
    outfile.write("       " + format_reference_cite(refdict["Rosenberg2001"], do_print, AUTHOR_PAREN, logfile) +
                  " partly cleared up the confusion between the two systems. More recent work by " +
                  format_reference_cite(refdict["Beinlich2006"], do_print, AUTHOR_PAREN, logfile) + ", " +
                  format_reference_cite(refdict["Shih2009"], do_print, AUTHOR_PAREN, logfile) + ", " +
                  format_reference_cite(refdict["Spivak2009"], do_print, AUTHOR_PAREN, logfile) + ", " +
                  format_reference_cite(refdict["Naderloo2010"], do_print, AUTHOR_PAREN, logfile) + ", " +
                  format_reference_cite(refdict["Landstorfer2010"], do_print, AUTHOR_PAREN, logfile) + ", and " +
                  format_reference_cite(refdict["Shih2015.2"], do_print, AUTHOR_PAREN, logfile) +
                  " have continued to refine the subgenera as detailed below.\n")
    outfile.write("      </p>\n")
    outfile.write("      <ul>\n")
    for subgen in subgenlist:
        outfile.write("        <li><a href=\"#"+subgen.subgenus + "\">Subgenus <em class=\"species\">" +
                      subgen.subgenus + "</em></a></li>\n")
    outfile.write("      </ul>\n")

    for subgen in subgenlist:
        outfile.write("      <hr />\n")
        outfile.write("      <h3 id=\"" + subgen.subgenus + "\" class=\"bookmark3\">Subgenus <em class=\"species\">" +
                      subgen.subgenus + "</em> " +
                      format_reference_cite(refdict[subgen.author], do_print, AUTHOR_NOPCOMMA, logfile) + "</h3>\n")
        outfile.write("      <dl>\n")
        outfile.write("        <dt>Type</dt>\n")
        outfile.write("        <dd>" + create_species_link(subgen.type_species, "", "", do_print) + "</dd>\n")
        outfile.write("        <dt>All Species</dt>\n")
        splist = []
        for s in specieslist:
            if s.subgenus == subgen.subgenus:
                splist.append(create_species_link(s.species, s.status, "", do_print))
        outfile.write("        <dd>" + ", ".join(splist) + "</dd>\n")
        outfile.write("      </dl>\n")
        outfile.write("      <p>\n")
        outfile.write("      " + subgen.notes + "\n")
        outfile.write("      </p>\n")
        outfile.write("\n")

    outfile.write("    </section>\n")
    outfile.write("\n")

    # species section
    outfile.write("    <section class=\"spsection\">\n")
    outfile.write("      <h2 id=\"species\" class=\"bookmark2\">Species Level Systematics</h2>\n")
    outfile.write("      <ul>\n")
    outfile.write("        <li><a href=\"" + SPECIES_URL + "\">Currently recognized species</a></li>\n")
    outfile.write("      </ul>\n")
    outfile.write("      <p>\n")
    outfile.write("For an overview of all <em class=\"species\">Uca</em> species, the best reference is " +
                  format_reference_cite(refdict["Crane1975"], do_print, AUTHOR_PAREN, logfile) +
                  "; any earlier major work would be "
                  "overridden by Crane's descriptions. For the most part, the taxa recognized by Crane are still "
                  "accepted today. A number of new species have been described since the publication of her "
                  "monograph, a few species has been discovered to be invalid, and two of her new species were "
                  "previously described by " +
                  format_reference_cite(refdict["Bott1973.2"], do_print, AUTHOR_PAREN, logfile) + "; as with the "
                  "subgenera, his names have priority and take precedence. These changes are summarized below.\n")
    outfile.write("      </p>\n")
    outfile.write("      <h3 class=\"nobookmark\">Changes to the species level taxonomy of the genus "
                  "<em class=\"species\">Uca</em> since Crane (1975)</h3>\n")
    outfile.write("      <table>\n")
    outfile.write("        <thead>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <th>New/Validated Extant Species</th><th>Reference(s)</th>\n")
    outfile.write("          </tr>\n")
    outfile.write("        </thead>\n")
    outfile.write("        <tfoot>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <td colspan=\"2\"><strong>Note:</strong> The newly described (relative to Crane) "
                  "species <em class=\"species\">Uca pavo</em> George &amp; Jones, 1982, is a junior subsynonym "
                  "of <em class=\"species\">Uca capricornis</em> (see " +
                  format_reference_cite(refdict["vonHagen1989"], do_print, AUTHOR_PAREN, logfile) + ")</td>\n")
    outfile.write("          </tr>\n")
    outfile.write("        </tfoot>\n")
    outfile.write("        <tbody>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <td><em class=\"species\">Uca panacea</em></td>\n")
    outfile.write("            <td>" +
                  format_reference_cite(refdict["Novak1974"], do_print, AUTHOR_PAREN, logfile) + "</td>\n")
    outfile.write("          </tr>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <td><em class=\"species\">Uca marguerita</em></td>\n")
    outfile.write("            <td>" +
                  format_reference_cite(refdict["Thurman1981.1"], do_print, AUTHOR_PAREN, logfile) + "</td>\n")
    outfile.write("          </tr>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <td><em class=\"species\">Uca elegans</em></td>\n")
    outfile.write("            <td>" + format_reference_cite(refdict["George1982"], do_print, AUTHOR_PAREN, logfile) +
                  "</td>\n")
    outfile.write("          </tr>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <td><em class=\"species\">Uca hirsutimanus</em></td>\n")
    outfile.write("            <td>" + format_reference_cite(refdict["George1982"], do_print, AUTHOR_PAREN, logfile) +
                  "</td>\n")
    outfile.write("          </tr>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <td><em class=\"species\">Uca intermedia</em></td>\n")
    outfile.write("            <td>" +
                  format_reference_cite(refdict["vonPrahl1985"], do_print, AUTHOR_PAREN, logfile) + "</td>\n")
    outfile.write("          </tr>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <td><em class=\"species\">Uca victoriana</em></td>\n")
    outfile.write("            <td>" +
                  format_reference_cite(refdict["vonHagen1987.1"], do_print, AUTHOR_PAREN, logfile) + "</td>\n")
    outfile.write("          </tr>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <td><em class=\"species\">Uca albimana</em></td>\n")
    outfile.write("            <td>" +
                  format_reference_cite(refdict["Kossmann1877"], do_print, AUTHOR_PAREN, logfile) +
                  ", " + format_reference_cite(refdict["Shih2009"], do_print, AUTHOR_PAREN, logfile) + ", " +
                  format_reference_cite(refdict["Naderloo2010"], do_print, AUTHOR_PAREN, logfile) + "</td>\n")
    outfile.write("          </tr>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <td><em class=\"species\">Uca iranica</em></td>\n")
    outfile.write("            <td>" +
                  format_reference_cite(refdict["Pretzmann1971"], do_print, AUTHOR_PAREN, logfile) +
                  ", " + format_reference_cite(refdict["Shih2009"], do_print, AUTHOR_PAREN, logfile) + ", " +
                  format_reference_cite(refdict["Naderloo2010"], do_print, AUTHOR_PAREN, logfile) + "</td>\n")
    outfile.write("          </tr>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <td><em class=\"species\">Uca cryptica</em></td>\n")
    outfile.write("            <td>" +
                  format_reference_cite(refdict["Naderloo2010"], do_print, AUTHOR_PAREN, logfile) +
                  "</td>\n")
    outfile.write("          </tr>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <td><em class=\"species\">Uca osa</em></td>\n")
    outfile.write("            <td>" +
                  format_reference_cite(refdict["Landstorfer2010"], do_print, AUTHOR_PAREN, logfile) + "</td>\n")
    outfile.write("          </tr>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <td><em class=\"species\">Uca jocelynae</em></td>\n")
    outfile.write("            <td>" + format_reference_cite(refdict["Shih2010.1"], do_print, AUTHOR_PAREN, logfile) +
                  "</td>\n")
    outfile.write("          </tr>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <td><em class=\"species\">Uca splendida</em></td>\n")
    outfile.write("            <td>" +
                  format_reference_cite(refdict["Stimpson1858"], do_print, AUTHOR_PAREN, logfile) +
                  ", " + format_reference_cite(refdict["Shih2012"], do_print, AUTHOR_PAREN, logfile) + "</td>\n")
    outfile.write("          </tr>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <td><em class=\"species\">Uca boninensis</em></td>\n")
    outfile.write("            <td>" + format_reference_cite(refdict["Shih2013.2"], do_print, AUTHOR_PAREN, logfile) +
                  "</td>\n")
    outfile.write("          </tr>\n")
    outfile.write("        </tbody>\n")
    outfile.write("      </table>\n")
    outfile.write("      <table>\n")
    outfile.write("        <thead>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <th>Junior Subsynonym</th><th>Correct Name</th><th>Reference(s)</th>\n")
    outfile.write("          </tr>\n")
    outfile.write("        </thead>\n")
    outfile.write("        <tfoot>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <td colspan=\"3\"><strong>Note:</strong> <em class=\"species\">Uca australiae</em> "
                  "is probably not a valid species; it is based on a single specimen found washed up on the "
                  "Australian shore (" +
                  format_reference_cite(refdict["George1982"], do_print, AUTHOR_NOPAREN, logfile) +
                  ", among others)</td>\n")
    outfile.write("          </tr>\n")
    outfile.write("        </tfoot>\n")
    outfile.write("        <tbody>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <td><em class=\"species\">Uca minima</em></td>\n")
    outfile.write("            <td><em class=\"species\">Uca signata</em></td>\n")
    outfile.write("            <td>" + format_reference_cite(refdict["George1982"], do_print, AUTHOR_PAREN, logfile) +
                  "</td>\n")
    outfile.write("          </tr>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <td><em class=\"species\">Uca spinata</em></td>\n")
    outfile.write("            <td><em class=\"species\">Uca paradussumieri</em></td>\n")
    outfile.write("            <td>" + format_reference_cite(refdict["Dai1991"], do_print, AUTHOR_PAREN, logfile) +
                  "; " + format_reference_cite(refdict["Jones1994"], do_print, AUTHOR_PAREN, logfile) + "</td>\n")
    outfile.write("          </tr>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <td><em class=\"species\">Uca pacificensis</em></td>\n")
    outfile.write("            <td><em class=\"species\">Uca excisa</em></td>\n")
    outfile.write("            <td>Unpublished\n")
    outfile.write("          </tr>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <td><em class=\"species\">Uca leptochela</em></td>\n")
    outfile.write("            <td><em class=\"species\">Uca festae</em></td>\n")
    outfile.write("            <td>" +
                  format_reference_cite(refdict["Beinlich2006"], do_print, AUTHOR_PAREN, logfile) + "</td>\n")
    outfile.write("          </tr>\n")
    outfile.write("        </tbody>\n")
    outfile.write("      </table>\n")
    outfile.write("      <table>\n")
    outfile.write("        <thead>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <th>Incorrect Spelling</th>\n")
    outfile.write("            <th>Correct Spelling</th>\n")
    outfile.write("            <th>Reference(s)</th>\n")
    outfile.write("          </tr>\n")
    outfile.write("        </thead>\n")
    outfile.write("        <tbody>\n")
    outfile.write("          <tr> \n")
    outfile.write("            <td><em class=\"species\">Uca longidigita</em></td>\n")
    outfile.write("            <td><em class=\"species\">Uca longidigitum</em></td>\n")
    outfile.write("            <td>" +
                  format_reference_cite(refdict["vonHagen1989"], do_print, AUTHOR_PAREN, logfile) + "</td>\n")
    outfile.write("          </tr>\n")
    outfile.write("          <tr>\n")
    outfile.write("            <td><em class=\"species\">Uca mjobergi</em></td>\n")
    outfile.write("            <td><em class=\"species\">Uca mjoebergi</em></td>\n")
    outfile.write("            <td>" +
                  format_reference_cite(refdict["vonHagen1989"], do_print, AUTHOR_PAREN, logfile) + "</td>\n")
    outfile.write("          </tr>\n")
    outfile.write("        </tbody>\n")
    outfile.write("      </table>\n")
    outfile.write("      <p>\n")
    outfile.write(format_reference_cite(refdict["Crane1975"], do_print, AUTHOR_PAREN, logfile) +
                  " tended to lump related taxa into "
                  "subspecies rather than treat them as distinct species. A number of studies since that time "
                  "have raised virtually all of her subspecies to specific status (<em>e.g.,</em> " +
                  format_reference_cite(refdict["Barnwell1980"], do_print, AUTHOR_NOPAREN, logfile) + "; " +
                  format_reference_cite(refdict["Barnwell1984.1"], do_print, AUTHOR_NOPAREN, logfile) + "; " +
                  format_reference_cite(refdict["Collins1984"], do_print, AUTHOR_NOPAREN, logfile) + "; " +
                  format_reference_cite(refdict["Green1980"], do_print, AUTHOR_NOPAREN, logfile) + "; " +
                  format_reference_cite(refdict["Salmon1979.2"], do_print, AUTHOR_NOPAREN, logfile) + "; " +
                  format_reference_cite(refdict["Salmon1987.2"], do_print, AUTHOR_NOPAREN, logfile) + "; " +
                  format_reference_cite(refdict["Thurman1979"], do_print, AUTHOR_NOPAREN, logfile) + "; " +
                  format_reference_cite(refdict["Thurman1982"], do_print, AUTHOR_NOPAREN, logfile) + "; " +
                  format_reference_cite(refdict["vonHagen1989"], do_print, AUTHOR_NOPAREN, logfile) + "). "
                  "It has become common practice with many authors to ignore all of the subspecific designations "
                  "and treat each as a separate species (<em>e.g.,</em> " +
                  format_reference_cite(refdict["George1982"], do_print, AUTHOR_NOPAREN, logfile) + "; " +
                  format_reference_cite(refdict["Jones1994"], do_print, AUTHOR_NOPAREN, logfile) + "; " +
                  format_reference_cite(refdict["vonHagen1989"], do_print, AUTHOR_NOPAREN, logfile) + "). "
                  "I follow this practice throughout this website.\n")
    outfile.write("      </p>\n")
    outfile.write("    </section>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "")


def summarize_year(yeardict):
    miny = CURRENT_YEAR
    maxy = 0
    for y in yeardict:
        if y < miny:
            miny = y
        elif y > maxy:
            maxy = y
    datalist = []
    c = 0
    # year, total pubs, cumulative pubs, pubs with cite info
    for y in range(miny, maxy+1):
        if y in yeardict:
            c = c + yeardict[y][0]
            datalist.append([y, yeardict[y][0], c, yeardict[y][1]])
        else:
            datalist.append([y, 0, c, 0])

    datalist1900 = []
    for y in range(1900, maxy+1):
        if y in yeardict:
            datalist1900.append([y, yeardict[y][0], yeardict[y][1]])
        else:
            datalist1900.append([y, 0, 0])
    return datalist, datalist1900


def summarize_languages(refs):
    languages = {}
    for ref in refs:
        l = ref.language
        if l != "":
            s = l.find(" ")
            if s > -1:
                l = l[:s]
            if l in languages:
                languages[l] += 1
            else:
                languages[l] = 1
    return languages


def write_life_cycle_pages(outfile, do_print):
    """ create the life cycle page """
    if do_print:
        start_page_division(outfile, "base_page")
        media_path = MEDIA_PATH
    else:
        common_html_header(outfile, "Fiddler Crab Life Cycle", "")
        media_path = ""

    outfile.write("    <header id=\"" + LIFECYCLE_URL + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Life Cycle</h1>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <p>\n")
    outfile.write("      Following is a rough outline of the stages of the life of a fiddler crab. "
                  "The photographs are from a mix of species.\n")
    outfile.write("    </p>\n")
    outfile.write("\n")
    outfile.write("    <section class=\"spsection\">\n")
    outfile.write("      <h2 class=\"bookmark2\">Egg</h2>\n")
    outfile.write("      <p>\n")
    outfile.write("      Fertilized female fiddler crabs carry hundreds to thousands of eggs under their abdomen. "
                  "These are sometimes known as &ldquo;sponge&rdquo; crabs.\n")
    outfile.write("      </p>\n")
    outfile.write("      <figure class=\"lcpic\">\n")
    outfile.write("        <a href=\"photos/u_rapax10.html\"><img src=\"" + media_path +
                  "photos/U_rapax10tn.jpg\" "
                  "alt=\"Gravid female photo\" title=\"Gravid female\" /></a>\n")
    outfile.write("        <figcaption>Gravid female</figcaption>\n")
    outfile.write("      </figure>\n")
    outfile.write("      <figure class=\"lcpic\">\n")
    outfile.write("        <a href=\"photos/u_rapax11.html\"><img src=\"" + media_path +
                  "photos/U_rapax11tn.jpg\" "
                  "alt=\"Gravid female photo\" title=\"Gravid female\" /></a>\n")
    outfile.write("        <figcaption>Close up of eggs</figcaption>\n")
    outfile.write("      </figure>\n")
    outfile.write("    </section>\n")
    outfile.write("\n")
    outfile.write("    <section class=\"spsection\">\n")
    outfile.write("      <h2 class=\"bookmark2\">Zoea</h2>\n")
    outfile.write("      <p>\n")
    outfile.write("        When the eggs are ready, the mother goes into the water and allows the eggs to hatch "
                  "into microscopic free-swimming larvae. The early stage larvae are known as zoea.\n")
    outfile.write("      </p>\n")
    outfile.write("      <figure class=\"lcpic\">\n")
    outfile.write("        <a href=\"photos/u_ecuadoriensis07.html\"><img src=\"" + media_path +
                  "photos/U_ecuadoriensis07tn.jpg\" alt=\"zoea photo\" title=\"zoea\" /></a>\n")
    outfile.write("        <figcaption>Zoea</figcaption>\n")
    outfile.write("      </figure>\n")
    outfile.write("      <figure class=\"lcpic\">\n")
    outfile.write("        <a href=\"photos/u_ecuadoriensis08.html\"><img src=\"" + media_path +
                  "photos/U_ecuadoriensis08tn.jpg\" alt=\"zoea photo\" title=\"zoea\" /></a>\n")
    outfile.write("        <figcaption>Zoea</figcaption>\n")
    outfile.write("      </figure>\n")
    outfile.write("    </section>\n")
    outfile.write("\n")
    outfile.write("    <section class=\"spsection\">\n")
    outfile.write("    <h2 class=\"bookmark2\">Megalopa</h2>\n")
    outfile.write("      <p>\n")
    outfile.write("        The larvae live in the open water as part of the plankton. "
                  "As they grow and go through a number of molt stages. Older larvae are known as megalopa.\n")
    outfile.write("      </p>\n")
    outfile.write("      <figure class=\"lcpic\">\n")
    outfile.write("        <a href=\"photos/u_ecuadoriensis09.html\"><img src=\"" + media_path +
                  "photos/U_ecuadoriensis09tn.jpg\" alt=\"megalopa photo\" title=\"megalopa\" /></a>\n")
    outfile.write("        <figcaption>Megalopa</figcaption>\n")
    outfile.write("      </figure>\n")
    outfile.write("    </section>\n")
    outfile.write("\n")
    outfile.write("    <section class=\"spsection\">\n")
    outfile.write("    <h2 class=\"bookmark2\">Crab</h2>\n")
    outfile.write("      <p>\n")
    outfile.write("        At the end of the final larval stage, the larvae molt into immature crabs. "
                  "The amount of time spent as a swimming larvae (hatching to true crab stage) varies among "
                  "species, but ranges from a few weeks to a few months.\n")
    outfile.write("      </p>\n")
    outfile.write("      <figure class=\"lcpic\">\n")
    outfile.write("        <a href=\"photos/u_ecuadoriensis10.html\"><img src=\"" + media_path +
                  "photos/U_ecuadoriensis10tn.jpg\" alt=\"early stage crab photo\" title=\"early stage crab\" /></a>\n")
    outfile.write("        <figcaption>Early Stage Full Crab</figcaption>\n")
    outfile.write("      </figure>\n")
    outfile.write("      <p style=\"clear: both\">\n")
    outfile.write("        The crabs return to land and begin to grow; juvenile male and female crabs look "
                  "alike.\n")
    outfile.write("      </p>\n")
    outfile.write("      <figure class=\"lcpic\">\n")
    outfile.write("        <a href=\"photos/u_pugilator21.html\"><img src=\"" + media_path +
                  "photos/U_pugilator21tn.jpg\" alt=\"juveniles photo\" title=\"juveniles\" /></a>\n")
    outfile.write("        <figcaption>Juvenile Crabs</figcaption>\n")
    outfile.write("      </figure>\n")
    outfile.write("      <p style=\"clear: both\">\n")
    outfile.write("        As they grown larger and turn into adults, the secondary-sexual characteristics "
                  "(<em>e.g.</em>, the asymmetric claws) begin to develop. "
                  "Adult crabs mate and the cycle starts over.\n")
    outfile.write("      </p>\n")
    outfile.write("      <figure class=\"lcpic\">\n")
    outfile.write("        <a href=\"photos/u_tangeri10.html\"><img src=\"" + media_path +
                  "photos/U_tangeri10tn.jpg\" alt=\"adult female photo\" title=\"adult female\" /></a>\n")
    outfile.write("        <figcaption>Adult Female</figcaption>\n")
    outfile.write("      </figure>\n")
    outfile.write("      <figure class=\"lcpic\">\n")
    outfile.write("        <a href=\"photos/u_tangeri12.html\"><img src=\"" + media_path +
                  "photos/U_tangeri12tn.jpg\" alt=\"adult male photo\" title=\"adult male\" /></a>\n")
    outfile.write("        <figcaption>Adult Male</figcaption>\n")
    outfile.write("      </figure>\n")
    outfile.write("    </section>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "")


def write_phylogeny_pages(outfile, do_print, refdict, logfile):
    """ create the phylogeny page """
    treelist = {"tree_species.svg", "tree_subgenera.svg"}
    if do_print:
        start_page_division(outfile, "base_page")
        media_path = "resources/"
    else:
        common_html_header(outfile, "Fiddler Crab Phylogeny", "")
        media_path = ""
        # copy trees to webout directory
        for tree in treelist:
            try:
                shutil.copy2("resources/images/" + tree, WEBOUT_PATH + "images/")
            except FileNotFoundError:
                report_error(logfile, "File missing: resources/images/" + tree)
    outfile.write("    <header id=\"" + TREE_URL + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Phylogeny</h1>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <p>\n")
    outfile.write("     The phylogeny of fiddler crabs is still largely unresolved. Two trees are shown below: one "
                  "just the subgenera and one including all species. These are both rough, conservative estimates "
                  "based on combining information from " +
                  format_reference_cite(refdict["Levinton1996"], do_print, AUTHOR_PAREN, logfile) + ", " +
                  format_reference_cite(refdict["Sturmbauer1996"], do_print, AUTHOR_PAREN, logfile) + ", " +
                  format_reference_cite(refdict["Rosenberg2001"], do_print, AUTHOR_PAREN, logfile) + ", " +
                  format_reference_cite(refdict["Shih2009"], do_print, AUTHOR_PAREN, logfile) + ", " +
                  format_reference_cite(refdict["Shih2010.1"], do_print, AUTHOR_PAREN, logfile) + ", " +
                  format_reference_cite(refdict["Landstorfer2010"], do_print, AUTHOR_PAREN, logfile) + ", " +
                  format_reference_cite(refdict["Shih2012"], do_print, AUTHOR_PAREN, logfile) + ", " +
                  format_reference_cite(refdict["Shih2013"], do_print, AUTHOR_PAREN, logfile) + ", " +
                  format_reference_cite(refdict["Shih2013.2"], do_print, AUTHOR_PAREN, logfile) + ", and " +
                  format_reference_cite(refdict["Shih2015.2"], do_print, AUTHOR_PAREN, logfile) + ".\n")
    outfile.write("    </p>\n")
    outfile.write("\n")
    outfile.write("    <section class=\"spsection\">\n")
    outfile.write("      <h2 class=\"bookmark2\">Subgenera Phylogeny</h2>\n")
    outfile.write("      <object id=\"subgenera_phylogeny\" class=\"tree_figure\" data=\"" + media_path +
                  "images/tree_subgenera.svg\" type=\"image/svg+xml\"></object>\n")
    outfile.write("    </section>\n")
    outfile.write("    <section class=\"spsection\">\n")
    outfile.write("      <h2 class=\"bookmark2\">Species Phylogeny</h2>\n")
    outfile.write("      <object id=\"species_phylogeny\" class=\"tree_figure\" data=\"" + media_path +
                  "images/tree_species.svg\" type=\"image/svg+xml\"></object>\n")
    outfile.write("    </section>\n")
    outfile.write("\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "")


def morphology_link(parent, character):
    if parent == ".":
        return character.replace(" ", "_")
    else:
        return parent.replace(" ", "_") + "_" + character.replace(" ", "_")


def find_morphology_parent(p, mlist):
    x = ""
    for m in mlist:
        if p == m.character:
            x = morphology_link(m.parent, m.character)
    return x


def write_morphology_page(morph, morphlist, do_print, outfile, logfile):
    """ create individual pages for morphology descriptions """
    if morph.parent == ".":
        p = ""
    else:
        p = " (" + morph.parent + ")"
    if do_print:
        start_page_division(outfile, "morph_page")
        media_path = MEDIA_PATH + "morphology/"
    else:
        common_html_header(outfile, "Fiddler Crab Morphology: " + morph.character + p, "../")
        media_path = ""
    outfile.write("    <header id=\"" + morphology_link(morph.parent, morph.character) + ".html" + "\">\n")
    if do_print:
        outfile.write("      <h1 class=\"bookmark2\">" + morph.character + p + "</h1>\n")
    else:
        outfile.write("      <h1 class=\"bookmark2\">" + morph.character + "</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        if morph.parent != ".":
            outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "") +
                          find_morphology_parent(morph.parent, morphlist) + ".html\">" + morph.parent + "</a></li>\n")
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "../") + MORPH_URL +
                      "\">General Morphology</a></li>\n")
        if do_print:
            index_page = "#morphology_index.html"
        else:
            index_page = "."
        outfile.write("          <li><a href=\"" + index_page +
                      "\"><span class=\"fa fa-list\"></span> Morphology Index</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <div class=\"morphdesc\">\n")
    outfile.write("     <p>\n")
    outfile.write("       " + morph.description + "\n")
    outfile.write("     </p>\n")
    c = 0
    for m in morphlist:
        if m.parent == morph.character:
            c += 1
    if c > 0:
        outfile.write("     <h2>More Detail</h2>\n")
        outfile.write("     <ul>\n")
        for m in morphlist:
            if m.parent == morph.character:
                outfile.write("       <li><a href=\"" + rel_link_prefix(do_print, "") +
                              morphology_link(m.parent, m.character) + ".html\">" + m.character + "</a></li>\n")
        outfile.write("     </ul>\n")
    outfile.write("    </div>\n")
    if "|" in morph.image:
        plist = morph.image.split("|")
        clist = morph.caption.split("|")
    else:
        plist = [morph.image]
        clist = [morph.caption]
    for i in range(len(plist)):
        outfile.write("    <figure class=\"morphimg\">\n")
        outfile.write("      <img src=\"" + media_path + plist[i] + "\" alt=\"" + clist[i] + " image\" "
                      "title=\"" + clist[i] + "\" />\n")
        outfile.write("      <figcaption>" + clist[i] + "</figcaption>\n")
        outfile.write("    </figure>\n")
        if not do_print:
            # copy images to web output directory
            tmp_name = "morphology/" + plist[i]
            try:
                shutil.copy2(MEDIA_PATH + tmp_name, WEBOUT_PATH + "morphology/")
            except FileNotFoundError:
                report_error(logfile, "Missing file: " + tmp_name)
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "../")


def write_morphology_index(morphlist, do_print, outfile):
    """ create index for morphology pages """
    if do_print:
        start_page_division(outfile, "index_page")
    else:
        common_html_header(outfile, "Morphology Index", "../")
    outfile.write("    <header id=\"morphology_index.html\">\n")
    outfile.write("      <h1 class=\"bookmark2\">Morphology Index</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "../") + MORPH_URL +
                      "\">General Morphology</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("     <ul class=\"morphlist\">\n")
    uniquelist = {}
    for m in morphlist:
        if m.character in uniquelist:
            uniquelist[m.character] += 1
        else:
            uniquelist[m.character] = 1

    sortlist = []
    for m in morphlist:
        if uniquelist[m.character] > 1:
            sortlist.append([m.character + " (" + m.parent + ")", m])
        else:
            sortlist.append([m.character, m])
    sortlist.sort()
    for s in sortlist:
        m = s[1]
        if uniquelist[m.character] > 1:
            p = " ("+m.parent+")"
        else:
            p = ""
        outfile.write("      <li><a href=\"" + rel_link_prefix(do_print, "") + morphology_link(m.parent, m.character) +
                      ".html\">" + m.character + p + "</a></li>\n")
    outfile.write("     </ul>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, "../")


def write_main_morphology_pages(morphology, outfile, do_print, logfile):
    """ create page for general morphology descriptions """
    if do_print:
        start_page_division(outfile, "base_page")
        media_path = MEDIA_PATH
    else:
        common_html_header(outfile, "Fiddler Crab Morphology", "")
        media_path = ""
    outfile.write("    <header id=\"" + MORPH_URL + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Morphology</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        if do_print:
            index_page = "#morphology_index.html"
        else:
            index_page = "morphology/index.html"
        outfile.write("          <li><a href=\"" + index_page + "\"><span class=\"fa fa-list\"></span> "
                      "Index</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <div class=\"morphdesc\">\n")
    outfile.write("     <p>\n")
    outfile.write("      Fiddler crabs are decapod &ldquo;true crabs&rdquo; which much of the standard morphology "
                  "found within this group. The following sections briefly describe major morphological features "
                  "as well as characteristics that are often used to distinguish among species.\n")
    outfile.write("     </p>\n")
    outfile.write("      The morphology is organized hierarchically by major body component with further details "
                  "within each section.\n")
    outfile.write("     <p>\n")
    outfile.write("     </p>\n")
    outfile.write("     <h2 class=\"nobookmark\">More Detail</h2>\n")
    outfile.write("     <ul>\n")
    for m in morphology:
        if m.parent == ".":
            outfile.write("      <li><a href=\"" + rel_link_prefix(do_print, "morphology/") +
                          morphology_link(m.parent, m.character) + ".html\">" + m.character + "</a></li>\n")
    outfile.write("     </ul>\n")
    outfile.write("    </div>\n")
    outfile.write("    <figure class=\"morphimg\">\n")
    outfile.write("      <img src=\"" + media_path + "morphology/dorsal_view.png\" "
                  "alt=\"dorsal view of crab image\" title=\"dorsal view of crab\" />\n")
    outfile.write("      <figcaption>Figure modified from Crane (1975).</figcaption>\n")
    outfile.write("    </figure>\n")
    outfile.write("    <figure class=\"morphimg\">\n")
    outfile.write("      <img src=\"" + media_path + "morphology/ventral_view.png\" "
                  "alt=\"ventral view of crab image\" title=\"ventral view of crab\" />\n")
    outfile.write("      <figcaption>Figure modified from Crane (1975).</figcaption>\n")
    outfile.write("    </figure>\n")
    outfile.write("    <figure class=\"morphimg\">\n")
    outfile.write("      <img src=\"" + media_path + "morphology/anterior_view.png\" "
                  "alt=\"anterior view of crab image\" title=\"anterior view of crab\" />\n")
    outfile.write("      <figcaption>Figure modified from Crane (1975).</figcaption>\n")
    outfile.write("    </figure>\n")
    if do_print:
        end_page_division(outfile)
        write_morphology_index(morphology, do_print, outfile)
        for m in morphology:
            write_morphology_page(m, morphology, do_print, outfile, logfile)
    else:
        common_html_footer(outfile, "")
        for m in morphology:
            with codecs.open(WEBOUT_PATH + "morphology/" + morphology_link(m.parent, m.character) + ".html",
                             "w", "utf-8") as suboutfile:
                write_morphology_page(m, morphology, do_print, suboutfile, logfile)
        with codecs.open(WEBOUT_PATH + "morphology/index.html", "w", "utf-8") as suboutfile:
            write_morphology_index(morphology, do_print, suboutfile)


def write_citation_page(refdict):
    """ create page with site citation info """
    with codecs.open(WEBOUT_PATH + CITE_URL, "w", "utf-8") as outfile:
        common_html_header(outfile, "Fiddler Crab Website Citation", "")
        outfile.write("    <header id=\"" + CITE_URL + "\">\n")
        outfile.write("      <h1>Citation Info</h1>\n")
        outfile.write("    </header>\n")
        outfile.write("\n")
        outfile.write("    <p>\n")
        outfile.write("      Generally it is best to cite the primary literature, whenever possible. However, the "
                      "following paper describes much of the data that is unique to this website:\n")
        outfile.write("    </p>\n")
        outfile.write("    <div class=\"reference_list\">\n")
        outfile.write("      <ul>\n")
        ref = refdict["Rosenberg2014"]  # citation describing the database
        outfile.write("        <li><a href=\"references/Rosenberg2014.html\">" + ref.formatted_html + "</a></li>\n")
        outfile.write("      </ul>\n")
        outfile.write("    </div>\n")
        outfile.write("    <ul class=\"fa-ul\">\n")
        outfile.write("      <li><span class=\"fa-li fa fa-file-pdf-o\"></span>"
                      "<a href=\"http://dx.plos.org/10.1371/journal.pone.0101704\">Read paper online at "
                      "PLoS ONE</a></li>\n")
        outfile.write("      <li><span class=\"fa-li fa fa-github\"></span>"
                      "<a href=\"https://github.com/msrosenberg/fiddlercrab.info\">Website data repository on "
                      "Github</a></li>\n")
        outfile.write("    </ul>\n")
        common_html_footer(outfile, "")


def write_introduction(outfile, species, do_print):
    """ create the site index """
    if do_print:
        start_page_division(outfile, "base_page")
        outfile.write("    <header id=\"introduction\">\n")
        outfile.write("      <h1 class=\"bookmark1\">Introduction</h1>\n")
        outfile.write("    </header>\n")
    else:
        common_html_header(outfile, "Fiddler Crabs (Genus Uca)", "")
    outfile.write("    <p>\n")
    scnt = 0
    for s in species:
        if s.status != "fossil":
            scnt += 1
    outfile.write("      Fiddler crabs are small, semi-terrestrial crabs of the genus <em "
                  "class=\"species\">Uca</em> that are characterized by extreme cheliped asymmetry in males.  "
                  "They are most closely related to the <em class=\"species\">Ocypode</em> (ghost crabs). "
                  "<a href=\"" + rel_link_prefix(do_print, "") + SPECIES_URL + "\">There are currently {} recognized "
                  "extant species</a>.\n".format(scnt))
    outfile.write("    </p>\n")
    if do_print:
        media_path = MEDIA_PATH
    else:
        media_path = ""
    outfile.write("    <div class=\"indeximages\">\n")
    outfile.write("      <img class=\"thumbnail\" src=\"" + media_path +
                  "photos/U_mjoebergi04tn.jpg\" alt=\"Uca mjoebergi photo\" />\n")
    outfile.write("      <img class=\"thumbnail\" src=\"" + media_path +
                  "photos/U_minax07tn.jpg\" alt=\"Uca minax photo\" />\n")
    outfile.write("      <img class=\"thumbnail\" src=\"" + media_path +
                  "photos/U_crassipes19tn.jpg\" alt=\"Uca crassipes photo\" />\n")
    outfile.write("    </div>\n")
    outfile.write("\n")
    outfile.write("    <h2 class=\"nobookmark\">Classification</h2>\n")
    outfile.write("    <table>\n")
    outfile.write("      <tr><td class=\"classcol1\">Kingdom</td><td>Animalia</td></tr>\n")
    outfile.write("      <tr><td class=\"classcol1\">Phylum</td><td>Arthropoda</td></tr>\n")
    outfile.write("      <tr><td class=\"classcol1\">Class</td><td>Crustacea</td></tr>\n")
    outfile.write("      <tr><td class=\"classcol1\">Sub-class</td><td>Malocostraca</td></tr>\n")
    outfile.write("      <tr><td class=\"classcol1\">Order</td><td>Decapoda</td></tr>\n")
    outfile.write("      <tr><td class=\"classcol1\">Infraorder</td><td>Brachyura</td></tr>\n")
    outfile.write("      <tr><td class=\"classcol1\">Superfamily</td><td>Ocypodoidea</td></tr>\n")
    outfile.write("      <tr><td class=\"classcol1\">Family</td><td>Ocypodidae</td></tr>\n")
    outfile.write("      <tr><td class=\"classcol1\">Subfamily</td><td>Ocypodinae</td>\n")
    outfile.write("      <tr><td class=\"classcol1\">Genus</td><td><em class=\"species\">Uca</em></td>\n")
    outfile.write("    </table>\n")
    outfile.write("\n")
    outfile.write("    <p>\n")
    outfile.write("      The common English name &ldquo;Fiddler Crab&rdquo; comes from the feeding of the "
                  "males, where the movement of the small claw from the ground to its mouth "
                  "resembles the motion of a someone moving a bow across a fiddle (the large claw).\n")
    outfile.write("    </p>\n")
    if do_print:
        end_page_division(outfile)
    else:
        outfile.write("    <h2>Information</h2>\n")
        outfile.write("    <ul class=\"fa-ul\">\n")
        outfile.write("      <li><span class=\"fa-li fa fa-signal fa-rotate-270\"></span><a href=\"" + SYST_URL +
                      "\">Systematics</a></li>\n")
        outfile.write("      <li><span class=\"fa-li fa fa-share-alt fa-rotate-270\"></span><a href=\"" + TREE_URL +
                      "\">Phylogeny</a></li>\n")
        outfile.write("      <li><span class=\"fa-li fa fa-list\"></span><a href=\"" + SPECIES_URL + "\">Species</a>\n")
        outfile.write("        <ul>\n")
        outfile.write("           <li><a href=\"names\">Name Index</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </li>\n")
        outfile.write("      <li><span class=\"fa-li fa fa-comments-o\"></span><a href=\"" + COMMON_URL +
                      "\">Common Names</a></li>\n")
        outfile.write("      <li><span class=\"fa-li fa fa-map-o\"></span><a href=\"" + MAP_URL +
                      "\">Geographic Ranges</a></li>\n")
        outfile.write("      <li><span class=\"fa-li fa fa-refresh\"></span><a href=\"" + LIFECYCLE_URL +
                      "\">Life Cycle</a></li>\n")
        outfile.write("      <li><span class=\"fa-li fa fa-heart-o\"></span><a href=\"" + MORPH_URL +
                      "\">Morphology</a></li>\n")
        outfile.write("      <li><span class=\"fa-li fa fa-book\"></span><a href=\"" + REF_URL +
                      "\">Comprehensive Reference List</a></li>\n")
        outfile.write("    </ul>\n")
        outfile.write("    <h2>Multimedia</h2>\n")
        outfile.write("    <ul class=\"fa-ul\">\n")
        outfile.write("      <li><span class=\"fa-li fa fa-camera\"></span><a href=\"" + PHOTO_URL +
                      "\">Photos</a></li>\n")
        outfile.write("      <li><span class=\"fa-li fa fa-video-camera\"></span><a href=\"" + VIDEO_URL +
                      "\">Videos</a></li>\n")
        outfile.write("      <li><span class=\"fa-li fa fa-paint-brush\"></span>Art\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"" + ART_SCI_URL + "\">Scientific Art</a></li>\n")
        outfile.write("          <li><a href=\"" + ART_STAMP_URL + "\">Postage Stamps</a></li>\n")
        outfile.write("          <li><a href=\"" + ART_CRAFT_URL + "\">Crafts</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </li>\n")
        outfile.write("    </ul>\n")
        outfile.write("    <h2>Miscellania</h2>\n")
        outfile.write("    <ul class=\"fa-ul\">\n")
        outfile.write("      <li><span class=\"fa-li fa fa-pencil\"></span>"
                      "<a href=\"" + CITE_URL + "\">Citation info for this website</a></li>\n")
        outfile.write("      <li><span class=\"fa-li fa fa-github\"></span>"
                      "<a href=\"https://github.com/msrosenberg/fiddlercrab.info\">Website data on Github</a></li>\n")
        outfile.write("    </ul>\n")
        common_html_footer(outfile, "")


def create_output_paths():
    """
    create web output directories if they do not already exist
    add a blank index to each one
    """
    def create_path_and_index(subdir):
        if not os.path.exists(WEBOUT_PATH + subdir):
            os.makedirs(WEBOUT_PATH + subdir)
        create_blank_index(WEBOUT_PATH + subdir + "index.html")

    create_path_and_index("")
    create_path_and_index("photos/")
    create_path_and_index("video/")
    create_path_and_index("references/")
    create_path_and_index("names/")
    create_path_and_index("art/")
    create_path_and_index("morphology/")
    create_path_and_index("maps/")
    create_path_and_index("images/")
    create_path_and_index("locations/")
    # create path for temp files
    if not os.path.exists(TMP_PATH):
        os.makedirs(TMP_PATH)
    if not os.path.exists(MAP_PATH):
        os.makedirs(MAP_PATH)


def copy_support_files(logfile):
    filelist = {"favicon128.png",
                "favicon96.png",
                "favicon72.png",
                "favicon48.png",
                "favicon32.png",
                "favicon24.png",
                "favicon16.png",
                "favicon.ico",
                "apple-touch-icon.png",
                "apple-touch-icon-precomposed.png",
                "apple-touch-icon-72x72.png",
                "apple-touch-icon-72x72-precomposed.png",
                "apple-touch-icon-114x114.png",
                "apple-touch-icon-114x114-precomposed.png",
                "apple-touch-icon-144x144.png",
                "apple-touch-icon-144x144-precomposed.png",
                "uca_style.css"}
    for filename in filelist:
        try:
            shutil.copy2("resources/" + filename, WEBOUT_PATH)
        except FileNotFoundError:
            report_error(logfile, "Missing file: resources/" + filename)
    filelist = {"film.png",
                "stylifera75.png"}
    for filename in filelist:
        try:
            shutil.copy2("resources/images/" + filename, WEBOUT_PATH + "images/")
        except FileNotFoundError:
            report_error(logfile, "Missing file: resources/images/" + filename)


def copy_map_files(species, logfile):
    def copy_file(filename):
        try:
            shutil.copy2(filename, WEBOUT_PATH + "maps/")
        except FileNotFoundError:
            report_error(logfile, "Missing file: " + filename)

    # individual species maps
    for s in species:
        if s.status != "fossil":
            copy_file(MAP_PATH + "u_" + s.species + ".kmz")
            copy_file(MAP_PATH + "u_" + s.species + "_points.kmz")
            copy_file(MAP_PATH + "u_" + s.species + "_map.svg")
            copy_file(MAP_PATH + "u_" + s.species + "_point_map.svg")
    # combined map
    copy_file(MAP_PATH + "uca.kmz")
    copy_file(MAP_PATH + "uca_points.kmz")
    copy_file(MAP_PATH + "uca_map.svg")
    copy_file(MAP_PATH + "uca_point_map.svg")


def print_cover():
    pass
    # outfile.write("    <div id=\"cover_page\">\n")
    # outfile.write("    <div>\n")
    # outfile.write("\n")


def print_title_page(outfile):
    outfile.write("    <div id=\"title_page\">\n")
    outfile.write("     <p class=\"book_title\">Fiddler Crabs</p>\n")
    outfile.write("     <p class=\"book_subtitle\">Fiddler Crabs</p>\n")
    outfile.write("     <p>Michael S. Rosenberg</p>\n")
    outfile.write("     <p><a href=\"http://www.fiddlercrab.info\">www.fiddlercrab.info</a></p>\n")
    outfile.write("    </div>\n")
    outfile.write("\n")


def print_copyright_page(outfile):
    outfile.write("    <div id=\"copyright_page\">\n")
    outfile.write("     <p>Copyright &copy; 2003&ndash;" + str(CURRENT_YEAR) +
                  " by Michael S. Rosenberg. All Rights Reserved</p>\n")
    outfile.write("     <p>Release: " + VERSION + "</p>\n")
    outfile.write("     <p><a href=\"http://www.fiddlercrab.info\">www.fiddlercrab.info</a></p>\n")
    outfile.write("     <p>\n")
    outfile.write("       The data and code used to produce this document can be found on Github at "
                  "<a href=\"https://github.com/msrosenberg/fiddlercrab.info\">"
                  "https://github.com/msrosenberg/fiddlercrab.info</a> and "
                  "<a href=\"https://github.com/msrosenberg/TaxonomyMonographBuilder\">"
                  "https://github.com/msrosenberg/TaxonomyMonographBuilder</a>.\n")
    outfile.write("     </p>\n")
    outfile.write("     <p>\n")
    outfile.write("       Please cite this document as:"
                  "Rosenberg, M.S. (xxxx) www.fiddlercrab.info, release " + VERSION + ".\n")
    outfile.write("     </p>\n")

    outfile.write("    </div>\n")
    outfile.write("\n")
    """
    outfile.write("    <p>\n")
    outfile.write("      Generally it is best to cite the primary literature, whenever possible. However, the "
                  "following paper describes much of the data that is unique to this website:\n")
    outfile.write("    </p>\n")
    outfile.write("    <div class=\"reference_list\">\n")
    outfile.write("      <ul>\n")
    ref = refdict["Rosenberg2014"]  # citation describing the database
    outfile.write("        <li><a href=\"references/Rosenberg2014.html\">" + ref.formatted_html + "</a></li>\n")
    outfile.write("      </ul>\n")
    outfile.write("    </div>\n")
    outfile.write("    <ul class=\"fa-ul\">\n")
    outfile.write("      <li><span class=\"fa-li fa fa-file-pdf-o\"></span>"
                  "<a href=\"http://dx.plos.org/10.1371/journal.pone.0101704\">Read paper online at "
                  "PLoS ONE</a></li>\n")
    outfile.write("      <li><span class=\"fa-li fa fa-github\"></span>"
                  "<a href=\"https://github.com/msrosenberg/fiddlercrab.info\">Website data repository on "
                  "Github</a></li>\n")
    outfile.write("    </ul>\n")
    """


def print_table_of_contents(outfile, species_list):
    outfile.write("    <div id=\"table_of_contents\">\n")
    outfile.write("     <h1 class=\"bookmark1\">Table of Contents</h1>\n")
    outfile.write("     <ul>\n")
    outfile.write("       <li><a href=\"#introduction\">Introduction</a></li>\n")
    outfile.write("       <li><a href=\"#" + COMMON_URL + "\">Common Names</a></li>\n")
    outfile.write("       <li><a href=\"#" + SYST_URL + "\">Systematics Overview</a>\n")
    outfile.write("         <ul>\n")
    outfile.write("           <li><a href=\"#genus\">Genus</a></li>\n")
    outfile.write("           <li><a href=\"#subgenera\">Subgenera</a></li>\n")
    outfile.write("           <li><a href=\"#species\">Species</a></li>\n")
    outfile.write("         </ul>\n")
    outfile.write("       </li>\n")
    outfile.write("       <li><a href=\"#" + TREE_URL + "\">Phylogeny</a></li>\n")
    outfile.write("       <li><a href=\"#" + MAP_URL + "\">Geography</a></li>\n")
    outfile.write("       <li><a href=\"#" + LIFECYCLE_URL + "\">Life Cycle</a></li>\n")
    outfile.write("       <li><a href=\"#" + MORPH_URL + "\">Morphology</a></li>\n")
    outfile.write("       <li><a href=\"#" + SPECIES_URL + "\">Species</a>\n")
    outfile.write("         <ul>\n")
    for species in species_list:
        outfile.write("           <li>" + create_species_link(species.species, "", "", True) + "</li>\n")
    outfile.write("         </ul>\n")
    outfile.write("       </li>\n")

    outfile.write("       <li><a href=\"#name_index\">Name Index</a>\n")
    outfile.write("         <ul>\n")
    outfile.write("           <li><a href=\"#binomials\">Binomials and Other Compound Names</a>\n")
    outfile.write("           <li><a href=\"#specificnames\">Specific Names</a>\n")
    outfile.write("           <li><a href=\"#" + NAME_SUM_URL + "\">Summary of Names</a>\n")
    outfile.write("         </ul>\n")
    outfile.write("       </li>\n")
    outfile.write("       <li><a href=\"#" + PHOTO_URL + "\">Photo Index</a></li>\n")
    outfile.write("       <li><a href=\"#" + VIDEO_URL + "\">Video Index</a></li>\n")
    outfile.write("       <li>Art\n")
    outfile.write("         <ul>\n")
    outfile.write("           <li><a href=\"#" + ART_SCI_URL + "\">Scientific Drawings</a></li>\n")
    outfile.write("           <li><a href=\"#" + ART_STAMP_URL + "\">Postage Stamps</a></li>\n")
    outfile.write("           <li><a href=\"#" + ART_CRAFT_URL + "\">Arts &amp; Crafts</a></li>\n")
    outfile.write("         </ul>\n")
    outfile.write("       </li>\n")
    outfile.write("       <li>References\n")
    outfile.write("         <ul>\n")
    outfile.write("           <li><a href=\"#" + REF_SUM_URL + "\">Summary of References</a></li>\n")
    outfile.write("           <li><a href=\"#" + REF_URL + "\">Full Reference List</a></li>\n")
    outfile.write("         </ul>\n")
    outfile.write("       </li>\n")
    outfile.write("     </ul>\n")
    outfile.write("    </div>\n")
    outfile.write("\n")


def print_specific_pages(outfile, species):
    # print_cover(outfile)
    print_title_page(outfile)
    print_copyright_page(outfile)
    print_table_of_contents(outfile, species)


def start_print(outfile):
    outfile.write("<!DOCTYPE HTML>\n")
    outfile.write("<html lang=\"en\">\n")
    outfile.write("  <head>\n")
    outfile.write("    <meta charset=\"utf-8\" />\n")
    outfile.write("    <title>Fiddler Crabs</title>\n")
    outfile.write("    <link rel=\"stylesheet\" href=\"resources/uca_style.css\" />\n")
    outfile.write("    <link rel=\"stylesheet\" href=\"resources/print.css\" />\n")
    outfile.write("    <link rel=\"stylesheet\" href=\"resources/images/font-awesome/css/font-awesome.min.css\" />\n")
    outfile.write("  </head>\n")
    outfile.write("\n")
    outfile.write("  <body>\n")


def end_print(outfile):
    outfile.write("  </body>\n")
    outfile.write("</html>\n")


def build_site(init_data):
    create_output_paths()
    with codecs.open(init_data.error_log, "w", "utf-8") as logfile:
        # read data and do computation
        print("...Reading References...")
        (references, refdict, citelist,
         yeardict, citecount) = TMB_Import.read_reference_data(init_data.reference_ciation_file,
                                                               init_data.reference_file,
                                                               init_data.citation_info_file,
                                                               logfile)
        clean_references(references)
        yeardat, yeardat1900 = summarize_year(yeardict)
        languages = summarize_languages(references)
        print("...Reading Species...")
        species = TMB_Import.read_species_data(init_data.species_data_file)
        print("...Connecting References...")
        compute_species_from_citation_linking(citelist)
        compute_applied_name_contexts(citelist)
        species_refs = connect_refs_to_species(species, citelist)
        print("...Reading Species Names...")
        specific_names = TMB_Import.read_specific_names_data(init_data.specific_names_file)
        (all_names, binomial_name_cnts, specific_name_cnts, genus_cnts, total_binomial_year_cnts,
         name_table, specific_point_locations,
         binomial_point_locations) = calculate_name_index_data(refdict, citelist, specific_names)
        common_name_data = TMB_Import.read_common_name_data(init_data.common_names_file)
        subgenera = TMB_Import.read_subgenera_data(init_data.subgenera_file)
        print("...Reading Photos and Videos...")
        photos = TMB_Import.read_photo_data(init_data.photo_file)
        videos = TMB_Import.read_video_data(init_data.video_file)
        art = TMB_Import.read_art_data(init_data.art_file)
        morphology = TMB_Import.read_morphology_data(init_data.morphology_file)
        point_locations = TMB_Import.read_location_data(init_data.location_file)
        location_dict = create_location_hierarchy(point_locations, logfile)
        print("...Creating Maps...")
        # write_all_locations(point_locations)
        if SHOW_NEW:
            TMB_Create_Maps.create_all_species_maps(init_data, species, point_locations, citelist, logfile)
            TMB_Create_Maps.create_all_name_maps(all_names, specific_names, point_locations,
                                                 specific_point_locations, binomial_point_locations)

        # temp location
        with codecs.open(WEBOUT_PATH + "locations/index.html", "w", "utf-8") as outfile:
            write_location_pages(outfile, False, point_locations, location_dict)

        # output website version
        if False:
            print("...Creating Web Version...")
            copy_support_files(logfile)
            print("......Writing References......")
            with codecs.open(WEBOUT_PATH + REF_URL, "w", "utf-8") as outfile:
                write_reference_bibliography(references, False, outfile, logfile)
            with codecs.open(WEBOUT_PATH + REF_SUM_URL, "w", "utf-8") as outfile:
                write_reference_summary(len(references), yeardat, yeardat1900, citecount, languages, False, outfile)
            write_reference_pages(references, refdict, citelist, False, None, logfile, name_table)
            print("......Writing Names Info......")
            with codecs.open(WEBOUT_PATH + "names/index.html", "w", "utf-8") as outfile:
                write_all_name_pages(refdict, citelist, all_names, specific_names, name_table, species_refs, genus_cnts,
                                     binomial_name_cnts, total_binomial_year_cnts, outfile, False, logfile)
            check_specific_names(citelist, specific_names, logfile)
            print("......Writing Species......")
            write_species_info_pages(species, references, specific_names, all_names, photos, videos, art, species_refs,
                                     refdict, binomial_name_cnts, specific_name_cnts, logfile, None, False)
            copy_map_files(species, logfile)
            with codecs.open(WEBOUT_PATH + SYST_URL, "w", "utf-8") as outfile:
                write_systematics_overview(subgenera, species, refdict, outfile, False, logfile)
            with codecs.open(WEBOUT_PATH + COMMON_URL, "w", "utf-8") as outfile:
                write_common_names_pages(outfile, replace_references(common_name_data, refdict, False, logfile), False)
            with codecs.open(WEBOUT_PATH + PHOTO_URL, "w", "utf-8") as outfile:
                write_photo_index(species, photos, False, outfile, logfile)
            write_all_art_pages(art, False, None, logfile)
            with codecs.open(WEBOUT_PATH + VIDEO_URL, "w", "utf-8") as outfile:
                write_video_index(videos, False, outfile, logfile)
            with codecs.open(WEBOUT_PATH + MAP_URL, "w", "utf-8") as outfile:
                write_geography_page(species, outfile, False)
            with codecs.open(WEBOUT_PATH + LIFECYCLE_URL, "w", "utf-8") as outfile:
                write_life_cycle_pages(outfile, False)
            with codecs.open(WEBOUT_PATH + TREE_URL, "w", "utf-8") as outfile:
                write_phylogeny_pages(outfile, False, refdict, logfile)
            with codecs.open(WEBOUT_PATH + MORPH_URL, "w", "utf-8") as outfile:
                write_main_morphology_pages(morphology, outfile, False, logfile)
            with codecs.open(WEBOUT_PATH + "index.html", "w", "utf-8") as outfile:
                write_introduction(outfile, species, False)
            write_citation_page(refdict)

        # output print version
        if False:
            print("...Creating Print Version...")
            with codecs.open("print.html", "w", "utf-8") as printfile:
                start_print(printfile)
                print_specific_pages(printfile, species)
                write_introduction(printfile, species, True)
                write_common_names_pages(printfile, replace_references(common_name_data, refdict, True, logfile), True)
                write_systematics_overview(subgenera, species, refdict, printfile, True, logfile)
                write_phylogeny_pages(printfile, True, refdict, logfile)
                write_geography_page(species, printfile, True)
                write_life_cycle_pages(printfile, True)
                write_main_morphology_pages(morphology, printfile, True, logfile)
                print("......Writing Species Pages......")
                write_species_info_pages(species, references, specific_names, all_names, photos, videos, art,
                                         species_refs, refdict, binomial_name_cnts, specific_name_cnts, logfile,
                                         printfile, True)
                print("......Writing Name Pages......")
                write_all_name_pages(refdict, citelist, all_names, specific_names, name_table, species_refs, genus_cnts,
                                     binomial_name_cnts, total_binomial_year_cnts, printfile, True, logfile)
                print("......Writing Media Pages......")
                write_photo_index(species, photos, True, printfile, logfile)
                write_video_index(videos, True, printfile, logfile)
                write_all_art_pages(art, True, printfile, logfile)
                print("......Writing Reference Pages......")
                write_reference_summary(len(references), yeardat, yeardat1900, citecount, languages, True, printfile)
                write_reference_bibliography(references, True, printfile, logfile)
                write_reference_pages(references, refdict, citelist, True, printfile, logfile, name_table)
                end_print(printfile)
    print("done")


def main():
    # will eventually need to put options here for choosing different paths, etc.
    init_data = TMB_Initialize.initialize()
    # will need to read options from file
    build_site(init_data)


if __name__ == "__main__":
    main()
