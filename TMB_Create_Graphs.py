"""
Module containing the various graph and chart drawing algorithms (except for those related to maps)
"""

# external dependencies
import matplotlib.pyplot as mplpy
from wordcloud import WordCloud

__TMP_PATH__ = "temp/"


def create_pie_chart_file(filename: str, data: dict) -> None:
    datalist = list(data.keys())
    datalist.sort()
    sizes = []
    for d in datalist:
        sizes.append(data[d])
    fig, faxes = mplpy.subplots(figsize=[6, 3])
    # my approximation of the pygal color scheme
    color_list = ["salmon", "royalblue", "lightseagreen", "gold", "darkorange", "mediumorchid", "deepskyblue",
                  "lightgreen", "sandybrown", "palevioletred", "lightskyblue", "mediumaquamarine", "lemonchiffon"]
    faxes.pie(sizes, colors=color_list, startangle=90, counterclock=False)
    faxes.axis("equal")
    faxes.legend(datalist, loc="upper left", frameon=False)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    # mplpy.savefig(__TMP_PATH__ + filename)
    mplpy.savefig(__TMP_PATH__ + filename, format="png", dpi=600)
    mplpy.close("all")


def create_bar_chart_file(filename: str, data: list, minx: int, maxx: int, y: int) -> None:
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
    # mplpy.savefig(__TMP_PATH__ + filename)
    mplpy.savefig(__TMP_PATH__ + filename, format="png", dpi=600)
    mplpy.close("all")


def create_stacked_bar_chart_file(filename: str, data: list, minx: int, maxx: int, cols: list) -> None:
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
    # mplpy.savefig(__TMP_PATH__ + filename)
    mplpy.savefig(__TMP_PATH__ + filename, format="png", dpi=600)
    mplpy.close("all")


def create_qual_bar_chart_file(filename: str, label_list: list, data_dict: dict, max_value: int) -> None:
    x_list = [x for x in range(len(label_list))]
    y_list = [data_dict[x] for x in label_list]
    fig, faxes = mplpy.subplots(figsize=[6.5, 2.5])
    faxes.bar(x_list, y_list, color="blue", edgecolor="darkblue")
    mplpy.xticks(rotation="vertical", style="italic")
    # tick_list = x_list[::4]
    # tick_labels = label_list[::4]
    # faxes.set_xticks(tick_list)
    # faxes.set_xticklabels(tick_labels)
    faxes.set_xticks(x_list)
    faxes.set_xticklabels(label_list)
    faxes.spines["right"].set_visible(False)
    faxes.spines["top"].set_visible(False)
    mplpy.ylim(0, max_value)
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    # mplpy.savefig(__TMP_PATH__ + filename)
    mplpy.savefig(__TMP_PATH__ + filename, format="png", dpi=600)
    mplpy.close("all")


def create_line_chart_file(filename: str, data: list, minx: int, maxx: int, y: int) -> None:
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
    # mplpy.savefig(__TMP_PATH__ + filename, format="svg")
    mplpy.savefig(__TMP_PATH__ + filename, format="png", dpi=600)
    mplpy.close("all")


def create_chronology_chart_file(filename: str, miny: int, maxy: int, maxcnt: int, yearly_data: dict) -> None:
    y_list = []
    for y in range(miny, maxy + 1):
        y_list.append(float(yearly_data[y]))

    x = [y for y in range(miny, maxy+1)]
    fig, faxes = mplpy.subplots(figsize=[6.5, 1.5])
    mplpy.ylim(-maxcnt, maxcnt)
    mplpy.xlim(miny, maxy)
    # faxes.fill(x, y_list, "black")
    # faxes.fill(x, y2_list, "black")
    faxes.stackplot(x, y_list, baseline="sym", colors=["black"])
    for spine in faxes.spines:
        faxes.spines[spine].set_visible(False)
    cur_axes = mplpy.gca()
    cur_axes.axes.get_yaxis().set_visible(False)
    mplpy.xticks([i for i in range(miny, maxy+1, 20)])
    mplpy.rcParams["svg.fonttype"] = "none"
    mplpy.tight_layout()
    # mplpy.savefig(__TMP_PATH__ + filename)
    mplpy.savefig(__TMP_PATH__ + filename, format="png", dpi=600)
    mplpy.close("all")


def create_word_cloud_image(binomial_cnts: dict, specific_cnts: dict) -> None:
    # fiddler_mask = np.array(Image.open("private/silhouette.png"))
    # generate wordcloud image from binomials
    wordcloud = WordCloud(width=2000, height=1500, background_color="white", max_words=1000,  normalize_plurals=False,
                          collocations=False).generate_from_frequencies(binomial_cnts)
    wordcloud.to_file(__TMP_PATH__ + "binomial_word_cloud.png")

    # generate wordcloud image from specific names
    wordcloud = WordCloud(width=2000, height=1500, background_color="white", max_words=1000,  normalize_plurals=False,
                          collocations=False).generate_from_frequencies(specific_cnts)
    wordcloud.to_file(__TMP_PATH__ + "specific_word_cloud.png")
