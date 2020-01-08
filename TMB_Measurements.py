
import math
import random
import matplotlib.pyplot as mplpy
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import numpy
import TMB_Classes

DATA_TYPES = ["individual", "range", "mean", "mean/sd", "mean/se", "classcount", "mean/sd/min/max"]


def sort_measurement_data(data: list) -> dict:
    """
    sort the measurement data into species and into male, female, etc.
    """
    species = set()
    for d in data:
        species.add(d.species)
    species_data = {}
    for s in species:
        sdata = TMB_Classes.SpeciesMeasurements()
        for dtype in DATA_TYPES:
            tall = []
            tother = []
            tmale = []
            tfemale = []
            for d in data:
                if d.species == s:
                    if d.type == dtype:
                        tall.append(d)
                        if d.sex == "male":
                            tmale.append(d)
                        elif d.sex == "female":
                            tfemale.append(d)
                        else:
                            tother.append(d)
            if len(tall) > 0:
                sdata.all[dtype] = tall
            if len(tother) > 0:
                sdata.other[dtype] = tother
            if len(tmale) > 0:
                sdata.male[dtype] = tmale
            if len(tfemale) > 0:
                sdata.female[dtype] = tfemale
        species_data[s] = sdata
    return species_data


def se_to_sd(se, n):
    return se * math.sqrt(n)


def combine_measurement_data(data):
    cdata = []
    if "individual" in data:
        n = 1
    else:
        n = 0
    subset = [t for t in DATA_TYPES if t != "individual"]
    for dtype in subset:
        if dtype in data:
            dat = data[dtype]
            for d in dat:
                n = max(n, d.n)
    if n > 0:
        maxr = 1000
        while n > maxr:
            maxr *= 10
        pern = round(maxr / n)
        if "individual" in data:
            dat = data["individual"]
            for d in dat:
                for r in range(pern):
                    cdata.append(d.value)
        if "range" in data:
            dat = data["range"]
            for d in dat:
                for r in range(pern):
                    cdata.append(d.value.max_val)
                    cdata.append(d.value.min_val)
                if d.n > 2:
                    sd = (d.value.max_val - d.value.min_val)/4
                    mp = d.value.midpoint()
                    for r in range(pern*(d.n - 2)):
                        v = random.gauss(mp, sd)
                        # do not allow simulated widths to exceed observed range
                        while (v < d.value.min_val) or (v > d.value.max_val):
                            v = random.gauss(mp, sd)
                        cdata.append(v)
        if "mean/sd" in data:
            dat = data["mean/sd"]
            for d in dat:
                for r in range(pern*d.n):
                    cdata.append(random.gauss(d.value.mean, d.value.sd))
        if "mean/se" in data:
            dat = data["mean/se"]
            for d in dat:
                sd = se_to_sd(d.value.se, d.n)
                for r in range(pern*d.n):
                    cdata.append(random.gauss(d.value.mean, sd))
        if "mean" in data:
            dat = data["mean"]
            for d in dat:
                # this essentially treats the mean as having variance of zero, which may be giving it too much power
                for r in range(pern*d.n):
                    cdata.append(d.value.mean)

        if "mean/sd/min/max" in data:
            dat = data["mean/sd/min/max"]
            for d in dat:
                for r in range(pern):
                    cdata.append(d.value.max_val)
                    cdata.append(d.value.min_val)
                if d.n > 2:
                    for r in range(pern*(d.n - 2)):
                        v = random.gauss(d.value.mean, d.value.sd)
                        # don't allow simulated widths to exceed observed range
                        while (v < d.value.min_val) or (v > d.value.max_val):
                            v = random.gauss(d.value.mean, d.value.sd)
                        cdata.append(v)

        if "classcount" in data:
            dat = data["classcount"]
            for d in dat:
                for r in range(int(round(pern*d.n, 0))):
                    cdata.append(d.value.midpoint())
    return cdata


def plot_individuals(faxes, data, yv, color):
    if "individual" in data:
        idata = data["individual"]
        x = []
        for d in idata:
            x.append(d.value)
        y = [yv + 0.75*random.random() for _ in idata]
        faxes.scatter(x, y, color=color, edgecolors="black", linewidths=0.25)
        yv += 1
    return yv


def plot_ranges(faxes, data, yv, color):
    if "range" in data:
        rdata = data["range"]
        x = []
        y = []
        for i, d in enumerate(rdata):
            x.append([d.value.min_val, d.value.max_val])
            # y.append(yv-i*1.5/len(rdata))
            y.append(yv)
            yv += 1
        parts = faxes.violinplot(x, y, points=10, vert=False, widths=0.5, showextrema=True, showmedians=False,
                                 showmeans=False)
        for pc in parts["bodies"]:
            pc.set_alpha(0)
        for p in ["cmins", "cmaxes", "cbars"]:
            parts[p].set_color(color)
            parts[p].set_linewidths(0.5)
    return yv


def plot_means(faxes, data, yv, color):
    if "mean" in data:
        mdata = data["mean"]
        x = []
        for d in mdata:
            x.append(d.value.mean)
        y = [yv for _ in mdata]
        faxes.scatter(x, y, color=color, edgecolors="black", linewidths=0.25, marker="d")
        yv += 1
    return yv


def plot_means_sd(faxes, data, yv, color):
    if "mean/sd" in data:
        mdata = data["mean/sd"]
        x = []
        e = []
        for d in mdata:
            x.append(d.value.mean)
            e.append(d.value.sd*1.96)
        y = [yv + i for i in range(len(mdata))]
        faxes.errorbar(x, y, xerr=e, color=color, marker="d", markeredgecolor="black", markeredgewidth=0.25, ls="none")
        yv += len(mdata)
    return yv


def plot_means_se(faxes, data, yv, color):
    if "mean/se" in data:
        mdata = data["mean/se"]
        x = []
        e = []
        for d in mdata:
            sd = se_to_sd(d.value.se, d.n)
            x.append(d.value.mean)
            e.append(sd*1.96)
        y = [yv + i for i in range(len(mdata))]
        faxes.errorbar(x, y, xerr=e, color=color, marker="d", markeredgecolor="black", markeredgewidth=0.25, ls="none")
        yv += len(mdata)
    return yv


def plot_classcount(faxes, data, yv, color):
    if "classcount" in data:
        classes = set()
        cdata = data["classcount"]
        boxes = []
        for d in cdata:
            classes.add(d.class_id)
        for c in classes:
            current_class = []
            maxn = 0
            for d in cdata:
                if d.class_id == c:
                    current_class.append(d)
                    maxn = max(maxn, d.n)
            for d in current_class:
                rect = Rectangle((d.value.min_val, yv), d.value.max_val-d.value.min_val, d.n/maxn)
                boxes.append(rect)
            yv += 1.25

        pc = PatchCollection(boxes, facecolor=color, edgecolor="black", linewidths=0.25, alpha=0.5)
        faxes.add_collection(pc)
    return yv


def plot_means_sd_min_max(faxes, data, yv, color):
    if "mean/sd/min/max" in data:
        mdata = data["mean/sd/min/max"]
        mx = []
        e = []
        x = []
        for i, d in enumerate(mdata):
            mx.append(d.value.mean)
            e.append(d.value.sd*1.96)
            x.append([d.value.min_val, d.value.max_val])
        y = [yv + i for i in range(len(mdata))]
        parts = faxes.violinplot(x, y, points=10, vert=False, widths=0.5, showextrema=True, showmedians=False,
                                 showmeans=False)
        for pc in parts["bodies"]:
            pc.set_alpha(0)
        for p in ["cmins", "cmaxes", "cbars"]:
            parts[p].set_color(color)
            parts[p].set_linewidths(0.5)
        faxes.errorbar(mx, y, xerr=e, color=color, marker="d", markeredgecolor="black", markeredgewidth=0.25, ls="none")
        yv += len(mdata)

    return yv


def plot_combined_data(faxes, combined_data, yv, color):
    if len(combined_data) > 0:
        quartile1, median, quartile3 = numpy.percentile(combined_data, [25, 50, 75])
        mean = numpy.mean(combined_data)

        parts = faxes.violinplot(combined_data, [yv], widths=2, points=1000, vert=False)
        for pc in parts["bodies"]:
            pc.set_color(color)
        for p in ["cmins", "cmaxes", "cbars"]:
            parts[p].set_color(color)
            # parts[p].set_linewidths(0.5)
        faxes.hlines(yv, quartile1, quartile3, color=color, linestyle='-', lw=5, alpha=0.5)
        faxes.scatter(median, yv, marker="o", color="white", edgecolor=color, zorder=3)
        faxes.scatter(mean, yv, marker="d", color="white", edgecolor=color, zorder=3)
        yv += 2.5
    return yv


def plot_measurement_data(species_dat, combined_data, comb_male_data, comb_female_data, filename):
    fig, faxes = mplpy.subplots(figsize=[6, 6])
    faxes.spines["right"].set_visible(False)
    faxes.spines["top"].set_visible(False)
    faxes.spines["left"].set_visible(False)
    faxes.get_yaxis().set_visible(False)
    mplpy.xlabel("carapace breadth (mm)")

    y = 1
    # plot individuals
    y = plot_individuals(faxes, species_dat.female, y, "red")
    y = plot_individuals(faxes, species_dat.male, y, "blue")
    y = plot_individuals(faxes, species_dat.other, y, "black")

    # plot ranges
    y = plot_ranges(faxes, species_dat.female, y, "red")
    y = plot_ranges(faxes, species_dat.male, y, "blue")
    y = plot_ranges(faxes, species_dat.other, y, "black")

    # plot means
    y = plot_means(faxes, species_dat.female, y, "red")
    y = plot_means(faxes, species_dat.male, y, "blue")
    y = plot_means(faxes, species_dat.other, y, "black")

    # plot means w/sd and se
    y = plot_means_sd(faxes, species_dat.female, y, "red")
    y = plot_means_se(faxes, species_dat.female, y, "red")
    y = plot_means_sd(faxes, species_dat.male, y, "blue")
    y = plot_means_se(faxes, species_dat.male, y, "blue")
    y = plot_means_sd(faxes, species_dat.other, y, "black")
    y = plot_means_se(faxes, species_dat.other, y, "black")

    y = plot_means_sd_min_max(faxes, species_dat.female, y, "red")
    y = plot_means_sd_min_max(faxes, species_dat.male, y, "blue")
    y = plot_means_sd_min_max(faxes, species_dat.other, y, "black")

    # plot classcounts
    y = plot_classcount(faxes, species_dat.female, y, "red")
    y = plot_classcount(faxes, species_dat.male, y, "blue")
    y = plot_classcount(faxes, species_dat.other, y, "black")

    y += 1
    y = plot_combined_data(faxes, comb_female_data, y, "red")
    y = plot_combined_data(faxes, comb_male_data, y, "blue")
    plot_combined_data(faxes, combined_data, y, "black")

    custom_lines = [Line2D([0], [0], color="black", lw=4),
                    Line2D([0], [0], color="blue", lw=4),
                    Line2D([0], [0], color="red", lw=4)]
    faxes.legend(custom_lines, ["All", "Males", "Females"], ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.01))

    mplpy.savefig(filename, format="png", dpi=600)
    mplpy.close("all")


# def main():
#     random.seed()
#
#     data = read_data()
#     # print(len(data))
#     species_data = sort_data(data)
#     for i, s in enumerate(species_data):
#         print("Creating size distribution of species {}: {}".format(i, s))
#         cdat = combine_data(species_data[s].all)
#         mdat = combine_data(species_data[s].male)
#         fdat = combine_data(species_data[s].female)
#         plot_data(s, species_data[s], cdat, mdat, fdat)
#
#
# if __name__ == "__main__":
#     main()
