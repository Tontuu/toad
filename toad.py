import argparse, re


def searchPatternInFile(inputFile, pattern):
    todoRegex = re.compile('(?i)todo:')
    matches = []
    with open(inputFile, 'r') as f:
       for i, line in enumerate(f):
           if todoRegex.search(line):
               matches.append({"str": line.strip(), "lineNumber": i+1})

    return matches

def formatBody(bodies, lineNumbers):
    result = []
    for i in range(len(bodies)):
        result.append("TODOS: {}\n  [{}]\n".format(bodies[i], lineNumbers[i]))

    return result

def splitMatchesByRegex(matches):
    bodies  = []
    lineNumbers = []

    for i in matches:
        (_, body) = i["str"].split(":")
        lineNumbers.append(i["lineNumber"])
        bodies.append(body.strip())

    return (bodies, lineNumbers)
    

parser = argparse.ArgumentParser(
    prog = "toad",
    description = "Parse TODO patterns inside a given file and store in a separated file.",
    formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=10)
)

parser.add_argument("-i", "--input-file",
                    help="Specifies input file for parsering TODOS")

# TODO: Remove -i argument and get file as positional argument

args = parser.parse_args()

inputFile = args.input_file

matches = searchPatternInFile(inputFile, "todos:")

(bodies, lineNumbers) = splitMatchesByRegex(matches)

todos = formatBody(bodies, lineNumbers)

file = open("todos.md", "w", encoding="utf-8")
for todo in todos:
    file.write("🞄 " + todo)
    file.write("---")
    file.write('\n')
file.close()

