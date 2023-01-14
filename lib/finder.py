import subprocess

def findInFiles(pattern, fileExtensions):
    findExtensionsCmd = ""

    for format in fileExtensions:
        findExtensionsCmd += "-o -name '*.{}' ".format(format)

    findCommand = \
    "find . -type f -not -path '*/\.git/*' -not -path '*/\.svn/*' \( -name '' " + \
    findExtensionsCmd + \
    "\) -exec grep -H -i -l '\<" + pattern + "\>' {} \;"

    output = subprocess.getoutput(findCommand).split('\n')
    output = [n[2:] for n in output]

    return output
