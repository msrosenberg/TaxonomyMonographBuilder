"""
Utility to help find variation in author names
"""

import codecs


def get_last_name(x):
    return x[:x.find(",")].strip()


def main():
    allnames = set()
    lastnames = set()

    with codecs.open("check_ref_names.txt", "r", "utf-8") as infile:
        for line in infile:
            names = line.strip().strip(";").lower().split(";")
            for name in names:
                allnames.add(name)
                lastnames.add(get_last_name(name))

    namecnt = {name: list() for name in lastnames}
    for name in allnames:
        tmplist = namecnt[get_last_name(name)]
        tmplist.append(name)

    with codecs.open("check_ref_names_duplicates.txt", "w", "utf-8") as outfile:
        lastlist = list(namecnt.keys())
        lastlist.sort()
        for lastname in lastlist:
            names = namecnt[lastname]
            names.sort()
            if len(names) > 1:
                for name in names:
                    outfile.write(name + "\n")
                outfile.write("\n")


if __name__ == "__main__":
    main()
