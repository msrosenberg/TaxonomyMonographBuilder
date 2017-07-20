"""
Error reporting
"""

LOGFILE = None


def report_error(outstr):
    print(outstr)
    LOGFILE.write(outstr + "\n")
