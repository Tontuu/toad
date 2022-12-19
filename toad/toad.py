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

  -l, --no-line                Does not show line number which pattern was matched, default is true
  -m, --no-markdown, --no-md   Does not show markdown separator symbol in output MD file

  -s, --no-sort                Enumerate todos in the pattern order found accordingly to specified order patterns
  -q, --quiet, --silent        Do not write todos to standard output
  -d, --delete                 Delete todos inside file, MAKE SURE your file doesn't contain inline todo comments
"""

def makeArgs():
    # Custom help message
    class MyArgumentParser(argparse.ArgumentParser):
        def format_help(self):
            return helpMessage

    parser = MyArgumentParser()

    parser.add_argument("-o", "--output-file", type=argparse.FileType('w'))
    parser.add_argument("-q", "--quiet", "--silent",      action="store_true")
    parser.add_argument("-m", "--no-markdown", "--no-md", action="store_false")
    parser.add_argument("-s", "--no-sort",                action="store_false")
    parser.add_argument("-l", "--no-line",                action="store_false")
    parser.add_argument("-d", "--delete")
    parser.add_argument("-t", "--target")
    parser.add_argument("--summary")
    parser.add_argument("--bullet")
    parser.add_argument("file", type=argparse.FileType('r'))

    args = parser.parse_args();

    if args.bullet and len(args.bullet) > 1:
        print("toad: error: bullet symbol must have only 1 character: " + args.bullet)
        return None

    return args

def parseMatch(line, target):
    todoFormatRegex = re.compile("{}[^ \n]*:".format(target), re.IGNORECASE)
    numberSurroundedRegex = re.compile("\((\d*)\)|\[(\d*)\]|\((\d*)\)|{(\d*)}")

    match = re.findall(todoFormatRegex, line)

    if not match:
        return None, None

    match = match[0]
    number = re.findall(r"\d+", match)

    if number: return match, int(number[0])

    return match, None

def grepTodos(file, target, isSortActive):
    target = target if target else "todo"
    todos = []
    positionalTodos = []

    with open(file.name) as f:
        for i, line in enumerate(f):
            if target in line.lower():
                number = 0
                if isSortActive:
                    (match, number) = parseMatch(line, target)
                else:
                    match = parseMatch(line, target)

                if not match: continue

                todo = {"body": line.strip(), "lineNumber": i+1}

                if number:
                    positionalTodos.append([todo, number])
                else:
                    todos.append(todo)

    if positionalTodos:
        return todos, positionalTodos
    else:
        return todos, None

def bubbleSort(positionalTodos):
    length = len(positionalTodos)
    for i in range(length, 1, -1):
        for j in range(0, i-1):
            x = positionalTodos[j][1]
            y = positionalTodos[j+1][1]
            if x > y:
                positionalTodos[j], positionalTodos[j+1] = \
                positionalTodos[j+1], positionalTodos[j]
            else:
                pass

    return positionalTodos
    
def sortTodos(todos, positionalTodos):
    positionalTodos = bubbleSort(positionalTodos)

    for todo in positionalTodos:
        todos.insert(todo[1]-1, todo[0])

    return todos

def formatTodos(todos, isSortActive=True, isLineNumberActive=True, isToFormatSummary=True, isToFormatNumber=True, summary=None, bulletSymbol=None):

    # User futurally choice.
    if isToFormatSummary is True:
        if summary is None: summary = "TODO"

    if bulletSymbol is None: bulletSymbol = "•"

    spaceToFill = " " * len(bulletSymbol)

    newTodos = []
    for i, todo in enumerate(todos):
        lineNumber = todo["lineNumber"]
        dict = {}


        if isToFormatSummary is False:
            body = todo["body"].strip()
            dict["str"] = "{}".format(body)
        else:
            body = todo["body"].split(":")[1].strip()

            if isSortActive:
                dict["str"] = "{} {}[{}]: {}".format(bulletSymbol, summary, i+1, body)
            else:
                dict["str"] = "{} {}: {}".format(bulletSymbol, summary, body)

        if isLineNumberActive:
            if isToFormatNumber is True:
                dict["lineNumber"] = " {}({})".format(spaceToFill, lineNumber)
            else:
                dict["lineNumber"] = lineNumber

        newTodos.append(dict)

    return newTodos

def printTodos(todos):
    # Get biggest string length to format as box
    biggestLength = 0
    for todo in todos:
         if (len(todo["str"]) > biggestLength):
             biggestLength = len(todo["str"])

    separator = '-' * (biggestLength+2)

    print(separator)
    for todo in todos:
        lineNumber = "{}".format(todo["lineNumber"])
        emptySpace = ' ' * (len(separator) - len(todo["str"]))

        print(todo["str"] + emptySpace + '|')

        if "lineNumber" in todo:
            emptySpace = ' ' * (len(separator) - len(lineNumber))
            print(lineNumber + emptySpace + '|')

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

    print("Found \033[1;31m{}\033[0m matches for \033[1;31m{}\033[0m"
          .format(count, target))

def deletePrompt(prompt):
    while "Invalid answer":
        reply=str(input(prompt + " [y/n]: ").lower().strip())
        if reply[:1] == 'y':
            return True
        if reply[:1] == 'n':
            return False

        print("Invalid answer")

def deleteTodos(file, target):
    isSortActive = False;
    isLineNumberActive = True
    isToFormatSummary = False
    isToFormatNumber = False

    todos = grepTodos(file, target, isSortActive)[0] # Index 0 because it's not sorted

    todos = formatTodos(todos, isSortActive, isLineNumberActive, isToFormatSummary, isToFormatNumber)

    printMatches(len(todos), target)
    printTodos(todos)

     # Double check
    isToDelete = deletePrompt("Are you sure you want to delete ALL todos in this file?")

    if isToDelete is False: exit(0)

    data = []
    with open(file.name, "r+") as f:
        for i, line in enumerate(f):
            isToDeleteLine = False;

            for todo in todos:
                if i+1 == todo["lineNumber"]:
                    isToDeleteLine = True
                    break;

            if isToDeleteLine is False: data.append(line)

        f.seek(0)

        for line in data:
            f.write(line)

        f.truncate()

    print("All matches has been deleted from file!")
    exit(0)
    
args = makeArgs()

if (args.delete):
    deleteTodos(args.file, args.delete)

if not args:
    print(helpMessage)
    exit(1)

todos = grepTodos(args.file, args.target, args.no_sort)

if not todos[0]: # If array is empty
    printMatches(len(todos[0]), args.target)
    exit(1)

if todos[1]: # If todos has positional arrays
    todos = sortTodos(todos[0], todos[1])
else:
    todos.pop()

isSortActive = args.no_sort; # Default is true
isLineNumberActive = args.no_line # Default is True
isToFormatSummary = True
isToFormatNumber = True

todos = formatTodos(todos, isSortActive, isLineNumberActive, isToFormatSummary, isToFormatNumber, args.summary, args.bullet)

printMatches(len(todos), args.target)

if not args.quiet:
    printTodos(todos)

if args.output_file:
    writeTodos(todos, args.output_file, args.no_markdown, args.no_line)

exit(0)