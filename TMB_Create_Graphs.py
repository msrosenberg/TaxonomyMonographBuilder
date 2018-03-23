"""
Module containing the various graph and chart drawing algorithms (except for those related to maps)
"""

# external dependencies
import matplotlib.pyplot as mplpy
from wordcloud import WordCloud
from typing import Optional

__TMP_PATH__ = "temp/"


def create_pie_chart_file(filename: str, data: dict, graph_font: Optional[str] = None) -> None:
    datalist = list(data.keys())
    datalist.sort()
    sizes = []
    for d in datalist:
        sizes.append(data[d])
    # my approximation of the pygal color scheme
    color_list = ["salmon", "royalblue", "lightseagreen", "gold", "darkorange", "mediumorchid", "deepskyblue",
                  "lightgreen", "sandybrown", "palevioletred", "lightskyblue", "mediumaquamarine", "lemonchiffon"]
    # create a two-panel plot, one for pie, one for legend
    fig, (panel1, panel2) = mplpy.subplots(1, 2, figsize=[6, 3])
    # create pie chart in first panel
    pie = panel1.pie(sizes, colors=color_list, startangle=90, counterclock=False)
    panel1.axis("equal")
    # create legend in second panel
    panel2.axis("off")  # hide axes in second plot
    panel2.legend(pie[0], datalist, loc="center", frameon=False, ncol=2, prop={"family": graph_font})
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    mplpy.savefig(__TMP_PATH__ + filename, format="png", dpi=600)
    mplpy.close("all")


def create_bar_chart_file(filename: str, data: list, minx: int, maxx: int, y: int,
                          graph_font: Optional[str] = None) -> None:
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
    mplpy.yticks(fontname=graph_font)
    mplpy.xticks([i for i in range(minx, maxx + 1, tick_step)], fontname=graph_font)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    mplpy.savefig(__TMP_PATH__ + filename, format="png", dpi=600)
    mplpy.close("all")


def create_stacked_bar_chart_file(filename: str, data: list, minx: int, maxx: int, cols: list,
                                  graph_font: Optional[str] = None) -> None:
    # currently assumes only two stacked bars
    x_list = [x for x in range(minx, maxx+1)]
    fig, faxes = mplpy.subplots(figsize=[6.5, 2])
    col_names = [c[0] for c in cols]
    y_list1 = [d[cols[0][1]] for d in data]
    y_list2 = [d[cols[1][1]] for d in data]
    faxes.bar(x_list, y_list1, color="blue", edgecolor="darkblue")
    faxes.bar(x_list, y_list2, bottom=y_list1, color="red", edgecolor="darkred")
    faxes.spines["right"].set_visible(False)
    faxes.spines["top"].set_visible(False)
    faxes.legend(col_names, loc="upper left", frameon=False, prop={"family": graph_font})
    mplpy.xticks(fontname=graph_font)
    mplpy.yticks(fontname=graph_font)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    mplpy.savefig(__TMP_PATH__ + filename, format="png", dpi=600)
    mplpy.close("all")


def create_qual_bar_chart_file(filename: str, label_list: list, data_dict: dict, max_value: int,
                               graph_font: Optional[str] = None) -> None:
    x_list = [x for x in range(len(label_list))]
    y_list = [data_dict[x] for x in label_list]
    fig, faxes = mplpy.subplots(figsize=[6.5, 2.5])
    faxes.bar(x_list, y_list, color="blue", edgecolor="darkblue")
    mplpy.yticks(fontname=graph_font)
    mplpy.xticks(rotation="vertical", style="italic", fontname=graph_font)
    faxes.set_xticks(x_list)
    faxes.set_xticklabels(label_list)
    faxes.spines["right"].set_visible(False)
    faxes.spines["top"].set_visible(False)
    mplpy.ylim(0, max_value)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    mplpy.savefig(__TMP_PATH__ + filename, format="png", dpi=600)
    mplpy.close("all")


def create_line_chart_file(filename: str, data: list, minx: int, maxx: int, y: int,
                           graph_font: Optional[str] = None) -> None:
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
    mplpy.yticks(fontname=graph_font)
    mplpy.xticks([i for i in range(minx, maxx + 1, tick_step)], fontname=graph_font)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    mplpy.savefig(__TMP_PATH__ + filename, format="png", dpi=600)
    mplpy.close("all")


def create_chronology_chart_file(filename: str, miny: int, maxy: int, maxcnt: int, yearly_data: dict,
                                 graph_font: Optional[str] = None) -> None:
    y_list = []
    for y in range(miny, maxy + 1):
        y_list.append(float(yearly_data[y]))

    x = [y for y in range(miny, maxy+1)]
    fig, faxes = mplpy.subplots(figsize=[6.5, 1.5])
    mplpy.ylim(-maxcnt, maxcnt)
    mplpy.xlim(miny, maxy)
    faxes.stackplot(x, y_list, baseline="sym", colors=["black"])
    for spine in faxes.spines:
        faxes.spines[spine].set_visible(False)
    cur_axes = mplpy.gca()
    cur_axes.axes.get_yaxis().set_visible(False)
    mplpy.xticks([i for i in range(miny, maxy+1, 20)], fontname=graph_font)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    mplpy.savefig(__TMP_PATH__ + filename, format="png", dpi=600)
    mplpy.close("all")


def create_word_cloud_image(binomial_cnts: dict, specific_cnts: dict, font_path: Optional[str] = None) -> None:
    # fiddler_mask = np.array(Image.open("private/silhouette.png"))
    # generate wordcloud image from binomials
    wordcloud = WordCloud(width=2000, height=1500, background_color="white", max_words=1000, normalize_plurals=False,
                          collocations=False, font_path=font_path).generate_from_frequencies(binomial_cnts)
    wordcloud.to_file(__TMP_PATH__ + "binomial_word_cloud.png")

    # generate wordcloud image from specific names
    wordcloud = WordCloud(width=2000, height=1500, background_color="white", max_words=1000, normalize_plurals=False,
                          collocations=False, font_path=font_path).generate_from_frequencies(specific_cnts)
    wordcloud.to_file(__TMP_PATH__ + "specific_word_cloud.png")


if __name__ == "__main__":
    pass
    # the following creates a quick chart of each type to check formatting changes
    test_data = {
        "English": 100,
        "German": 50,
        "Chinese": 20,
        "Dutch": 10,
        "French": 50,
        "Italian": 50,
        "Japanese": 50,
        "Latin": 10,
        "Polish": 3,
        "Portuguese": 3,
        "Russian": 3,
        "Spanish": 3,
        "Thai": 3,
        "Danish": 3,
        "Korean": 3,
        "Vietnamese": 3
    }
    create_pie_chart_file("testpie.png", test_data)
    create_word_cloud_image(test_data, test_data, r"C:\Windows\Fonts\NotoSerif-regular.ttf")
    test_data = {
        1800: 5,
        1801: 4,
        1802: 1,
        1803: 0,
        1804: 2,
        1805: 2,
        1806: 7,
        1807: 12,
        1808: 14,
        1809: 10,
        1810: 10
    }
    create_chronology_chart_file("testchron.png", 1800, 1810, 14, test_data)
    test_data = [
        [5],
        [4],
        [1],
        [0],
        [2],
        [2],
        [7],
        [12],
        [14],
        [10],
        [10]
    ]
    create_line_chart_file("testline.png", test_data, 1800, 1810, 0)
    create_bar_chart_file("testbar.png", test_data, 1800, 1810, 0)
    create_stacked_bar_chart_file("teststackbar.png", test_data, 1800, 1810, [["A", 0], ["B", 0]])
    test_data = {
        "pugilator": 20,
        "pugnax": 5,
        "tangeri": 12
    }
    create_qual_bar_chart_file("testqualbar.png", ["pugilator", "pugnax", "tangeri"], test_data, 20)
