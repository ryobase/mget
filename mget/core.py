import sys
import shutil
import os
import tempfile
import math
import requests
import click
import re
import time
import traceback
# from mget.consoleUtil import getTerminalSize

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse

"""
Global 
"""

defaults = {
    "version": "0.1.0",
    "tries": 1,
    "verbose": True,
    "prefix": "", 
    "suffix": "",
    "chunk_size": (1024 * 1024)
}
sizes = ["Bytes", "KB", "MB", "GB", "TB"]
spinners = ["/|\\"]
DIRNAME = os.getcwd()
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


"""
Helpers
"""


def filenameFromUrl(url):
    """Return file name base on the last portion of the url
    """
    fname = os.path.basename(urlparse.urlparse(url).path)
    if len(fname.strip(" \n\t.")) == 0:
        return None
    return fname


def getFileExtension(name):
    """Crude way to retrieve file extension using regular expression
    Return the file extension string
    """
    pat = re.compile(r"\/(\w+)")
    m = pat.search(name)
    if m is None:
        raise ValueError("Unable to parse file extension. Exiting the program")
    return m.group(1)


def isExist(fname):
    """Check whether a there already is a file with the same name
    or not. Return a boolean
    """
    names = [x for x in os.listdir(DIRNAME) if x.startswith(fname)]
    return len(names) > 0


def fixFileExists(name, ext):
    """Expand filename with numeric ' (x)' suffix to
    return filename that doesn't exist already.
    """
    dirname = DIRNAME
    # name, ext = filename.rsplit('.', 1)
    names = [x for x in os.listdir(dirname) if x.startswith(name)]
    names = [x.rsplit('.', 1)[0] for x in names]
    suffixes = [x.replace(name, '') for x in names]
    suffixes = [x[2:-1] for x in suffixes if x.startswith(' (') and x.endswith(')')]
    indexes = [int(x) for x in suffixes if set(x) <= set('0123456789')]
    idx = 1
    if indexes:
        idx += sorted(indexes)[-1]
    return '%s (%d).%s' % (name, idx, ext)


def progressBar(curr, total, b_length=60, prefix='', suffix='', decimals=0):
    """Return the progress bar

    Code from https://gist.github.com/aubricus/f91fb55dc6ba5557fbab06119420dd6a
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (curr/ float(total)))
    filled_len = int(round(b_length * curr / float(total)))
    bar = '█' * filled_len + '░' * (b_length - filled_len)

    return '\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)


def convertBytes(num):
    if num is 0:
        return "n/a"
    i = int(math.floor(math.log(num) / math.log(1024)))
    if i is 0:
        return "{num} {sizes}".format(num=num, sizes=sizes[i])
    size = "{0:0.1f}".format(num / math.pow(1024, i))
    return "{size} {sizes}".format(size=size, sizes=sizes[i])


def download(url, output_name):
    """Main function to download stuff
    """
    fileop = dict()

    r = requests.get(url, stream=True, headers={'Accept-Encoding': None})
    total_size = int(r.headers["content-length"])
    chunk_size = 0
    fname = filenameFromUrl(url)
    try:
        fileop["name"], fileop["ext"] = fname.rsplit('.', 1)
    except ValueError as err:
        # Provided url does not contain file extension
        # we will have to extract it from the header
        fileop["name"] = fname
        fileop["ext"] = getFileExtension(r.headers["content-type"])

    path_to_file = os.path.abspath(output_name or ".")

    fileop["fullname"] = fileop["name"] + "." + fileop["ext"]

    if isExist(fileop["fullname"]):
        fileop["fullname"] = fixFileExists(fileop["name"], fileop["ext"])

    if r.status_code is 200:
        try:
            with open(path_to_file + "/" + fileop["fullname"], "wb") as fd:
                for chunk in r.iter_content(chunk_size=defaults["chunk_size"]):
                    chunk_size = min(chunk_size, total_size)

                    stats = progressBar \
                    ( \
                        chunk_size, \
                        total_size, \
                        80, f'{defaults["prefix"]}', \
                    )
                    sys.stdout.write(stats)
                    sys.stdout.flush()

                    chunk_size += defaults["chunk_size"]
                    fd.write(chunk)

                if chunk_size >= total_size:
                    stats = progressBar \
                    ( \
                        100, \
                        100, \
                        80, f'{defaults["prefix"]}', \
                    )
                    sys.stdout.write(stats)
                    # sys.stdout.write('\n')
                    # sys.stdout.write("Download completed")
                    sys.stdout.flush()
        except Exception as err:
            print("Unexpected error: {0}".format(err))
    else:
        r.raise_for_status()
    r.close()


"""
Command-Line Interface
"""


@click.command(context_settings=CONTEXT_SETTINGS, options_metavar='<options>')
@click.option("--version", "-v", help="Display version and exit", is_flag=True)
# @click.option("--quiet", "-q", help="Turn off output", is_flag=True)
@click.option("--chunk_size", help="Chunk size of the binary output", type=click.INT,\
    default=defaults["chunk_size"], nargs=1)
@click.option("--output", "-o", help="Output filename", type=click.STRING, \
    default="", nargs=1)
@click.argument("url", metavar="<url>", default="", nargs=1, type=click.STRING)
@click.pass_context
def cli(ctx, version, chunk_size, output, url):
    """wget clone written in Python 3"""
    ctx.obj = defaults.copy()
    if version:
        click.echo("mget version " + ctx.obj["version"])
    elif len(url) > 0:
        download(url, output)
    else:
        click.echo("Program exit with code 0")


if __name__ == "__main__":
    cli(obj={})
