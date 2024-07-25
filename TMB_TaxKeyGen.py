"""
Taxonomic Key Generator
"""

from typing import Optional, Tuple, Union
from collections import Counter
from TMB_Error import report_error


class Taxon:
    def __init__(self):
        self.name = ""
        self.characters = []
        self.species = None

    def find_variant(self, trait):
        t = None
        for c in self.characters:
            if c is not None:
                if trait == c.trait:
                    t = c
        return t


class TraitVariant:
    def __init__(self):
        self.trait = None
        self.id = 0
        self.description = ""
        self.figures = []

    def __lt__(self, other):
        if self.id < other.id:
            return True
        else:
            return False

    def __str__(self):
        return self.description


class Trait:
    def __init__(self):
        self.title = ""
        self.variants = {}
        self.priority = 1
        self.id = 0
        self.notes = ""
        self.figures = []
        self.fnumber = None
        self.generic_notes = []

    def __len__(self):
        return len(self.variants)

    def add_variant(self, variant: TraitVariant) -> None:
        self.variants[variant.id] = variant
        variant.trait = self


class VariantDist:
    def __init__(self):
        self.trait = None
        self.variants = set()
        self.vfreq = Counter()
        self.pattern = ""
        self.cluster = None

    def __len__(self):
        return len(self.variants)

    def __repr__(self):
        freqs = []
        for v in self.vfreq:
            freqs.append("{}: {}".format(v.description, self.vfreq[v]))
        return "Variant Distribution of Trait: {}\n\tFreqs: {}\n\rPattern: {}".format(self.trait.title,
                                                                                      ", ".join(freqs),
                                                                                      self.pattern)

    def add_variant(self, variant):
        self.variants.add(variant)
        self.vfreq.update([variant])

    def add_to_cluster(self, cluster):
        cluster.append(self)
        self.cluster = cluster

    def freq_ratio(self) -> float:
        c0 = self.pattern.count("0")
        c1 = self.pattern.count("1")
        n = c0 + c1
        return min(c0/n, c1/n)

    def __lt__(self, other):
        if self.trait.priority < other.trait.priority:
            return True
        elif self.trait.priority > other.trait.priority:
            return False
        elif self.freq_ratio() < other.freq_ratio():
            return True
        elif self.freq_ratio() > other.freq_ratio():
            return False
        elif len(self.cluster) < len(other.cluster):
            return True
        else:
            return False


class KeyNode:
    def __init__(self):
        self.parent = None
        self.child0 = None
        self.child1 = None
        self.child0variants = []
        self.child1variants = []
        self.traits = []
        self.number = 0

    def new_child_node(self, c):
        child = KeyNode()
        if c == 0:
            self.child0 = child
        else:
            self.child1 = child
        child.parent = self
        return child


class TraitFigure:
    def __init__(self, image: str, caption: str):
        self.image = image
        self.caption = caption


class GenericNote:
    def __init__(self):
        self.id = 0
        self.title = ""
        self.notes = ""
        self.figures = []
        self.fnumber = None


class KeyText:
    def __init__(self):
        self.header = []
        self.body = []


def extract_figures(x: str) -> list:
    figs = []
    if x != ".":
        fs = x.split("||")
        for f in fs:
            fig, cap = f.split("|")
            figs.append(TraitFigure(fig, cap))
    return figs


def sorted_taxa_keys(tax_dict: dict) -> list:
    return sorted(tax_dict.keys())


def read_taxa_data(inname: str) -> dict:
    taxa_dict = {}
    with open(inname, "r", encoding="UTF-8") as infile:
        full_file = infile.readlines()
        for line in full_file[1:]:
            data = line.strip().split("\t")
            taxon = Taxon()
            taxa_dict[data[0]] = taxon
            taxon.name = data[0]
            taxon.characters = data[1:]
    return taxa_dict


def read_trait_data(inname: str) -> dict:
    trait_dict = {}
    with open(inname, "r") as infile:
        full_file = infile.readlines()
        for line in full_file[1:]:
            data = line.strip().split("\t")
            trait = Trait()
            trait_dict[data[0]] = trait
            trait.id = data[0]
            trait.title = data[1]
            trait.priority = int(data[2])
            if data[3] != ".":
                trait.notes = data[3]
            trait.figures = extract_figures(data[4])
            if data[5] != ".":
                trait.generic_notes = data[5].split(",")
    return trait_dict


def read_variant_data(inname: str, traits: dict) -> int:
    cnt = 0
    with open(inname, "r") as infile:
        full_file = infile.readlines()
        for line in full_file[1:]:
            data = line.strip().split("\t")
            n, _ = data[0].split(".")
            trait = traits[n]
            tv = TraitVariant()
            tv.id = data[0]
            tv.description = data[1]
            tv.figures = extract_figures(data[2])
            trait.add_variant(tv)
            cnt += 1
    return cnt


def read_generic_notes(inname: str) -> dict:
    gnotes = {}
    with open(inname, "r") as infile:
        full_file = infile.readlines()
        for line in full_file[1:]:
            data = line.strip().split("\t")
            note = GenericNote()
            note.id = data[0]
            note.title = data[1]
            note.notes = data[2]
            note.figures = extract_figures(data[3])
            gnotes[note.id] = note
    return gnotes


def match_traits_to_taxa(trait_data: dict, taxa_data: dict) -> None:
    """
    replace trait keys from taxon data file with references to matching trait objects
    """
    for t in taxa_data:
        taxon = taxa_data[t]
        for i, c in enumerate(taxon.characters):
            trait_id, v = c.split(".")
            trait = trait_data[trait_id]
            if v != "?" and v != "-":
                taxon.characters[i] = trait.variants[c]
            else:
                taxon.characters[i] = None


def match_generic_notes_to_traits(trait_data: dict, generic_notes: dict) -> None:
    """
    add generic notes to associated traits
    """
    for t in trait_data:
        trait = trait_data[t]
        for i, n in enumerate(trait.generic_notes):
            trait.generic_notes[i] = generic_notes[n]


def determine_variant_freqs(taxa_data: dict, trait_data: dict) -> list:
    """
    determine which variants are present in the taxa for each trait and determine the frequency
    of each as well
    """
    var_freqs = []
    for t_key in trait_data:
        trait = trait_data[t_key]
        var_dist = VariantDist()
        var_dist.trait = trait
        for tax_key in sorted_taxa_keys(taxa_data):
            taxon = taxa_data[tax_key]
            tax_var = taxon.find_variant(trait)
            var_dist.add_variant(tax_var)
        var_freqs.append(var_dist)
    return var_freqs


def filter_var_freqs(var_freqs: list) -> list:
    """
    filter out traits without exactly two variants
    """
    new_freqs = []
    for vf in var_freqs:
        if len(vf) == 2:
            if None not in vf.variants:
                new_freqs.append(vf)
    return new_freqs


def determine_var_pattern(var_freqs: list, taxa_data: dict) -> None:
    """
    determine the pattern of variants across taxa

    at this stage only binary traits are examined, so the patten is stored as a string of 0's and 1's
    """
    for vf in var_freqs:
        variants = sorted(vf.variants)
        for tk in sorted_taxa_keys(taxa_data):
            taxon = taxa_data[tk]
            tv = taxon.find_variant(vf.trait)
            vf.pattern += str(variants.index(tv))


def reverse_pattern(x: str) -> str:
    """
    returns the inverse of a binary string

    thus 00011100 -> 11100011
    """
    return x.translate(str.maketrans("01", "10"))


def cluster_traits(var_freqs: list) -> list:
    # seed with first variant
    vf = var_freqs[0]
    c = []
    vf.add_to_cluster(c)
    clusters = [c]
    for vf in var_freqs[1:]:
        match = False
        for c in clusters:
            cpattern = c[0].pattern
            if (cpattern == vf.pattern) or (cpattern == reverse_pattern(vf.pattern)):
                vf.add_to_cluster(c)
                match = True
        if not match:
            c = []
            clusters.append(c)
            vf.add_to_cluster(c)
    return clusters


def split_taxa(taxa_data: dict, key_vf: VariantDist) -> Tuple[list, list]:
    """
    split taxa into two groups based on the key variant
    """
    taxa0 = []
    taxa1 = []
    variants = sorted(key_vf.variants)
    for tk in sorted_taxa_keys(taxa_data):
        taxon = taxa_data[tk]
        tv = taxon.find_variant(key_vf.trait)
        i = variants.index(tv)
        if i == 0:
            taxa0.append(taxon)
        else:
            taxa1.append(taxon)
    return taxa0, taxa1


def trait_list(cluster: list) -> list:
    tlist = []
    for vf in cluster:
        tlist.append(vf.trait)
    return tlist


def match_variants(t_list: list, taxon: Taxon):
    return [taxon.find_variant(t) for t in t_list]


def create_key_tree(taxa_data: dict, trait_data: dict, node: KeyNode) -> set:
    """
    primary key tree creation function
    """
    warning_set = set()
    var_freqs = determine_variant_freqs(taxa_data, trait_data)
    var_freqs = filter_var_freqs(var_freqs)
    if len(var_freqs) > 0:
        determine_var_pattern(var_freqs, taxa_data)
        cluster_traits(var_freqs)
        var_freqs.sort(reverse=True)
        key_vf = var_freqs[0]
        taxa0, taxa1 = split_taxa(taxa_data, key_vf)
        node.traits = trait_list(key_vf.cluster)  # assign all traits which align with this split to node
        node.child0variants = match_variants(node.traits, taxa0[0])
        node.child1variants = match_variants(node.traits, taxa1[0])
        if len(taxa0) > 1:
            new_node = node.new_child_node(0)
            tset = create_key_tree({t.name: t for t in taxa0}, trait_data, new_node)
            if len(tset) > 0:
                warning_set |= tset
        else:
            node.child0 = taxa0[0]
        if len(taxa1) > 1:
            new_node = node.new_child_node(1)
            tset = create_key_tree({t.name: t for t in taxa1}, trait_data, new_node)
            if len(tset) > 0:
                warning_set |= tset
        else:
            node.child1 = taxa1[0]
    else:  # taxa are undivisible
        if node == node.parent.child0:
            node.parent.child0 = taxa_data
        else:
            node.parent.child1 = taxa_data
        # report_error("Warning. Undivisable group: " + ", ".join(sorted_taxa_keys(taxa_data)))
        warning_set.add("Warning. Undivisable group: " + ", ".join(sorted_taxa_keys(taxa_data)))
    return warning_set


def number_nodes(tree: KeyNode, node_number: int) -> int:
    """
    number the tree nodes

    this is used for the numbering rules in the key, 'if xxxxx, go to NUMBER'
    """
    tree.number = node_number
    if isinstance(tree.child0, KeyNode):
        node_number = number_nodes(tree.child0, node_number+1)
    if isinstance(tree.child1, KeyNode):
        node_number = number_nodes(tree.child1, node_number+1)
    return node_number


def output_header(output: list, nnodes: int) -> None:
    output.append("    <style>\n")
    output.append("      .tree-grid {\n")
    output.append("                    display: grid;\n")
    output.append("                    grid-template-columns: 4ch 1fr;\n")
    output.append("                    grid-template-areas: \"fork-number fork-option\";\n")
    output.append("                    grid-row-gap: 10px;\n")
    output.append("                 }\n")
    for n in range(nnodes):
        output.append("      #key-fork-n-{} {{grid-area: {} / fork-number }}\n".format(n+1, n*2 + 1))
        output.append("      #key-fork-a-{} {{grid-area: {} / fork-option }}\n".format(n+1, n*2 + 1))
        output.append("      #key-fork-b-{} {{grid-area: {} / fork-option }}\n".format(n+1, (n+1)*2))
    output.append("      .key-fork-n { font-weight: bold }\n")
    output.append("      .key-fork-a { padding-left: 3ch; text-indent: -3ch }\n")
    output.append("      .key-fork-b { padding-left: 3ch; text-indent: -3ch; padding-bottom: 1em; "
                  "border-bottom: 1px solid silver}\n")
    output.append("      .variant-fig { margin: 0.25em; display: inline-block; text-indent: 0; text-align: center; "
                  "vertical-align: text-top}\n")
    output.append("      .variant-fig img { height: 200px }\n")
    output.append("      .variant-fig figcaption { font-style: italic; font-size: 0.75em; margin-top: 0.25em; "
                  "margin-left: auto; margin-right: auto; max-width: 250px }\n")
    output.append("      #key_footnotes li { padding-bottom: 1em }\n")
    output.append("      .tkg_title { font-style: italic }\n")
    output.append("      .key_intro { padding-bottom: 2em; font-size: 0.75em }\n")
    output.append("    </style>\n")


def get_var_figs(variants: list) -> str:
    fig_str = ""
    for v in variants:
        for f in v.figures:
            fig_str += "<figure class=\"variant-fig\"><img src=\"images/{}\" />".format(f.image)
            if f.caption != ".":
                fig_str += "<figcaption>{}</figcaption>".format(f.caption)
            fig_str += "</figure> "
    return fig_str


def write_key(tree: KeyNode, output: list, footnotes: set, append_footnotes: bool = False) -> None:
    """
    recursive function to write the generated key to html
    """
    def fork_str(letter: str, variants: list, tip: Union[KeyNode, Taxon], n: int):
        """
        create the output string for each fork from a node
        """
        var_strs = []
        for v in variants:
            fn_list = []
            for gn in v.trait.generic_notes:
                if gn not in footnotes:
                    footnotes.add(gn)
                    gn.fnumber = len(footnotes)
                fn_list.append("<a href=\"#fn{0}\">footnote {0}</a>".format(gn.fnumber))
            if v.trait.notes != "":
                if v.trait not in footnotes:
                    footnotes.add(v.trait)
                    v.trait.fnumber = len(footnotes)
                fn_list.append("<a href=\"#fn{0}\">footnote {0}</a>".format(v.trait.fnumber))
                # fn_str = " [<a href=\"#fn{0}\">footnote {0}</a>]".format(v.trait.fnumber)
            if len(fn_list) > 0:
                fn_str = " [" + ", ".join(fn_list) + "]"
            else:
                fn_str = ""
            var_strs.append(str(v) + fn_str)
        var_figs = get_var_figs(variants)
        outstr = "    <div id=\"key-fork-{0}-{1}\" class=\"key-fork-{0}\">{0}. ".format(letter, n) + \
                 ". ".join(var_strs) + ". &mdash; "
        if isinstance(tip, KeyNode):
            outstr += "<a href=\"#key-node-{0}\">Go to {0}</a>".format(tip.number)
        elif isinstance(tip, Taxon):
            outstr += tip.name
        elif isinstance(tip, dict):
            taxa_names = sorted_taxa_keys(tip)
            if len(taxa_names) == 2:
                outstr += taxa_names[0] + " or " + taxa_names[1]
            else:
                outstr += ", ".join(taxa_names[:-1]) + ", or " + taxa_names[len(taxa_names)-1]
        else:
            report_error("ERROR: Child node of invalid type:" + str(tip))
        if var_figs != "":
            outstr += "<br/>" + var_figs
        return outstr + "</div>\n"

    output.append("    <div id=\"key-fork-n-{0}\" class=\"key-fork-n\">"
                  "<a name=\"key-node-{0}\">{0}.</a></div>\n".format(tree.number))
    output.append(fork_str("a", tree.child0variants, tree.child0, tree.number))
    output.append(fork_str("b", tree.child1variants, tree.child1, tree.number))
    if isinstance(tree.child0, KeyNode):
        write_key(tree.child0, output, footnotes)
    if isinstance(tree.child1, KeyNode):
        write_key(tree.child1, output, footnotes)
    if append_footnotes and (len(footnotes) > 0):
        output.append("    </div>\n")
        output.append("    <div>\n")
        output.append("      <h2>Footnotes</h2>\n")
        fdict = {f.fnumber: f for f in footnotes}
        fkeys = sorted(fdict.keys())
        output.append("      <ol id=\"key_footnotes\">\n")
        for f in fkeys:
            fn = fdict[f]
            output.append("        <li>\n")
            output.append("          <a name=\"fn{}\">{}</a>\n".format(fn.fnumber, fn.notes))
            if len(fn.figures) > 0:
                fig_str = ""
                for fig in fn.figures:
                    fig_str += "<figure class=\"variant-fig\"><img src=\"images/{}\" />".format(fig.image)
                    if fig.caption != ".":
                        fig_str += "<figcaption>{}</figcaption>".format(fig.caption)
                    fig_str += "</figure> "
                output.append("          <br/>\n")
                output.append("          " + fig_str + "\n")
            output.append("        </li>\n")
        output.append("      </ol>\n")


def generate_taxonomic_key(trait_data: dict, taxa_data: dict, out_name: Optional[str] = None,
                           verbose: bool = True) -> Tuple[KeyText, set]:
    key_tree = KeyNode()
    warning_set = create_key_tree(taxa_data, trait_data, key_tree)
    total_nodes = number_nodes(key_tree, 1)
    # output = []
    output = KeyText()
    output_header(output.header, total_nodes)
    output.body.append("    <div class=\"tree-grid\">\n")
    write_key(key_tree, output.body, set(), append_footnotes=True)
    output.body.append("    </div>\n")
    # end_output(output)
    if out_name is not None:
        pass
        with open(out_name, "w", encoding="utf-8") as outfile:
            outfile.write("<html>\n")
            outfile.write("  <head>\n")
            outfile.writelines(output.header)
            outfile.write("  </head>\n")
            outfile.write("  <body>\n")
            outfile.write("    <h1>Taxonomic Key</h1>\n")
            outfile.write("    <div class=\"key_intro\">This key was auto-generated by "
                          "<span class=\"tkg_title\">TaxKeyGen</span> "
                          "(<a href=\"https://github.com/msrosenberg/TaxKeyGen\">"
                          "https://github.com/msrosenberg/TaxKeyGen</a>)</div>")
            outfile.writelines(output.body)
            outfile.write("  </body>\n")
            outfile.write("</html>\n")
        if verbose:
            print("Key written to {}".format(out_name))
    if verbose:
        print("Finished")
        for w in sorted(warning_set):
            report_error(w)
    return output, warning_set


def input_query(query: str, default: str) -> str:
    x = input("{} [default: {}]: ".format(query, default))
    if x == "":
        x = default
    return x


def link_taxonomic_key_data(trait_data: dict, generic_notes: dict, taxa_data: dict) -> None:
    match_traits_to_taxa(trait_data, taxa_data)
    match_generic_notes_to_traits(trait_data, generic_notes)


def read_data_files(trait_name: str, var_name: str, generic_name: str, taxa_name: str,
                    verbose: bool = True) -> Tuple[dict, dict, dict]:
    trait_data = read_trait_data(trait_name)
    if verbose:
        print()
        print("Read {} traits from {}".format(len(trait_data), trait_name))
    nv = read_variant_data(var_name, trait_data)
    if verbose:
        print("Read {} trait variants from {}".format(nv, var_name))
    generic_notes = read_generic_notes(generic_name)
    if verbose:
        print("Read {} generic notes from {}".format(len(generic_notes), generic_name))
    taxa_data = read_taxa_data(taxa_name)
    if verbose:
        print("Read {} taxa from {}".format(len(taxa_data), taxa_name))
        print()
    return trait_data, generic_notes, taxa_data


def main():
    trait_file = input_query("Trait data file", "fiddlercrab.info/data/tax_key_trait_data.txt")
    trait_var_file = input_query("Trait variant data file", "fiddlercrab.info/data/tax_key_variant_data.txt")
    generic_file = input_query("Generic notes file", "fiddlercrab.info/data/tax_key_generic_notes.txt")
    taxa_file = input_query("Taxa data file", "fiddlercrab.info/data/tax_key_taxa_data.txt")
    output_file = input_query("Output HTML file", "output.html")

    trait_data, generic_notes, taxa_data = read_data_files(trait_file, trait_var_file, generic_file, taxa_file)
    link_taxonomic_key_data(trait_data, generic_notes, taxa_data)
    generate_taxonomic_key(trait_data, taxa_data, output_file)


if __name__ == "__main__":
    main()
