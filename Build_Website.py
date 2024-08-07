"""
Taxonomy Monograph Builder
"""

# built-in dependencies
import datetime
import random
import os
import shutil
import re
import math
import collections
from typing import Optional, Tuple, TextIO
import numpy
# local dependencies
import TMB_Import
import TMB_Create_Maps
from TMB_Error import report_error
import TMB_Error
from TMB_Common import *
import TMB_Initialize
import TMB_Classes
import TMB_Create_Graphs
import TMB_TaxKeyGen
import TMB_Measurements
from TMB_SpeciesXRef import init_species_crossref, find_species_by_name
import phy2html


WEBOUT_PATH = "webout/"
MEDIA_PATH = "media/"
TMP_PATH = "temp/"
TMP_MAP_PATH = TMP_PATH + "maps/"

FOSSIL_IMAGE = " <span class=\"fossil-img\">&#9760;</span>"
STAR = "<sup>*</sup>"
DAGGER = "<sup>†</sup>"
DOUBLEDAGGER = "<sup>‡</sup>"

CitationStyle = int
AUTHOR_NOPAREN = 0      # Smith 1970
AUTHOR_PAREN = 1        # Smith (1970)
AUTHOR_TAXON = 2        # Smith, 1970  <-- this one is needed for taxonomic name authority

# this flag is to hide/display new materials still in progress from the general release
SHOW_NEW = True
# this flag can be used to suppress redrawing all of the maps, which is fairly time-consuming
DRAW_MAPS = True
# this flag suppresses creation of output files, allowing data integrity checking without the output time cost
CHECK_DATA = False
# this flag creates the location web pages only; it is for checking changes and not general use
CHECK_LOCATIONS = False
# this flag controls whether additional location data should be fetched from iNaturalist
INCLUDE_INAT = True
# Suppress some of the more time-consuming output; only meant for when testing others elements
OUTPUT_REFS = True
OUTPUT_LOCS = True
# these flags control creating print and web output, respectively
OUTPUT_PRINT = False
OUTPUT_WEB = True

# randSeed = random.randint(0, 10000)


def init_data() -> TMB_Initialize.InitializationData:
    return TMB_Initialize.INIT_DATA


def remove_html(x: str) -> str:
    """
    remove any stray html tags from string before using as title of html document
    """
    regex = r"<.+?>"
    return re.sub(regex, "", x)


def common_header_part1(outfile: TextIO, title: str, indexpath: str = "") -> None:
    """
    part 1 of the common header for all webout html files
    """
    outfile.write("<!DOCTYPE HTML>\n")
    outfile.write("<html lang=\"en\">\n")
    outfile.write("  <head>\n")
    outfile.write("  <!-- Google tag (gtag.js) -->\n")
    outfile.write("  <script async src=\"https://www.googletagmanager.com/gtag/js?id=G-94FNMMTWTQ\"></script>\n")
    outfile.write("  <script>\n")
    outfile.write("    window.dataLayer = window.dataLayer || [];\n")
    outfile.write("    function gtag(){dataLayer.push(arguments);}\n")
    outfile.write("    gtag('js', new Date());\n")
    outfile.write("    gtag('config', 'G-94FNMMTWTQ');\n")
    outfile.write("  </script>\n")
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
    outfile.write("    <link rel=\"stylesheet\" href=\"" + indexpath + "uca_style.css\" />\n")
    outfile.write("    <script defer src=\"" + indexpath + "js/solid.min.js\"></script>\n")
    outfile.write("    <script defer src=\"" + indexpath + "js/regular.min.js\"></script>\n")
    outfile.write("    <script defer src=\"" + indexpath + "js/brands.min.js\"></script>\n")
    outfile.write("    <script defer src=\"" + indexpath + "js/fontawesome.min.js\"></script>\n")
    outfile.write("    <link rel=\"stylesheet\" href=\"" + indexpath +
                  "images/flag-icon-css/css/flag-icons.min.css\" />\n")
    outfile.write("    <link rel=\"author\" href=\"" + init_data().site_author_email + "\" />\n")


def common_header_part2(outfile: TextIO, indexpath: str = "", include_map: bool = False) -> None:
    """
    part 2 of the common header for all webout html files
    """
    outfile.write("  </head>\n")
    outfile.write("\n")
    if include_map:
        outfile.write("  <body onload=\"initialize()\">\n")
    else:
        outfile.write("  <body>\n")
    outfile.write("    <div id=\"skip-links\" role=\"complementary\" aria-label=\"Skip links menu\">")
    outfile.write("<a href=\"#Main\" tabindex=\"1\">Skip to content</a></div>\n")
    outfile.write("    <div id=\"home\">\n")
    outfile.write("      <a href=\"" + indexpath + "index.html\" class=\"home-title\">Fiddler Crabs</a>\n")
    outfile.write("      <a href=\"" + indexpath +
                  "index.html\" class=\"home-link\">" + fetch_fa_glyph("home") + "Home</a>\n")
    # outfile.write("      <a href=\"" + indexpath +
    #               "blog\" class=\"home-link\">" + fetch_fa_glyph("blog") + "Blog</a>\n")
    outfile.write("    </div>\n")


def start_google_map_header(outfile: TextIO) -> None:
    """
    start of common header entries for webout html files which contain Google maps elements
    """
    outfile.write("    <script type=\"text/javascript\"\n")
    outfile.write("      src=\"https://maps.googleapis.com/maps/api/js?"
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


def end_google_map_header(outfile: TextIO) -> None:
    """
    end of common header entries for webout html files which contain Google maps elements
    """
    outfile.write("      }\n")
    outfile.write("    </script>\n")


def write_google_map_range_header(outfile: TextIO, map_name: str) -> None:
    """
    common header entries for webout html files which contain Google maps elements - range map version
    """
    outfile.write("        var range_map = new google.maps.Map(document.getElementById(\"range_map_canvas\"),"
                  "mapOptions);\n")
    outfile.write("        var range_layer = new google.maps.KmlLayer(\"" + init_data().site_url() + "/maps/" +
                  rangemap_name(map_name) + ".kmz\",{suppressInfoWindows: true});\n")
    outfile.write("        range_layer.setMap(range_map);\n")


# def write_google_map_point_header(outfile: TextIO, map_name: str,
#                                   location: Optional[TMB_Classes.LocationClass]) -> None:
#     """
#     common header entries for webout html files which contain Google maps elements - point map version
#     """
#     do_bounds = False
#     preserve = ""
#     if location is not None:
#         if location.sw_lon is not None:
#             do_bounds = True
#             preserve = ", preserveViewport: true"
#
#     outfile.write("        var point_map = new google.maps.Map(document.getElementById(\"point_map_canvas\"),"
#                   "mapOptions);\n")
#     outfile.write("        var point_layer = "
#                   "new google.maps.KmlLayer(\"" + init_data().site_url() + "/maps/" + pointmap_name(map_name) +
#                   ".kmz\",{suppressInfoWindows: false" + preserve + "});\n")
#     outfile.write("        point_layer.setMap(point_map);\n")
#     if do_bounds:
#         outfile.write("        var necorner = new google.maps.LatLng(" +
#                       str(location.ne_lat) + ", " + str(location.ne_lon) + ");\n")
#         outfile.write("        var swcorner = new google.maps.LatLng(" +
#                       str(location.sw_lat) + ", " + str(location.sw_lon) + ");\n")
#         outfile.write("        var bounds = new google.maps.LatLngBounds(swcorner, necorner);\n")
#         outfile.write("        point_map.fitBounds(bounds);\n")


def write_google_map_point_header(outfile: TextIO, map_name: str) -> None:
    """
    common header entries for webout html files which contain Google maps elements - point map version
    """
    outfile.write("        var point_map = new google.maps.Map(document.getElementById(\"point_map_canvas\"),"
                  "mapOptions);\n")
    outfile.write("        var point_layer = "
                  "new google.maps.KmlLayer(\"" + init_data().site_url() + "/maps/" + pointmap_name(map_name) +
                  ".kmz\",{suppressInfoWindows: false});\n")
    outfile.write("        point_layer.setMap(point_map);\n")


def start_google_chart_header(outfile: TextIO) -> None:
    """
    start of common header entries for webout html files which contain Google chart elements
    """
    outfile.write("    <script type=\"text/javascript\" src=\"https://www.google.com/jsapi\"></script>\n")
    outfile.write("    <script type=\"text/javascript\">\n")
    outfile.write("      google.load(\"visualization\", \"1\", {packages:[\"corechart\"]});\n")
    outfile.write("      google.setOnLoadCallback(drawChart);\n")
    outfile.write("      function drawChart() {\n")


def end_google_chart_header(outfile: TextIO) -> None:
    """
    end of common header entries for webout html files which contain Google maps elements - range map version
    """
    outfile.write("      }\n")
    outfile.write("    </script>\n")


def common_html_header(outfile: TextIO, title: str, indexpath: str = "") -> None:
    """
    write common header for webout html files without special scripts
    """
    common_header_part1(outfile, title, indexpath=indexpath)
    common_header_part2(outfile, indexpath=indexpath)


def common_html_footer(outfile: TextIO, indexpath: str = "") -> None:
    """
    common footer and closing elements for all webout html files
    """
    outfile.write("\n")
    outfile.write("    <footer>\n")
    outfile.write("       <figure id=\"footmap\"><script type=\"text/javascript\" "
                  "src=\"//rf.revolvermaps.com/0/0/4.js?i=5f9t1sywiez&amp;m=0&amp;h=75&amp;c=ff0000&amp;r=30\" "
                  "async=\"async\"></script><figcaption>Visitors</figcaption></figure>\n")
    outfile.write("       <p id=\"citation\"><a href=\"" + indexpath + init_data().cite_url +
                  "\">" + fetch_fa_glyph("site cite") + "How to cite this site</a></p>\n")
    outfile.write("       <p id=\"contact\">Questions or comments about the site? Contact "
                  "<a href=\"mailto:" + init_data().site_author_email + "\">" + fetch_fa_glyph("mail") +
                  "Dr. Michael S. Rosenberg</a></p>\n")
    outfile.write("       <p id=\"copyright\">Release: " + init_data().version +
                  " &mdash; Copyright &copy; 2003&ndash;" + str(init_data().current_year) +
                  " All Rights Reserved</p>\n")
    outfile.write("    </footer>\n")
    outfile.write("  </body>\n")
    outfile.write("</html>\n")


def start_page_division(outfile: TextIO, page_class: str) -> None:
    """
    write start page information for print output
    """
    outfile.write("  <div class=\"" + page_class + "\">\n")


def end_page_division(outfile: TextIO) -> None:
    """
    write end page information for print output
    """
    outfile.write("  </div>\n")


def create_blank_index(fname: str) -> None:
    """
    create a blank index.html file for webout directories to prevent browsers from listing containing files
    """
    with open(fname, "w") as outfile:
        outfile.write("<!DOCTYPE HTML>\n")
        outfile.write("<html lang=\"en\">\n")
        outfile.write("  <head>\n")
        outfile.write("    <meta charset=\"utf-8\" />\n")
        outfile.write("    <title>n/a</title>\n")
        outfile.write("    <meta name=\"description\" content=\"n/a\" />\n")
        outfile.write("  </head>\n")
        outfile.write("  <body>\n")
        outfile.write("  </body>\n")
        outfile.write("</html>\n")


def fetch_fa_glyph(glyph: Optional[str]) -> str:
    """
    decorate text with a fontawesome glyph

    centralized function to create fontawesome decoration based on specified glyph keyword/style
    """
    if glyph is None:
        return ""
    else:
        x = "<span  role=\"presentation\" class=\"fa"
        if glyph == "home":
            x += " fa-home\" aria-hidden"
        elif glyph == "blog":
            x += " fa-pencil-alt\" aria-hidden"
        elif glyph == "mail":
            x += " fa-envelope\" aria-hidden"
        elif glyph == "site cite":
            x += " fa-pencil-alt\" aria-hidden"
        elif glyph == "index":
            x += " fa-list\" aria-hidden"
        elif glyph == "summary charts":
            x += " fa-chart-line\" aria-hidden"
        elif glyph == "location":
            x += " fa-map-marker-alt\" aria-hidden"
        elif glyph == "citation":
            x += " fa-edit\" aria-hidden"
        elif glyph == "specimen":
            x += " fa-flask\" aria-hidden"
        elif glyph == "sequence":
            x += " fa-dna\" aria-hidden"
        elif glyph == "original":
            x += " fa-arrow-alt-left\" aria-hidden"
        elif glyph == "computed":
            x += " fa-cogs\" aria-hidden"
        elif glyph == "geography":
            x += "r fa-map\" aria-hidden"
        elif glyph == "synonymy":
            x += " fa-exchange\" aria-hidden"
        elif glyph == "specific name":
            x += " fa-window-minimize\" aria-hidden"
        elif glyph == "info":
            x += " fa-info-circle\" aria-hidden"
        elif glyph == "accepted species":
            x += " fa-check-circle\" aria-hidden"
        elif glyph == "download":
            x += " fa-download\" aria-hidden"
        elif glyph == "file download":
            x += " fa-file-download\" aria-hidden"
        elif glyph == "maps":
            x += "r fa-map\" aria-hidden"
        elif glyph == "photo":
            x += " fa-camera-alt\" aria-hidden"
        elif glyph == "video":
            x += " fa-video\" aria-hidden"
        elif glyph == "references":
            x += " fa-book\" aria-hidden"
        elif glyph == "art":
            x += " fa-paint-brush\" aria-hidden"
        elif glyph == "measure":
            x += "r fa-ruler\" aria-hidden"
        elif glyph == "handedness":
            x += " fa-hands\" aria-hidden"
        elif glyph == "list pdf":
            x += "-li far fa-file-pdf\" aria-hidden"
        elif glyph == "list github":
            x += "-li fab fa-github\" aria-hidden"
        elif glyph == "list systematics":
            x += "-li fa fa-signal fa-rotate-270\" aria-hidden"
        elif glyph == "list phylogeny":
            x += "-li fa fa-share-alt fa-rotate-270\" aria-hidden"
        elif glyph == "list species":
            x += "-li fa fa-list\" aria-hidden"
        elif glyph == "list common":
            x += "-li far fa-comments\" aria-hidden"
        elif glyph == "list ranges":
            x += "-li far fa-map\" aria-hidden"
        elif glyph == "list morphology":
            x += "-li far fa-heart\" aria-hidden"
        elif glyph == "list references":
            x += "-li fa fa-book\" aria-hidden"
        elif glyph == "list lifecycle":
            x += "-li fa fa-sync\" aria-hidden"
        elif glyph == "list photo":
            x += "-li fa fa-camera-alt\" aria-hidden"
        elif glyph == "list video":
            x += "-li fa fa-video\" aria-hidden"
        elif glyph == "list art":
            x += "-li fa fa-paint-brush\" aria-hidden"
        elif glyph == "list site cite":
            x += "-li fa fa-pencil-alt\" aria-hidden"
        elif glyph == "list unusual dev":
            x += "-li fa fa-transgender-alt\" aria-hidden"
        elif glyph == "bad location":
            x += " fa-exclamation-triangle\" style=\"color: red\" title=\"Problematic Location: Outside range of " \
                 "all fiddler crabs or this particular species.\""
        elif glyph == "questionable id":
            x += " fa-question-circle\" style=\"color: goldenrod\" title=\"Questionable ID: Species identity " \
                 "uncertain.\""
        elif glyph == "tax key":
            x += " fa-key\" ara-hidden"
        elif glyph == "location marker":
            x += "r fa-map-marked-alt\" ara-hidden"
        else:
            report_error("missing glyph: " + glyph)
            return ""
        return x + "></span> "


def rel_link_prefix(do_print: bool, prefix: str = "") -> str:
    if do_print:
        return "#"
    else:
        return prefix


def abs_link_prefix(do_absolute: bool) -> str:
    if do_absolute:
        return init_data().site_url() + "/"
    else:
        return ""


def format_reference_full(ref: TMB_Classes.ReferenceClass, do_print: bool) -> str:
    if ref.cite_key == "<pending>":
        return ref.formatted_html
    else:
        try:
            return ("<a href=\"" + rel_link_prefix(do_print, "references/") + ref.cite_key + ".html\">" +
                    ref.formatted_html + "</a>")
        except LookupError:
            report_error("missing label: " + ref.cite_key)
            return ref.cite_key


def format_reference_cite(ref: TMB_Classes.ReferenceClass, do_print: bool, author_style: CitationStyle,
                          path: str = "") -> str:
    if author_style == AUTHOR_PAREN:  # Smith (1900)
        outstr = ref.citation
    elif author_style == AUTHOR_NOPAREN:  # Smith 1900
        outstr = ref.author() + " " + str(ref.year())
    elif author_style == AUTHOR_TAXON:  # Smith, 1900
        if ref.taxon_author is not None:  # used to avoid et al. or for papers with slightly unusual authority
            outstr = ref.taxon_author
        else:
            outstr = ref.author() + ", " + str(ref.year())
    else:
        outstr = ref.citation
    if ref.cite_key == "<pending>":
        return outstr
    else:
        try:
            return ("<a href=\"" + rel_link_prefix(do_print, path + "references/") + ref.cite_key +
                    ".html\">" + outstr + "</a>")
        except LookupError:
            report_error("missing label: " + ref.cite_key)
            return ref.cite_key


def replace_species_in_string(instr: str, include_link: bool = False, do_print: bool = False, path: str = "") -> str:
    search_str = r"{{(?P<species>.+?)}}"
    # for every species tagged in the string
    for match in re.finditer(search_str, instr):
        # look up full species name
        name = match.group("species")
        if name.startswith("+"):
            include_authority = True
            name = name[1:]
        else:
            include_authority = False
        s = find_species_by_name(name)
        if include_link:
            name_str = create_species_link(s.genus, s.species, do_print, s.status, path=path)
        else:
            name_str = "<em class=\"species\">" + s.binomial() + "</em>"
        if include_authority:
            a = " " + s.authority()
        else:
            a = ""
        instr = re.sub(search_str, name_str + a, instr, 1)
    return instr


def replace_species_references(in_list: list) -> list:
    out_list = []
    for line in in_list:
        out_list.append(replace_species_in_string(line))
    return out_list


def replace_reference_in_string(instr: str, refdict: dict, do_print: bool, path: str = "") -> str:
    search_str = r"\[\[(?P<key>.+?),(?P<format>.+?)\]\]"
    # for every citation reference in the string
    for match in re.finditer(search_str, instr):
        # create the new link text
        ref = refdict[match.group("key")]
        if match.group("format") == ".out":
            link_str = format_reference_cite(ref, do_print, AUTHOR_PAREN, path=path)
        elif match.group("format") == ".in":
            link_str = format_reference_cite(ref, do_print, AUTHOR_NOPAREN, path=path)
        else:
            link_str = "<a href=\"" + rel_link_prefix(do_print, path + "references/") + ref.cite_key + ".html\">" + \
                       match.group("format") + "</a>"
        # replace the cross-reference with the correct text
        instr = re.sub(search_str, link_str, instr, 1)
    return instr


def replace_references(in_list: list, refdict: dict, do_print: bool, path: str = "") -> list:
    out_list = []
    for line in in_list:
        out_list.append(replace_reference_in_string(line, refdict, do_print, path))
    return out_list


def connect_type_references(species: list, refdict: dict) -> None:
    """
    function to replace species type reference keys with point to reference object
    """
    for s in species:
        s.type_reference = refdict[s.type_reference]


def clean_reference_html(ref: str) -> str:
    """
    add slightly better formatting to html formatted references
      in particular, replace hyphens with n-dashes for commonly seen ranges
    """
    # replace hyphens with an n-dash in page ranges
    sstr = r"((?:Pp\. |:)[\D]?[\d]+)(-)([\D]?[\d]+)"
    ref = re.sub(sstr, r"\1&ndash;\3", ref)

    # replace hyphens with an n-dash in volume ranges
    sstr = r"(\([\d]+)(-)([\d]+\))"
    ref = re.sub(sstr, r"\1&ndash;\3", ref)

    # remove (?) from entries with unknown years
    ref = ref.replace(" (?) ", " ")
    return ref


def clean_references(references: list) -> None:
    for ref in references:
        ref.formatted_html = clean_reference_html(ref.formatted_html)


def format_language(x: str) -> str:
    """
    beautify language listings for references by adding flag icons for each language and replacing the word
    'and' with an ampersand
    """
    # language_replace_list = [
    #     [" and ", " &amp; "],
    #     ["German", "<span class=\"flag-icon flag-icon-de\"></span> German"],
    #     ["Spanish", "<span class=\"flag-icon flag-icon-es\"></span> Spanish"],
    #     ["Russian", "<span class=\"flag-icon flag-icon-ru\"></span> Russian"],
    #     ["French", "<span class=\"flag-icon flag-icon-fr\"></span> French"],
    #     ["Portuguese", "<span class=\"flag-icon flag-icon-pt\"></span> Portuguese"],
    #     ["Danish", "<span class=\"flag-icon flag-icon-dk\"></span> Danish"],
    #     ["Dutch", "<span class=\"flag-icon flag-icon-nl\"></span> Dutch"],
    #     ["Japanese", "<span class=\"flag-icon flag-icon-jp\"></span> Japanese"],
    #     ["Chinese", "<span class=\"flag-icon flag-icon-cn\"></span> Chinese"],
    #     ["English", "<span class=\"flag-icon flag-icon-us\"></span> English"],
    #     ["Thai", "<span class=\"flag-icon flag-icon-th\"></span> Thai"],
    #     ["Latin", "<span class=\"flag-icon flag-icon-va\"></span> Latin"],
    #     ["Italian", "<span class=\"flag-icon flag-icon-it\"></span> Italian"],
    #     ["Vietnamese", "<span class=\"flag-icon flag-icon-vn\"></span> Vietnamese"],
    #     ["Korean", "<span class=\"flag-icon flag-icon-kr\"></span> Korean"],
    #     ["Polish", "<span class=\"flag-icon flag-icon-pl\"></span> Polish"],
    #     ["Arabic", "<span class=\"flag-icon flag-icon-sa\"></span> Arabic"],
    #     ["Indonesian", "<span class=\"flag-icon flag-icon-id\"></span> Indonesian"],
    #     ["Afrikaans", "<span class=\"flag-icon flag-icon-za\"></span> Afrikaans"],
    #     ["Malay", "<span class=\"flag-icon flag-icon-my\"></span> Malay"],
    #     ["Malagasy", "<span class=\"flag-icon flag-icon-mg\"></span> Malagasy"],
    #     ["Persian", "<span class=\"flag-icon flag-icon-ir\"></span> Persian"],
    #     ["Burmese", "<span class=\"flag-icon flag-icon-mm\"></span> Burmese"]
    # ]
    language_replace_list = [
        [" and ", " &amp; "],
        ["German", "<span class=\"fi fi-de\"></span> German"],
        ["Spanish", "<span class=\"fi fi-es\"></span> Spanish"],
        ["Russian", "<span class=\"fi fi-ru\"></span> Russian"],
        ["French", "<span class=\"fi fi-fr\"></span> French"],
        ["Portuguese", "<span class=\"fi fi-pt\"></span> Portuguese"],
        ["Danish", "<span class=\"fi fi-dk\"></span> Danish"],
        ["Dutch", "<span class=\"fi fi-nl\"></span> Dutch"],
        ["Japanese", "<span class=\"fi fi-jp\"></span> Japanese"],
        ["Chinese", "<span class=\"fi fi-cn\"></span> Chinese"],
        ["English", "<span class=\"fi fi-us\"></span> English"],
        ["Thai", "<span class=\"fi fi-th\"></span> Thai"],
        ["Latin", "<span class=\"fi fi-va\"></span> Latin"],
        ["Italian", "<span class=\"fi fi-it\"></span> Italian"],
        ["Vietnamese", "<span class=\"fi fi-vn\"></span> Vietnamese"],
        ["Korean", "<span class=\"fi fi-kr\"></span> Korean"],
        ["Polish", "<span class=\"fi fi-pl\"></span> Polish"],
        ["Arabic", "<span class=\"fi fi-sa\"></span> Arabic"],
        ["Indonesian", "<span class=\"fi fi-id\"></span> Indonesian"],
        ["Afrikaans", "<span class=\"fi fi-za\"></span> Afrikaans"],
        ["Malay", "<span class=\"fi fi-my\"></span> Malay"],
        ["Malagasy", "<span class=\"fi fi-mg\"></span> Malagasy"],
        ["Persian", "<span class=\"fi fi-ir\"></span> Persian"],
        ["Burmese", "<span class=\"fi fi-mm\"></span> Burmese"]
    ]
    for r in language_replace_list:
        x = x.replace(r[0], r[1])
    return x


def write_reference_summary(outfile: TextIO, do_print: bool, nrefs: int, year_data: list, year_data_1900: list,
                            cite_count: int, languages, languages_by_year: dict) -> None:
    if do_print:
        start_page_division(outfile, "")
    else:
        common_header_part1(outfile, "Fiddler Crab Reference Summary")
        start_google_chart_header(outfile)
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
        for lang in langlist:
            outfile.write("          ['" + lang + "', " + str(languages[lang]) + "],\n")
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
        end_google_chart_header(outfile)
        common_header_part2(outfile)

    outfile.write("    <header id=\"" + init_data().ref_sum_url + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Summary of References</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print) + init_data().ref_url +
                      "\">" + fetch_fa_glyph("index") + "Full Reference List</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <p>\n")
    outfile.write("      A summary of the references  in the database (last updated {}).\n".
                  format(datetime.date.isoformat(datetime.date.today())))
    outfile.write("      " + str(cite_count) + " of " + str(nrefs) +
                  " references  have had citation data recorded.\n")
    outfile.write("      See also the <a href=\"" + rel_link_prefix(do_print, "names/") + init_data().name_sum_url +
                  "\">name summary page</a> for information on reference patterns to specific species.\n")
    outfile.write("    </p>\n")
    if do_print:
        # pie chart of languages
        filename = "language_pie.png"
        TMB_Create_Graphs.create_pie_chart_file(filename, languages, init_data().graph_font)
        outfile.write("    <h3 class=\"nobookmark\">Primary Language of References</h3>\n")
        outfile.write("    <figure class=\"graph\">\n")
        outfile.write("      <img src=\"" + TMP_PATH + filename + "\" class=\"pie_chart\" />\n")
        outfile.write("    </figure>\n")

        # bar chart of languages by year
        filename = "year_language_bar.png"
        TMB_Create_Graphs.create_language_bar_chart_file(filename, languages_by_year, init_data().graph_font)
        outfile.write("    <h3 class=\"nobookmark\">Proportion of References in Primary Language each Year</h3>\n")
        outfile.write("    <figure class=\"graph\">\n")
        outfile.write("      <img src=\"" + TMP_PATH + filename + "\" class=\"bar_chart\" />\n")
        outfile.write("    </figure>\n")

        # pubs per year bar chart
        miny = init_data().current_year
        maxy = init_data().start_year
        for y in year_data:
            miny = min(miny, y[0])
            maxy = max(maxy, y[0])

        filename = "pubs_per_year_bar.png"
        TMB_Create_Graphs.create_bar_chart_file(filename, year_data, miny, maxy, 1, init_data().graph_font)
        outfile.write("    <h3 class=\"nobookmark\">References by Year</h3>\n")
        outfile.write("    <figure class=\"graph\">\n")
        outfile.write("      <img src=\"" + TMP_PATH + filename + "\" class=\"bar_chart\" />\n")
        outfile.write("    </figure>\n")

        # pubs per year since 1900 bar chart
        filename = "pubs_per_year_1900_bar.png"
        TMB_Create_Graphs.create_bar_chart_file(filename, year_data_1900, 1900, maxy, 1, init_data().graph_font)
        outfile.write("    <h3 class=\"nobookmark\">References by Year (since 1900)</h3>\n")
        outfile.write("    <figure class=\"graph\">\n")
        outfile.write("      <img src=\"" + TMP_PATH + filename + "\" class=\"bar_chart\" />\n")
        outfile.write("    </figure>\n")

        # citation data in database
        filename = "pubs_per_year_1900_complete_bar.png"
        tmp_dat = []
        for y in year_data_1900:
            tmp_dat.append([y[2], y[1] - y[2]])
        dat_info = [["Citations in DB", 0], ["Pending", 1]]
        TMB_Create_Graphs.create_stacked_bar_chart_file(filename, tmp_dat, 1900, maxy, dat_info, init_data().graph_font)
        outfile.write("    <h3 class=\"nobookmark\">References with Citation Data in Database (since 1900; all "
                      "pre-1900 literature is complete)</h3>\n")
        outfile.write("    <figure class=\"graph\">\n")
        outfile.write("      <img src=\"" + TMP_PATH + filename + "\" class=\"bar_chart\" />\n")
        outfile.write("    </figure>\n")

        # cumulative publications line chart
        filename = "cumulative_pubs_line.png"
        TMB_Create_Graphs.create_line_chart_file(filename, year_data, miny, maxy, 2, init_data().graph_font)
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
        common_html_footer(outfile)


def write_reference_bibliography(outfile: TextIO, do_print: bool, reflist: list) -> None:
    if do_print:
        start_page_division(outfile, "index_page")
    else:
        common_html_header(outfile, "Fiddler Crab Publications")
    outfile.write("    <header id=\"" + init_data().ref_url + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Full Reference List</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print) + init_data().ref_sum_url +
                      "\">" + fetch_fa_glyph("summary charts") + "Reference/Citation Summary</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <p>\n")
    outfile.write("      Following is a fairly comprehensive list of papers, books, and theses that deal or refer "
                  "to fiddler crabs. The list currently contains {:0,} references "
                  "(last updated {}).\n".format(len(reflist), datetime.date.isoformat(datetime.date.today())))
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
    # for ref in tqdm(reflist):
    for ref in reflist:
        outfile.write("          <li>" + format_reference_full(ref, do_print) + "</li>\n")
    outfile.write("        </ul>\n")
    outfile.write("      </div>\n")
    outfile.write("    </section>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile)


def create_name_table(citelist: list) -> dict:
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


def match_num_ref(x: str, y: str) -> bool:
    if (("." in x) and ("." in y)) or (("." not in x) and ("." not in y)):
        return x == y
    elif "." in x:
        return x[:x.find(".")] == y
    else:
        return y[:y.find(".")] == x


def compute_applied_name_contexts(citelist: list) -> None:
    """
    function to gather list of primary contexts referred to by other citation entries
    """
    for i, cite in enumerate(citelist):
        if (cite.context == "specimen") or (cite.context == "location") or (cite.context == "sequence"):
            cite.applied_cites = {cite}
        elif cite.context == "citation":
            for j in range(i):  # only look at entries up to the current one
                tmp = citelist[j]
                if (tmp.cite_key == cite.application) and match_num_ref(tmp.name_key, cite.cite_n):
                    if (tmp.context == "specimen") or (tmp.context == "location") or (tmp.context == "sequence"):
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


def compute_species_from_citation_linking(citelist: list) -> None:
    """
    function to update correct species citations through cross-references to earlier works
    """
    # for i, cite in enumerate(tqdm(citelist)):
    unrecorded_xrefs = []
    recorded_refs = set()
    for i, cite in enumerate(citelist):
        recorded_refs.add(cite.cite_key)
        if cite.actual == "=":
            cname = ""
            crossnames = collections.Counter()
            for j in range(i):  # only look at entries up to the current one
                tmp = citelist[j]
                if (tmp.cite_key == cite.application) and match_num_ref(tmp.name_key, cite.cite_n):
                    cname = tmp.name
                    crossnames.update([tmp.actual])
            if len(crossnames) == 0:
                unrecorded_xrefs.append([cite.cite_key, cite.application, cite.name_key, cite.cite_n])
            elif len(crossnames) == 1:
                cite.actual = list(crossnames.keys())[0]
            else:
                # find name(s) with largest count
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

    for x in unrecorded_xrefs:
        if x[1] in recorded_refs:
            report_error("Reference {} ({}) does not appear until after citation from {} ({})".format(x[1], x[3],
                                                                                                      x[0], x[2]))


def create_species_link(genus: str, species: str, do_print: bool, status: str = "", path: str = "") -> str:
    if status == "fossil":
        sc = FOSSIL_IMAGE
    else:
        sc = ""
    return ("<a href=\"" + rel_link_prefix(do_print, path) + "u_" + species + ".html\"><em class=\"species\">" + genus +
            " " + species + "</em>" + sc + "</a>")


def rank_tags(x: str) -> Tuple[str, str]:
    if ("genus" in x) or ("species" in x):
        return "<em class=\"species\">", "</em>"
    else:
        return "", ""


def create_taxon_link(rank: str, name: str, do_print: bool, same_page: bool = False, path: str = "",
                      include_rank: bool = True) -> str:
    """
    create a link to a higher-order taxonomic entry
    """
    start_tag, end_tag = rank_tags(rank)
    if same_page:
        x = ""
    else:
        x = path + init_data().syst_url
    if include_rank:
        rc = rank.capitalize() + " "
    else:
        rc = ""
    return "<a href=\"" + rel_link_prefix(do_print, x + "#") + \
           "{0}_{1}\">{2}{3}{1}{4}</a>".format(rank, name, rc, start_tag, end_tag)


def create_location_link(location: TMB_Classes.LocationClass, display_name: str, do_print: bool, path: str = "",
                         mark_unknown: bool = False, mark_secondary: bool = False, inc_icon: bool = False) -> str:
    if mark_unknown and location.unknown:
        suffix = DAGGER
    elif mark_secondary:
        suffix = STAR
    else:
        suffix = ""
    if do_print:  # put the suffix inside the link when printing
        endstr = suffix + "</a>"
    else:  # put the suffix outside the link for the web
        endstr = "</a>" + suffix
    if inc_icon:
        iconstr = fetch_fa_glyph("location marker")
    else:
        iconstr = ""
    return ("<a href=\"" + rel_link_prefix(do_print, path) + place_to_filename(location.name) + ".html\">" +
            iconstr + display_name + endstr)


def strip_location_subtext(x: str) -> str:
    """
    remove extra information from a location string when present
    """
    # remove <!> indicator from locations
    x = x.replace("<!>", "").strip()
    x = x.replace("<?>", "").strip()
    # remove information in []'s from a location string
    if "[" in x:
        x = x[:x.find("[") - 1]
    return x


def format_name_string(x: str) -> str:
    """
    properly emphasize species names, but not non-name signifiers
    """
    # get rid of [#] when present
    if "{" in x:
        x = x[:x.find("{")-1]
    if "var." in x.lower():
        p = x.lower().find("var.")
        return "<em class=\"species\">" + x[:p] + "</em> " + x[p:p+4] + " <em class=\"species\">" + x[p+4:] + "</em>"
    elif " var " in x.lower():  # need the spaces around var, because some names have the letters var in them
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


def clean_specific_name(x: str) -> str:
    """
    function to extract the specific names from binomials
    """

    # this is a list of terms that are not actual species names or specific names that have never been part of
    # a fiddler genus
    skip_list = ("sp.",
                 "spp.",
                 "spp",
                 "var.",
                 "nov.",
                 "a",
                 "ete",
                 "panema",
                 "pagurus",
                 "quadratus",
                 "albidus",
                 "vociferans",
                 "raniformis",
                 "nigra",
                 "albicans",
                 "arenarius",
                 "raninus",
                 "serratus",
                 "cordimana",
                 "spec.",
                 "complex",
                 "5",
                 "6",
                 "1",
                 "afruca",
                 "gelasimus")

    # if (" " not in x) or ("(" in x):
    #     return ""
    # else:
    #     if "{" in x:
    #         x = x[:x.find("{")-1]
    #     y = x.split(" ")
    #     x = y[len(y)-1].lower()
    #     if (x in skip_list) or ("gruppe" in x) or ("group" in x) or ("complex" in x):
    #         return ""
    #     else:
    #         return x.lower()

    # regex = r"\(.+?\)"
    # x = re.sub(regex, "", x)
    # regex = r"[.+?]"
    # x = re.sub(regex, "", x)

    if x.endswith(")") or (" " not in x):
        return ""
    if "{" in x:
        x = x[:x.find("{")-1]
    y = x.split(" ")
    x = y[len(y)-1].lower()
    if (x in skip_list) or ("gruppe" in x) or ("group" in x) or ("complex" in x):
        return ""
    return x.lower()


def output_name_table(outfile: TextIO, do_print: bool, is_name: bool, itemlist: list, unique_set: set,
                      notecnt: int, comcnt: int, refdict: dict, name_table: dict, point_locations: dict) -> None:
    """
    create output name table for reference and name pages
    """

    def create_location_sublink(x: str) -> str:
        """
        create a link to location pages, preserving [] info when applicable
        """
        tmpname = strip_location_subtext(x)
        if tmpname in point_locations:
            loc = point_locations[tmpname]
            tmpstr = create_location_link(loc, tmpname, do_print, path="../locations/")
            if tmpname != x:
                tmpstr += x[len(tmpname):]
                tmpstr = tmpstr.replace("<!>", fetch_fa_glyph("bad location"))
                # tmpstr = tmpstr.replace("<?>", fetch_fa_glyph("questionable id"))
                tmpstr = tmpstr.replace("<?>", "").strip()
        else:
            tmpstr = x
        return tmpstr

    # ---main part of loop---
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
        if nref in unique_set:
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
            unique_set -= {nref}
        else:
            outfile.write("      <td>&nbsp;</td>\n")
            if comcnt > 0:
                outfile.write("      <td>&nbsp;</td>\n")
            outfile.write("      <td>&nbsp;</td>\n")

        # applies to...
        if n.context == "location":
            outstr = create_location_sublink(n.application)
            outfile.write("      <td>" + fetch_fa_glyph("location") + "location: " + outstr + "</td>\n")
        elif n.context == "citation":
            if n.application in refdict:
                crossref = refdict[n.application]
                if n.application in name_table:
                    nstr = n.cite_n
                    if nstr == "0":
                        outfile.write("      <td>" + fetch_fa_glyph("citation") + "citation: "
                                      "<a href=\"" + rel_link_prefix(do_print, "../references/") + crossref.cite_key +
                                      ".html\">" + crossref.citation + "</a></td>\n")
                    else:
                        if "." in nstr:
                            try:
                                extraref = " [" + name_table[n.application][nstr][1] + "]"
                                refname = name_table[n.application][nstr][0]
                            except LookupError:
                                if is_name:  # only print errors on one pass
                                    report_error("Error in citation: " + n.cite_key + " cites" + nstr +
                                                 " in " + n.application)
                                extraref = ""
                                refname = ""
                        else:
                            extraref = ""                                
                            try:
                                refname = name_table[n.application][int(nstr)]
                            except ValueError:
                                report_error("Citation " + n.cite_key + " tried to cite " + n.application +
                                             " #" + nstr)
                                refname = ""
                        outfile.write("      <td>" + fetch_fa_glyph("citation") + "citation: "
                                      "<a href=\"" + rel_link_prefix(do_print, "../references/") + crossref.cite_key +
                                      ".html\">" + crossref.citation + "</a> → " + format_name_string(refname) +
                                      extraref + "</td>\n")
                else:
                    outfile.write("      <td>" + fetch_fa_glyph("citation") + "citation: "
                                  "<a href=\"" + rel_link_prefix(do_print, "../references/") + crossref.cite_key +
                                  ".html\">" + crossref.citation + "</a></td>\n")
            else:
                outfile.write("      <td>" + fetch_fa_glyph("citation") + "citation: " + n.application +
                              "</td>\n")
                if is_name and not do_print:  # only print on one pass
                    report_error("Citation not in DB: " + n.cite_key + " cites " + n.application)
        elif n.context == "specimen":
            if n.application == "?":
                outfile.write("      <td>" + fetch_fa_glyph("specimen") + "specimen: unknown locality</td>\n")
            else:
                outstr = create_location_sublink(n.application)
                outfile.write("      <td>" + fetch_fa_glyph("specimen") + "specimen: " + outstr + "</td>\n")
        elif n.context == "sequence":
            if n.application == "?":
                outfile.write("      <td>" + fetch_fa_glyph("sequence") + "sequence: unknown locality</td>\n")
            else:
                outstr = create_location_sublink(n.application)
                outfile.write("      <td>" + fetch_fa_glyph("sequence") + "sequence: " + outstr + "</td>\n")

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
        elif n.actual.startswith(">"):
            outfile.write("      <td><em class=\"species\">" + n.actual[1:] + "</em></td>\n")
        elif n.actual.startswith("#"):
            t_rank, t_name = n.actual[1:].split("#")
            outfile.write("      <td>" + create_taxon_link(t_rank, t_name, do_print, path="../") + "</td>\n")
        else:
            s = find_species_by_name(n.actual)
            if "<?>" in n.application:
                glyphstr = " " + fetch_fa_glyph("questionable id")
            else:
                glyphstr = ""
            outfile.write("      <td><a href=\"" + rel_link_prefix(do_print, "../") + "u_" + n.actual +
                          ".html\"><em class=\"species\">" + s.binomial() + "</em></a>" + glyphstr + "</td>\n")

        # source of accepted species
        if n.source == ".":  # currently not listed
            outfile.write("      <td>&nbsp;</td>\n")
        elif n.source == "<":  # original name retained
            outfile.write("      <td>" + fetch_fa_glyph("original") + "Original</td>\n")
        elif n.source == "=":  # automatically computer
            outfile.write("      <td>" + fetch_fa_glyph("computed") + "Computed</td>\n")
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
                    tmpsource = tmpsource.replace("geography", fetch_fa_glyph("geography") + "Geography")
                    tmpsource = tmpsource.replace("synonymy", fetch_fa_glyph("synonymy") + "Synonymy")
                    source_strs.append(tmpsource)
            outfile.write("      <td>" + ", ".join(source_strs) + "</td>\n")

        # notes
        if notecnt > 0:
            if n.name_note == ".":
                outfile.write("      <td>&nbsp;</td>\n")
            else:
                outfile.write("      <td>" + replace_species_in_string(n.name_note) + "</td>\n")
        outfile.write("    </tr>\n")
    outfile.write("    </table>\n")


def check_citation_cross_references(citelist: list, refdict: dict, name_table: dict) -> None:
    for c in citelist:
        if c.context == "citation":
            if c.application in refdict:
                if c.application in name_table:
                    nstr = c.cite_n
                    if nstr == "0":
                        pass
                    else:
                        if "." in nstr:
                            try:
                                _ = name_table[c.application][nstr][1]
                                _ = name_table[c.application][nstr][0]
                            except LookupError:
                                report_error("Error in citation: " + c.cite_key + " cites" + nstr +
                                             " in " + c.application)
                        else:
                            try:
                                _ = name_table[c.application][int(nstr)]
                            except ValueError:
                                report_error("Citation " + c.cite_key + " tried to cite " + c.application +
                                             " #" + nstr + " (Value error)")
                            except KeyError:
                                report_error("Citation " + c.cite_key + " tried to cite " + c.application +
                                             " #" + nstr + " (Key error)")
            else:
                report_error("Citation not in DB: " + c.cite_key + " cites " + c.application)


def write_reference_page(outfile: TextIO, do_print: bool, ref: TMB_Classes.ReferenceClass, citelist: list,
                         refdict: dict, name_table: dict, point_locations: dict) -> None:
    """
    create output page for a reference
    """
    if do_print:
        start_page_division(outfile, "ref_page")
    else:
        common_html_header(outfile, ref.citation, indexpath="../")
    outfile.write("    <header id=\"" + ref.cite_key + ".html\">\n")
    outfile.write("      <h2 class=\"nobookmark\">" + ref.formatted_html + "</h2>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"../" + init_data().ref_url +
                      "\">" + fetch_fa_glyph("index") + "Full Reference List</a></li>\n")
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
            outfile.write("      " + replace_species_in_string(n.general_note) + "\n")
        if n.common != ".":
            comcnt += 1
        if n.name_note != ".":
            notecnt += 1
        uniquenames |= {n.name}
    if started_note:
        outfile.write("    </p>\n")

    if ref.language != "":
        outfile.write("<p><strong>Language:</strong> " + format_language(ref.language) + "</p>\n")
    if ref.doi is not None:
        outfile.write("<p><strong>Online:</strong> ")
        if ref.doi.startswith("10"):
            outfile.write("<img src=\"../images/DOI_logo.svg\" style=\"height: 1em; vertical-align: middle\" "
                          "alt=\"DOI\"> ")
            outfile.write("<a href=\"https://doi.org/{0}\">https://doi.org/{0}</a></p>\n".format(ref.doi))
        else:
            outfile.write("{0}</p>\n".format(ref.doi))

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
        output_name_table(outfile, do_print, False, names, uniquenames, notecnt, comcnt, refdict, name_table,
                          point_locations)
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
                cs |= {"<a href=\"" + rel_link_prefix(do_print) + crossref.cite_key +
                       ".html\">" + crossref.citation + "</a>"}
            else:
                cs |= {c.cite_key}
        cl = []
        for x in cs:
            cl.append(x)
        cl.sort()
        outfile.write("     " + ", ".join(cl) + "\n")
        outfile.write("    </p>\n")

    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, indexpath="../")


def write_reference_pages(printfile: Optional[TextIO], do_print: bool, reflist: list, refdict: dict,
                          citelist: list, name_table: dict, point_locations: dict) -> None:
    """
    control function to loop through creating a page for every reference
    """
    # for ref in tqdm(reflist):
    for ref in reflist:
        if ref.cite_key != "<pending>":
            if do_print:
                write_reference_page(printfile, do_print, ref, citelist, refdict, name_table, point_locations)
            else:
                with open(WEBOUT_PATH + "references/" + ref.cite_key + ".html", "w", encoding="utf-8") as outfile:
                    write_reference_page(outfile, do_print, ref, citelist, refdict, name_table, point_locations)


def clean_name(x: str) -> str:
    """
    function to clean up names so that variation such as punctuation does not prevent a match
    """
    x = x.replace(", var.", " var.")
    if "{" in x:
        x = x[:x.find("{")-1]
    return x


def calculate_binomial_yearly_cnts(name: str, refdict: dict, citelist: list) -> Tuple[dict, int]:
    miny = init_data().start_year
    maxy = init_data().current_year
    # find citations for this name
    cites = []
    for c in citelist:
        clean = clean_name(c.name)
        if clean.lower() == name.lower():
            cites.append(c)
    unique_cites = set()
    for c in cites:
        unique_cites |= {c.cite_key}
    name_by_year = {y: 0 for y in range(miny, maxy+1)}
    total = 0
    for c in unique_cites:
        y = refdict[c].year()
        if y is not None:
            if miny <= y <= maxy:
                name_by_year[y] += 1
                total += 1
    return name_by_year, total


def write_binomial_name_page(outfile: TextIO, do_print: bool, name: str, namefile: str, name_by_year: dict,
                             refdict: dict, citelist: list, name_table: dict, species_name: str, location_set: set,
                             point_locations: dict) -> None:
    """
    create a page listing all citations using (and other information about) a specific binomial or compound name
    """
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

    miny = init_data().start_year
    maxy = init_data().current_year
    maxcnt = max(name_by_year.values())
    image_name = ""
    if do_print:
        start_page_division(outfile, "name_page")
        if maxcnt > 0:
            image_name = name_to_filename(name) + "_chronology.png"
            TMB_Create_Graphs.create_chronology_chart_file(image_name,  miny, maxy, maxcnt, name_by_year,
                                                           init_data().graph_font)
    else:
        common_header_part1(outfile, name, indexpath="../")
        if len(location_set) > 0:
            start_google_map_header(outfile)
            write_google_map_point_header(outfile, "name_" + name)
            end_google_map_header(outfile)

        if maxcnt > 0:
            start_google_chart_header(outfile)
            image_name = 0
            setup_chronology_chart(outfile, image_name, miny, maxy, maxcnt, name_by_year)
            end_google_chart_header(outfile)
        common_header_part2(outfile, indexpath="../", include_map=True)

    outfile.write("    <header id=\"" + namefile + ".html\" class=\"tabular_page\">\n")
    outfile.write("      <h1 class=\"nobookmark\">" + format_name_string(name) + "</h1>\n")
    outfile.write("      <nav>\n")
    outfile.write("        <ul>\n")
    if species_name != "":
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print) + "sn_" + species_name +
                      ".html\">" + fetch_fa_glyph("specific name") + format_name_string(species_name) +
                      "</a></li>\n")
        if not do_print:
            outfile.write("          <li><a href=\"index.html\">" + fetch_fa_glyph("index") + "Full Name "
                          "Index</a></li>\n")
    outfile.write("        </ul>\n")
    outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")

    if len(location_set) > 0:
        outfile.write("    <div class=\"map_section\">\n")
        outfile.write("    <h3 class=\"nobookmark\">Locations Where the Name has Been Applied</h3>\n")
        if do_print:
            outfile.write("      <figure>\n")
            outfile.write("        <img src=\"" + TMP_MAP_PATH + pointmap_name("name_" + name_to_filename(name)) +
                          ".png\" alt=\"Point Map\" title=\"Point map of name application\" />\n")
            outfile.write("      </figure>\n")
        else:
            outfile.write("           <div id=\"point_map_canvas\" class=\"sp_map\"></div>\n")
        outfile.write("    </div>\n")
    if maxcnt > 0:
        write_chronology_chart_div(outfile, do_print, image_name, None, "Number of Uses of Name per Year", False, False)
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
    output_name_table(outfile, do_print, True, cites, uniquecites, notecnt, comcnt, refdict, name_table,
                      point_locations)
    outfile.write("    <p>\n")
    outfile.write("    </p>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, indexpath="../")


def calculate_specific_name_yearly_cnts(specific_name: TMB_Classes.SpecificNameClass, binomial_names: list,
                                        binomial_cnts: dict) -> Tuple[dict, int]:
    miny = init_data().start_year
    maxy = init_data().current_year
    year_cnts = {y: 0 for y in range(miny, maxy+1)}
    total = 0
    for n in binomial_names:
        sp_name = clean_specific_name(n)
        tmpnamelist = specific_name.variations.split(";")
        if (sp_name != "") and (sp_name in tmpnamelist):
            cnts = binomial_cnts[clean_name(n)]
            for y in cnts:
                if miny <= y <= maxy:
                    year_cnts[y] += cnts[y]
                    total += cnts[y]
    return year_cnts, total


def calculate_specific_locations(specific_name: TMB_Classes.SpecificNameClass, binomial_names: list,
                                 binomial_locations: dict) -> set:
    locs = set()
    for n in binomial_names:
        sp_name = clean_specific_name(n)
        tmpnamelist = specific_name.variations.split(";")
        if (sp_name != "") and (sp_name in tmpnamelist):
            locs |= binomial_locations[clean_name(n)]
    return locs


def write_specific_name_page(outfile: TextIO, do_print: bool, specific_name: TMB_Classes.SpecificNameClass,
                             binomial_names: list, refdict: dict, binomial_cnts: dict, location_set: set) -> None:
    """
    create a page with the history of a specific name
    """
    miny = init_data().start_year
    maxy = init_data().current_year
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
            image_name = name_to_filename(specific_name.name) + "_chronology.png"
            TMB_Create_Graphs.create_chronology_chart_file(image_name,  miny, maxy, maxcnt, byears,
                                                           init_data().graph_font)
    else:
        common_header_part1(outfile, specific_name.name, indexpath="../")

        if len(location_set) > 0:
            start_google_map_header(outfile)
            write_google_map_point_header(outfile, "sn_" + specific_name.name)
            end_google_map_header(outfile)

        if maxcnt > 0:
            start_google_chart_header(outfile)
            image_name = 0
            setup_chronology_chart(outfile, image_name, miny, maxy, maxcnt, byears)
            end_google_chart_header(outfile)
        common_header_part2(outfile, indexpath="../", include_map=True)

    outfile.write("    <header id=\"sn_" + specific_name.name + ".html\" class=\"tabular_page\">\n")
    outfile.write("      <h1 class=\"nobookmark\">" + format_name_string(specific_name.name) + "</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"index.html\">" + fetch_fa_glyph("index") + "Full Name Index</a></li>\n")
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
            s = find_species_by_name(specific_name.synonym)
            outfile.write("          <dd>" + create_species_link(s.genus, s.species, do_print, path="../") +
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
            report_error(specific_name.priority_source)
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

    if len(location_set) > 0:
        outfile.write("    <div class=\"map_section\">\n")
        outfile.write("    <h3 class=\"nobookmark\">Locations Where the Name has Been Applied</h3>\n")
        if do_print:
            outfile.write("      <figure>\n")
            outfile.write("        <img src=\"" + TMP_MAP_PATH + pointmap_name("sn_" + specific_name.name) +
                          ".png\" alt=\"Point Map\" title=\"Point map of name application\" />\n")
            outfile.write("      </figure>\n")
        else:
            outfile.write("           <div id=\"point_map_canvas\" class=\"sp_map\"></div>\n")
        outfile.write("    </div>\n")

    if maxcnt > 0:
        write_chronology_chart_div(outfile, do_print, image_name, None, "Number of Uses of Name per Year", False, False)
        outfile.write("\n")

    if specific_name.notes != ".":
        outfile.write("    <section class=\"spsection\" style=\"clear: both\">\n")
        outfile.write("      <h3 class=\"nobookmark\">Notes/Comments</h3>\n")
        outfile.write("      <p>\n")
        outfile.write("        " + replace_species_in_string(specific_name.notes) + "\n")
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
            outfile.write("      <li><a href=\"" + rel_link_prefix(do_print) + namefile + ".html\">" +
                          format_name_string(n) + "</a></li>\n")
    outfile.write("      </ul>\n")
    outfile.write("    </section>\n")

    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, indexpath="../")


def setup_chronology_chart(outfile: TextIO, n: int, miny: int, maxy: int, maxcnt: int, yearly_data: dict) -> None:
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


def write_chronology_chart_div(outfile: TextIO, do_print: bool, n: Union[str, int], linkfile: Optional[str],
                               title: str, is_species: bool, do_multi: bool) -> None:
    # n can be either the file name (print) or the chart # on the page (web)
    if is_species:
        if linkfile is not None:
            fn = rel_link_prefix(do_print) + name_to_filename(linkfile) + ".html"
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


def create_synonym_chronology(outfile: TextIO, do_print: bool, species_name: str, binomial_synlist: list,
                              binomial_name_counts: dict, specific_synlist: list, specific_name_counts: dict) -> None:
    """
    create a page with the chronological history of a specific name and its synonyms
    """
    miny = init_data().start_year
    maxy = init_data().current_year
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
    sp_order = [species_name]
    for x in name_cnts:
        if x[1] != species_name:
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
    species = find_species_by_name(species_name)
    # if ("Uca " + species) in binomial_synlist:
    if (species.binomial()) in binomial_synlist:
        bi_order = [species.binomial()]
    else:
        bi_order = []
    for x in name_cnts:
        # if x[1] != "Uca " + species:
        if x[1] != species.binomial():
            bi_order.append(x[1])

    if do_print:
        start_page_division(outfile, "synonym_page")
        image_name = "synonym_" + name_to_filename(species_name) + "_total_chronology.png"
        TMB_Create_Graphs.create_chronology_chart_file(image_name,  miny, maxy, maxcnt, total_cnts,
                                                       init_data().graph_font)
        for name in sp_order:
            image_name = "synonym_" + name_to_filename(name) + "_chronology.png"
            TMB_Create_Graphs.create_chronology_chart_file(image_name, miny, maxy, maxcnt, specific_name_counts[name],
                                                           init_data().graph_font)
        for name in bi_order:
            image_name = "synonym_" + name_to_filename(name) + "_chronology.png"
            TMB_Create_Graphs.create_chronology_chart_file(image_name, miny, maxy, maxcnt,
                                                           binomial_name_counts[clean_name(name)],
                                                           init_data().graph_font)
    else:
        common_header_part1(outfile, species_name, indexpath="../")
        start_google_chart_header(outfile)
        image_name = 0
        setup_chronology_chart(outfile, image_name, miny, maxy, maxcnt, total_cnts)
        adjust = 1
        for i, name in enumerate(sp_order):
            setup_chronology_chart(outfile, i + adjust, miny, maxy, maxcnt, specific_name_counts[name])
        adjust += len(specific_synlist)
        for i, name in enumerate(bi_order):
            setup_chronology_chart(outfile, i + adjust, miny, maxy, bmaxcnt, binomial_name_counts[clean_name(name)])
        end_google_chart_header(outfile)
        common_header_part2(outfile)

    outfile.write("    <header>\n")
    # outfile.write("      <h1 class=\"nobookmark\">Synonym Chronology of " + format_name_string("Uca " + species) +
    outfile.write("      <h1 class=\"nobookmark\">Synonym Chronology of " + format_name_string(species.binomial()) +
                  "</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "../") + "u_" + species_name +
                      ".html\">" + fetch_fa_glyph("info") + "Species page</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    if do_print:
        image_name = "synonym_" + name_to_filename(species_name) + "_total_chronology.png"
    else:
        image_name = 0
    write_chronology_chart_div(outfile, do_print, image_name, None, "All Names", False, True)
    adjust = 1
    outfile.write("    <p style=\"clear: both\">Accepted name is listed first, followed by synonyms in decreasing "
                  "order of use.</p>\n")
    outfile.write("    <h2 class=\"nobookmark\">Specific Synonyms</h2>\n")
    for i, name in enumerate(sp_order):
        if do_print:
            image_name = "synonym_" + name_to_filename(name) + "_chronology.png"
        else:
            image_name = i + adjust
        write_chronology_chart_div(outfile, do_print, image_name, "sn_" + name, name, True, True)
    adjust += len(specific_synlist)
    outfile.write("    <h2  class=\"nobookmark\" style=\"clear: both\">Binomial Synonyms</h2>\n")
    for i, name in enumerate(bi_order):
        if do_print:
            image_name = "synonym_" + name_to_filename(name) + "_chronology.png"
        else:
            image_name = i + adjust
        write_chronology_chart_div(outfile, do_print, image_name, name, name, True, True)

    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, indexpath="../")


def match_specific_name(name: str, specific_names: list) -> str:
    """
    match the specific name from a binomial to the list of accepted specific names
    """
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


def create_name_summary(outfile: TextIO, do_print: bool, binomial_year_cnts: dict, specific_year_cnts: dict,
                        species_refs: dict) -> None:
    if do_print:
        per_graph = 40
    else:
        per_graph = 60
    ngraph = int(math.ceil(len(species_refs) / per_graph))

    miny = init_data().start_year
    maxy = init_data().current_year
    byears = []
    c = 0
    for y in range(miny, maxy+1):
        if y in binomial_year_cnts:
            c = c + binomial_year_cnts[y]
            byears.append([y, binomial_year_cnts[y], c])
        else:
            byears.append([y, 0, c])

    miny = 1758
    maxy = init_data().current_year
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
    maxcnt = 0
    for s in ref_cnts:
        maxcnt = max(maxcnt, ref_cnts[s])

    if do_print:
        start_page_division(outfile, "base_page")
    else:
        common_header_part1(outfile, "Fiddler Crab Name Summary", indexpath="../")
        start_google_chart_header(outfile)
        outfile.write("        var cumulative_biname_data = google.visualization.arrayToDataTable([\n")
        outfile.write("          ['Year', 'Cumulative Unique Binomial/Compound Names'],\n")
        for y in byears:
            outfile.write("          ['" + str(y[0]) + "', " + str(y[2]) + "],\n")
        outfile.write("        ]);\n")
        outfile.write("\n")
        outfile.write("        var biname_data = google.visualization.arrayToDataTable([\n")
        outfile.write("          ['Year', 'New Unique Binomial/Compound Names'],\n")
        for y in byears:
            outfile.write("          ['" + str(y[0]) + "', " + str(y[1]) + "],\n")
        outfile.write("        ]);\n")
        outfile.write("\n")
        outfile.write("        var cumulative_spname_data = google.visualization.arrayToDataTable([\n")
        outfile.write("          ['Year', 'Cumulative Unique Specific Names'],\n")
        for y in syears:
            outfile.write("          ['" + str(y[0]) + "', " + str(y[2]) + "],\n")
        outfile.write("        ]);\n")
        outfile.write("\n")
        outfile.write("        var spname_data = google.visualization.arrayToDataTable([\n")
        outfile.write("          ['Year', 'New Unique Specific Names'],\n")
        for y in syears:
            outfile.write("          ['" + str(y[0]) + "', " + str(y[1]) + "],\n")
        outfile.write("        ]);\n")
        outfile.write("\n")
        c = 0
        for g in range(ngraph):
            c += 1
            outfile.write("        var spcnt_data" + str(c) + " = google.visualization.arrayToDataTable([\n")
            outfile.write("          ['Species', 'Referring References'],\n")
            start = g*per_graph
            end = start + per_graph
            if end > len(tmpslist):
                nblank = end - len(tmpslist)
                end = len(tmpslist)
            else:
                nblank = 0
            for i in range(start, end):
                s = tmpslist[i]
                outfile.write("          ['" + s + "', " + str(ref_cnts[s]) + "],\n")
            for i in range(nblank):
                outfile.write("          ['" "', 0],\n")
            outfile.write("        ]);\n")

        outfile.write("\n")
        outfile.write("        var line_name_options = {\n")
        outfile.write("          legend: { position: 'none' },\n")
        outfile.write("          chartArea: { height: '75%', top: 10 }\n")
        outfile.write("        };\n")
        outfile.write("\n")
        outfile.write("        var bar_name_options = {\n")
        outfile.write("          legend: { position: 'none' },\n")
        outfile.write("          bar: { groupWidth: '80%' },\n")
        outfile.write("          chartArea: { height: '75%', top: 10 }\n")
        outfile.write("        };\n")
        outfile.write("\n")
        outfile.write("        var spcnt_options = {\n")
        outfile.write("          legend: { position: 'none' },\n")
        outfile.write("          vAxis: { maxValue: " + str(maxcnt) + ", minValue: 0 },\n")
        outfile.write("          hAxis: { slantedTextAngle: 90,\n")
        outfile.write("                   textStyle: { italic: true, fontSize: 12 }},\n")
        outfile.write("          bar: { groupWidth: '80%' },\n")
        outfile.write("          chartArea: { height: '50%', top: 10 }\n")
        outfile.write("        };\n")
        outfile.write("\n")
        outfile.write("        var cumulative_biname_chart = new google.visualization.LineChart(document.getElementById"
                      "('cumulative_biname_chart_div'));\n")
        outfile.write("        cumulative_biname_chart.draw(cumulative_biname_data, line_name_options);\n")
        outfile.write("        var biname_chart = new google.visualization.ColumnChart(document.getElementById"
                      "('biname_chart_div'));\n")
        outfile.write("        biname_chart.draw(biname_data, bar_name_options);\n")
        outfile.write("        var cumulative_spname_chart = new google.visualization.LineChart(document.getElementById"
                      "('cumulative_spname_chart_div'));\n")
        outfile.write("        cumulative_spname_chart.draw(cumulative_spname_data, line_name_options);\n")
        outfile.write("        var spname_chart = new google.visualization.ColumnChart(document.getElementById"
                      "('spname_chart_div'));\n")
        outfile.write("        spname_chart.draw(spname_data, bar_name_options);\n")
        c = 0
        for g in range(ngraph):
            c += 1
            j = str(c)
            outfile.write("        var spcnt_chart" + j + " = "
                          "new google.visualization.ColumnChart(document.getElementById"
                          "('spcnt_chart" + j + "_div'));\n")
            outfile.write("        spcnt_chart" + j + ".draw(spcnt_data" + j + ", spcnt_options);\n")

        end_google_chart_header(outfile)
        common_header_part2(outfile)

    outfile.write("    <header>\n")
    outfile.write("      <h1 id=\"" + init_data().name_sum_url + "\" class=\"bookmark2\">Summary of Names</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\".\">" + fetch_fa_glyph("index") + "Name Index</a></li>\n")
        outfile.write("          <li><a href=\"../" + init_data().species_url +
                      "\">" + fetch_fa_glyph("accepted species") + "Accepted Species</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <p>\n")
    outfile.write("      A summary of the names in the database (last updated {}).\n".
                  format(datetime.date.isoformat(datetime.date.today())))
    outfile.write("      Most of these data are only based on <a href=\"../" + init_data().ref_sum_url +
                  "\">references whose citation data is already included in the database</a>.\n")
    outfile.write("    </p>\n")

    outfile.write("    <h3 class=\"nobookmark\">Cumulative Unique Binomial/Compound Names by Year</h3>\n")
    if do_print:
        filename = "cumulative_binames_line.png"
        TMB_Create_Graphs.create_line_chart_file(filename, byears, init_data().start_year, init_data().current_year, 2,
                                                 init_data().graph_font)
        outfile.write("    <figure class=\"graph\">\n")
        outfile.write("      <img src=\"" + TMP_PATH + filename + "\" class=\"line_chart\" />\n")
        outfile.write("    </figure>\n")
    else:
        outfile.write("    <div id=\"cumulative_biname_chart_div\" class=\"name_chart\"></div>\n")

    outfile.write("    <h3 class=\"nobookmark\">Unique Binomial/Compound Names by Year</h3>\n")
    if do_print:
        filename = "binames_per_year_bar.png"
        TMB_Create_Graphs.create_bar_chart_file(filename, byears, init_data().start_year, init_data().current_year, 1,
                                                init_data().graph_font)
        outfile.write("    <figure class=\"graph\">\n")
        outfile.write("      <img src=\"" + TMP_PATH + filename + "\" class=\"bar_chart\" />\n")
        outfile.write("    </figure>\n")
    else:
        outfile.write("    <div id=\"biname_chart_div\" class=\"name_chart\"></div>\n")

    outfile.write("    <h3 class=\"nobookmark\">Cumulative Unique Specific Names by Year</h3>\n")
    if do_print:
        filename = "cumulative_spnames_line.png"
        TMB_Create_Graphs.create_line_chart_file(filename, syears, 1758, init_data().current_year, 2,
                                                 init_data().graph_font)
        outfile.write("    <figure class=\"graph\">\n")
        outfile.write("      <img src=\"" + TMP_PATH + filename + "\" class=\"line_chart\" />\n")
        outfile.write("    </figure>\n")
    else:
        outfile.write("    <div id=\"cumulative_spname_chart_div\" class=\"name_chart\"></div>\n")

    outfile.write("    <h3 class=\"nobookmark\">Unique Specific Names by Year</h3>\n")
    if do_print:
        filename = "spnames_per_year_bar.png"
        TMB_Create_Graphs.create_bar_chart_file(filename, syears, 1758, init_data().current_year, 1,
                                                init_data().graph_font)
        outfile.write("    <figure class=\"graph\">\n")
        outfile.write("      <img src=\"" + TMP_PATH + filename + "\" class=\"bar_chart\" />\n")
        outfile.write("    </figure>\n")
    else:
        outfile.write("    <div id=\"spname_chart_div\" class=\"name_chart\"></div>\n")

    outfile.write("    <h3 class=\"nobookmark pagebreak\">Number of References Referring to Accepted Species</h3>\n")
    c = 0
    for i in range(ngraph):
        c += 1
        if do_print:
            filename = "refs_per_species_bar" + str(c) + ".png"
            sublist = tmpslist[i*per_graph:(i+1)*per_graph]
            ref_cnts[""] = 0
            for j in range(len(sublist), per_graph):
                sublist.append("")
            TMB_Create_Graphs.create_qual_bar_chart_file(filename, sublist, ref_cnts, maxcnt, init_data().graph_font)
            outfile.write("    <figure class=\"graph\">\n")
            outfile.write("      <img src=\"" + TMP_PATH + filename + "\" class=\"bar_chart\" />\n")
            outfile.write("    </figure>\n")
        else:
            outfile.write("    <div id=\"spcnt_chart" + str(c) + "_div\" class=\"name_bar_chart\"></div>\n")

    outfile.write("    <h3 class=\"nobookmark pagebreak\">Word Cloud of Binomial/Compound Names in Literature</h3>\n")
    outfile.write("    <figure class=\"graph\">\n")
    if do_print:
        outfile.write("      <img src=\"" + TMP_PATH + "binomial_word_cloud.png\" class=\"word_cloud\" />\n")
    else:
        outfile.write("      <img src=\"../images/binomial_word_cloud.png\" class=\"word_cloud\" />\n")
    outfile.write("    </figure>\n")
    outfile.write("    <h3 class=\"nobookmark\">Word Cloud of Specific Names in Literature</h3>\n")
    outfile.write("    <figure class=\"graph\">\n")
    if do_print:
        outfile.write("      <img src=\"" + TMP_PATH + "specific_word_cloud.png\" class=\"word_cloud\" />\n")
    else:
        outfile.write("      <img src=\"../images/specific_word_cloud.png\" class=\"word_cloud\" />\n")
    outfile.write("    </figure>\n")

    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, indexpath="../")


def extract_genus(name: str) -> str:
    if " " in name:
        return name[:name.find(" ")]
    else:
        return name


def create_genus_chronology(outfile: TextIO, do_print: bool, genus_cnts: dict) -> None:
    """
    create a page with the chronological history of the genera
    """
    miny = init_data().start_year
    maxy = init_data().current_year
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
    order = [x[1] for x in name_cnts]
    if do_print:
        start_page_division(outfile, "synonym_page")
        filename = "Genus_total_chronology.png"
        TMB_Create_Graphs.create_chronology_chart_file(filename, miny, maxy, maxcnt, total_cnts, init_data().graph_font)
        for name in order:
            filename = "Genus_" + name + "_chronology.png"
            TMB_Create_Graphs.create_chronology_chart_file(filename, miny, maxy, maxcnt, genus_cnts[name],
                                                           init_data().graph_font)
    else:
        common_header_part1(outfile, "Uca", indexpath="../")
        start_google_chart_header(outfile)
        setup_chronology_chart(outfile, 0, miny, maxy, maxcnt, total_cnts)
        adjust = 1
        for i, name in enumerate(order):
            setup_chronology_chart(outfile, i + adjust, miny, maxy, maxcnt, genus_cnts[name])
        end_google_chart_header(outfile)
        common_header_part2(outfile)

    outfile.write("    <header>\n")
    outfile.write("      <h1 class=\"bookmark2\">Chronology of Fiddler Crab Genera</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print) +
                      "index.html\">" + fetch_fa_glyph("index") + "Full Name Index</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    if do_print:
        filename = "Genus_total_chronology.png"
    else:
        filename = 0
    outfile.write("    <p>Chronological charts of different generic names for fiddler crabs. The charts include "
                  "instances when fiddler crabs were placed in other, valid, genera (<em>e.g.,</em> "
                  "<em class=\"species\">Cancer</em>) as well as cases in the 19<sup>th</sup> century when the "
                  "genus <em class=\"species\">Uca</em> was used for non-fiddler crabs.</p>\n")
    write_chronology_chart_div(outfile, do_print, filename, None, "All Genera", False, True)
    adjust = 1
    outfile.write("    <p style=\"clear: both\">Genera are listed in decreasing order of use.</p>\n")
    outfile.write("    <h2 class=\"nobookmark\">Fiddler Crab Genera</h2>\n")
    for i, name in enumerate(order):
        if do_print:
            filename = "Genus_" + name + "_chronology.png"
        else:
            filename = i + adjust
        write_chronology_chart_div(outfile, do_print, filename, None, name, True, True)

    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, indexpath="../")


def calculate_binomial_locations(name: str, citelist: list) -> set:
    """
    find all locations this name is applied to
    """
    locs = set()
    for c in citelist:
        clean = clean_name(c.name)
        if clean.lower() == name.lower():
            if c.applied_cites is not None:
                for a in c.applied_cites:
                    p = a.application
                    if (p != ".") and (p[0] != "[") and (p != "?"):
                        locs |= {strip_location_subtext(p)}
    return locs


def clean_genus(genus: str) -> str:
    """
    fix and match alternate genus spellings when performing summaries
    """
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


def calculate_name_index_data(refdict: dict, citelist: list, specific_names: list) -> Tuple[list, dict, dict, dict,
                                                                                            dict, dict, dict, dict,
                                                                                            dict, dict]:
    """
    calculate all the data associated with binomials and specific names
    """
    name_table = create_name_table(citelist)
    unique_names = list()
    nameset = set()
    # total_binomial_year_cnts = {}
    total_binomial_year_cnts = collections.Counter()
    for c in citelist:
        if c.name != ".":
            clean = clean_name(c.name)
            if not clean.lower() in nameset:
                nameset |= {clean.lower()}
                unique_names.append(clean)
                y = refdict[c.cite_key].year()
                if y is not None:
                    total_binomial_year_cnts.update([y])
                    # if y in total_binomial_year_cnts:
                    #     total_binomial_year_cnts[y] += 1
                    # else:
                    #     total_binomial_year_cnts[y] = 1
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
            if init_data().start_year <= y <= init_data().current_year:
                genera_set = genera_per_paper[c]
                for genus in genera_set:
                    genus = clean_genus(genus)
                    if genus != "":
                        genus_cnts.setdefault(genus, {y: 0 for y in range(init_data().start_year,
                                                                          init_data().current_year + 1)})[y] += 1
                        # if genus not in genus_cnts:
                        #     genus_cnts[genus] = {y: 0 for y in range(init_data().start_year,
                        #                                              init_data().current_year + 1)}
                        # gcnts = genus_cnts[genus]
                        # gcnts[y] += 1

    binomial_usage_cnts_by_year = {}
    binomial_location_applications = {}
    binomial_usage_cnts = {}
    for name in unique_names:
        binomial_usage_cnts_by_year[name], tmptotal = calculate_binomial_yearly_cnts(name, refdict, citelist)
        if tmptotal > 0:
            binomial_usage_cnts[name] = tmptotal
        binomial_location_applications[name] = calculate_binomial_locations(name, citelist)

    # specific_year_cnts = {}
    specific_year_cnts = collections.Counter()
    specific_usage_cnts_by_year = {}
    specific_location_applications = {}
    specific_usage_cnts = {}
    for name in specific_names:
        (specific_usage_cnts_by_year[name.name],
         tmptotal) = calculate_specific_name_yearly_cnts(name, unique_names, binomial_usage_cnts_by_year)
        if tmptotal > 0:
            specific_usage_cnts[name.name] = tmptotal
        specific_location_applications[name] = calculate_specific_locations(name, unique_names,
                                                                            binomial_location_applications)
        tmpkey = name.priority_source
        if tmpkey != ".":
            y = refdict[tmpkey].year()
            if y is not None:
                specific_year_cnts.update([y])
                # if y in specific_year_cnts:
                #     specific_year_cnts[y] += 1
                # else:
                #     specific_year_cnts[y] = 1
    return (unique_names, binomial_usage_cnts_by_year, specific_usage_cnts_by_year, genus_cnts,
            total_binomial_year_cnts, name_table, specific_location_applications, binomial_location_applications,
            binomial_usage_cnts, specific_usage_cnts)


def write_all_name_pages(outfile: TextIO, do_print: bool, refdict: dict, citelist: list, unique_names: list,
                         specific_names: list, name_table: dict, species_refs: dict, genus_cnts: dict,
                         binomial_usage_cnts_by_year: dict, total_binomial_year_cnts: dict, binomial_locations: dict,
                         specific_locations: dict, point_locations: dict) -> None:
    """
    create an index of binomials and specific names
    """
    if do_print:
        start_page_division(outfile, "index_page")
    else:
        common_html_header(outfile, "Name Index", indexpath="../")
    outfile.write("    <header id=\"name_index\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Name Index</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print) + init_data().name_sum_url +
                      "\">" + fetch_fa_glyph("summary charts") + "Name Summary</a></li>\n")
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "../") + init_data().species_url +
                      "\">" + fetch_fa_glyph("accepted species") + "Accepted Species</a></li>\n")
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print) + init_data().synonyms_genera +
                      "\">Genera Usage Patterns</a></li>\n")
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
    for name in unique_names:
        namefile = name_to_filename(name)
        outfile.write("        <li><a href=\"" + rel_link_prefix(do_print) + namefile + ".html\">" +
                      format_name_string(name) + "</a></li>\n")

    outfile.write("      </ul>\n")
    outfile.write("    </div>\n")
    outfile.write("    <div class=\"namecol pagebreak\">\n")
    outfile.write("      <h3 id=\"specificnames\" class=\"bookmark2\">Specific Names</h3>\n")
    outfile.write("      <ul class=\"spnamelist\">\n")

    # specific_year_cnts = {}
    specific_year_cnts = collections.Counter()
    for name in specific_names:
        outfile.write("        <li><a href=\"" + rel_link_prefix(do_print) + "sn_" + name.name + ".html\">" +
                      format_name_string(name.name) + "</a></li>\n")
        tmpkey = name.priority_source
        if tmpkey != ".":
            y = refdict[tmpkey].year()
            if y is not None:
                specific_year_cnts.update([y])
                # if y in specific_year_cnts:
                #     specific_year_cnts[y] += 1
                # else:
                #     specific_year_cnts[y] = 1
    outfile.write("      </ul>\n")
    outfile.write("    </div>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, indexpath="../")

    if do_print:
        create_name_summary(outfile, do_print, total_binomial_year_cnts, specific_year_cnts, species_refs)
        create_genus_chronology(outfile, do_print, genus_cnts)
    else:
        with open(WEBOUT_PATH + "names/" + init_data().name_sum_url, "w", encoding="utf-8") as suboutfile:
            create_name_summary(suboutfile, do_print, total_binomial_year_cnts, specific_year_cnts, species_refs)
        with open(WEBOUT_PATH + "names/" + init_data().synonyms_genera, "w", encoding="utf-8") as suboutfile:
            create_genus_chronology(suboutfile, do_print, genus_cnts)

    # write out individual pages for each binomial name and specific name
    print("..........Unique/Binomial Names..........")
    # for name in tqdm(unique_names):
    for name in unique_names:
        sname = match_specific_name(name, specific_names)
        namefile = name_to_filename(name)
        if do_print:
            write_binomial_name_page(outfile, True, name, namefile, binomial_usage_cnts_by_year[name], refdict,
                                     citelist, name_table, sname, binomial_locations[name], point_locations)
        else:
            with open(WEBOUT_PATH + "names/" + namefile + ".html", "w", encoding="utf-8") as suboutfile:
                write_binomial_name_page(suboutfile, False, name, namefile, binomial_usage_cnts_by_year[name], refdict,
                                         citelist, name_table, sname, binomial_locations[name], point_locations)
    print("..........Specific Names..........")
    # for name in tqdm(specific_names):
    for name in specific_names:
        if do_print:
            write_specific_name_page(outfile, True, name, unique_names, refdict, binomial_usage_cnts_by_year,
                                     specific_locations[name])
        else:
            with open(WEBOUT_PATH + "names/sn_" + name.name + ".html", "w", encoding="utf-8") as suboutfile:
                write_specific_name_page(suboutfile, False, name, unique_names, refdict, binomial_usage_cnts_by_year,
                                         specific_locations[name])


def check_specific_names(citelist: list, specific_names: list) -> None:
    """
    checks all specific names used to confirm they are accounted for in the full synonymy list
    """
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
            report_error("Missing specific name: " + n)


def create_all_taxonomic_keys(point_locations: dict, location_species: dict, location_range_species: dict,
                              trait_data: dict, all_taxa_data: dict) -> dict:
    """
    create taxonomic keys for every unique set of species identified across all locations
    """

    all_keys = {}

    # find all unique sets of species
    species_sets = set()
    for p in point_locations:
        loc = point_locations[p]
        all_species = set()
        all_species |= location_species[loc.name]
        if loc.n_direct_children() > 0:
            for c in loc.direct_children():
                all_species |= fetch_child_data(c, location_species)

        range_species = set(find_species_by_name(s) for s in location_range_species[loc])
        all_species |= range_species
        if len(all_species) > 0:
            species_sets.add(frozenset(all_species))

    # create keys for each unique set of species
    warnings = set()
    for sp_set in species_sets:
        taxa_data = {}
        for s in sp_set:
            try:
                taxa_data["Male " + s.binomial()] = all_taxa_data["♂ Male {{" + s.species + "}}"]
                taxa_data["Female " + s.binomial()] = all_taxa_data["♀ Female {{" + s.species + "}}"]
            except KeyError:
                report_error("Missing taxonomic key data: " + s.species)

        all_keys[sp_set], new_warning = TMB_TaxKeyGen.generate_taxonomic_key(trait_data, taxa_data, verbose=False)
        warnings |= new_warning

    # global key for all species
    all_keys["all"], new_warning = TMB_TaxKeyGen.generate_taxonomic_key(trait_data, all_taxa_data, verbose=False)
    warnings |= new_warning

    for w in sorted(warnings):
        report_error(w)

    return all_keys


def write_taxonomic_key(outfile: TextIO, do_print: bool, taxkey: TMB_TaxKeyGen.KeyText,
                        location: Optional[TMB_Classes.LocationClass]) -> None:
    """
    write pre-generated taxonomic key to html
    """
    if do_print:
        start_page_division(outfile, "base_page")
    else:
        if location is None:
            common_header_part1(outfile, "Fiddler Crab Taxonomic Key", indexpath="../../")
        else:
            common_header_part1(outfile, location.trimmed_name + ": Taxonomic Key", indexpath="../../")
        outfile.writelines(taxkey.header)
        common_header_part2(outfile, indexpath="../../")

    if location is None:
        outfile.write("    <header id=\"all_taxkey.html\">\n")
        outfile.write("      <h1 class=\"nobookmark\">Taxonomic Key to All Fiddler Crabs</h1>\n")
    else:
        outfile.write("    <header id=\"" + place_to_filename(location.name) + "_taxkey.html\">\n")
        outfile.write("      <h1 class=\"nobookmark\">" + location.trimmed_name + ": Taxonomic Key</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        if location is not None:
            outfile.write("          <li>" + create_location_link(location, location.trimmed_name, do_print, path="../",
                                                                  inc_icon=True) + "</li>\n")
            outfile.write("          <li><a href=\"../index.html\">" + fetch_fa_glyph("index") +
                          "Location Index</a></li>\n")
        outfile.write("          <li><a href=\"index.html\">" + fetch_fa_glyph("tax key") +
                      "Taxonomic Key Guide</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("    <p>&nbsp;</p>\n")

    for line in taxkey.body:
        outfile.write(replace_species_in_string(line, True, do_print, "../../"))

    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile)


def write_taxonomic_key_guide(outfile: TextIO, do_print: bool) -> None:
    """
    output a general guide and description for the taxonomic keys
    """
    if do_print:
        start_page_division(outfile, "base_page")
    else:
        common_html_header(outfile, "Fiddler Crab Taxonomic Key Guide", indexpath="../../")
    outfile.write("    <header id=\"key_index.html\">\n")
    outfile.write("      <h1 class=\"nobookmark\">Taxonomic Key Guide</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"../index.html\">" + fetch_fa_glyph("index") +
                      "Location Index</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <section class=\"topspsection\">\n")
    outfile.write("      <p>\n")
    outfile.write("          The taxonomic keys on this sites are explicitly designed to serve as field/photographic "
                  "identification keys for fiddler crabs and thus only focus on characters that may reasonably "
                  "be seen without dissection, microscopy, or other invasive procedures. As such there may be "
                  "occasional ambiguity in the division of very similar species. The keys include both male and "
                  "female fiddler crabs for each species as diagnostic characters may vary between the sexes.")
    outfile.write("      </p>\n")
    outfile.write("      <p>\n")
    outfile.write("          All of these guides are classic dichotomous keys where at each step of the process a "
                  "single decision is made to follow one of two paths, based on differential characteristics, until "
                  "a species is identified or no further division is possible. Figures and descriptions of characters "
                  "and variants are generally included as part of the key. Additional details and caveats may be "
                  "found in footnotes.")
    outfile.write("      </p>\n")
    outfile.write("      <p>\n")
    outfile.write("          All of the keys are algorithmically generated from a data matrix of species "
                  "characteristics. This allows us to create an individual key for every location, based only on "
                  "the species thought to be present at that location. It also means that the order of splits in "
                  "each key are driven by an algorithm rather than explicit human design and different keys may "
                  "prioritize different characters at different stages.")
    outfile.write("      </p>\n")
    # outfile.write("      <p>\n")
    # outfile.write("          A discussion of the development of this key generating algorithm can be found in "
    #               "<a href=\"http://www.rosenberglab.net/blog/2019/05/02/"
    #               "automatic-taxonomic-key-generation-part-1-introduction/\">a series of 10 blog posts</a> on my "
    #               "lab website. The <a href=\"https://github.com/msrosenberg/TaxKeyGen\">original code is found on "
    #               "Github</a>, although it has since been modified to work within the larger framework of this "
    #               "website generator.")
    # outfile.write("      </p>\n")
    outfile.write("      <p>\n")
    outfile.write("          We welcome comments or corrections about these guides and hope they prove to be "
                  "useful.")
    outfile.write("      </p>\n")
    outfile.write("    </section>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile)


def write_geography_page(outfile: TextIO, do_print: bool, species: list) -> None:
    """
    output geographic ranges to HTML
    """
    regions = ("Eastern Atlantic Realm",
               "Western Atlantic Realm",
               "Eastern Pacific Realm",
               "Indo-West Pacific Realm")
    if do_print:
        start_page_division(outfile, "index_page")
    else:
        common_header_part1(outfile, "Fiddler Crab Geographic Ranges")
        start_google_map_header(outfile)
        # write_google_map_range_header(outfile, "fiddlers_all")
        write_google_map_point_header(outfile, "fiddlers_all")
        end_google_map_header(outfile)
        common_header_part2(outfile, include_map=True)

    outfile.write("    <header id=\"" + init_data().map_url + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Geographic Ranges</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"locations/index.html\">" + fetch_fa_glyph("index") + "Location "
                      "Index</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <section class=\"topspsection\">\n")
    outfile.write("      <div class=\"map_section\">\n")
    if do_print:
        outfile.write("      <figure>\n")
        outfile.write("        <img src=\"" + TMP_MAP_PATH + rangemap_name("fiddlers_all") + ".png\" alt=\"Map\" "
                      "title=\"Map of fiddler crab distribution\" />\n")
        outfile.write("      </figure>\n")
        outfile.write("      <figure>\n")
        outfile.write("        <img src=\"" + TMP_MAP_PATH + pointmap_name("fiddlers_all") + ".png\" alt=\"Point Map\" "
                      "title=\"Point map of fiddler crab distribution\" />\n")
        outfile.write("      </figure>\n")
    else:
        # outfile.write("        <div id=\"range_map_canvas\"></div>\n")
        outfile.write("        <div id=\"map_density\"><a href=\"maps/" + rangemap_name("fiddlers_all") +
                      ".png\"><img src=\"maps/" + rangemap_name("fiddlers_all") + ".png\"></a></div>\n")
        outfile.write("        <div id=\"point_map_canvas\"></div>\n")
        outfile.write("        <div class=\"map_download\">\n")
        # outfile.write("          <a href=\"maps/" + rangemap_name("fiddlers_all") + ".png\">" +
        #               fetch_fa_glyph("download") + "Download PNG line map of ranges.</a> \n")
        outfile.write("          <a href=\"maps/" + pointmap_name("fiddlers_all") + ".png\">" +
                      fetch_fa_glyph("download") + "Download PNG line map of point locations.</a>\n")
        outfile.write("        </div>\n")
    outfile.write("      </div>\n")
    outfile.write("      <p>\n")
    outfile.write("        The first map shows the approximate density of species richness")
    if do_print:
        index_page = "#location_index.html"
        outfile.write(". ")
    else:
        index_page = "locations/index.html"
        outfile.write(" (click on map for larger view). ")
    outfile.write("The second map shows approximate point locations where fiddler crabs "
                  "have been recorded in the scientific record. Red markers indicate points where fiddler crabs are "
                  "found; purple indicates fossil-only locations; blue indicate false location records. See "
                  "the <a href=\"" + index_page + "\">location index</a> for a full list of all point locations.")
    outfile.write("\n      </p>\n")
    outfile.write("      <p>\n")
    outfile.write("        Specific ranges for a species or name can be found on its associated pages. "
                  "The list below sorts the species by major zoogeographic realm.\n")
    outfile.write("      </p>\n")

    outfile.write("    </section>\n")
    for r in regions:
        outfile.write("\n")
        outfile.write("    <section class=\"spsection\">\n")
        outfile.write("      <h2 class=\"nobookmark\">" + r + "</h2>\n")
        outfile.write("      <ul class=\"splist\">\n")
        for s in species:
            if s.realm == r:
                if s.status != "fossil":
                    outfile.write("        <li>" + create_species_link(s.genus, s.species, do_print) + "</li>\n")
        outfile.write("      </ul>\n")
        outfile.write("    </section>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile)


def create_location_hierarchy(point_locations: dict) -> dict:
    """
    go through all locations and add children to the parent locations
    """
    loc_dict = {}
    for p in point_locations:
        loc = point_locations[p]
        if loc.parent is not None:
            if loc.parent in point_locations:
                ploc = point_locations[loc.parent]
                ploc.children.append(loc)
            else:
                report_error("Location missing: " + loc.parent)
        for sp in loc.secondary_parents:
            if sp in point_locations:
                ploc = point_locations[sp]
                ploc.secondary_children.append(loc)
            else:
                report_error("Location missing: " + sp)
        if loc.trimmed_name in loc_dict:
            report_error("Duplicate trimmed location name: " + loc.trimmed_name)
        else:
            loc_dict[loc.trimmed_name] = loc
        for a in loc.alternates:
            if a in loc_dict:
                report_error("Duplicate trimmed location name: " + a)
            else:
                loc_dict[a] = loc
    return loc_dict


def fetch_child_ref_data(loc: TMB_Classes.LocationClass, ref_dict: dict) -> set:
    refset = ref_dict[loc.name]
    if loc.n_direct_children() > 0:
        for c in loc.direct_children():
            refset |= fetch_child_ref_data(c, ref_dict)
    return refset


def fetch_child_data(loc: TMB_Classes.LocationClass, location_dict: dict) -> set:
    locset = location_dict[loc.name]
    if loc.n_direct_children() > 0:
        for c in loc.direct_children():
            locset |= fetch_child_data(c, location_dict)
    return locset


def write_location_page(outfile: TextIO, do_print: bool, loc: TMB_Classes.LocationClass, point_locations: dict,
                        location_species: dict, location_bi_names: dict, location_sp_names: dict,
                        location_direct_refs: dict, location_cited_refs: dict, references: list,
                        locations_range_species: dict, location_keys: Optional[dict]) -> None:
    """
    write the output page for an individual location
    """

    def format_latlon(lat: float, lon: float) -> str:
        """
        subfunction to format a lat,lon pair for printing
        """
        if lat < 0:
            latdir = "S"
        else:
            latdir = "N"
        if lon < 0:
            londir = "W"
        else:
            londir = "E"
        return "{:1.6f}&deg;{}, {:1.6f}&deg;{}".format(abs(lat), latdir, abs(lon), londir)

    # main function code
    if do_print:
        start_page_division(outfile, "base_page")
    else:
        common_header_part1(outfile, loc.trimmed_name, indexpath="../")
        if not loc.unknown:
            start_google_map_header(outfile)
            write_google_map_point_header(outfile, "location_" + place_to_filename(loc.name))
            end_google_map_header(outfile)
        common_header_part2(outfile, indexpath="../", include_map=True)

    outfile.write("    <header id=\"" + place_to_filename(loc.name) + ".html\">\n")
    outfile.write("      <h1 class=\"nobookmark\">" + loc.trimmed_name + "</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"index.html\">" + fetch_fa_glyph("index") + "Location Index</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("    <dl>\n")

    if loc.n_alternates() > 0:
        outfile.write("    <dt>Also Known As</dt>\n")
        outfile.write("      <dd>" + ", ".join(loc.alternates) + "</dd>\n")
    if loc.n_parents() > 0:
        outfile.write("    <dt>Included Within</dt>\n")
        if loc.parent is not None:
            p = point_locations[loc.parent]
            dstr = create_location_link(p, p.trimmed_name, do_print)
        else:
            dstr = None
        if loc.n_secondary_parents() > 0:
            if dstr is None:
                dlist = []
            else:
                dlist = [dstr]
            for a in loc.secondary_parents:
                p = point_locations[a]
                dlist.append(create_location_link(p, p.trimmed_name, do_print))
            dstr = ", ".join(dlist)
        outfile.write("      <dd>" + dstr + "</dd>\n")
    if loc.unknown:
        outfile.write("    <dt>Location Could not be Identified</dt>\n")
        if loc.notes is not None:
            outfile.write("      <dd>" + loc.notes + "</dd>\n")
    else:
        if loc.notes is not None:
            outfile.write("    <dt>Note</dt>\n")
            outfile.write("      <dd>" + loc.notes + "</dd>\n")
        outfile.write("    <dt>Approximate Coordinates</dt>\n")
        outfile.write("      <dd>" + format_latlon(loc.latitude, loc.longitude) + "</dd>\n")
        outfile.write("    <div class=\"map_section\">\n")
        if do_print:
            outfile.write("      <figure>\n")
            outfile.write("        <img src=\"" + TMP_MAP_PATH +
                          pointmap_name("location_" + place_to_filename(loc.name)) + ".png\" alt=\"" +
                          loc.trimmed_name + "\" title=\"Map of " + loc.trimmed_name + "\" />\n")
            outfile.write("      </figure>\n")
        else:
            outfile.write("           <div id=\"point_map_canvas\" class=\"sp_map\"></div>\n")

        outfile.write("        <div class=\"map_download\">\n")
        outfile.write("         The red marker indicates the coordinates used to represent this location, "
                      "yellow markers all other locations contained within this location. Purple markers indicate "
                      "fossil-only locations or sub-locations.\n")
        outfile.write("        </div>\n")

        outfile.write("    </div>\n")
    outfile.write("    </dl>\n")
    all_species = set()
    all_species |= location_species[loc.name]
    all_bi_names = set()
    all_bi_names |= location_bi_names[loc.name]
    all_sp_names = set()
    all_sp_names |= location_sp_names[loc.name]
    all_refs = set()
    all_refs |= location_direct_refs[loc.name]
    all_refs |= location_cited_refs[loc.name]
    if loc.n_direct_children() > 0:
        outfile.write("  <section class=\"spsection\">\n")
        outfile.write("    <h3 class=\"nobookmark\">Includes Subareas</h3>\n")
        outfile.write("    <ul class=\"locpagelist\">\n")
        for c in loc.direct_children():
            outfile.write("    <li>" + create_location_link(c, c.trimmed_name, do_print) + "</li>\n")
            all_species |= fetch_child_data(c, location_species)
            all_bi_names |= fetch_child_data(c, location_bi_names)
            all_sp_names |= fetch_child_data(c, location_sp_names)
            all_refs |= fetch_child_ref_data(c, location_direct_refs)
            all_refs |= fetch_child_ref_data(c, location_cited_refs)
        outfile.write("    </ul>\n")
        outfile.write("  </section>\n")

    # add species
    range_species = set(find_species_by_name(s) for s in locations_range_species[loc])
    range_species -= all_species
    all_species |= range_species

    is_error = True
    print_star = False
    print_double = False
    outfile.write("  <section class=\"spsection\">\n")
    outfile.write("    <h3 class=\"nobookmark\">Currently Recognized Species</h3>\n")
    if len(all_species) > 0:
        is_error = False
        # outfile.write("  <section class=\"spsection\">\n")
        # outfile.write("    <h3 class=\"nobookmark\">Currently Recognized Species</h3>\n")
        outfile.write("    <ul class=\"locpagelist\">\n")
        for s in sorted(list(all_species)):
            if s in location_species[loc.name]:
                suffix = ""
            elif s in range_species:
                suffix = DOUBLEDAGGER
                print_double = True
            else:
                suffix = STAR
                print_star = True
            outfile.write("      <li>" +
                          create_species_link(s.genus, s.species, do_print, status=s.status, path="../") +
                          suffix + "</li>\n")
        outfile.write("    </ul>\n")
    else:
        outfile.write("  <p>None</p>\n")
    outfile.write("  </section>\n")

    if len(all_bi_names) > 0:
        is_error = False
        outfile.write("  <section class=\"spsection\">\n")
        outfile.write("    <h3 class=\"nobookmark\">Names Which Have Been Used for This Area</h3>\n")
        outfile.write("    <ul class=\"locpagelist\">\n")
        for s in sorted(list(all_bi_names)):
            if s in location_bi_names[loc.name]:
                suffix = ""
            else:
                suffix = STAR
                print_star = True
            outfile.write("      <li><a href=\"" + rel_link_prefix(do_print, "../names/") + name_to_filename(s) +
                          ".html\">" + format_name_string(s) + "</a>" + suffix + "</li>\n")
        outfile.write("    </ul>\n")
        outfile.write("  </section>\n")

    if len(all_sp_names) > 0:
        is_error = False
        outfile.write("  <section class=\"spsection\">\n")
        outfile.write("    <h3 class=\"nobookmark\">Specific Names Which Have Been Used for This Area</h3>\n")
        outfile.write("    <ul class=\"locpagelist\">\n")
        for s in sorted(list(all_sp_names)):
            if s in location_sp_names[loc.name]:
                suffix = ""
            else:
                suffix = STAR
                print_star = True
            outfile.write("      <li><a href=\"" + rel_link_prefix(do_print, "../names/") + "sn_" + s.name +
                          ".html\">" + format_name_string(s.name) + "</a>" + suffix + "</li>\n")
        outfile.write("    </ul>\n")
        outfile.write("  </section>\n")

    # the following is to identify locations which may no longer used in the DB and can be removed
    # if is_error:
    #     report_error("Phantom Location: " + loc.name)

    write_annotated_reference_list(outfile, do_print, references, all_refs, location_direct_refs[loc.name],
                                   location_cited_refs[loc.name], "../")

    if len(location_direct_refs[loc.name]) != len(location_cited_refs[loc.name]):
        key_str = "Entries marked with " + DAGGER + " represent indirect references to location through citation. "
    else:
        key_str = ""
    if print_star:
        key_str += "Entries marked with " + STAR + " are inferred from subareas. "
    if print_double:
        key_str += "Entries marked with " + DOUBLEDAGGER + " represent potential inhabitants inferred from " \
                                                           "species ranges."
    if key_str != "":
        outfile.write("    <p>" + key_str.strip() + "</p>\n")

    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile)

    # output place specific taxonomic key
    if (location_keys is not None) and (len(all_species) > 0):
        if do_print:
            write_taxonomic_key(outfile, do_print, location_keys[frozenset(all_species)], loc)
        else:
            with open(WEBOUT_PATH + "locations/keys/" + place_to_filename(loc.name) + "_taxkey.html", "w",
                      encoding="utf-8") as suboutfile:
                write_taxonomic_key(suboutfile, do_print, location_keys[frozenset(all_species)], loc)

    # write out children pages (primary children only)
    if loc.n_children() > 0:
        for c in loc.children:
            if do_print:
                write_location_page(outfile, do_print, c, point_locations, location_species, location_bi_names,
                                    location_sp_names, location_direct_refs, location_cited_refs, references,
                                    locations_range_species, location_keys)
            else:
                with open(WEBOUT_PATH + "locations/" + place_to_filename(c.name) + ".html", "w",
                          encoding="utf-8") as suboutfile:
                    write_location_page(suboutfile, do_print, c, point_locations, location_species, location_bi_names,
                                        location_sp_names, location_direct_refs, location_cited_refs, references,
                                        locations_range_species, location_keys)


def write_location_index_entry(outfile: TextIO, do_print: bool, loc: TMB_Classes.LocationClass,
                               point_locations: dict, is_primary: bool) -> None:
    """
    print a location and all of its child locations
    """
    mark2 = not is_primary
    outfile.write("<li>" + create_location_link(loc, loc.trimmed_name, do_print, mark_unknown=True,
                                                mark_secondary=mark2))
    if is_primary and (loc.n_direct_children() > 0):
        child_list = []
        for child in loc.children:
            child_list.append([child.name, True])
        for child in loc.secondary_children:
            child_list.append([child.name, False])
        child_list.sort()
        outfile.write("\n <ul>\n")
        for child in child_list:
            write_location_index_entry(outfile, do_print, point_locations[child[0]], point_locations, child[1])
        outfile.write(" </ul>\n")
    outfile.write("</li>\n")


def write_location_index(outfile: TextIO, do_print: bool, point_locations: dict, location_dict: dict,
                         location_species: dict, location_sp_names: dict, location_bi_names: dict,
                         location_direct_refs: dict, location_cited_refs: dict, references: list,
                         location_range_species: dict, location_keys: Optional[dict]) -> None:
    """
    output observation location index to HTML
    """
    if do_print:
        start_page_division(outfile, "index_page")
    else:
        common_html_header(outfile, "Fiddler Crab Observation Locations", indexpath="../")
    outfile.write("    <header id=\"location_index\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Location Index</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"../" + init_data().map_url +
                      "\">" + fetch_fa_glyph("maps") + "Range Maps</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <p>\n")
    outfile.write("      The following indices include all locations extracted from the literature in the database "
                  "where fiddler crabs have been reported. The first list includes all modern names in a rough, "
                  "hierarchical framework, mostly by country and subregions within country. Bodies of water which "
                  "cannot be associated with a single country are listed independently. The hierarchy is imperfect "
                  "because some observations were general enough to cross political or other structural boundaries. "
                  "To deal with this, sublocations may contain duplicate listings within the hierarchy. Such "
                  "duplicates are marked by a " + STAR + " and do not display further sublocations under these "
                  "duplicate entries within the index (although all sublocations are included on all location-specific "
                  "pages).\n")
    outfile.write("    </p>\n")
    outfile.write("    <p>\n")
    outfile.write("      The second list is strictly alphabetical and includes archaic and older place names.\n")
    outfile.write("    </p>\n")
    outfile.write("    <p>\n")
    outfile.write("    Each location is expressed as a single pair of coordinates, so all plotted points "
                  "should only be viewed as an approximate location. Generally, a point on the shore was chosen to "
                  "represent each locality, but occasionally an interior land point may have been chosen when no "
                  "single shore point made sense, for example, in the case of a record on an island.\n")
    outfile.write("    </p>\n")
    outfile.write("    <p>\n")
    outfile.write("    Species lists for each area are automatically generated from the database and take "
                  "advantage of the hierarchical structure to fill in species for larger containing areas. These "
                  "lists may be incomplete due to the imperfect nature of the hierachy; similarly, a listed species "
                  "for a large area may only be found in a small part of the total region.\n")
    outfile.write("    </p>\n")
    outfile.write("    <p>\n")
    outfile.write("    Locations marked by " + DAGGER + " represent place names from the literature which could not be "
                  "identified or associated with a modern name or place.\n")
    outfile.write("    </p>\n")
    outfile.write("\n")
    outfile.write("  <div class=\"namecol\">\n")
    outfile.write("    <h3 id=\"location_index_hier\" class=\"bookmark2\">Hierarchical List of Modern Location "
                  "Names</h3>\n")
    top_list = []
    for p in point_locations:
        loc = point_locations[p]
        if loc.parent is None:
            top_list.append(loc.name)
    top_list.sort()
    outfile.write("    <ul class=\"hlocationlist\">\n")
    for p in top_list:
        loc = point_locations[p]
        write_location_index_entry(outfile, do_print, loc, point_locations, True)
    outfile.write("    </ul>\n")
    outfile.write("  </div>\n")

    outfile.write("  <div class=\"namecol pagebreak\">\n")
    outfile.write("    <h3 id=\"location_index_alpha\" class=\"bookmark2\">Alphabetical List of All Location "
                  "Names</h3>\n")
    full_list = list(location_dict.keys())
    full_list.sort()
    outfile.write("    <ul class=\"locationlist\">\n")
    for p in full_list:
        loc = location_dict[p]
        outfile.write("   <li>" + create_location_link(loc, p, do_print, mark_unknown=False) + "</li>\n")
    outfile.write("    </ul>\n")
    outfile.write("  </div>\n")

    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile)

    if location_keys is not None:
        if do_print:
            write_taxonomic_key_guide(outfile, do_print)
            write_taxonomic_key(outfile, do_print, location_keys["all"], None)
        else:
            with open(WEBOUT_PATH + "locations/keys/index.html", "w", encoding="utf-8") as suboutfile:
                write_taxonomic_key_guide(suboutfile, do_print)
            with open(WEBOUT_PATH + "locations/keys/all_taxkey.html", "w", encoding="utf-8") as suboutfile:
                write_taxonomic_key(suboutfile, do_print, location_keys["all"], None)

    # for p in tqdm(top_list):
    for p in top_list:
        loc = point_locations[p]
        if do_print:
            write_location_page(outfile, do_print, loc, point_locations, location_species, location_bi_names,
                                location_sp_names, location_direct_refs, location_cited_refs, references,
                                location_range_species, location_keys)
        else:
            with open(WEBOUT_PATH + "locations/" + place_to_filename(loc.name) + ".html", "w",
                      encoding="utf-8") as suboutfile:
                write_location_page(suboutfile, do_print, loc, point_locations, location_species, location_bi_names,
                                    location_sp_names, location_direct_refs, location_cited_refs, references,
                                    location_range_species, location_keys)


def check_location_page(loc: TMB_Classes.LocationClass, location_species: dict, location_bi_names: dict,
                        location_sp_names: dict) -> None:
    """
    check the output page for an individual location
    """
    all_species = set()
    all_species |= location_species[loc.name]
    all_bi_names = set()
    all_bi_names |= location_bi_names[loc.name]
    all_sp_names = set()
    all_sp_names |= location_sp_names[loc.name]
    if loc.n_direct_children() > 0:
        for c in loc.direct_children():
            all_species |= fetch_child_data(c, location_species)
            all_bi_names |= fetch_child_data(c, location_bi_names)
            all_sp_names |= fetch_child_data(c, location_sp_names)

    # if (len(all_species) == 0) and (len(all_bi_names) == 0) and (len(all_sp_names) == 0):
    #     report_error("Phantom Location: " + loc.name)

    if loc.n_children() > 0:
        for c in loc.children:
            check_location_page(c, location_species, location_bi_names, location_sp_names)


def check_location_index(point_locations: dict, location_species: dict, location_sp_names: dict,
                         location_bi_names: dict) -> None:
    top_list = []
    for p in point_locations:
        loc = point_locations[p]
        if loc.parent is None:
            top_list.append(loc.name)
    top_list.sort()

    for p in top_list:
        loc = point_locations[p]
        check_location_page(loc, location_species, location_bi_names, location_sp_names)


def match_names_to_locations(species: list, specific_point_locations: dict,  binomial_point_locations: dict,
                             point_locations: dict, citelist: list) -> Tuple[dict, dict, dict, dict, dict, dict,  dict,
                                                                             dict, dict, dict]:
    species_plot_locations = {}
    invalid_species_locations = {}
    questionable_id_locations = {}
    location_species = {x: set() for x in point_locations}
    location_bi_names = {x: set() for x in point_locations}
    location_sp_names = {x: set() for x in point_locations}
    location_cited_refs = {x: set() for x in point_locations}
    location_direct_refs = {x: set() for x in point_locations}
    missing_set = set()
    for s in species:
        if s.status != "fossil":
            places = set()
            invalid_places = set()
            questionable_ids = set()
            good_ids = set()
            for c in citelist:
                if (c.actual == s.species) and ((c.context == "location") or
                                                (c.context == "specimen") or
                                                (c.context == "sequence")):
                    p = c.application
                    if p[0] != "[":
                        p = strip_location_subtext(p)
                        if p in point_locations:
                            places.add(p)
                            # location_species[p] |= {s}
                            if "<!>" in c.application:
                                invalid_places.add(p)
                            elif "<?>" in c.application:
                                questionable_ids.add(p)
                            else:
                                good_ids.add(p)
                                location_species[p] |= {s}
                        elif p != "?":
                            missing_set |= {p}
            species_plot_locations[s] = sorted(list(places))
            invalid_species_locations[s] = invalid_places
            questionable_id_locations[s] = questionable_ids - good_ids
        else:
            species_plot_locations[s] = None
            invalid_species_locations[s] = None
            questionable_id_locations[s] = None

    # create set of all citations that refer to each location
    for c in citelist:
        if (c.context == "location") or (c.context == "specimen") or (c.context == "sequence"):
            p = c.application
            if (p != ".") and (p[0] != "[") and (p != "?"):
                loc = strip_location_subtext(p)
                if loc in point_locations:
                    location_direct_refs[loc] |= {c.cite_key}
    for c in citelist:
        if c.applied_cites is not None:
            for a in c.applied_cites:
                p = a.application
                if (p != ".") and (p[0] != "[") and (p != "?"):
                    loc = strip_location_subtext(p)
                    if (loc in point_locations) and (loc not in location_direct_refs[loc]):
                        location_cited_refs[loc] |= {c.cite_key}

    binomial_plot_locations = {}
    for name in binomial_point_locations:
        places = set()
        point_set = binomial_point_locations[name]
        for p in point_set:
            if p in point_locations:
                places |= {p}
                location_bi_names[p] |= {name}
            elif p != "?":
                missing_set |= {p}
        binomial_plot_locations[name] = sorted(list(places))

    specific_plot_locations = {}
    for name in specific_point_locations:
        places = set()
        point_set = specific_point_locations[name]
        for p in point_set:
            if p in point_locations:
                places |= {p}
                location_sp_names[p] |= {name}
            elif p != "?":
                missing_set |= {p}
        specific_plot_locations[name] = sorted(list(places))

    if len(missing_set) > 0:
        missing_list = sorted(list(missing_set))
        for m in missing_list:
            report_error("Missing point location: " + m)

    return (species_plot_locations, invalid_species_locations, binomial_plot_locations, specific_plot_locations,
            location_species, location_sp_names, location_bi_names, location_direct_refs, location_cited_refs,
            questionable_id_locations)


def compare_ranges_to_locations(species_range_blocks: dict, point_locations: dict) -> dict:
    """
    create a list of point locations that should contain a species, based on the official range data
    """
    point_range_species = {}
    for p in point_locations:
        dat = point_locations[p]
        slist = []
        if not dat.unknown:
            for species in species_range_blocks:
                blocks = species_range_blocks[species]
                inside = False
                for b in blocks:
                    if b.inside(dat.latitude, dat.longitude):
                        inside = True
                if inside:
                    slist.append(species)
        point_range_species[dat] = slist
    return point_range_species


def write_common_names_pages(outfile: TextIO, do_print: bool, common_name_data: list) -> None:
    """
    output common names to HTML
    """
    if do_print:
        start_page_division(outfile, "base_page")
    else:
        common_html_header(outfile, "Common Names of Fiddler Crabs")
    outfile.write("    <header id=\"" + init_data().common_url + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Common Names of Fiddler Crabs</h1>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <p>\n")
    outfile.write("      Following is a summary of common names for fiddler crabs. See <a href=\"" +
                  rel_link_prefix(do_print) + init_data().species_url +
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
        common_html_footer(outfile)


def connect_refs_to_species(species: list, citelist: list) -> dict:
    """
    create a list of references for each species
    """
    # create a dictionary with empty reference lists
    species_refs = {s.species: set() for s in species}
    # go through all citations
    # for c in tqdm(citelist):
    for c in citelist:
        if c.actual in species_refs:
            reflist = species_refs[c.actual]
            reflist |= {c.cite_key}
    return species_refs


def write_species_list(outfile: TextIO, do_print: bool, specieslist: list) -> None:
    """
    create an index of all valid species
    """
    if do_print:
        start_page_division(outfile, "index_page")
        link_str = "#name_index"
    else:
        common_html_header(outfile, "Fiddler Crab Species")
        link_str = "names/"
    outfile.write("    <header id=\"" + init_data().species_url + "\">\n")
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
        outfile.write("      <li>" + create_species_link(species.genus, species.species, do_print,
                                                         status=species.status) + "</li>\n")
    outfile.write("    </ul>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile)


def write_species_photo_page(outfile: TextIO, do_print: bool, fname: str, species_name: str, common_name: str,
                             caption: str, pn: int, pspecies: str, refdict: dict) -> None:
    """
    create a page for a specific photo
    """
    if ";" in pspecies:
        spname = pspecies.replace(";", "_")
        tmplist = pspecies.split(";")
        slist = []
        for t in tmplist:
            tmps = find_species_by_name(t)
            slist.append(tmps.binomial())
        ptitle = " & ".join(slist)
        # ptitle = "Uca " + pspecies.replace(";", " & Uca ")
        is_multi = True
    else:
        spname = species_name
        species = find_species_by_name(species_name)
        ptitle = species.binomial()
        is_multi = False
    if do_print:
        start_page_division(outfile, "photo_page")
        media_path = MEDIA_PATH + "photos/"
    else:
        common_html_header(outfile, ptitle + " Photo", indexpath="../")
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
            sp = find_species_by_name(s)
            outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "../") + "u_" + s +
                          ".html\">" + fetch_fa_glyph("info") + "<em class=\"species\">" + sp.binomial() +
                          "</em> page</a></li>\n")
    else:
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "../") + "u_" + species_name +
                      ".html\">" + fetch_fa_glyph("info") + "Species page</a></li>\n")
    if not do_print:
        outfile.write("          <li><a href=\"../" + init_data().photo_url + "\">" + fetch_fa_glyph("photo") +
                      "All species photos</a></li>\n")
    outfile.write("        </ul>\n")
    outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <figure class=\"fullpic\">\n")
    outfile.write("      <img src=\"" + media_path + "U_" + spname + format(pn, "0>2") + ".jpg\" alt=\"" +
                  ptitle + " photo\" title=\"" + ptitle + " photo\" />\n")
    caption = replace_reference_in_string(caption, refdict, do_print, path="../")
    outfile.write("      <figcaption>" + replace_species_in_string(caption) + "</figcaption>\n")
    outfile.write("    </figure>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, indexpath="../")


def write_species_video_page(fname: str, video: TMB_Classes.VideoClass, vn: int) -> None:
    """
    create a page for a specific video
    """
    with open(fname, "w", encoding="utf-8") as outfile:
        if ";" in video.species:
            spname = video.species.replace(";", "_")
            tmplist = video.species.split(";")
            slist = []
            for t in tmplist:
                tmps = find_species_by_name(t)
                slist.append(tmps.binomial())
            vtitle = " & ".join(slist)
            # vtitle = "Uca " + video.species.replace(";", " & Uca ")
            is_multi = True
        else:
            spname = video.species
            species = find_species_by_name(spname)
            vtitle = species.binomial()
            is_multi = False
        common_html_header(outfile, vtitle + " Video", indexpath="../")
        outfile.write("    <header>\n")
        outfile.write("      <h1 class=\"nobookmark\"><em class=\"species\">" + vtitle + "</em> Video</h1>\n")
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        if is_multi:
            splist = video.species.split(";")
            for s in splist:
                sp = find_species_by_name(s)
                outfile.write("          <li><a href=\"../u_" + s +
                              ".html\">" + fetch_fa_glyph("info") + "<em class=\"species\">" + sp.binomial() +
                              "</em> page</a></li>\n")
        else:
            outfile.write("          <li><a href=\"../u_" + video.species +
                          ".html\">" + fetch_fa_glyph("info") + "Species page</a></li>\n")
        outfile.write("          <li><a href=\"../" + init_data().video_url + "\">" + fetch_fa_glyph("video") +
                      "All species videos</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
        outfile.write("    </header>\n")
        outfile.write("\n")
        outfile.write("    <h2>" + replace_species_in_string(video.caption) + "</h2>\n")
        outfile.write("    <video width=\"{:d}\" height=\"{:d}\" controls>\n".format(video.width, video.height))
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
        outfile.write("        <dd>{:d} &times; {:d}</dd>\n".format(video.width, video.height))
        outfile.write("      <dt>Format</dt>\n")
        outfile.write("        <dd>" + video.format + "</dd>\n")
        if video.notes != "#":
            outfile.write("      <dt>Notes</dt>\n")
            outfile.write("        <dd>" + video.notes + "</dd>\n")
        outfile.write("    </dl>\n")
        common_html_footer(outfile, indexpath="../")


def write_annotated_reference_list(outfile: TextIO, do_print: bool, references: list, all_citations: list,
                                   dir_citations: list, cited_citations: list, path: str) -> None:
    outfile.write("    <section class=\"spsection\">\n")
    if do_print:
        outfile.write("      <h3 class=\"nobookmark\">" + fetch_fa_glyph("references") + "References</h3>\n")
    else:
        outfile.write("      <h3 id=\"references\" class=\"nobookmark\">" + fetch_fa_glyph("references") +
                      "References</h3>\n")
    outfile.write("      <p>\n")
    reflist = []
    for ref in references:
        if ref.cite_key in all_citations:
            if ref.cite_key in dir_citations:
                suffix = ""
            elif ref.cite_key in cited_citations:
                suffix = DAGGER
            else:
                suffix = STAR
            reflist.append(format_reference_cite(ref, do_print, AUTHOR_PAREN, path=path) + suffix)
    outfile.write(", \n".join(reflist))
    outfile.write("      </p>\n")
    outfile.write("    </section>\n")


def write_reference_list(outfile: TextIO, do_print: bool, references: list, citations: dict) -> None:
    outfile.write("    <section class=\"spsection\">\n")
    if do_print:
        outfile.write("      <h2 class=\"nobookmark\">" + fetch_fa_glyph("references") + "References</h2>\n")
    else:
        outfile.write("      <h2 id=\"references\" class=\"nobookmark\">" + fetch_fa_glyph("references") +
                      "References</h2>\n")
    outfile.write("      <p>\n")
    reflist = []
    for ref in references:
        if ref.cite_key in citations:
            reflist.append(format_reference_cite(ref, do_print, AUTHOR_PAREN))
    outfile.write(", \n".join(reflist))
    outfile.write("      </p>\n")
    outfile.write("    </section>\n")


def size_label(w: float) -> str:
    if w < 10:
        return "Very Small"
    elif w < 20:
        return "Small"
    elif w < 30:
        return "Medium"
    elif w < 40:
        return "Large"
    else:
        return "Very Large"


def write_species_page(outfile: TextIO, do_print: bool, species: TMB_Classes.SpeciesClass, references: list,
                       specific_names: list, all_names: list, photos: list, videos: list, artlist: list,
                       sprefs: dict, refdict: dict, binomial_name_counts: dict, specific_name_cnts: dict,
                       higher_dict: dict, measurement_data: dict, handedness_data: list) -> None:
    """
    create the master page for a valid species
    """
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
            common_html_header(outfile, species.binomial() + " / Fossil")
            # common_html_header(outfile, "Uca " + species.species + " / Fossil")
        else:
            # common_header_part1(outfile, "Uca " + species.species + " / " + species.common)
            if species.common != ".":
                common_header_part1(outfile, species.binomial() + " / " + species.common)
            else:
                common_header_part1(outfile, species.binomial())
            start_google_map_header(outfile)
            write_google_map_range_header(outfile, "u_" + species.species)
            write_google_map_point_header(outfile, "u_" + species.species)
            end_google_map_header(outfile)
            common_header_part2(outfile, include_map=True)

    if species.species in measurement_data:
        mdata = measurement_data[species.species]
        if do_print:
            mean, std = create_species_cb_page(outfile, do_print, species, mdata, refdict)
        else:
            with open(WEBOUT_PATH + "sizes/" + species.species + "_cb.html", "w", encoding="utf-8") as suboutfile:
                mean, std = create_species_cb_page(suboutfile, do_print, species, mdata, refdict)
    else:
        mdata = None
        mean = 0
        std = 0

    if not is_fossil:
        if do_print:
            create_species_handedness_page(outfile, species, handedness_data, refdict, do_print)
        else:
            with open(WEBOUT_PATH + "handedness/" + species.species + "_handedness.html", "w",
                      encoding="utf-8") as suboutfile:
                create_species_handedness_page(suboutfile, species, handedness_data, refdict, do_print)

    outfile.write("    <header id=\"u_" + species.species + ".html\">\n")
    if is_fossil:
        sc = FOSSIL_IMAGE
    else:
        sc = ""
    outfile.write("      <h1 class=\"species bookmark2\">" + species.binomial() + sc + "</h1>\n")
    if is_fossil:
        outfile.write("      <h2 class=\"nobookmark\">Fossil</h2>\n")
    elif species.common != ".":
        outfile.write("      <h2 class=\"nobookmark\">" + species.common + "</h2>\n")
    # the species page navigation links only make sense on a webpage, not the printed version
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"#type\">Type</a></li>\n")
        outfile.write("          <li><a href=\"#info\">" + fetch_fa_glyph("info") + "Information</a></li>\n")
        outfile.write("          <li><a href=\"#pics\">" + fetch_fa_glyph("photo") + "Photos</a></li>\n")
        if not is_fossil:
            outfile.write("          <li><a href=\"#video\">" + fetch_fa_glyph("video") + "Video</a></li>\n")
            outfile.write("          <li><a href=\"#art\">" + fetch_fa_glyph("art") + "Art</a></li>\n")
        outfile.write("          <li><a href=\"#references\">" + fetch_fa_glyph("references") + "References</a></li>\n")
        if mdata is not None:
            outfile.write("          <li><a href=\"sizes/{}_cb.html\">".format(species.species) +
                          fetch_fa_glyph("measure") + "Size Data</a></li>\n")
        if not is_fossil:
            outfile.write("          <li><a href=\"handedness/{}_handedness.html\">".format(species.species) +
                          fetch_fa_glyph("handedness") + "Handedness</a></li>\n")
        outfile.write("          <li><a href=\"" + init_data().species_url + "\">" + fetch_fa_glyph("index") +
                      "Species List</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <section class=\"topspsection\">\n")
    if species.key_photo != ".":
        outfile.write("        <figure class=\"species_key_fig\">\n")
        outfile.write("          <img class=\"species_key_photo\" src=\"" + media_path + "photos/" + species.key_photo +
                      "\" alt=\"" + species.binomial() + "\" title=\"" + species.binomial() + "\" />\n")
        outfile.write("        </figure>\n")
        # copy photo to web output directory
        try:
            shutil.copy2(MEDIA_PATH + "photos/" + species.key_photo, WEBOUT_PATH + "photos/")
        except FileNotFoundError:
            report_error("Missing file: " + species.key_photo)

    if do_print:
        outfile.write("      <h2 class=\"nobookmark\">Type Description</h2>\n")
    else:
        outfile.write("      <h2 id=\"type\" class=\"nobookmark\">Type Description</h2>\n")
    outfile.write("      <dl>\n")
    outfile.write("        <dt><em class=\"species\">" + species.type_species + "</em></dt>\n")
    outfile.write("        <dd>" + species.type_reference.formatted_html + "</dd>\n")
    outfile.write("      </dl>\n")
    outfile.write("    </section>\n")
    outfile.write("\n")
    outfile.write("    <section class=\"spsection\">\n")
    if do_print:
        outfile.write("      <h2 class=\"nobookmark\">" + fetch_fa_glyph("info") + "Information</h2>\n")
    else:
        outfile.write("      <h2 id=\"info\" class=\"nobookmark\">" + fetch_fa_glyph("info") + "Information</h2>\n")
    outfile.write("      <dl>\n")
    hlist = []
    if species.subgenus != "":
        ctaxa = higher_dict["subgenus" + species.subgenus]
        hlist.append(ctaxa)
    ctaxa = higher_dict["genus" + species.genus]
    hlist.append(ctaxa)
    ctaxa = ctaxa.parent
    while ctaxa.parent is not None:
        hlist.append(ctaxa)
        ctaxa = ctaxa.parent
    tlist = []
    for ctaxa in hlist[::-1]:
        tlist.append(create_taxon_link(ctaxa.taxon_rank, ctaxa.name, do_print))
    outfile.write("       <dt>Taxonomy</dt>\n")
    outfile.write("       <dd>" + " &rarr; ".join(tlist) + "</dd>\n")

    if not is_fossil and (species.commonext != "."):
        outfile.write("       <dt>Common Names</dt>\n")
        # outfile.write("         <dd>" + species.commonext + "</dd>\n")
        common_name_list = species.commonext.split(";")
        name_languages = set()
        name_dict = {}
        for c in common_name_list:
            language, com_name = c.split("|")
            name_languages.add(language)
            if language not in name_dict:
                name_dict[language] = []
            name_dict[language].append(com_name)
        name_languages = sorted(name_languages)
        for language in name_languages:
            name_list = sorted(name_dict[language])
            outfile.write("        <dd>{}: {}</dd>\n".format(format_language(language), ", ".join(name_list)))

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
        tmpstr += " (<a href=\"" + rel_link_prefix(do_print, "names/") + "synonyms_" + species.species + \
                  ".html\">Chronology</a>)"
        outfile.write("       <dt>" + tmpstr + "</dt>\n")
        outfile.write("         <dd><em class=\"species\">" + ", ".join(llist) + "</em></dd>\n")

    # Size Data
    if mdata is not None:
        outfile.write("       <dt>Size</dt>\n")
        slabel = size_label(mean + 1.96*std)
        outfile.write("         <dd>{} Carapace Breadth: {:0.1f} mm ± {:0.2f} (sd), 95% range: "
                      "{:0.1f}&ndash;{:0.1f} mm, (<a href=\"sizes/{}_cb.html\">Data"
                      "</a>)</dd>\n".format(slabel, mean, std, max(mean - 1.96*std, 0), mean + 1.96*std,
                                            species.species))
        # outfile.write("         <dd>{}</dd>\n".format(slabel))
        # outfile.write("         <dd>Carapace Breadth: {:0.1f} mm ± {:0.2f} (sd), 95% range: "
        #               "{}&ndash;&{} mm</dd>\n".format(mean, std, mean - 1.96*std, mean + 1.96*std))
        # outfile.write("         <dd>(<a href=\"sizes/{}_cb.html\">Size Data</a>)</dd>\n".format(species.species))
        # outfile.write("         <dd>Carapace Breadth: {:0.1f} mm (95%: {:0.1f}&ndash;{:0.1f}) "
        #               "(<a href=\"sizes/{}_cb.html\">data</a>)</dd>\n".format(mean, mean - 1.96*std,
        #                                                                       mean + 1.96*std, species.species))

        # temp
        # print("{}\t{}\t{}\n".format(species.species, mean, std))

    # Geographic Range
    outfile.write("       <dt class=\"pagebreak\">Geographic Range</dt>\n")
    outfile.write("         <dd>" + species.realm + ": " + species.range + "</dd>\n")
    if not is_fossil:
        outfile.write("         <dd>\n")
        if do_print:
            outfile.write("           <img src=\"" + TMP_MAP_PATH + rangemap_name("u_" + species.species) +
                          ".png\" alt=\"Map\" />\n")
            outfile.write("           <img src=\"" + TMP_MAP_PATH + pointmap_name("u_" + species.species) +
                          ".png\" alt=\"Map\" />\n")
        else:
            outfile.write("           <div id=\"range_map_canvas\" class=\"sp_map\"></div>\n")
            outfile.write("           <div id=\"point_map_canvas\" class=\"sp_map\"></div>\n")
            outfile.write("           <div class=\"map_download\">\n")
            outfile.write("             <a href=\"maps/" + rangemap_name("u_" + species.species) + ".png\">" +
                          fetch_fa_glyph("download") + "Download PNG line map of ranges.</a> \n")
            outfile.write("             <a href=\"maps/" + pointmap_name("u_" + species.species) + ".png\">" +
                          fetch_fa_glyph("download") + "Download PNG line map of point locations.</a>\n")
            outfile.write("           </div>\n")
        outfile.write("         </dd>\n")

        outfile.write("         <dd class=\"map_data\">\n")
        if species.inatid != ".":
            x = "/taxa/" + species.inatid
        else:
            x = ""
        outfile.write("           Red markers indicate locations where this species is found according to the "
                      "scientific record; blue markers represent false or mistaken observations from the scientific "
                      "record; green markers represent &ldquo;research grade&rdquo; observations imported from "
                      "<a href=\"https://www.inaturalist.org" + x + "\">iNaturalist</a>.\n")
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
        outfile.write("           Range map data derived from: " + "; ".join(mapcitelist) + "\n")
        outfile.write("         </dd>\n")

    # External links
    if not do_print:
        outfile.write("       <dt>External Links</dt>\n")
        if species.eolid != ".":
            outfile.write("         <dd><a href=\"https://eol.org/pages/" + species.eolid +
                          "/overview\">Encyclopedia of Life</a></dd>\n")
        outfile.write("         <dd><a href=\"https://en.wikipedia.org/wiki/Uca_" + species.species +
                      "\">Wikipedia</a></dd>\n")
        if species.inatid != ".":
            outfile.write("         <dd><a href=\"https://www.inaturalist.org/taxa/" + species.inatid +
                          "\">iNaturalist</a></dd>\n")
        if species.taxonid != ".":
            outfile.write("         <dd><a href=\"https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=" +
                          species.taxonid + "\">NCBI Taxonomy Browser/Genbank</a></dd>\n")
        if species.gbifid != ".":
            outfile.write("         <dd><a href=\"https://www.gbif.org/species/" + species.gbifid +
                          "\">GBIF</a></dd>\n")

    outfile.write("      </dl>\n")
    outfile.write("    </section>\n")
    outfile.write("\n")
    outfile.write("    <section class=\"spsection\">\n")
    if do_print:
        outfile.write("      <h2 class=\"nobookmark\">" + fetch_fa_glyph("photo") + "Photos</h2>\n")
    else:
        outfile.write("      <h2 id=\"pics\" class=\"nobookmark\">" + fetch_fa_glyph("photo") + "Photos</h2>\n")
    photo_n = 0
    for photo in photos:
        slist = photo.species.split(";")
        if species.species in slist:
            pn = int(photo.n)
            if ";" in photo.species:
                nl = photo.species.replace(";", "_")
                pfname = "photo_u_" + nl + format(pn, "0>2") + ".html"
                tname = nl
            else:
                pfname = "photo_u_" + species.species + format(pn, "0>2") + ".html"
                tname = species.species
            outfile.write("      <figure class=\"sppic\">\n")
            outfile.write("        <a href=\"" + rel_link_prefix(do_print, "photos/") + pfname +
                          "\"><img class=\"thumbnail\" src=\"" + media_path + "photos/U_" + tname +
                          format(pn, "0>2") + "tn.jpg\" alt=\"" + species.binomial() + " thumbnail\" title=\"" +
                          species.binomial() + "\" /></a>\n")
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
            outfile.write("      <h2 class=\"nobookmark\">" + fetch_fa_glyph("video") + "Video</h2>\n")
        else:
            outfile.write("      <h2 id=\"video\" class=\"nobookmark\">" + fetch_fa_glyph("video") + "Video</h2>\n")
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
                        outfile.write("      Videos are available on the web at <a href=\"" + init_data().site_url() +
                                      "/" + init_data().video_url + "\">" + init_data().site_url() +
                                      "/" + init_data().video_url + "</a> or by following the embedded links.")
                        outfile.write("    </p>\n")
                    outfile.write("      <dl class=\"vidlist\">\n")
                outfile.write("            <dt><a class=\"vidlink\" href=\"" + abs_link_prefix(do_print) + vfname +
                              "\">" + replace_species_in_string(video.caption) + "</a></dt>\n")
                outfile.write("              <dd>{}, {:d} &times; {:d}, {}</dd>\n".format(video.length, video.width,
                                                                                          video.height, video.format))
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
            outfile.write("      <h2 class=\"nobookmark\">" + fetch_fa_glyph("art") + "Art</h2>\n")
        else:
            outfile.write("      <h2 id=\"art\" class=\"nobookmark\">" + fetch_fa_glyph("art") + "Art</h2>\n")
        artn = 0
        for art in artlist:
            slist = art.species.split(";")
            if species.species in slist:
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

    write_reference_list(outfile, do_print, references, sprefs)
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile)

    if len(binomial_synlist) > 0:
        if do_print:
            create_synonym_chronology(outfile, do_print, species.species, binomial_synlist, binomial_name_counts,
                                      specific_synlist, specific_name_cnts)
        else:
            with open(WEBOUT_PATH + "names/synonyms_" + species.species + ".html", "w", encoding="utf-8") as suboutfile:
                create_synonym_chronology(suboutfile, do_print, species.species, binomial_synlist, binomial_name_counts,
                                          specific_synlist, specific_name_cnts)


def create_species_handedness_page(outfile: TextIO, species: TMB_Classes.SpeciesClass, handedness_data: list,
                                   refdict: dict, do_print: bool = False):
    """
    write species handedness data page
    """
    if do_print:
        start_page_division(outfile, "base_page")
    else:
        common_html_header(outfile, species.binomial() + " Handedness", indexpath="../")
    outfile.write("    <header id=\"" + species.species + "_handedness.html\">\n")
    outfile.write("      <h1 class=\"nobookmark\"><em class=\"species\">" + species.binomial() +
                  "</em> Handedness</h1>\n")

    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "../") + "u_" + species.species +
                      ".html\">" + fetch_fa_glyph("info") + "Species page</a></li>\n")
        outfile.write("          <li><a href=\"index.html\">" + fetch_fa_glyph("handedness") +
                      "About Handedness</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")

    outfile.write("       <h2>Summary</h2>\n")
    if species.genus == "Gelasimus":
        expected = "95% or more right-handed"
    else:
        expected = "50% right-handed and 50% left-handed"
    outfile.write("<p>Expected handedness for <em class=\"species\">{}</em> is {}</p>\n".format(species.binomial(),
                                                                                                expected))

    data = []
    for d in handedness_data:
        if d.species == species.species:
            data.append(d)

    if len(data) > 0:
        right_total, left_total = 0, 0
        for d in data:
            right_total += d.right_cnt
            left_total += d.left_cnt
        outfile.write("<p>Observed handedness (based on raw totals across all data sets) is {:0.2%} right-handed, "
                      "{:0.2%} left-handed</p>\n".format(right_total/(right_total + left_total),
                                                         left_total/(right_total + left_total)))

        filename = WEBOUT_PATH + "handedness/" + species.species + "_handedness.png"
        TMB_Create_Graphs.create_handedness_chart_file(filename, data)

        outfile.write("    <p>The following figure displays the left and right counts for each individual data "
                      "set.</p>\n")
        outfile.write("    <figure class=\"sizeimg\">\n")
        outfile.write("      <img src=\"{0}_handedness.png\" alt=\"handedness data for {1}\" "
                      "title=\"handedness data for {1}\"/>\n".format(species.species, species.binomial()))
        outfile.write("    </figure>\n")

        with open(WEBOUT_PATH + "handedness/" + species.species + "_handedness.txt", "w") as datfile:
            outfile.write("    <h2>Data</h2>\n")
            outfile.write("    <p><a href=\"" + species.species + "_handedness.txt\">" +
                          fetch_fa_glyph("file download") + " Download Data</a></p>")
            outfile.write("<table class=\"size_data_table\">\n")
            outfile.write("<tr><th>Reference</th><th>Right Count</th><th>Left Count</th>"
                          "<th>Right %</th><th>Left %</th><th>Notes</th></tr>\n")
            datfile.write("Reference\tRight Count\tLeft Count\tRight %\tLeft %\tNotes\n")
            for d in data:
                note_str = replace_species_in_string(d.notes)
                rstr = format_reference_cite(refdict[d.ref], do_print, AUTHOR_PAREN, "../")
                outfile.write("<tr><td>{}</td><td>{}</td><td>{}</td><td>{:0.3f}</td><td>{:0.3f}</td>"
                              "<td>{}</td></tr>\n".format(rstr, d.right_cnt, d.left_cnt, d.right_p, d.left_p, note_str))
                datfile.write("{}\t{}\t{}\t{:0.3f}\t{:0.3f}\t{}\n".format(d.ref, d.right_cnt, d.left_cnt, d.right_p,
                                                                          d.left_p, note_str))
            outfile.write("</table>\n")
            datfile.write("\n")
    else:
        outfile.write("<p><em>No data available at this time.</em></p>\n")

    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile)


def create_species_cb_page(outfile: TextIO, do_print: bool, species: TMB_Classes.SpeciesClass,
                           measurement_data: TMB_Classes.SpeciesMeasurements, refdict: dict) -> Tuple[float, float]:
    """
    write species carapace width page
    """
    if do_print:
        start_page_division(outfile, "base_page")
    else:
        common_html_header(outfile, species.binomial() + " Carapace Breadth", indexpath="../")
    outfile.write("    <header id=\"" + species.species + "_cb.html\">\n")
    outfile.write("      <h1 class=\"nobookmark\"><em class=\"species\">" + species.binomial() +
                  "</em> Carapace Breadth</h1>\n")

    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "../") + "u_" + species.species +
                      ".html\">" + fetch_fa_glyph("info") + "Species page</a></li>\n")
        outfile.write("          <li><a href=\"index.html\">" + fetch_fa_glyph("measure") +
                      "Measurement Guide</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")

    cdat = TMB_Measurements.combine_measurement_data(measurement_data.all)
    mdat = TMB_Measurements.combine_measurement_data(measurement_data.male)
    fdat = TMB_Measurements.combine_measurement_data(measurement_data.female)

    filename = WEBOUT_PATH + "sizes/" + species.species + "_cb.png"
    TMB_Measurements.plot_measurement_data(measurement_data, cdat, mdat, fdat, filename)

    mean = numpy.mean(cdat)
    std = numpy.std(cdat)

    outfile.write("       <h2>Summary</h2>\n")
    slabel = size_label(mean + 1.96*std)
    outfile.write("         <p>{} Carapace Breadth: {:0.1f} mm ± {:0.2f} (sd), 95% range: "
                  "{:0.1f}&ndash;{:0.1f} mm</p>\n".format(slabel, mean, std, max(mean - 1.96*std, 0), mean + 1.96*std))

    outfile.write("    <figure class=\"sizeimg\">\n")
    outfile.write("      <img src=\"{0}_cb.png\" alt=\"size data for {1}\" "
                  "title=\"size data for {1}\"/>\n".format(species.species, species.binomial()))
    outfile.write("    </figure>\n")

    with open(WEBOUT_PATH + "sizes/" + species.species + "_cb.txt", "w") as datfile:
        outfile.write("    <h2>Data</h2>\n")
        outfile.write("    <p>All measurements are in millimeters (mm). <a href=\"" + species.species + "_cb.txt\">" +
                      fetch_fa_glyph("file download") + " Download Data</a></p>")
        if "individual" in measurement_data.all:
            outfile.write("    <h3>Individuals</h3>\n")
            outfile.write("<table class=\"size_data_table\">\n")
            outfile.write("<tr><th>Reference</th><th>Sex</th><th>Width</th><th>Notes</th></tr>\n")
            datfile.write("Individuals\n")
            datfile.write("Reference\tSex\tWidth\tNotes\n")
            idata = measurement_data.all["individual"]
            for d in idata:
                rstr = format_reference_cite(refdict[d.ref], do_print, AUTHOR_PAREN, "../")
                outfile.write("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>\n".format(rstr, d.sex, d.value,
                                                                                               d.notes))
                datfile.write("{}\t{}\t{}\t{}\n".format(d.ref, d.sex, d.value, d.notes))
            outfile.write("</table>\n")
            datfile.write("\n")

        if "range" in measurement_data.all:
            outfile.write("    <h3>Ranges</h3>\n")
            outfile.write("<table class=\"size_data_table\">\n")
            outfile.write("<tr><th>Reference</th><th>Sex</th><th>n</th><th>Min</th><th>Max</th><th>Notes</th></tr>\n")
            datfile.write("Ranges\n")
            datfile.write("Reference\tSex\tn\tMin\tMax\tNotes\n")
            idata = measurement_data.all["range"]
            for d in idata:
                rstr = format_reference_cite(refdict[d.ref], do_print, AUTHOR_PAREN, "../")
                outfile.write("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td>"
                              "<td>{}</td><td>{}</td></tr>\n".format(rstr, d.sex, d.n, d.value.min_val,
                                                                     d.value.max_val, d.notes))
                datfile.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(d.ref, d.sex, d.n, d.value.min_val, d.value.max_val,
                                                                d.notes))
            outfile.write("</table>\n")
            datfile.write("\n")

        if "mean" in measurement_data.all:
            outfile.write("    <h3>Means</h3>\n")
            outfile.write("<table class=\"size_data_table\">\n")
            outfile.write("<tr><th>Reference</th><th>Sex</th><th>n</th><th>Mean</th><th>Notes</th></tr>\n")
            datfile.write("Means\n")
            datfile.write("Reference\tSex\tn\tMean\tNotes\n")
            idata = measurement_data.all["mean"]
            for d in idata:
                rstr = format_reference_cite(refdict[d.ref], do_print, AUTHOR_PAREN, "../")
                outfile.write("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td>"
                              "<td>{}</td></tr>\n".format(rstr, d.sex, d.n, d.value.mean, d.notes))
                datfile.write("{}\t{}\t{}\t{}\t{}\n".format(d.ref, d.sex, d.n, d.value.mean, d.notes))
            outfile.write("</table>\n")
            datfile.write("\n")

        if "mean/sd" in measurement_data.all:
            outfile.write("    <h3>Means w/Standard Deviation</h3>\n")
            outfile.write("<table class=\"size_data_table\">\n")
            outfile.write("<tr><th>Reference</th><th>Sex</th><th>n</th><th>Mean</th><th>SD</th><th>Notes</th></tr>\n")
            datfile.write("Means w/Standard Deviation\n")
            datfile.write("Reference\tSex\tn\tMean\tSD\tNotes\n")
            idata = measurement_data.all["mean/sd"]
            for d in idata:
                rstr = format_reference_cite(refdict[d.ref], do_print, AUTHOR_PAREN, "../")
                outfile.write("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>"
                              "<td>{}</td></tr>\n".format(rstr, d.sex, d.n, d.value.mean, d.value.sd, d.notes))
                datfile.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(d.ref, d.sex, d.n, d.value.mean, d.value.sd, d.notes))
            outfile.write("</table>\n")
            datfile.write("\n")

        if "mean/se" in measurement_data.all:
            outfile.write("    <h3>Means w/Standard Error</h3>\n")
            outfile.write("<table class=\"size_data_table\">\n")
            outfile.write("<tr><th>Reference</th><th>Sex</th><th>n</th><th>Mean</th><th>SE</th><th>Notes</th></tr>\n")
            datfile.write("Means w/Standard Error\n")
            datfile.write("Reference\tSex\tn\tMean\tSE\tNotes\n")
            idata = measurement_data.all["mean/se"]
            for d in idata:
                rstr = format_reference_cite(refdict[d.ref], do_print, AUTHOR_PAREN, "../")
                outfile.write("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>"
                              "<td>{}</td></tr>\n".format(rstr, d.sex, d.n, d.value.mean, d.value.se, d.notes))
                datfile.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(d.ref, d.sex, d.n, d.value.mean, d.value.se, d.notes))
            outfile.write("</table>\n")
            datfile.write("\n")

        if "mean/sd/min/max" in measurement_data.all:
            outfile.write("    <h3>Means w/Range and Standard Deviation</h3>\n")
            outfile.write("<table class=\"size_data_table\">\n")
            outfile.write("<tr><th>Reference</th><th>Sex</th><th>n</th><th>Mean</th><th>SD</th><th>Min</th>"
                          "<th>Max</th><th>Notes</th></tr>\n")
            datfile.write("Means w/Range and Standard Deviation\n")
            datfile.write("Reference\tSex\tn\tMean\tSD\tMin\tMax\tNotes\n")
            idata = measurement_data.all["mean/sd/min/max"]
            for d in idata:
                rstr = format_reference_cite(refdict[d.ref], do_print, AUTHOR_PAREN, "../")
                outfile.write("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>"
                              "<td>{}</td></tr>\n".format(rstr, d.sex, d.n, d.value.mean, d.value.sd,
                                                          d.value.min_val, d.value.max_val, d.notes))
                outfile.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(d.ref, d.sex, d.n, d.value.mean, d.value.sd,
                                                                        d.value.min_val, d.value.max_val, d.notes))
            outfile.write("</table>\n")
            datfile.write("\n")

        if "classcount" in measurement_data.all:
            outfile.write("    <h3>Histogram Counts</h3>\n")
            outfile.write("<table class=\"size_data_table\">\n")
            outfile.write("<tr><th>Reference</th><th>Set</th><th>Sex</th><th>n</th><th>Min</th><th>Max</th>"
                          "<th>Notes</th></tr>\n")
            datfile.write("Histogram Counts\n")
            datfile.write("Reference\tSet\tSex\tn\tMin\tMax\tNotes\n")
            idata = measurement_data.all["classcount"]
            classes = set()
            for d in idata:
                classes.add(d.class_id)
            for c in classes:
                current_class = []
                for d in idata:
                    if c == d.class_id:
                        current_class.append(d)
                for d in current_class:
                    rstr = format_reference_cite(refdict[d.ref], do_print, AUTHOR_PAREN, "../")
                    outfile.write("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>"
                                  "<td>{}</td></tr>\n".format(rstr, c, d.sex, d.n, d.value.min_val, d.value.max_val,
                                                              d.notes))
                    datfile.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(d.ref, c, d.sex, d.n, d.value.min_val,
                                                                        d.value.max_val, d.notes))
                outfile.write("<tr><td colspan=7>&nbsp;</td></tr>\n")
                datfile.write("\n")
            outfile.write("</table>\n")

    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile)

    return float(mean), float(std)


def write_photo_index(outfile: TextIO, do_print: bool, specieslist: list, photos: list, refdict: dict) -> None:
    """
    create an index of all photos
    """
    if do_print:
        start_page_division(outfile, "index_page")
        media_path = MEDIA_PATH
    else:
        common_html_header(outfile, "Fiddler Crab Photos")
        media_path = ""
    outfile.write("    <header id=\"" + init_data().photo_url + "\">\n")
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
        outfile.write("      <h2 class=\"nobookmark\">" +
                      create_species_link(sp.genus, species, do_print, status=status) + "</h2>\n")
        photo_n = 0
        for photo in photos:
            splist = photo.species.split(";")
            if species in splist:
                pn = int(photo.n)
                if ";" in photo.species:
                    spname = photo.species.replace(";", "_")
                else:
                    spname = photo.species
                pfname = "photo_u_" + spname + format(pn, "0>2") + ".html"
                outfile.write("      <figure class=\"sppic\">\n")
                outfile.write("        <a href=\"" + rel_link_prefix(do_print, "photos/") + pfname +
                              "\"><img class=\"thumbnail\" src=\"" + media_path + "photos/U_" + spname +
                              format(pn, "0>2") + "tn.jpg\" alt=\"" + spname + " thumbnail\" title=\"" +
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
        common_html_footer(outfile)

    # output individual photo pages
    for sp in specieslist:
        species = sp.species
        # for photo in tqdm(photos):
        for photo in photos:
            splist = photo.species.split(";")
            if species == splist[0]:  # only output one time
                pn = int(photo.n)
                if ";" in photo.species:
                    spname = photo.species.replace(";", "_")
                else:
                    spname = photo.species
                pfname = "photo_u_" + spname + format(pn, "0>2") + ".html"
                if do_print:
                    write_species_photo_page(outfile, True, pfname, species, sp.common, photo.caption, pn,
                                             photo.species, refdict)
                else:
                    # copy photos and thumbnails to web output directory
                    tmp_name = "photos/U_" + spname + format(pn, "0>2")
                    try:
                        shutil.copy2(MEDIA_PATH + tmp_name + ".jpg",  WEBOUT_PATH + "photos/")
                    except FileNotFoundError:
                        report_error("Missing file: " + tmp_name + ".jpg")
                    try:
                        shutil.copy2(MEDIA_PATH + tmp_name + "tn.jpg", WEBOUT_PATH + "photos/")
                    except FileNotFoundError:
                        report_error("Missing file: " + tmp_name + "tn.jpg")
                    with open(WEBOUT_PATH + "photos/" + pfname, "w", encoding="utf-8") as suboutfile:
                        write_species_photo_page(suboutfile, False, pfname, species, sp.common, photo.caption, pn,
                                                 photo.species, refdict)


def write_video_index(outfile: TextIO, do_print: bool, videos: list) -> None:
    """
    create an index of all videos
    """
    sectitle = ("Feeding", "Male Waving and Other Displays", "Female Display", "Fighting", "Mating", "Miscellaneous")
    secshort = ("Feeding", "Male Display", "Female Display", "Fighting", "Mating", "Miscellaneous")
    secanchor = ("video_feeding", "video_display", "video_female", "video_fighting", "video_mating", "video_misc")
    if do_print:
        start_page_division(outfile, "index_page")
    else:
        common_html_header(outfile, "Fiddler Crab Videos")
    outfile.write("    <header id=\"" + init_data().video_url + "\">\n")
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
        outfile.write("      Videos are available on the web at <a href=\"" + init_data().site_url() +
                      "/" + init_data().video_url + "\">" + init_data().site_url() +
                      "/" + init_data().video_url + "</a> or by following the embedded links.")
        outfile.write("    </p>\n")
    outfile.write("    <p>\n")
    if do_print:
        linktxt = "individual species' page"
    else:
        linktxt = "<a href=\"" + rel_link_prefix(do_print) + init_data().species_url + "\">individual species' page</a>"
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
                              "\">" + replace_species_in_string(video.caption) + "</a></dt>\n")
                outfile.write("              <dd>{}, {:d} &times; {:d}, {}</dd>\n".format(video.length, video.width,
                                                                                          video.height, video.format))
        outfile.write("      </dl>\n")
        outfile.write("    </section>\n")
    # write individual video pages
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile)
        # for video in tqdm(videos):
        for video in videos:
            vn = int(video.n)
            if ";" in video.species:
                spname = video.species.replace(";", "_")
            else:
                spname = video.species
            vfname = WEBOUT_PATH + "video/video_u_" + spname + format(vn, "0>2") + ".html"
            write_species_video_page(vfname, video, vn)
            # copy video to web output directory
            tmp_name = "video/U_" + spname + format(vn, "0>2") + "." + video.format.lower()
            try:
                shutil.copy2(MEDIA_PATH + tmp_name, WEBOUT_PATH + "video/")
            except FileNotFoundError:
                report_error("Missing file: " + tmp_name)


def write_specific_art_page(outfile: TextIO, do_print: bool, art: TMB_Classes.ArtClass, backurl: str,
                            backtext: str, refdict: dict) -> None:
    """
    create a page for a piece of art
    """
    if (art.art_type == "science") and (art.cite_key != "n/a"):
        ref = refdict[art.cite_key]
        author = ref.citation
    else:
        author = art.author + " (" + art.year + ")"
    ptitle = art.title + ": " + author

    if do_print:
        start_page_division(outfile, "art_page")
        media_path = MEDIA_PATH + "art/"
    else:
        common_html_header(outfile, ptitle, indexpath="../")
        media_path = ""
    outfile.write("    <header id=\"" + art.image + ".html\">\n")
    outfile.write("      <h1 class=\"nobookmark\"><em class=\"species\">" + art.title + "</em></h1>\n")
    outfile.write("      <h2 class=\"nobookmark\">" + author + "</h2>\n")
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
    outstr = replace_reference_in_string(art.notes, refdict, do_print, path="../")
    outfile.write("      <figcaption>" + replace_species_in_string(outstr) + "</figcaption>\n")
    outfile.write("    </figure>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, indexpath="../")


def write_art_science_pages(outfile: TextIO, do_print: bool, artlist: list, refdict: dict) -> None:
    """
    create an index for all scientific art
    """
    if do_print:
        start_page_division(outfile, "index_page")
        media_path = MEDIA_PATH
    else:
        common_html_header(outfile, "Fiddler Crab Art - Scientific")
        media_path = ""
    outfile.write("    <header id=\"" + init_data().art_sci_url + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Scientific Drawings</h1>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    artsource = []
    cnt = 0
    for art in artlist:
        if art.art_type == "science":
            cnt += 1
            if art.cite_key != "n/a":
                ref = refdict[art.cite_key]
                artist = ref.citation
            else:
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
                if art.cite_key != "n/a":
                    ref = refdict[art.cite_key]
                    artist = ref.citation
                else:
                    artist = art.author + " (" + art.year + ")"
                if artist == a:
                    outfile.write("      <figure class=\"sppic\">\n")
                    outfile.write("        <a href=\"" + rel_link_prefix(do_print, "art/") + art.image +
                                  ".html\"><img class=\"thumbnail\" src=\"" + media_path + "art/" +
                                  art.image + "_tn." + art.ext + "\" alt=\"" + art.title + " thumbnail\" title=\"" +
                                  art.title + "\" /></a>\n")
                    outfile.write("      </figure>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile)
    for a in artsource:
        for art in artlist:
            if art.art_type == "science":
                if art.cite_key != "n/a":
                    ref = refdict[art.cite_key]
                    artist = ref.citation
                else:
                    artist = art.author + " (" + art.year + ")"
                if artist == a:
                    if do_print:
                        write_specific_art_page(outfile, do_print, art, init_data().art_sci_url,
                                                "All Scientific Drawings", refdict)
                    else:
                        with open(WEBOUT_PATH + "art/" + art.image + ".html", "w", encoding="utf-8") as suboutfile:
                            write_specific_art_page(suboutfile, do_print, art, init_data().art_sci_url,
                                                    "All Scientific Drawings", refdict)


def write_art_stamps_pages(outfile: TextIO, do_print: bool, artlist: list, refdict: dict) -> None:
    """
    create an index for all stamps
    """
    if do_print:
        start_page_division(outfile, "index_page")
        media_path = MEDIA_PATH
    else:
        common_html_header(outfile, "Fiddler Crab Stamps")
        media_path = ""
    outfile.write("    <header id=\"" + init_data().art_stamp_url + "\">\n")
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
                    outfile.write("      <figure class=\"sppic\">\n")
                    outfile.write("        <a href=\"" + rel_link_prefix(do_print, "art/") + art.image +
                                  ".html\"><img class=\"thumbnail\" src=\"" + media_path + "art/" +
                                  art.image + "_tn." + art.ext + "\" alt=\"" + art.title + " thumbnail\" title=\"" +
                                  art.title + "\" /></a>\n")
                    outfile.write("      </figure>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile)
    for a in artsource:
        for art in artlist:
            if art.art_type == "stamp":
                if art.author == a:
                    if do_print:
                        write_specific_art_page(outfile, do_print, art, init_data().art_stamp_url, "All Stamps",
                                                refdict)
                    else:
                        with open(WEBOUT_PATH + "art/" + art.image + ".html", "w", encoding="utf-8") as suboutfile:
                            write_specific_art_page(suboutfile, do_print, art, init_data().art_stamp_url, "All Stamps",
                                                    refdict)

    
def write_art_crafts_pages(outfile: TextIO, do_print: bool, artlist: list, refdict: dict) -> None:
    """
    create an index for all crafts
    """
    if do_print:
        start_page_division(outfile, "index_page")
        media_path = MEDIA_PATH
    else:
        common_html_header(outfile, "Fiddler Crab Crafts")
        media_path = ""
    outfile.write("    <header id=\"" + init_data().art_craft_url + "\">\n")
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
        common_html_footer(outfile)
    for a in artsource:
        for art in artlist:
            if art.art_type == "origami":
                if art.author == a:
                    if do_print:
                        write_specific_art_page(outfile, do_print, art, init_data().art_craft_url, "All Crafts",
                                                refdict)
                    else:
                        with open(WEBOUT_PATH + "art/" + art.image + ".html", "w", encoding="utf-8") as suboutfile:
                            write_specific_art_page(suboutfile, do_print, art, init_data().art_craft_url, "All Crafts",
                                                    refdict)


def write_all_art_pages(outfile: Optional[TextIO], do_print: bool, artlist: list, refdict: dict) -> None:
    """
    create all art pages
    """
    if do_print:
        write_art_science_pages(outfile, do_print, artlist, refdict)
        write_art_stamps_pages(outfile, do_print, artlist, refdict)
        write_art_crafts_pages(outfile, do_print, artlist, refdict)
    else:
        with open(WEBOUT_PATH + init_data().art_craft_url, "w", encoding="utf-8") as suboutfile:
            write_art_crafts_pages(suboutfile, do_print, artlist, refdict)
        with open(WEBOUT_PATH + init_data().art_stamp_url, "w", encoding="utf-8") as suboutfile:
            write_art_stamps_pages(suboutfile, do_print, artlist, refdict)
        with open(WEBOUT_PATH + init_data().art_sci_url, "w", encoding="utf-8") as suboutfile:
            write_art_science_pages(suboutfile, do_print, artlist, refdict)
    # copy art files
    if not do_print:
        for art in artlist:
            try:
                shutil.copy2(MEDIA_PATH + "art/" + art.image + "." + art.ext, WEBOUT_PATH + "art/")
            except FileNotFoundError:
                report_error("Missing file: " + MEDIA_PATH + "art/" + art.image + "." + art.ext)
            try:
                shutil.copy2(MEDIA_PATH + "art/" + art.image + "_tn." + art.ext, WEBOUT_PATH + "art/")
            except FileNotFoundError:
                report_error("Missing file: " + MEDIA_PATH + "art/" + art.image + "_tn." + art.ext)


def write_species_info_pages(outfile: Optional[TextIO], do_print: bool, specieslist: list, references: list,
                             specific_names: list, all_names: list, photos: list, videos: list, art: list,
                             species_refs: dict, refdict: dict, binomial_name_cnts: dict,
                             specific_name_cnts: dict, higher_dict: dict, measurement_data: dict,
                             handedness_data: list) -> None:
    """
    create the species index and all individual species pages
    """
    if do_print:
        write_species_list(outfile, True, specieslist)
    else:
        with open(WEBOUT_PATH + init_data().species_url, "w", encoding="utf-8") as suboutfile:
            write_species_list(suboutfile, False, specieslist)
    # for species in tqdm(specieslist):
    for species in specieslist:
        sprefs = species_refs[species.species]
        if do_print:
            write_species_page(outfile, True, species, references, specific_names, all_names, photos, videos, art,
                               sprefs, refdict, binomial_name_cnts, specific_name_cnts, higher_dict, measurement_data,
                               handedness_data)
        else:
            with open(WEBOUT_PATH + "u_" + species.species + ".html", "w", encoding="utf-8") as suboutfile:
                write_species_page(suboutfile, False, species, references, specific_names, all_names, photos, videos,
                                   art, sprefs, refdict, binomial_name_cnts, specific_name_cnts, higher_dict,
                                   measurement_data, handedness_data)

    if do_print:
        write_measurement_guide(outfile, True)
        write_handedness_guide(outfile, refdict, True)
    else:
        with open(WEBOUT_PATH + "sizes/index.html", "w") as suboutfile:
            write_measurement_guide(suboutfile, False)
        with open(WEBOUT_PATH + "handedness/index.html", "w") as suboutfile:
            write_handedness_guide(suboutfile, refdict, False)


def write_handedness_guide(outfile: TextIO, refdict: dict, do_print: bool = False):
    """
    output a general guide to the measurement data
    """
    if do_print:
        start_page_division(outfile, "base_page")
    else:
        common_html_header(outfile, "Male Fiddler Crab Handedness", indexpath="../")
    outfile.write("    <header id=\"handedness_index.html\">\n")
    outfile.write("      <h1 class=\"nobookmark\">Male Handedness</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"../" + init_data().species_url + "\">" + fetch_fa_glyph("index") +
                      "Species List</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <section class=\"topspsection\">\n")
    outfile.write("      <p>\n")
    outfile.write("          One of the most striking features of fiddler crabs is the extreme claw asymmetry found "
                  "in males and one of the most common questions I get asked is whether males tend to be right- or "
                  "left-handed. Most people seem to assume they are mostly one or the other, but in fact, most "
                  "fiddler crab species appear to be evenly split 50:50 between right- and left-handed males. "
                  "The exceptions are the species in the genus <em>Gelasimus</em>, where males are almost entirely "
                  "right-handed (generally >95%).\n")
    outfile.write("      </p>\n")
    weis_ref = format_reference_cite(refdict["Weis2019"], do_print, AUTHOR_NOPAREN, path="../")
    outfile.write("      <p>\n")
    outfile.write("          An extremely common misconception is that when a male fiddler crab loses its large "
                  "claw that the handedness switches and the small claws grows into a new large one. This is simply "
                  "wrong! The crab will regenerate a large claw on the same side; the small claw remains small. "
                  "This urban legend is so persistent that it's appeared (and been removed) from Wikipedia multiple "
                  "times. Judith Weis recently wrote a paper about the origins and persistence of this "
                  "myth ({}).\n".format(weis_ref))
    outfile.write("      </p>\n")

    morgan23_ref = format_reference_cite(refdict["Morgan1923.1"], do_print, AUTHOR_PAREN, path="../")
    morgan24_ref = format_reference_cite(refdict["Morgan1924"], do_print, AUTHOR_PAREN, path="../")
    vernberg66_ref = format_reference_cite(refdict["Vernberg1966.1"], do_print, AUTHOR_PAREN, path="../")
    yamaguchi77_ref = format_reference_cite(refdict["Yamaguchi1977"], do_print, AUTHOR_PAREN, path="../")
    yamaguchi78_ref = format_reference_cite(refdict["Yamaguchi1978"], do_print, AUTHOR_PAREN, path="../")
    ahmed781_ref = format_reference_cite(refdict["Ahmed1978.1"], do_print, AUTHOR_PAREN, path="../")
    ahmed782_ref = format_reference_cite(refdict["Ahmed1978.2"], do_print, AUTHOR_PAREN, path="../")
    krishnan92_ref = format_reference_cite(refdict["Krishnan1992.3"], do_print, AUTHOR_PAREN, path="../")
    yamaguchi01_ref = format_reference_cite(refdict["Yamaguchi2001.8"], do_print, AUTHOR_PAREN, path="../")

    outfile.write("      <p>\n")
    outfile.write("          How handedness is determined has been studied by researchers numerous times, but the "
                  "answer is still not entirely clear, as different studies have not always come to the same "
                  "conclusion and there are a number of possible explanations for the variation in results. "
                  "For the mostly right-handed species, right-handedness is likely genetically hardwired with the "
                  "occasional left-handed individuals probably due to environmental damage at a critical "
                  "developmental stage leading to the development of left-handedness. For the rest of the species, "
                  "it is probably randomly determined by the environment, although there could be a genetic factor or "
                  "a combination of both. "
                  "Breeding experiments to examine heritability in fiddlers are not particularly easy or feasible. "
                  "Some of the studies on this question include "
                  "{}, {}, {}, {}, {}, {}, {}, {}, and {}.\n".format(morgan23_ref, morgan24_ref, vernberg66_ref,
                                                                     yamaguchi77_ref, yamaguchi78_ref, ahmed781_ref,
                                                                     ahmed782_ref, krishnan92_ref, yamaguchi01_ref))
    outfile.write("      </p>\n")
    alt_ref = format_reference_cite(refdict["Altevogt1979"], do_print, AUTHOR_PAREN, path="../")
    outfile.write("      <p>\n")
    outfile.write("          Species information pages on this site include a link to information about the "
                  "handedness for that species, including the predicted handedness based on taxonomy and the "
                  "observed data that has been recorded (if any), including an overall estimate of the handedness "
                  "based on the (usually limited) available data. Data has been updated to reflect our current "
                  "taxonomy rather than the name used in the publication; some samples may include mixed species "
                  "if certain species boundaries were not recognized at the time of original publication. "
                  "Not all papers that "
                  "record handedness have been entered yet, but many species have not been formally examined for "
                  "handedness ratios, particularly with large sample sizes. Sometimes when they are commented upon, "
                  "key data and specifics are not provided. For example, {} report that 23 non-specified "
                  "species have 50:50 ratios, and that "
                  "more recent re-examination of three of these species still have 50:50 rations, while a fourth "
                  "has a 50:50 from over 400 specimens examined. No actual counts are specified. They then state that "
                  "in another species, only one left-handed male was found out of more than 1,000 examined. "
                  "While useful general statements, these numbers lack the specificity one would want for "
                  "computational analysis (For what it's worth, they also claim that the right-handed skewed species "
                  "used to be 50:50 and shifted to the skew, but it is more likely that they never paid close "
                  "attention in previous years.)\n".format(alt_ref))
    outfile.write("      </p>\n")

    outfile.write("    </section>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile)


def write_measurement_guide(outfile: TextIO, do_print: bool):
    """
    output a general guide to the measurement data
    """
    if do_print:
        start_page_division(outfile, "base_page")
    else:
        common_html_header(outfile, "Fiddler Crab Carapace Breadth Measurements", indexpath="../")
    outfile.write("    <header id=\"size_index.html\">\n")
    outfile.write("      <h1 class=\"nobookmark\">Carapace Breadth Guide</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"../" + init_data().species_url + "\">" + fetch_fa_glyph("index") +
                      "Species List</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <section class=\"topspsection\">\n")
    outfile.write("      <p>\n")
    outfile.write("          This is a general guide to the data and figures on fiddler crab size on the site. At "
                  "this time size is presented as carapace width (or breadth). This is either measured as the "
                  "maximum breadth of the carapace or the distance between the tips of the antero-lateral angles; "
                  "usually (although not always) these are the same thing, although the difference is always "
                  "minor when there is one. All measurements are presented in millimeters (mm).\n")
    outfile.write("      </p>\n")
    outfile.write("<figure class=\"morphimg\">\n")
    outfile.write("  <img src=\"../morphology/carapace2.png\" "
                  "alt=\"Illustration of carpace width and length. Figure modified from Crane (1975).\" "
                  "title=\"Illustration of carpace width and length. Figure modified from Crane (1975).\" />\n")
    outfile.write("  <figcaption>Illustration of carpace width and length. "
                  "Figure modified from Crane (1975).</figcaption>\n")
    outfile.write("</figure>\n")
    outfile.write("      <p>\n")
    outfile.write("          For each species, the bottom part of its size page lists all of the data values, "
                  "including source. In some cases data was extracted from figues (should be indicated in the notes). "
                  "The data for each species can also be downloaded as a tab-separated text document. The top "
                  "of each page begins with a graphical illustration of all of the data, including a summary "
                  "figure which integrates all of the data into a single estimated distribution. Different types of "
                  "data are displayed in a different manner in the figures, and are described below.\n")
    outfile.write("      </p>\n")
    outfile.write("      <p>\n")
    outfile.write("         As a general rule, data are added to the figure from the bottom up. Blue data points and "
                  "images refer to male data, red refers to female data, and black refers to mixed/combined/"
                  "sex-unspecified data. Male data and female data are always plotted separately, except when "
                  "combined into the summary distribution (black) at the top of each figure.\n")
    outfile.write("      </p>\n")
    outfile.write("      <h2>Individuals</h2>\n")
    outfile.write("      <p>\n")
    outfile.write("         The most sraight-forward data are direct measurements of individuals. These are "
                  "graphically displayed as round points at the bottom of each figure. The vertical shifting of the "
                  "points is meaningless, arbitrary noise used to help better display the density of similar "
                  "measurements.\n")
    outfile.write("      </p>\n")
    outfile.write("<figure class=\"morphimg\">\n")
    outfile.write("  <img src=\"../images/size_ind.png\" alt=\"Example of individual size plot.\" "
                  "title=\"Example of individual size plot.\" />\n")
    outfile.write("</figure>\n")
    outfile.write("      <h2>Ranges</h2>\n")
    outfile.write("      <p>\n")
    outfile.write("         Range data represents the largest and smallest values for a group of individuals, "
                  "including sample size when available. When unavailable, the sample size was assumed to be 2 as "
                  "this is the miniumm number necessary to create a range. Ranges are drawn as horizontal lines with "
                  "vertical endcaps representing the minimum and maximum widths. Each range is drawn separately; "
                  "sample size is not indicated on the graph (but is in the data table).\n")
    outfile.write("      </p>\n")
    outfile.write("<figure class=\"morphimg\">\n")
    outfile.write("  <img src=\"../images/size_range.png\" alt=\"Example of range plots.\" "
                  "title=\"Example of range plots.\" />\n")
    outfile.write("</figure>\n")
    outfile.write("      <h2>Means</h2>\n")
    outfile.write("      <p>\n")
    outfile.write("         Means represent average sizes of a sample. Reported means may include sample size, "
                  "standard deviation, standard error, and even minimum and maximum values. Sometimes they include "
                  "none of these (in which case the sample size is assumed to be 1, <em>i.e.,</em> equivalent to an "
                  "individual. Each combination of data reporting is listed in a separate data table. Visually, "
                  "means are drawn on the figure as diamonds, each on it's own line. A 95% confidence interval is "
                  "included when an SD or SE is available. If both SD and min/max are available, the figure "
                  "includes both a thicker line indicating the 95% CI and a thinner line with vertical endcaps "
                  "indicating the maximum and minimum values.\n")
    outfile.write("      </p>\n")
    outfile.write("<figure class=\"morphimg\">\n")
    outfile.write("  <img src=\"../images/size_mean.png\" alt=\"Example of means plots.\" "
                  "title=\"Example of means plots.\" />\n")
    outfile.write("</figure>\n")
    outfile.write("      <h2>Histograms</h2>\n")
    outfile.write("      <p>\n")
    outfile.write("       Occasionally a size distribution is available as a histogram. In this case, the data is "
                  "presented as the min and max of each histogram bar and the sample size (height) of the bar. "
                  "Bars for the same histogram are labeled in the data by a unique set name. Histograms are drawn "
                  "on the figure as standard histograms, except that each unique histogram is scaled to the "
                  "identical maximum height, thus the drawn histograms can be used for general distribution comparison "
                  "but do not indicate the case where one may be based on a much larger sample than another (all "
                  "sample sizes are part of the data table).\n")
    outfile.write("      </p>\n")
    outfile.write("<figure class=\"morphimg\">\n")
    outfile.write("  <img src=\"../images/size_hist.png\" alt=\"Example of histogram plots.\" "
                  "title=\"Example of histogram plots.\" />\n")
    outfile.write("</figure>\n")
    outfile.write("      <h2>Summary Distributions</h2>\n")
    outfile.write("      <p>\n")
    outfile.write("       The summary distributions are calculated for males and females independently, as well as "
                  "combined (the top figure in black). These distributions are created through a simulated integration "
                  "across all of the data for that species. The simulation creates a large &ldquo;data set&rdquo; of "
                  "individual measurements from all of the distinct data sets and types. The data set with the "
                  "largest sample size is scaled to provide 1,000 values to our simulated data set. All other data "
                  "sets provide values proportionally (<em>e.g.</em>, if the largest data set has <em>n</em>=50, that "
                  "data set will provide 1,000 values, while one with an <em>n</em>=10 would provide 200). (In the "
                  "unlikely event that the largest observed data set has n > 1,000, the algorithm automatically "
                  "rescales the largest sample by orders of magnitude until it exceeds the largest n). Data values are "
                  "&ldquo;simulated&rdquo; based on each data set depending on the type of data. Individual measures, "
                  "which definitionally have <em>n</em>=1, are added directly to the simulated set in numbers "
                  "proportional to the largest sample. Frequency histograms are also directly added to the simulated "
                  "set with the midpoint of each bin representing the value added and the total count of the bin "
                  "representing the <em>n</em> to scale to the largest sample. For measures represented by means with "
                  "an estimate of variance; values are simulated from a normal distribution (with expected mean and "
                  "variance). If a mean is reported without a variance, it is treated as if the variance were "
                  "zero; this has the obvious potential to give too much weight to that estimate, but generally "
                  "these have very small sample sizes so the effect appears to be minor.\n")
    outfile.write("      <p>\n")
    outfile.write("       Range data is the most complicated part of the simulation. First, the end points of the "
                  "range are added as if they were individual measures. If the sample size of the range is greater "
                  "than two, then the remaining samples (after those representing the endpoints are accounted for) "
                  "are drawn from a restricted normal distribution whose mean is represented by the midpoint of the "
                  "range and whose standard deviation is estimated as the width of the range divided by four "
                  "(the &ldquo;range rule of thumb&rdquo;). The restriction is that only simulated values that fall "
                  "within the reported range are accepted.\n")
    outfile.write("      </p>\n")
    outfile.write("      <p>\n")
    outfile.write("All of these simulated data points from all of these data types are combined together into one "
                  "overall set. From this set, 1,000 values are then randomly subsampled to estimate the overall "
                  "distribution, mean, median, etc.\n")
    outfile.write("      </p>\n")
    outfile.write("      <p>\n")
    outfile.write("       The simulated summary results are shown by the violin graphs at the tops of each figure. "
                  "These reveal a lot of information. Each of these graphs show the full range of the distribution, "
                  "a density estimate of sizes (based on the colored, curvy background), the mean (diamond), "
                  "median (circle), and quartile (thick center line).\n")
    outfile.write("      </p>\n")
    outfile.write("<figure class=\"morphimg\">\n")
    outfile.write("  <img src=\"../images/size_summary.png\" alt=\"Example of size summary plot.\" "
                  "title=\"Example of size summary plot.\" />\n")
    outfile.write("</figure>\n")
    outfile.write("    </section>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile)


def replace_media_path(x: str, p: str) -> str:
    return x.replace("%%MEDIA_PATH%%", p)


# def write_systematics_overview(outfile: TextIO, do_print: bool, taxon_ranks: list, higher_taxa_list: list,
#                                specieslist: list, refdict: dict, species_changes_new: list,
#                                species_changes_synonyms: list, species_changes_spelling: list) -> None:
def write_systematics_overview(outfile: TextIO, do_print: bool, taxon_ranks: list, higher_taxa_list: list,
                               specieslist: list, refdict: dict) -> None:
    """
    create the systematics page
    """

    # def write_species_table(header: list, data_list: list) -> None:
    #     outfile.write("      <table>\n")
    #     outfile.write("        <thead>\n")
    #     outfile.write("          <tr>\n")
    #     for h in header:
    #         outfile.write("            <th>" + h + "</th>\n")
    #     outfile.write("          </tr>\n")
    #     outfile.write("        </thead>\n")
    #     outfile.write("        <tbody>\n")
    #     for data in data_list:
    #         outfile.write("          <tr>\n")
    #         outfile.write("            <td><em class=\"species\">Uca " + data[0] + "</em></td>\n")
    #         if data[1] != ".":
    #             outfile.write("            <td><em class=\"species\">Uca " + data[1] + "</em></td>\n")
    #         if data[2] == ".":
    #             outfile.write("            <td>Unpublished</td>\n")
    #         else:
    #             refs = data[2].split(";")
    #             frefs = [format_reference_cite(refdict[r], do_print, AUTHOR_PAREN) for r in refs]
    #             outfile.write("            <td>" + ", ".join(frefs) + "</td>\n")
    #         outfile.write("          </tr>\n")
    #     outfile.write("        </tbody>\n")
    #     outfile.write("      </table>\n")

    # def rank_tags(x: str) -> Tuple[str, str]:
    #     if ("genus" in x) or ("species" in x):
    #         return "<em>", "</em>"
    #     else:
    #         return "", ""

    def taxon_link(tax: TMB_Classes.RankedTaxonClass) -> str:
        return tax.taxon_rank + "_" + tax.name

    def write_taxon_item(tax: TMB_Classes.RankedTaxonClass, ind: str) -> None:
        """
        subfunction to write a hierarchical list of taxonomic names to html
        """
        # starttag, endtag = rank_tags(tax.taxon_rank)
        # outfile.write(ind + "<li><a href=\"#{}\">{} {}{}{}</a>".format(taxon_link(tax), tax.taxon_rank.capitalize(),
        #                                                                starttag, tax.name, endtag))
        outfile.write(ind + "<li>" + create_taxon_link(tax.taxon_rank, tax.name, do_print, same_page=True) + "\n")
        outfile.write(ind + "  <ul>\n")
        if tax.n_children() > 0:
            for cc in sorted(tax.children):
                write_taxon_item(cc, ind + 4 * " ")
        else:
            ssplist = []
            for ss in specieslist:
                if tax.taxon_rank == "genus":
                    if ss.genus == tax.name:
                        ssplist.append(create_species_link(ss.genus, ss.species, do_print, status=ss.status))
                elif tax.taxon_rank == "subgenus":
                    if ss.subgenus == tax.name:
                        ssplist.append(create_species_link(ss.genus, ss.species, do_print, status=ss.status))
            outfile.write(ind + "    <li>" + ", ".join(ssplist) + "</li>\n")
        outfile.write(ind + "  </ul>\n")
        outfile.write(ind + "</li>\n")

    # main function code

    # create list of present taxa ranks for navigation
    rank_cnts = {t.rank: 0 for t in taxon_ranks}
    for t in higher_taxa_list:
        rank_cnts[t.taxon_rank] += 1
    nav_list = []
    for t in taxon_ranks:
        if rank_cnts[t.rank] == 1:
            nav_list.append(t.rank)
        elif rank_cnts[t.rank] > 1:
            nav_list.append(t.plural)

    if do_print:
        start_page_division(outfile, "base_page")
        media_path = MEDIA_PATH
    else:
        common_html_header(outfile, "Fiddler Crab Systematics")
        media_path = ""
    outfile.write("    <header id=\"" + init_data().syst_url + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Systematics</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        for n in nav_list:
            outfile.write("          <li><a href=\"#{}\">{}</a></li>\n".format(n, n.capitalize()))
        # outfile.write("          <li><a href=\"#genus\">Genus</a></li>\n")
        # outfile.write("          <li><a href=\"#subgenera\">Subgenera</a></li>\n")
        # outfile.write("          <li><a href=\"#species\">Species</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")

    outfile.write("    <div class=\"topsection\">\n")
    outfile.write("      <h2>Systematic Hierarchy</h2>\n")
    outfile.write("      <ul>\n")
    for t in sorted(higher_taxa_list):
        if t.parent is None:
            write_taxon_item(t, 8*" ")
    outfile.write("      </ul>\n")
    outfile.write("\n")

    # outfile.write("    <p>The following information is an expansion and update of that found in:</p>\n")
    # outfile.write("    <blockquote>\n")
    # outfile.write("      Rosenberg, M.S. 2001. The systematics and taxonomy of fiddler crabs: A phylogeny of the "
    #               "genus <em class=\"species\">Uca.</em> <em>Journal of Crustacean Biology</em> 21(3):839-869.\n")
    # outfile.write("    </blockquote>\n")
    # outfile.write("    <p>Additional references for updated information will be detailed below.</p>")
    # outfile.write("    </div>\n")
    # outfile.write("\n")

    # outfile.write("    <section class=\"spsection\">\n")
    # outfile.write("      <h2>A Note on Classification</h2>\n")
    # outfile.write("        <p>" + format_reference_cite(refdict["Shih2016.2"], do_print, AUTHOR_PAREN) +
    #               " published a paper which uses a phylogenetic tree showing "
    #               "ghost crabs as a subgroup of fiddler crabs to justify splitting fiddler crabs into eleven "
    #               "different genera (essentially, raising the subgenera listed below to genera, except for "
    #               "<em class=\"species\">Australuca</em> which they find to be a subset of <em class=\"species\">"
    #               "Tubuca</em>). While one can argue whether differences among the subgroups warrant being "
    #               "considered genera or subgenera, I do not believe the phylogenetic tree which they use to justify "
    #               "this change is correct and for now "
    #               "am sticking with the more traditional approach of keeping all fiddler crabs within a single "
    #               "genus on this website. I will update this site to match their classification if additional data "
    #               "and future analyses continue to support their result.</p>")
    # outfile.write("    </section>\n")
    # outfile.write("\n")

    for t_rank in taxon_ranks:
        rank = t_rank.rank
        if rank_cnts[rank] > 0:
            if rank_cnts[rank] == 1:
                rank_title = rank
            else:
                rank_title = t_rank.plural
            outfile.write("    <section class=\"spsection\">\n")
            outfile.write("      <h2 id=\"{}\" class=\"bookmark2\">{}</h2>\n".format(rank_title,
                                                                                     rank_title.capitalize()))
            if t_rank.notes != ".":
                outfile.write("      <p>\n")
                outstr = replace_media_path(t_rank.notes, media_path)
                outfile.write("        " + replace_reference_in_string(outstr, refdict, do_print) + "\n")
                outfile.write("      </p>\n")
            # extract and alphabetically sort taxa at current rank
            rank_list = []
            for taxon in higher_taxa_list:
                if taxon.taxon_rank == rank:
                    rank_list.append(taxon)
            rank_list.sort()
            for taxon in rank_list:
                outfile.write("      <hr />\n")
                start_tag, end_tag = rank_tags(rank)
                if taxon.author == ".":
                    authorstr = ""
                else:
                    authorstr = format_reference_cite(refdict[taxon.author], do_print, AUTHOR_TAXON)
                outfile.write("      <h3 id=\"" + taxon_link(taxon) + "\">" + taxon.taxon_rank.capitalize() + " " +
                              start_tag + taxon.name + end_tag + " " + authorstr + "</h2>\n")
                if taxon.type_species.startswith(">>"):
                    typestr = "Genus <em>" + taxon.type_species[2:] + "</em>"
                elif taxon.type_species.startswith(">"):
                    typestr = "<a href=\"#genus_" + taxon.type_species[1:] + "\">Genus <em>" + \
                              taxon.type_species[1:] + "</em></a>"
                else:
                    s = find_species_by_name(taxon.type_species)
                    typestr = create_species_link(s.genus, s.species, do_print, status=s.status)
                outfile.write("      <dl>\n")
                outfile.write("        <dt>Type</dt>\n")
                outfile.write("        <dd>" + typestr + "</dd>\n")
                if taxon.parent is not None:
                    outfile.write("        <dt>Part of " + taxon.parent.taxon_rank + "</dt>\n")
                    # start_tag, end_tag = rank_tags(taxon.parent.taxon_rank)
                    # outfile.write("        <dd><a href=\"#" + taxon_link(taxon.parent) + "\">" +
                    #               start_tag + taxon.parent.name + end_tag + "</a></dd>\n")
                    outfile.write("        <dd>" + create_taxon_link(taxon.parent.taxon_rank, taxon.parent.name,
                                                                     do_print, same_page=True) + "</dd>\n")
                c_label = "Contains "
                if taxon.n_children() > 0:
                    if taxon.n_children() == 1:
                        c_label += taxon.children[0].taxon_rank
                    else:
                        i = 0
                        while taxon_ranks[i].rank != taxon.children[0].taxon_rank:
                            i += 1
                        c_label += taxon_ranks[i].plural
                    children = []
                    for c in taxon.children:
                        # start_tag, end_tag = rank_tags(c.taxon_rank)
                        # children.append("<a href=\"#" + taxon_link(c) + "\">" + start_tag + c.name + end_tag + "</a>")
                        children.append(create_taxon_link(c.taxon_rank, c.name, do_print, same_page=True))
                    children.sort()
                    outfile.write("        <dt>" + c_label + "</dt>\n")
                    outfile.write("        <dd>" + ", ".join(children) + "</dd>\n")
                else:
                    outfile.write("        <dt>Contains species</dt>\n")
                    splist = []
                    for s in specieslist:
                        if taxon.taxon_rank == "genus":
                            if s.genus == taxon.name:
                                splist.append(create_species_link(s.genus, s.species, do_print, status=s.status))
                        elif taxon.taxon_rank == "subgenus":
                            if s.subgenus == taxon.name:
                                splist.append(create_species_link(s.genus, s.species, do_print, status=s.status))
                    outfile.write("        <dd>" + ", ".join(splist) + "</dd>\n")
                outfile.write("      </dl>\n")
                if taxon.notes != ".":
                    outstr = replace_media_path(taxon.notes, media_path)
                    outfile.write("      <p>" +
                                  replace_species_in_string(replace_reference_in_string(outstr, refdict, do_print)) +
                                  "</p>\n")
            outfile.write("    </section>\n")
            outfile.write("\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile)


def summarize_year(yeardict: dict) -> Tuple[list, list]:
    miny = init_data().current_year
    maxy = 0
    for y in yeardict:
        miny = min(y, miny)
        maxy = max(y, maxy)
        # if y < miny:
        #     miny = y
        # elif y > maxy:
        #     maxy = y
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


def summarize_languages(refs: list) -> Tuple[dict, dict]:
    def primary_language(x: str) -> str:
        """
        remove abstract and summary and secondary language notations
        """
        s = x.find(" ")
        if s > -1:
            x = x[:s]
        return x

    # languages = {}
    languages = collections.Counter()
    miny = init_data().current_year
    maxy = 0
    language_set = set()
    for ref in refs:
        # print(ref.year())
        if ref.year() is not None:
            miny = min(miny, ref.year())
            maxy = max(maxy, ref.year())
            if ref.language != "":
                lang = primary_language(ref.language)
                language_set.add(lang)
    languages_by_year = {lang: {y: 0 for y in range(miny, maxy+1)} for lang in language_set}

    for ref in refs:
        lang = ref.language
        if lang != "":
            lang = primary_language(lang)
            languages.update([lang])
            # if lang in languages:
            #     languages[lang] += 1
            # else:
            #     languages[lang] = 1
            if ref.year() is not None:
                lyear = languages_by_year[lang]
                lyear[ref.year()] += 1
    return languages, languages_by_year


def write_unusual_development_pages(outfile: TextIO, abdevdata: list, refdict: dict, do_print: bool) -> None:
    """
    create the unusual development page
    """
    if do_print:
        start_page_division(outfile, "base_page")
        media_path = MEDIA_PATH
    else:
        common_html_header(outfile, "Unusual Development in Fiddler Crabs")
        media_path = ""
    outfile.write("    <header id=\"" + init_data().unsuual_dev_url + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Unusual Development</h1>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <p>\n")
    outfile.write("      The following is a collection of references to unusual development of secondary "
                  "sexual characters in fiddler crabs, divided by basic type. It is not meant bo be a thorough "
                  "overview of developmental studies. This also does not include anomalies in claw size due to "
                  "regeneration status.\n")
    outfile.write("    </p>\n")
    outfile.write("\n")
    not_first = False
    for line in abdevdata:
        if line.strip() != "":
            data = line.strip().split("\t")
            if data[0].startswith(":"):
                if not_first:
                    outfile.write("      </table>\n")
                    outfile.write("    </section>\n")
                else:
                    not_first = True
                outfile.write("    <section class=\"spsection\">\n")
                outfile.write("      <h2 class=\"bookmark2\">" + data[1] + "</h2>\n")
                outstr = replace_media_path(data[2], media_path)
                outfile.write("      <p>\n")
                outfile.write(replace_species_in_string(outstr, do_print=do_print) + "\n")
                outfile.write("      </p>\n")
                outfile.write("      <table>\n")
            else:
                species = find_species_by_name(data[1])
                outfile.write("        <tr>\n")
                if data[0].startswith("http"):
                    url, caption = data[0].split("|")
                    outfile.write("          <td><a href=\"" + url + "\">" + caption + "</a></td>\n")
                else:
                    ref = refdict[data[0]]
                    outfile.write("          <td>" + format_reference_cite(ref, do_print, AUTHOR_PAREN) + "</td>\n")
                outfile.write("          <td>" + create_species_link(species.genus, species.species, do_print) +
                              "</td>\n")
                if data[2] != ".":
                    outfile.write("          <td>" + data[2] + "</td>\n")
                outfile.write("        </tr>\n")

    outfile.write("      </table>\n")
    outfile.write("    </section>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile)


def write_life_cycle_pages(outfile: TextIO, do_print: bool) -> None:
    """
    create the life cycle page
    """
    if do_print:
        start_page_division(outfile, "base_page")
        media_path = MEDIA_PATH
    else:
        common_html_header(outfile, "Fiddler Crab Life Cycle")
        media_path = ""

    outfile.write("    <header id=\"" + init_data().lifecycle_url + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Life Cycle</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"#{}\">{}</a></li>\n".format(init_data().unsuual_dev_url,
                                                                           "Unusual Development"))
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")

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
        common_html_footer(outfile)


def create_html_phylogenies():
    gen_tree = phy2html.create_html_tree("data/fiddler_genera_tree.nwk", "", prefix="genera_")
    sp_tree = phy2html.create_html_tree("data/fiddler_species_tree.nwk", "", prefix="species_")
    return gen_tree, sp_tree


def write_phylogeny_pages(outfile: TextIO, genera_tree: list, species_tree: list, do_print: bool,
                          refdict: dict) -> None:
    """
    create the phylogeny page
    """

    def split_html_tree(intree: list) -> Tuple[list, list]:
        """
        take a phy2html output file and split it into style and body sections
        """
        instyle = False
        inbody = False
        style_list = []
        body_list = []
        for inline in intree:
            if "<style>" in inline:
                instyle = True
            elif "</style>" in inline:
                instyle = False
            elif "<body>" in inline:
                inbody = True
            elif "</body>" in inline:
                inbody = False
            elif instyle:
                style_list.append(inline)
            elif inbody:
                body_list.append(inline)
        return style_list, body_list

    def add_link_to_genus(inline: str) -> str:
        if "id=\"genera_taxon" in inline:
            i = inline.find(">")
            start = inline[:i+1]
            tname = inline[i+1:]
            j = tname.find("<")
            end = tname[j:]
            tname = tname[:j]
            tname = create_taxon_link("genus", tname, do_print=do_print, include_rank=False)
            return start + tname + end
        else:
            return inline

    # --- main function code ---
    gen_style, gen_body = split_html_tree(genera_tree)
    sp_style, sp_body = split_html_tree(species_tree)

    if do_print:
        start_page_division(outfile, "base_page")
    else:
        common_header_part1(outfile, "Fiddler Crab Phylogeny")
    outfile.write("    <style>\n")
    for line in gen_style:
        outfile.write(line)
    outfile.write("\n")
    for line in sp_style:
        outfile.write(line)
    outfile.write("\n")
    outfile.write("    .phylogeny_grid { padding: 30px;  }\n")  # add a little extra padding
    outfile.write("    </style>\n")

    if not do_print:
        common_header_part2(outfile)

    outfile.write("    <header id=\"" + init_data().tree_url + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Phylogeny</h1>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <p>\n")
    outfile.write("     The phylogeny of fiddler crabs is still largely unresolved. Two trees are shown below: one "
                  "of just the genera and one including all species. The tree of genera is fairly solid, "
                  "but the species tree is a rough estimate with many polytomies. Both are predominantly based on the "
                  "work of " + format_reference_cite(refdict["Shih2016.2"], do_print, AUTHOR_PAREN) + ".\n")
    outfile.write("    </p>\n")
    outfile.write("\n")
    outfile.write("    <section class=\"spsection\">\n")
    outfile.write("      <h2 class=\"bookmark2\">Genera Phylogeny</h2>\n")
    for line in gen_body:
        outfile.write(add_link_to_genus(line))
    outfile.write("    </section>\n")
    outfile.write("    <section class=\"spsection\">\n")
    outfile.write("      <h2 class=\"bookmark2\">Species Phylogeny</h2>\n")
    for line in sp_body:
        outfile.write(replace_species_in_string(line, True, do_print))
    outfile.write("    </section>\n")
    outfile.write("\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile)


def morphology_link(parent: str, character: str) -> str:
    if parent == ".":
        return character.replace(" ", "_")
    else:
        return parent.replace(" ", "_") + "_" + character.replace(" ", "_")


def find_morphology_parent(p: str, mlist: list) -> str:
    x = ""
    for m in mlist:
        if p == m.character:
            x = morphology_link(m.parent, m.character)
    return x


def write_morphology_page(outfile: TextIO, do_print: bool, morph: TMB_Classes.MorphologyClass,
                          morphlist: list) -> None:
    """
    create individual pages for morphology descriptions
    """
    if morph.parent == ".":
        p = ""
    else:
        p = " (" + morph.parent + ")"
    if do_print:
        start_page_division(outfile, "morph_page")
        media_path = MEDIA_PATH + "morphology/"
    else:
        common_html_header(outfile, "Fiddler Crab Morphology: " + morph.character + p, indexpath="../")
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
            outfile.write("          <li><a href=\"" + rel_link_prefix(do_print) +
                          find_morphology_parent(morph.parent, morphlist) + ".html\">" + morph.parent + "</a></li>\n")
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "../") + init_data().morph_url +
                      "\">General Morphology</a></li>\n")
        if do_print:
            index_page = "#morphology_index.html"
        else:
            index_page = "."
        outfile.write("          <li><a href=\"" + index_page + "\">" + fetch_fa_glyph("index") +
                      "Morphology Index</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <div class=\"morphdesc\">\n")
    outfile.write("     <p>\n")
    outfile.write("       " + replace_species_in_string(morph.description) + "\n")
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
                outfile.write("       <li><a href=\"" + rel_link_prefix(do_print) +
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
        outfile.write("      <img src=\"" + media_path + plist[i] + "\" alt=\"" + clist[i] + "\" "
                      "title=\"" + clist[i] + "\" />\n")
        outfile.write("      <figcaption>" + clist[i] + "</figcaption>\n")
        outfile.write("    </figure>\n")
        if not do_print:
            # copy images to web output directory
            tmp_name = "morphology/" + plist[i]
            try:
                shutil.copy2(MEDIA_PATH + tmp_name, WEBOUT_PATH + "morphology/")
            except FileNotFoundError:
                report_error("Missing file: " + tmp_name)
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, indexpath="../")


def write_morphology_index(outfile: TextIO, do_print: bool, morphlist: list) -> None:
    """
    create index for morphology pages
    """
    if do_print:
        start_page_division(outfile, "index_page")
    else:
        common_html_header(outfile, "Morphology Index", indexpath="../")
    outfile.write("    <header id=\"morphology_index.html\">\n")
    outfile.write("      <h1 class=\"bookmark2\">Morphology Index</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"" + rel_link_prefix(do_print, "../") + init_data().morph_url +
                      "\">General Morphology</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("     <ul class=\"morphlist\">\n")
    # uniquelist = {}
    uniquelist = collections.Counter(m.character for m in morphlist)
    # for m in morphlist:
    #     uniquelist.update(m.character)
    #     # if m.character in uniquelist:
    #     #     uniquelist[m.character] += 1
    #     # else:
    #     #     uniquelist[m.character] = 1

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
        outfile.write("      <li><a href=\"" + rel_link_prefix(do_print) + morphology_link(m.parent, m.character) +
                      ".html\">" + m.character + p + "</a></li>\n")
    outfile.write("     </ul>\n")
    if do_print:
        end_page_division(outfile)
    else:
        common_html_footer(outfile, indexpath="../")


def write_main_morphology_pages(outfile: TextIO, do_print: bool, morphology: list) -> None:
    """
    create page for general morphology descriptions
    """
    if do_print:
        start_page_division(outfile, "base_page")
        media_path = MEDIA_PATH
    else:
        common_html_header(outfile, "Fiddler Crab Morphology")
        media_path = ""
    outfile.write("    <header id=\"" + init_data().morph_url + "\">\n")
    outfile.write("      <h1 class=\"bookmark1\">Morphology</h1>\n")
    if not do_print:
        outfile.write("      <nav>\n")
        outfile.write("        <ul>\n")
        if do_print:
            index_page = "#morphology_index.html"
        else:
            index_page = "morphology/index.html"
        outfile.write("          <li><a href=\"" + index_page + "\">" + fetch_fa_glyph("index") + "Index</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </nav>\n")
    outfile.write("    </header>\n")
    outfile.write("\n")
    outfile.write("    <div class=\"morphdesc\">\n")
    outfile.write("     <p>\n")
    outfile.write("      Fiddler crabs are decapod &ldquo;true crabs&rdquo; with much of the standard morphology "
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
        write_morphology_index(outfile, do_print, morphology)
        for m in morphology:
            write_morphology_page(outfile, do_print, m, morphology)
    else:
        common_html_footer(outfile)
        for m in morphology:
            with open(WEBOUT_PATH + "morphology/" + morphology_link(m.parent, m.character) + ".html", "w",
                      encoding="utf-8") as suboutfile:
                write_morphology_page(suboutfile, do_print, m, morphology)
        with open(WEBOUT_PATH + "morphology/index.html", "w", encoding="utf-8") as suboutfile:
            write_morphology_index(suboutfile, do_print, morphology)


def write_citation_page(refdict: dict) -> None:
    """
    create page with site citation info
    """
    with open(WEBOUT_PATH + init_data().cite_url, "w", encoding="utf-8") as outfile:
        common_html_header(outfile, "Fiddler Crab Website Citation")
        outfile.write("    <header id=\"" + init_data().cite_url + "\">\n")
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
        outfile.write("      <li>" + fetch_fa_glyph("list pdf") +
                      "<a href=\"https://dx.plos.org/10.1371/journal.pone.0101704\">Read paper online at "
                      "PLoS ONE</a></li>\n")
        outfile.write("      <li>" + fetch_fa_glyph("list github") +
                      "<a href=\"https://github.com/msrosenberg/fiddlercrab.info\">Website data repository on "
                      "GitHub</a></li>\n")
        outfile.write("    </ul>\n")
        common_html_footer(outfile)


def write_introduction(outfile: TextIO, do_print: bool, species: list, higher_taxa: list) -> None:
    """
    create the site index
    """
    if do_print:
        start_page_division(outfile, "base_page")
        outfile.write("    <header id=\"introduction\">\n")
        outfile.write("      <h1 class=\"bookmark1\">Introduction</h1>\n")
        outfile.write("    </header>\n")
    else:
        common_html_header(outfile, "Fiddler Crabs")
    outfile.write("    <p>\n")
    scnt = 0
    for s in species:
        if s.status != "fossil":
            scnt += 1
    outfile.write("      Fiddler crabs are small, semi-terrestrial crabs are characterized by extreme cheliped "
                  "asymmetry in males. They are most closely related to the <em class=\"species\">Ocypode</em> "
                  "(ghost crabs). <a href=\"" + rel_link_prefix(do_print) + init_data().species_url +
                  "\">There are currently {} recognized extant species</a>.\n".format(scnt))
    outfile.write("    </p>\n")
    if do_print:
        media_path = MEDIA_PATH
    else:
        media_path = ""
    outfile.write("    <div class=\"indeximages\">\n")
    outfile.write("      <img class=\"thumbnail\" src=\"" + media_path +
                  "photos/U_mjoebergi04tn.jpg\" alt=\"Austruca mjoebergi photo\" />\n")
    outfile.write("      <img class=\"thumbnail\" src=\"" + media_path +
                  "photos/U_minax07tn.jpg\" alt=\"Minuca minax photo\" />\n")
    outfile.write("      <img class=\"thumbnail\" src=\"" + media_path +
                  "photos/U_crassipes19tn.jpg\" alt=\"Paraleptuca crassipes photo\" />\n")
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
    # outfile.write("      <tr><td class=\"classcol1\">Subfamily</td><td>Ocypodinae</td>\n")
    # outfile.write("      <tr><td class=\"classcol1\">Genus</td><td><em class=\"species\">Uca</em></td>\n")
    genera = []
    for t in higher_taxa:
        if t.taxon_rank == "genus":
            genera.append(t.name)
    genera.sort()
    outfile.write("      <tr><td class=\"classcol1\">Genera</td><td><em class=\"species\">" +
                  ", ".join(genera) + "</em></td>\n")

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
        outfile.write("      <li>" + fetch_fa_glyph("list systematics") + "<a href=\"" + init_data().syst_url +
                      "\">Systematics</a></li>\n")
        outfile.write("      <li>" + fetch_fa_glyph("list phylogeny") + "<a href=\"" + init_data().tree_url +
                      "\">Phylogeny</a></li>\n")
        outfile.write("      <li>" + fetch_fa_glyph("list species") + "<a href=\"" + init_data().species_url +
                      "\">Species</a>\n")
        outfile.write("        <ul>\n")
        outfile.write("           <li><a href=\"names\">Name Index</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </li>\n")
        outfile.write("      <li>" + fetch_fa_glyph("list common") + "<a href=\"" + init_data().common_url +
                      "\">Common Names</a></li>\n")
        outfile.write("      <li>" + fetch_fa_glyph("list ranges") + "<a href=\"" + init_data().map_url +
                      "\">Geographic Ranges</a>\n")
        outfile.write("        <ul>\n")
        outfile.write("           <li><a href=\"locations\">Location Index</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </li>\n")
        outfile.write("      <li>" + fetch_fa_glyph("list lifecycle") + "<a href=\"" + init_data().lifecycle_url +
                      "\">Life Cycle</a>\n")
        outfile.write("        <ul>\n")
        # outfile.write("           <li>" + fetch_fa_glyph("list unusual dev") + "<a href=\"" +
        #               init_data().unsuual_dev_url + "\">Unusual Development</a></li>\n")
        outfile.write("           <li><a href=\"" + init_data().unsuual_dev_url + "\">Unusual Development</a></li>\n")
        outfile.write("        </ul></li>\n")

        outfile.write("      <li>" + fetch_fa_glyph("list morphology") + "<a href=\"" + init_data().morph_url +
                      "\">Morphology</a>\n")
        outfile.write("        <ul>\n")
        outfile.write("           <li><a href=\"" + init_data().handedness_url + "\">Male Handedness</a></li>\n")
        outfile.write("        </ul></li>\n")
        outfile.write("      <li>" + fetch_fa_glyph("list references") + "<a href=\"" + init_data().ref_url +
                      "\">Comprehensive Reference List</a></li>\n")
        outfile.write("    </ul>\n")
        outfile.write("    <h2>Multimedia</h2>\n")
        outfile.write("    <ul class=\"fa-ul\">\n")
        outfile.write("      <li>" + fetch_fa_glyph("list photo") + "<a href=\"" + init_data().photo_url +
                      "\">Photos</a></li>\n")
        outfile.write("      <li>" + fetch_fa_glyph("list video") + "<a href=\"" + init_data().video_url +
                      "\">Videos</a></li>\n")
        outfile.write("      <li>" + fetch_fa_glyph("list art") + "Art\n")
        outfile.write("        <ul>\n")
        outfile.write("          <li><a href=\"" + init_data().art_sci_url + "\">Scientific Art</a></li>\n")
        outfile.write("          <li><a href=\"" + init_data().art_stamp_url + "\">Postage Stamps</a></li>\n")
        outfile.write("          <li><a href=\"" + init_data().art_craft_url + "\">Crafts</a></li>\n")
        outfile.write("        </ul>\n")
        outfile.write("      </li>\n")
        outfile.write("    </ul>\n")
        outfile.write("    <h2>Miscellania</h2>\n")
        outfile.write("    <ul class=\"fa-ul\">\n")
        outfile.write("      <li>" + fetch_fa_glyph("list site cite") + "<a href=\"" + init_data().cite_url +
                      "\">Citation info for this website</a></li>\n")
        outfile.write("      <li>" + fetch_fa_glyph("list github") +
                      "<a href=\"https://github.com/msrosenberg/fiddlercrab.info\">Website data on GitHub</a></li>\n")
        outfile.write("    </ul>\n")
        common_html_footer(outfile)


def create_path_and_index(subdir: str) -> None:
    """
    function to create an output path if it doesn't exist and auto-populate it with a blank index file
    """
    if not os.path.exists(WEBOUT_PATH + subdir):
        os.makedirs(WEBOUT_PATH + subdir)
    create_blank_index(WEBOUT_PATH + subdir + "index.html")


def create_web_output_paths() -> None:
    """
    create web output directories if they do not already exist
    """
    create_path_and_index("")
    create_path_and_index("photos/")
    create_path_and_index("video/")
    create_path_and_index("references/")
    create_path_and_index("names/")
    create_path_and_index("art/")
    create_path_and_index("morphology/")
    create_path_and_index("maps/")
    create_path_and_index("images/")
    create_path_and_index("images/flag-icon-css/")
    create_path_and_index("images/flag-icon-css/css/")
    create_path_and_index("images/flag-icon-css/flags/")
    create_path_and_index("images/flag-icon-css/flags/4x3/")
    create_path_and_index("locations/")
    create_path_and_index("locations/keys/")
    create_path_and_index("js/")
    create_path_and_index("sizes/")
    create_path_and_index("handedness/")


def create_temp_output_paths() -> None:
    """
    create temporary output directories if they do not already exist
    """
    if not os.path.exists(TMP_PATH):
        os.makedirs(TMP_PATH)
    if not os.path.exists(TMP_MAP_PATH):
        os.makedirs(TMP_MAP_PATH)


def copy_support_files() -> None:
    """
    copy a variety of resource and output files into the correct web output directories
    this includes icons, supporting images, and css files
    """
    # root folder files
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
            report_error("Missing file: resources/" + filename)
    # image folder files
    filelist = {"film.png",
                "stylifera75.png",
                "DOI_logo.svg",
                "size_hist.png",
                "size_ind.png",
                "size_mean.png",
                "size_range.png",
                "size_summary.png",
                "double_clawed.jpg"}
    for filename in filelist:
        try:
            shutil.copy2("resources/images/" + filename, WEBOUT_PATH + "images/")
        except FileNotFoundError:
            report_error("Missing file: resources/images/" + filename)
    filelist = {"specific_word_cloud.png",
                "binomial_word_cloud.png"}
    for filename in filelist:
        try:
            shutil.copy2(TMP_PATH + filename, WEBOUT_PATH + "images/")
        except FileNotFoundError:
            report_error("Missing file: " + TMP_PATH + filename)
    # font-awesome files
    filelist = {"fontawesome.min.js",
                "brands.min.js",
                "regular.min.js",
                "solid.min.js"}
    for filename in filelist:
        try:
            shutil.copy2("resources/font-awesome/js/" + filename, WEBOUT_PATH + "js/")
        except FileNotFoundError:
            report_error("Missing file: resources/font-awesome/js/" + TMP_PATH + filename)
    # flag-icon files
    filelist = {"flag-icons.min.css"}
    for filename in filelist:
        try:
            shutil.copy2("resources/flag-icon-css/css/" + filename, WEBOUT_PATH + "images/flag-icon-css/css/")
        except FileNotFoundError:
            report_error("Missing file: images/flag-icon-css/css/" + TMP_PATH + filename)
    filelist = {"de.svg",  # Germany
                "es.svg",  # Spain
                "ru.svg",  # Russia
                "fr.svg",  # France
                "pt.svg",  # Portugal
                "dk.svg",  # Denmark
                "nl.svg",  # Netherlands
                "jp.svg",  # Japan
                "cn.svg",  # China
                "us.svg",  # USA
                "th.svg",  # Thailand
                "va.svg",  # Vatican
                "it.svg",  # Italy
                "kr.svg",  # South Korea
                "pl.svg",  # Poland
                "se.svg",  # Sweden
                "mm.svg",  # Myanamar (Burma)
                "sa.svg",  # Saudi Arabia (best option for Arabic of those available)
                "id.svg",  # Indonesia
                "za.svg",  # South Africa (best option for Afrikaans)
                "my.svg",  # Malaysia (for Malay)
                "mg.svg",  # Madagascar (for Malagasy)
                "ir.svg",  # Iran (for Persian)
                "vn.svg"}  # Vietnam
    for filename in filelist:
        try:
            shutil.copy2("resources/flag-icon-css/flags/4x3/" + filename, WEBOUT_PATH +
                         "images/flag-icon-css/flags/4x3/")
        except FileNotFoundError:
            report_error("Missing file: images/flag-icon-css/flags/4x3/" + TMP_PATH + filename)


def copy_map_files(species: list, all_names: list, specific_names: list, point_locations: dict) -> None:
    """
    copy all created map files (kmz and svg) from temp directory to web output directory
    """
    def copy_file(filename: str) -> None:
        try:
            shutil.copy2(filename, WEBOUT_PATH + "maps/")
        except FileNotFoundError:
            report_error("Missing file: " + filename)

    # def scour_svg(filename: str) -> None:
    #     """
    #     run scour to reduce size of svg maps
    #
    #     theoretically scour could be imported and run from within the code, but it is really not designed
    #     to be run that way
    #     """
    #     subprocess.Popen("scour -i " + filename + " -o " + filename + "z").wait()

    # individual species maps
    for s in species:
        if s.status != "fossil":
            copy_file(TMP_MAP_PATH + rangemap_name("u_" + s.species) + ".kmz")
            copy_file(TMP_MAP_PATH + pointmap_name("u_" + s.species) + ".kmz")
            # scour_svg(TMP_MAP_PATH + rangemap_name("u_" + s.species) + ".svg")
            # scour_svg(TMP_MAP_PATH + pointmap_name("u_" + s.species) + ".svg")
            # copy_file(TMP_MAP_PATH + rangemap_name("u_" + s.species) + ".svgz")
            # copy_file(TMP_MAP_PATH + pointmap_name("u_" + s.species) + ".svgz")
            copy_file(TMP_MAP_PATH + rangemap_name("u_" + s.species) + ".png")
            copy_file(TMP_MAP_PATH + pointmap_name("u_" + s.species) + ".png")
    # combined map
    # copy_file(TMP_MAP_PATH + rangemap_name("fiddlers_all") + ".kmz")
    copy_file(TMP_MAP_PATH + pointmap_name("fiddlers_all") + ".kmz")
    copy_file(TMP_MAP_PATH + rangemap_name("fiddlers_all") + ".png")
    copy_file(TMP_MAP_PATH + pointmap_name("fiddlers_all") + ".png")

    # binomial maps
    for n in all_names:
        copy_file(TMP_MAP_PATH + pointmap_name("name_" + name_to_filename(n)) + ".kmz")
        # scour_svg(TMP_MAP_PATH + pointmap_name("name_" + name_to_filename(n)) + ".svg")
        # copy_file(TMP_MAP_PATH + pointmap_name("name_" + name_to_filename(n)) + ".svgz")
        copy_file(TMP_MAP_PATH + pointmap_name("name_" + name_to_filename(n)) + ".png")
    # specific name maps
    for n in specific_names:
        copy_file(TMP_MAP_PATH + pointmap_name("sn_" + n.name) + ".kmz")
        # scour_svg(TMP_MAP_PATH + pointmap_name("sn_" + n.name) + ".svg")
        # copy_file(TMP_MAP_PATH + pointmap_name("sn_" + n.name) + ".svgz")
        copy_file(TMP_MAP_PATH + pointmap_name("sn_" + n.name) + ".png")
    # point location maps
    for p in point_locations:
        if not point_locations[p].unknown:
            copy_file(TMP_MAP_PATH + pointmap_name("location_" + place_to_filename(p)) + ".kmz")


def print_cover(outfile: TextIO) -> None:
    """
    create cover for monographic print output
    """
    outfile.write("    <div id=\"cover_page\">\n")
    for i in range(1, 29):
        outfile.write("      <img id=\"cover_img" + str(i) + "\" class=\"cover_img\" "
                      "src=\"media/cover images/cover" + str(i) + ".jpg\" />\n")
    outfile.write("      <p class=\"cover_title\">" + init_data().site_title + "</p>\n")
    outfile.write("      <p class=\"cover_author\">" + init_data().site_author + "</p>\n")
    outfile.write("    </div>\n")
    outfile.write("\n")


def print_title_page(outfile: TextIO) -> None:
    """
    create title page for monographic print output
    """
    outfile.write("    <div id=\"title_page\">\n")
    outfile.write("     <p class=\"book_title\">" + init_data().site_title + "</p>\n")
    outfile.write("     <p class=\"book_subtitle\">" + init_data().site_subtitle + "</p>\n")
    outfile.write("     <p class=\"book_author\">" + init_data().site_author + "</p>\n")
    outfile.write("     <figure class=\"title_image\"><img src=\"resources/images/stylifera75.png\" /></figure>\n")
    outfile.write("     <p class=\"book_address\"><a href=\"" + init_data().site_url() + "\">" +
                  init_data().site_address + "</a></p>\n")
    outfile.write("    </div>\n")
    outfile.write("\n")


def print_copyright_page(outfile: TextIO, refdict: dict) -> None:
    """
    create copyright page for monographic print output
    """
    outfile.write("    <div id=\"copyright_page\">\n")
    outfile.write("     <p>Copyright &copy; 2003&ndash;" + str(init_data().current_year) +
                  " by " + init_data().site_author + ". All Rights Reserved</p>\n")
    outfile.write("     <p>Release: " + init_data().version + "</p>\n")
    outfile.write("     <p><a href=\"" + init_data().site_url() + "\">" + init_data().site_address + "</a></p>\n")
    outfile.write("     <p>\n")
    outfile.write("       The data and code used to produce this document can be found on GitHub at")
    outfile.write("     </p>\n")
    outfile.write("     <p>\n")
    outfile.write("       <a href=\"https://github.com/msrosenberg/fiddlercrab.info\">"
                  "https://github.com/msrosenberg/fiddlercrab.info</a>\n")
    outfile.write("     </p>\n")
    outfile.write("     <p>and</p>\n")
    outfile.write("     <p>\n")
    outfile.write("       <a href=\"https://github.com/msrosenberg/TaxonomyMonographBuilder\">"
                  "https://github.com/msrosenberg/TaxonomyMonographBuilder</a>.\n")
    outfile.write("     </p>\n")
    outfile.write("     <p class=\"copy_cite\">\n")
    outfile.write("       Please cite this document as:\n")
    outfile.write("     </p>\n")
    outfile.write("     <p>\n")
    outfile.write("       Rosenberg, M.S. (" + str(init_data().current_year) + ") www.fiddlercrab.info, v." +
                  init_data().version + ".\n")
    outfile.write("     </p>\n")

    outfile.write("     <p>\n")
    outfile.write("       Certain key elements of this work are described in:\n")
    key_ref = "Rosenberg2014"  # citation describing the database
    ref = refdict[key_ref]
    outfile.write("      <div class=\"reference_list\">\n")
    outfile.write("        <ul>\n")
    outfile.write("          <li><a href=\"" + rel_link_prefix(True, "references/") + key_ref + ".html\">" +
                  ref.formatted_html + "</a></li>\n")
    outfile.write("        </ul>\n")
    outfile.write("      </div>\n")
    outfile.write("    </div>\n")
    outfile.write("\n")


def print_table_of_contents(outfile: TextIO, species_list: list) -> None:
    """
    create Table of Contents for monographic print output
    """
    outfile.write("    <div id=\"table_of_contents\">\n")
    outfile.write("     <h1 class=\"bookmark1\">Table of Contents</h1>\n")
    outfile.write("     <ul>\n")
    outfile.write("       <li><a href=\"#introduction\">Introduction</a></li>\n")
    outfile.write("       <li><a href=\"#" + init_data().common_url + "\">Common Names</a></li>\n")
    outfile.write("       <li><a href=\"#" + init_data().syst_url + "\">Systematics Overview</a>\n")
    outfile.write("         <ul>\n")
    outfile.write("           <li><a href=\"#genus\">Genus</a></li>\n")
    outfile.write("           <li><a href=\"#subgenera\">Subgenera</a></li>\n")
    outfile.write("           <li><a href=\"#species\">Species</a></li>\n")
    outfile.write("         </ul>\n")
    outfile.write("       </li>\n")
    outfile.write("       <li><a href=\"#" + init_data().tree_url + "\">Phylogeny</a></li>\n")
    outfile.write("       <li><a href=\"#" + init_data().lifecycle_url + "\">Life Cycle</a></li>\n")
    outfile.write("         <ul>\n")
    outfile.write("           <li><a href=\"#" + init_data().unsuual_dev_url + "\">Unusual Development</a></li>\n")
    outfile.write("         </ul>\n")

    outfile.write("       <li><a href=\"#" + init_data().species_url + "\">Species</a>\n")
    outfile.write("         <ul>\n")
    for species in species_list:
        outfile.write("           <li>" + create_species_link(species.genus, species.species, True) + "</li>\n")
    outfile.write("         </ul>\n")
    outfile.write("       </li>\n")

    outfile.write("       <li><a href=\"#name_index\">Name Index</a>\n")
    outfile.write("         <ul>\n")
    outfile.write("           <li><a href=\"#binomials\">Binomials and Other Compound Names</a>\n")
    outfile.write("           <li><a href=\"#specificnames\">Specific Names</a>\n")
    outfile.write("           <li><a href=\"#" + init_data().name_sum_url + "\">Summary of Names</a>\n")
    outfile.write("         </ul>\n")
    outfile.write("       </li>\n")
    outfile.write("       <li><a href=\"#" + init_data().map_url + "\">Geography</a>\n")
    outfile.write("         <ul>\n")
    outfile.write("           <li><a href=\"#location_index\">Location Index</a></li>\n")
    outfile.write("         </ul>\n")
    outfile.write("       </li>\n")
    outfile.write("       <li><a href=\"#" + init_data().morph_url + "\">Morphology</a></li>\n")
    outfile.write("       <li><a href=\"#" + init_data().photo_url + "\">Photo Index</a></li>\n")
    outfile.write("       <li><a href=\"#" + init_data().video_url + "\">Video Index</a></li>\n")
    outfile.write("       <li>Art\n")
    outfile.write("         <ul>\n")
    outfile.write("           <li><a href=\"#" + init_data().art_sci_url + "\">Scientific Drawings</a></li>\n")
    outfile.write("           <li><a href=\"#" + init_data().art_stamp_url + "\">Postage Stamps</a></li>\n")
    outfile.write("           <li><a href=\"#" + init_data().art_craft_url + "\">Arts &amp; Crafts</a></li>\n")
    outfile.write("         </ul>\n")
    outfile.write("       </li>\n")
    outfile.write("       <li>References\n")
    outfile.write("         <ul>\n")
    outfile.write("           <li><a href=\"#" + init_data().ref_sum_url + "\">Summary of References</a></li>\n")
    outfile.write("           <li><a href=\"#" + init_data().ref_url + "\">Full Reference List</a></li>\n")
    outfile.write("         </ul>\n")
    outfile.write("       </li>\n")
    outfile.write("     </ul>\n")
    outfile.write("    </div>\n")
    outfile.write("\n")


def write_print_only_pages(outfile: TextIO, species: list, refdict: dict) -> None:
    """
    create starting pages that are unique to print output
    """
    print_cover(outfile)
    print_title_page(outfile)
    print_copyright_page(outfile, refdict)
    print_table_of_contents(outfile, species)


def start_print(outfile: TextIO) -> None:
    """
    start html file for print monographic output
    """
    outfile.write("<!DOCTYPE HTML>\n")
    outfile.write("<html lang=\"en\">\n")
    outfile.write("  <head>\n")
    outfile.write("    <meta charset=\"utf-8\" />\n")
    outfile.write("    <title>Fiddler Crabs</title>\n")
    outfile.write("    <link rel=\"stylesheet\" href=\"resources/uca_style.css\" />\n")
    outfile.write("    <link rel=\"stylesheet\" href=\"resources/print.css\" />\n")
    outfile.write("    <link rel=\"stylesheet\" href=\"resources/font-awesome/css/fontawesome.min.css\" />\n")
    outfile.write("    <link rel=\"stylesheet\" href=\"resources/font-awesome/css/solid.min.css\" />\n")
    outfile.write("    <link rel=\"stylesheet\" href=\"resources/font-awesome/css/brands.min.css\" />\n")
    outfile.write("    <link rel=\"stylesheet\" href=\"resources/font-awesome/css/regular.min.css\" />\n")
    outfile.write("    <link rel=\"stylesheet\" href=\"resources/flag-icon-css/css/flag-icons.min.css\" />\n")
    outfile.write("  </head>\n")
    outfile.write("\n")
    outfile.write("  <body>\n")


def end_print(outfile: TextIO) -> None:
    """
    end html file for print monographic output
    """
    outfile.write("  </body>\n")
    outfile.write("</html>\n")


# def build_site(init_data):
def build_site() -> None:
    start_time = datetime.datetime.now()
    print("Start Time:", start_time)
    create_temp_output_paths()
    with open(init_data().error_log, "w", encoding="utf-8") as TMB_Error.LOGFILE:
        # read data and do computation
        print("...Reading References...")
        (references, refdict, citelist,
         yeardict, citecount) = TMB_Import.read_reference_data(init_data().reference_ciation_file,
                                                               init_data().reference_file,
                                                               init_data().citation_info_file)
        clean_references(references)
        yeardat, yeardat1900 = summarize_year(yeardict)
        languages, languages_by_year = summarize_languages(references)
        print("...Reading Species...")
        species = TMB_Import.read_species_data(init_data().species_data_file)
        init_species_crossref(species)
        connect_type_references(species, refdict)

        print("...Connecting References...")
        print("......Computing Species from Citation Linking......")
        compute_species_from_citation_linking(citelist)
        # print("......Computing Applied Name Contexts......")
        compute_applied_name_contexts(citelist)
        print("......Connecting References to Species......")
        species_refs = connect_refs_to_species(species, citelist)

        print("...Reading Species Names...")
        specific_names = TMB_Import.read_specific_names_data(init_data().specific_names_file)
        check_specific_names(citelist, specific_names)
        (all_names, binomial_name_cnts, specific_name_cnts, genus_cnts, total_binomial_year_cnts,
         name_table, specific_point_locations, binomial_point_locations, binomial_usage_cnts,
         specific_usage_cnts) = calculate_name_index_data(refdict, citelist, specific_names)
        common_name_data = TMB_Import.read_common_name_data(init_data().common_names_file)
        common_name_data = replace_species_references(common_name_data)

        taxon_ranks = TMB_Import.read_taxon_rank_data(init_data().taxon_ranks_file)
        higher_taxa, higher_dict = TMB_Import.read_higher_taxa_data(init_data().higher_taxa_file)
        if not CHECK_DATA:
            print("...Creating Wordclouds...")
            TMB_Create_Graphs.create_word_cloud_image(binomial_usage_cnts, specific_usage_cnts,
                                                      init_data().wc_font_path)

        print("...Reading Photos and Videos...")
        photos = TMB_Import.read_photo_data(init_data().photo_file)
        videos = TMB_Import.read_video_data(init_data().video_file)
        art = TMB_Import.read_art_data(init_data().art_file)
        morphology = TMB_Import.read_morphology_data(init_data().morphology_file)
        unusual_development_data = TMB_Import.read_unusual_development_data(init_data().unusual_development_file)

        print("...Reading Ranges...")
        species_range_blocks = TMB_Import.read_species_blocks(init_data().species_range_blocks)

        print("...Reading Locations...")
        # a dict of locations, keys = full location names
        point_locations = TMB_Import.read_location_data(init_data().location_file)
        # a dict of locations, keys = trimmed location names and aliases
        location_dict = create_location_hierarchy(point_locations)
        # location_species is a dict of sets of species objects, key = location full names
        # location_sp_names is a dict of sets of specific name objects, key = location full names
        # location_bi_names is a dict of sets of names (strings), keys = location full names
        (species_plot_locations, invalid_species_locations, binomial_plot_locations,
         specific_plot_locations, location_species, location_sp_names, location_bi_names, location_direct_refs,
         location_cited_refs, questionable_id_locations) = match_names_to_locations(species, specific_point_locations,
                                                                                    binomial_point_locations,
                                                                                    point_locations, citelist)
        location_range_species = compare_ranges_to_locations(species_range_blocks, point_locations)

        print("...Creating Taxonomic Keys...")
        (tk_trait_data, tk_generic_notes,
         tk_taxa_data) = TMB_TaxKeyGen.read_data_files(init_data().tax_key_trait_file,
                                                       init_data().tax_key_trait_var_file,
                                                       init_data().tax_key_generic_file, init_data().tax_key_taxa_file)
        TMB_TaxKeyGen.link_taxonomic_key_data(tk_trait_data, tk_generic_notes, tk_taxa_data)
        # clean_key_taxa(tk_taxa_data, species)

        location_keys = create_all_taxonomic_keys(point_locations, location_species, location_range_species,
                                                  tk_trait_data, tk_taxa_data)

        genera_tree, species_tree = create_html_phylogenies()

        measurement_data = TMB_Import.read_measurement_data(init_data().measurement_file)
        measurement_data = TMB_Measurements.sort_measurement_data(measurement_data)

        handedness_data = TMB_Import.read_handedness_data(init_data().handedness_file)

        if INCLUDE_INAT and (not CHECK_DATA) and DRAW_MAPS:
            species_inat = TMB_Import.fetch_inat_data(species)
        else:
            species_inat = None

        if CHECK_DATA:
            # run functions that cross-check data but skip the output
            check_location_index(point_locations, location_species, location_sp_names, location_bi_names)
            check_citation_cross_references(citelist, refdict, name_table)

        elif CHECK_LOCATIONS:
            if DRAW_MAPS:
                print("...Creating Maps...")
                TMB_Create_Maps.create_all_maps(init_data(), point_locations)  # only draw location maps
            print("......Writing Locations......")
            with open(WEBOUT_PATH + "locations/index.html", "w", encoding="utf-8") as outfile:
                write_location_index(outfile, False, point_locations, location_dict, location_species,
                                     location_sp_names, location_bi_names, location_direct_refs,
                                     location_cited_refs, references, location_range_species, location_keys)
        else:
            if DRAW_MAPS:
                print("...Creating Maps...")
                map_start_time = datetime.datetime.now()
                print("......Map Start Time:", map_start_time)
                TMB_Create_Maps.create_all_maps(init_data(), point_locations, species, species_plot_locations,
                                                invalid_species_locations, all_names, binomial_plot_locations,
                                                specific_names, specific_plot_locations, species_inat,
                                                questionable_id_locations, species_range_blocks)
                map_end_time = datetime.datetime.now()
                print("......Map End Time:", map_end_time)
                print("...Total Map Creation Time:", map_end_time - map_start_time)

            # output website version
            if OUTPUT_WEB:
                create_web_output_paths()
                print("...Creating Web Version...")
                copy_support_files()

                if OUTPUT_REFS:
                    print("......Writing References......")
                    with open(WEBOUT_PATH + init_data().ref_url, "w", encoding="utf-8") as outfile:
                        write_reference_bibliography(outfile, False, references)
                    with open(WEBOUT_PATH + init_data().ref_sum_url, "w", encoding="utf-8") as outfile:
                        write_reference_summary(outfile, False, len(references), yeardat, yeardat1900, citecount,
                                                languages, languages_by_year)
                    write_reference_pages(None, False, references, refdict, citelist, name_table, point_locations)
                print("......Writing Names Info......")
                with open(WEBOUT_PATH + "names/index.html", "w", encoding="utf-8") as outfile:
                    write_all_name_pages(outfile, False, refdict, citelist, all_names, specific_names, name_table,
                                         species_refs, genus_cnts, binomial_name_cnts, total_binomial_year_cnts,
                                         binomial_point_locations, specific_point_locations, point_locations)

                print("......Writing Species......")
                write_species_info_pages(None, False, species, references, specific_names, all_names, photos, videos,
                                         art, species_refs, refdict, binomial_name_cnts, specific_name_cnts,
                                         higher_dict, measurement_data, handedness_data)
                if DRAW_MAPS:
                    print("......Copying Maps......")
                    copy_map_files(species, all_names, specific_names, point_locations)
                if OUTPUT_LOCS:
                    print("......Writing Locations......")
                    with open(WEBOUT_PATH + "locations/index.html", "w", encoding="utf-8") as outfile:
                        write_location_index(outfile, False, point_locations, location_dict, location_species,
                                             location_sp_names, location_bi_names, location_direct_refs,
                                             location_cited_refs, references, location_range_species, location_keys)
                    with open(WEBOUT_PATH + init_data().map_url, "w", encoding="utf-8") as outfile:
                        write_geography_page(outfile, False, species)
                print("......Writing Media Pages......")
                with open(WEBOUT_PATH + init_data().photo_url, "w", encoding="utf-8") as outfile:
                    write_photo_index(outfile, False, species, photos, refdict)
                write_all_art_pages(None, False, art, refdict)
                with open(WEBOUT_PATH + init_data().video_url, "w", encoding="utf-8") as outfile:
                    write_video_index(outfile, False, videos)
                print("......Writing Misc......")
                with open(WEBOUT_PATH + init_data().syst_url, "w", encoding="utf-8") as outfile:
                    write_systematics_overview(outfile, False, taxon_ranks, higher_taxa, species, refdict)
                with open(WEBOUT_PATH + init_data().common_url, "w", encoding="utf-8") as outfile:
                    write_common_names_pages(outfile, False, replace_references(common_name_data, refdict, False))
                with open(WEBOUT_PATH + init_data().lifecycle_url, "w", encoding="utf-8") as outfile:
                    write_life_cycle_pages(outfile, False)
                with open(WEBOUT_PATH + init_data().unsuual_dev_url, "w", encoding="utf-8") as outfile:
                    write_unusual_development_pages(outfile, unusual_development_data, refdict, False)

                with open(WEBOUT_PATH + init_data().tree_url, "w", encoding="utf-8") as outfile:
                    write_phylogeny_pages(outfile, genera_tree, species_tree, False, refdict)
                with open(WEBOUT_PATH + init_data().morph_url, "w", encoding="utf-8") as outfile:
                    write_main_morphology_pages(outfile, False, morphology)
                with open(WEBOUT_PATH + "index.html", "w", encoding="utf-8") as outfile:
                    write_introduction(outfile, False, species, higher_taxa)
                write_citation_page(refdict)

            # output print version
            if OUTPUT_PRINT:
                print("...Creating Print Version...")
                with open("print.html", "w", encoding="utf-8") as printfile:
                    start_print(printfile)
                    write_print_only_pages(printfile, species, refdict)
                    write_introduction(printfile, True, species, higher_taxa)
                    write_common_names_pages(printfile, True, replace_references(common_name_data, refdict, True))
                    write_systematics_overview(printfile, True, taxon_ranks, higher_taxa, species, refdict)
                    write_phylogeny_pages(printfile, genera_tree, species_tree, True, refdict)
                    write_life_cycle_pages(printfile, True)
                    write_unusual_development_pages(printfile, unusual_development_data, refdict, True)
                    print("......Writing Species Pages......")
                    write_species_info_pages(printfile, True, species, references, specific_names, all_names, photos,
                                             videos, art, species_refs, refdict, binomial_name_cnts, specific_name_cnts,
                                             higher_dict, measurement_data, handedness_data)
                    print("......Writing Name Pages......")
                    write_all_name_pages(printfile, True, refdict, citelist, all_names, specific_names, name_table,
                                         species_refs, genus_cnts, binomial_name_cnts, total_binomial_year_cnts,
                                         binomial_point_locations, specific_point_locations, point_locations)
                    if OUTPUT_LOCS:
                        print("......Writing Location Pages......")
                        write_geography_page(printfile, True, species)
                        write_location_index(printfile, True, point_locations, location_dict, location_species,
                                             location_sp_names, location_bi_names, location_direct_refs,
                                             location_cited_refs, references, location_range_species, None)
                    print("......Writing Media Pages......")
                    write_main_morphology_pages(printfile, True, morphology)
                    write_photo_index(printfile, True, species, photos, refdict)
                    write_video_index(printfile, True, videos)
                    write_all_art_pages(printfile, True, art, refdict)
                    if OUTPUT_REFS:
                        print("......Writing Reference Pages......")
                        write_reference_summary(printfile, True, len(references), yeardat, yeardat1900, citecount,
                                                languages, languages_by_year)
                        write_reference_bibliography(printfile, True, references)
                        write_reference_pages(printfile, True, references, refdict, citelist, name_table,
                                              point_locations)
                    end_print(printfile)
    end_time = datetime.datetime.now()
    print("End Time:", end_time)
    print("Total Run Time:", end_time - start_time)
    print("done")


def main():
    # will eventually need to put options here for choosing different paths, etc.
    TMB_Initialize.initialize()
    random.seed()
    # will need to read options from file
    build_site()


if __name__ == "__main__":
    main()
