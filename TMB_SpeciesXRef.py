"""
Module holds a dictionary of species objects listed by name, allowing one to find the
particular object representing that name
"""

import TMB_Classes
from TMB_Error import report_error

SPECIES_XREF = {}


def init_species_crossref(species: list):
    global SPECIES_XREF
    SPECIES_XREF = {}
    for s in species:
        SPECIES_XREF[s.species] = s


def find_species_by_name(x: str) -> TMB_Classes.SpeciesClass:
    if x in SPECIES_XREF:
        return SPECIES_XREF[x]
    else:
        report_error("Crossref Error: Cannot find species " + x)
        return SPECIES_XREF["vocans"]  # default to prevent crashing
