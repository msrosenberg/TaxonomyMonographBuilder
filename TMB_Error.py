"""
Error reporting
"""

LOGFILE = None


def report_error(outstr: str) -> None:
    print(outstr)
    if LOGFILE is not None:
        LOGFILE.write(outstr + "\n")
