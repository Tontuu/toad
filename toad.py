# TODO: Argument to delete all TODOS patterns in the given file

import argparse, re

helpMessage = """\
\033[1;31mUsage\033[0m: toad [OPTION...] file

Parse TODO patterns in a file

\033[1;31mOptions\033[0m:
  -h, --help                   Show this help message and exit

  -t, --target                 Specifies target pattern
  -o, --output-file            Specifies the output file
  --summary                    Specifies custom summary
  --bullet                     Specifies custom bullet list symbol

  -l, --no-line                Does not show line number that pattern was matched, default is true
  -m, --no-markdown, --no-md   Does not show markdown separator symbol in output MD file

  -s, --no-sort                Enumerate todos in the pattern order found accordingly to accordingly to specified order patterns
  -q, --quiet, --silent        Do not write todos to standard output
  -d, --delete                 Delete all todos patterns in the file
"""

def makeArgs():
    class MyArgumentParser(argparse.ArgumentParser):
        def format_help(self):
            return helpMessage

    parser = MyArgumentParser()

    parser.add_argument("-o", "--output-file", type=argparse.FileType('w'))
    parser.add_argument("-q", "--quiet", "--silent",      action="store_true")
    parser.add_argument("-m", "--no-markdown", "--no-md", action="store_false")
    parser.add_argument("-s", "--no-sort",                action="store_false")
    parser.add_argument("-l", "--no-line",                action="store_false")
    parser.add_argument("-t", "--target")
    parser.add_argument("--summary")
    parser.add_argument("--bullet")
    parser.add_argument("file", type=argparse.FileType('r'))

    args = parser.parse_args();

    if len(args.bullet) > 1:
        print("toad: error: bullet symbol must have only 1 character: " + args.bullet)
        return None

    return args

def grepTodos(file, target):
    target = target if target else "todo"
    todos = []
    positionalTodos = []

    with open(file.name) as f:
        for i, line in enumerate(f):
            if target in line.lower():
                (match, number) = parseMatch(line, target)

                todo = {"body": line.strip(), "lineNumber": i+1}

                if number:
                    positionalTodos.append([todo, number])
                else:
                    todos.append(todo)

    return todos, positionalTodos

def parseMatch(line, target):
    todoFormatRegex = re.compile("{}[^ \n]*:".format(target), re.IGNORECASE)
    numberSurroundedRegex = re.compile("\((\d*)\)|\[(\d*)\]|\((\d*)\)|{(\d*)}")

    match = re.findall(todoFormatRegex, line)[0]
    number = re.findall(r"\d+", match)

    if number: return match, number[0]

    return match, None
    
def sortTodos(todos, positionalTodos):
    for todo in positionalTodos:
        todos.insert(int(todo[1])-1, todo[0])

    return todos

def formatTodos(todos, isSortActive, isLineNumberActive, summary, bulletSymbol):
    # User futurally choice.
    summary = summary if summary else "TODO"
    bulletSymbol = bulletSymbol if bulletSymbol else "•"
    spaceToFill = " " * len(bulletSymbol)

    newTodos = []

    for i, todo in enumerate(todos):
        lineNumber = todo["lineNumber"]
        body = todo["body"].split(":")[1].strip()

        dict = {}

        if isSortActive:
            dict["str"] = "{} {}[{}]: {}".format(bulletSymbol, summary, i+1, body)
        else:
            dict["str"] = "{} {}: {}".format(bulletSymbol, summary, body)

            
        if isLineNumberActive:
            dict["lineNumber"] = " {}({})".format(spaceToFill, lineNumber)

        newTodos.append(dict)

    return newTodos

def echoTodos(todos):
    # Get biggest string length to format as box
    biggestLength = 0
    for todo in todos:
         if (len(todo["str"]) > biggestLength):
             biggestLength = len(todo["str"])

    separator = '-' * (biggestLength+2)

    print(separator)
    for todo in todos:
        emptySpace = ' ' * (len(separator) - len(todo["str"]))

        print(todo["str"] + emptySpace + '|')
        
        emptySpace = ' ' * (len(separator) - 7)

        if "lineNumber" in todo:
            print(todo["lineNumber"] + emptySpace + '|')

        print(separator)


def writeTodos(todos, file, markdown, isLineNumberActive):
    for todo in todos:
        file.write(todo["str"])
        file.write('\n')

        if "lineNumber" in todo:
            file.write(todo["lineNumber"])
            file.write('\n')

        if markdown:
            if file.name.endswith('.md'):
                file.write("---")
                file.write('\n')

        if todo != todos[-1]:
            file.write('\n')

    file.close()

def printMatches(count, target):
    target = target if target else "todo"

    print("Found \033[1;31m{}\033[0m matches for \033[1;31m{}\033[0m".format(count, target))
    if count == 0:
        exit(1)

# Change argparser help to script help message
args = makeArgs()

if not args:
    print(helpMessage)
    exit(1)

todos, positionalTodos  = grepTodos(args.file, args.target)

if positionalTodos:
    todos = sortTodos(todos, positionalTodos)

todos = formatTodos(todos, args.no_sort, args.no_line, args.summary, args.bullet)

printMatches(len(todos), args.target)

if not args.quiet:
    echoTodos(todos)

if args.output_file:
    writeTodos(todos, args.output_file, args.no_markdown, args.no_line)

exit(0)
