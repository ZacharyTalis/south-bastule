import os, subprocess, string, sys, time, webvtt, youtubesearchpython

# Global paths
runPath = sys.path[0]
tempPath = f"{runPath}/temp"
resourcesPath = f"{runPath}/resources"
scriptPath = f"{resourcesPath}/text/script"
currentScriptPath = scriptPath

# Global ints
resultsLimit = 4
searchLimit = 2
maxOptionsAvailable = 2

def intro():
    clearTerminal()
    print("=== The Pride of South Bastule ===\n~~ A microgame by Zachary Talis ~~\n")
    input("Press ENTER to continue.")
    clearTerminal()

def clearTerminal():
    os.system('cls||clear')

def makeStringGenericList(inputString):
    return inputString.translate(str.maketrans('', '', string.punctuation)).lower().split()

def getSearchResults(searchText):
    return youtubesearchpython.VideosSearch(searchText, limit = resultsLimit).result()

def getTrimmedHeaderInDir(dir, uniqueWords):
    headerText = ""
    with open(f"{dir}/header.script") as header:
        contents = header.read()
    contents = makeStringGenericList(contents)
    for word in contents:
        if word in uniqueWords:
            headerText += f"{word} "
    return headerText[:-1]

def getPrompt():
    with open(f"{currentScriptPath}/prompt.script") as prompt:
        return prompt.read()

def getNewUniqueWords(currentUniqueWords, searchResults):
    newUniqueWords = currentUniqueWords
    priorPath = sys.path[0]
    os.chdir(tempPath)
    for result in searchResults["result"]:
        id = result["id"]
        subprocess.call(["youtube-dl", "--write-sub", "--write-auto-sub", "--skip-download", "--sub-format", "vtt", "--sub-lang", "en", f"https://www.youtube.com/watch?v={id}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for filename in os.scandir(tempPath):
        fullPath = filename.path
        if (filename.is_file() and not ".gitinclude" in fullPath):
            for caption in webvtt.read(fullPath):
                newWords = makeStringGenericList(caption.text)
                for word in newWords:
                    if word not in newUniqueWords:
                        newUniqueWords.append(word)
            os.remove(fullPath)
    os.chdir(priorPath)
    return newUniqueWords

def getOptions(uniqueWords):
    dirsInCurrentScriptPath = []
    options = []
    for filename in os.scandir(currentScriptPath):
        if filename.is_dir():
            dirsInCurrentScriptPath.append(filename.path)
    for dir in dirsInCurrentScriptPath:
        options.append([dir, getTrimmedHeaderInDir(dir, uniqueWords)])
    return options

def pruneOptions(allOptions, maxOptionCount):
    allOptions = sorted(allOptions, key=lambda x:len(x[1]), reverse=True)
    if len(allOptions) < maxOptionCount:
        return allOptions
    else:
        return allOptions[:maxOptionCount]

def printPrompt(prompt):
    print(f"{prompt}\n")

def printOptions(options):
    i = 1
    for option in options:
        print(f"{i} ~ {option[1]}")
        i += 1
    print()

def printBody():
    with open(f"{currentScriptPath}/body.script") as body:
        bodyText = body.read()
    print(f"{bodyText}\n")
    return ("FIN" in bodyText)

def searchLoop(prompt):
    uniqueWords = []
    searchesLeft = searchLimit
    allOptions = getOptions([])
    prunedOptions = pruneOptions(allOptions, maxOptionsAvailable)
    printPrompt(prompt)
    while (searchesLeft > 0):

        # Search for YT videos based on user input
        searchText = ""
        while (searchText == ""):
            searchText = input(f"({searchesLeft}):  "); print()
        clearTerminal()
        printPrompt(prompt)
        printOptions(prunedOptions)
        print("...")
        searchResults = getSearchResults(searchText)

        # Get and print options
        allOptions = getOptions(getNewUniqueWords(uniqueWords, searchResults))
        clearTerminal()
        prunedOptions = pruneOptions(allOptions, maxOptionsAvailable)
        printPrompt(prompt)
        printOptions(prunedOptions)

        # One less search left
        searchesLeft -= 1
    return prunedOptions

def chooseOption(options):
    while (True):
        try:
            choice = int(input("#:  "))
            if (choice > 0 and choice < len(options) + 1):
                return options[choice-1]
            print("Invalid choice!")
        except:
            print("Invalid choice!")

def getExplosionString(length):
    explosionString = ""
    while (len(explosionString) < length):
        explosionString += "* < * > "
    return explosionString

def optionTransition(chosenOption):
    global currentScriptPath
    currentScriptPath = chosenOption[0]
    with open(f"{currentScriptPath}/header.script") as header:
        contents = header.read()

    clearTerminal()
    print(chosenOption[1])
    time.sleep(1)
    clearTerminal()
    print(getExplosionString(len(chosenOption[1])))
    time.sleep(0.25)
    clearTerminal()
    print(f"{contents}\n")
    time.sleep(0.5)

def gameplayLoop():
    if (not printBody()):
        prompt = getPrompt()
        chosenOption = chooseOption(searchLoop(prompt))
        optionTransition(chosenOption)
        return False
    else:
        return True

intro()
hasEnded = False
while (not hasEnded):
    hasEnded = gameplayLoop()