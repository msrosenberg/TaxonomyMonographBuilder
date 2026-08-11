"""
Error reporting
"""

LOGFILE = None


def report_error(outstr: str) -> None:
    print(outstr)
    if LOGFILE is not None:
        # LOGFILE.write(f"{outstr}\n")
        print(outstr, file=LOGFILE)
