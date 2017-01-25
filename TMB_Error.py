"""
Error reporting
"""


def report_error(logfile, outstr):
    print(outstr)
    logfile.write(outstr + "\n")
