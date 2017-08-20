"""
Error reporting
"""

LOGFILE = None


def report_error(outstr: str) -> None:
    print(outstr)
    LOGFILE.write(outstr + "\n")
