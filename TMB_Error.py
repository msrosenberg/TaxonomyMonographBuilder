"""
Error reporting
"""

LOGFILE = None


def report_error(outstr: str) -> None:
    print(outstr)
    if LOGFILE is not None:
        print(outstr, file=LOGFILE)
