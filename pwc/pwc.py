import os, sys, pickle, time, signal
from itertools import islice
from multiprocessing import Process, Array, Value, Semaphore


# --- Check Arguments Function --- #

def checkArguments(arguments):
    """
    Checks the arguments passed to the command pwc to see if any -p option was been passed

    Requires: arguments - list of strings
    Return: Boolean, if the number of processes was been passed returns True, else returns False
    """
    '''
    Errors...

    except ValueError as error:
        print('Caught this error: ' + repr(error))
        sys.exit()
    '''

    pass

# --- Write Function --- #

def writeBinary(file_name, start, end):

    with open(file_name, "r") as file:
        string = ""

        for line in islice(file, start, end):
            string += " " + line

    with open("file.bin", "w+b") as output_file:

        pickle.dump(string, output_file)


# --- Count Functions --- #

def linesCountingAux(file_name, nProcesses):
    """
    Counts the lines of a file as a support for other count functions
    """

    linesPerProcessesList = []

    with open(file_name, "r") as file:
        lineCounting = 0

        for line in file:
            lineCounting += 1 #discover the lines in the text file

    linesPerProcesses = lineCounting // nProcesses

    for number in range(nProcesses):
        linesPerProcessesList.append(linesPerProcesses)
    if sum(linesPerProcessesList) < lineCounting:
        for number in range (lineCounting - sum(linesPerProcessesList)):
            linesPerProcessesList[number] += 1

    return linesPerProcessesList

def countLines(file_name, start, end):
    """
    Counts the lines of the .txt file given

    Requires: file_name - .txt file
    Ensures: returns the number of lines in the file
    """
    with open(file_name, "r") as file:
        counter_lines = 0

        for line in islice(file, start, end):
            counter_lines += 1

    return counter_lines

def biggestLine(file_name, start, end):
    """
    Counts the length of the longest line in the .txt file given

    Requires: file_name - .txt file
    Ensures: returns the number of the biggest line in the file
    """
    with open(file_name, "r") as file:
        bg_line = 0

        bg_line = len(file.readline())

        for line in islice(file, start, end):

            if bg_line < len(line):
                bg_line = len(line)

    return bg_line

def countWords(file_name, start, end):
    """
    Counts the words of the .txt file given

    Requires: file_name - .txt file
    Ensures: returns the number of words in the file
    """
    with open(file_name, "r") as file:
        counter_words = 0

        for line in islice(file, start, end):
            res = len(line.split())
            counter_words += res

    return counter_words

def countCharacters(file_name, start, end):
    """
    Counts the characters of the .txt file given

    Requires: file_name - .txt file
    Ensures: returns the number of chars in the file
    """
    with open(file_name, "r") as file:
        counter_chars = 0

        for line in islice(file, start, end):
            counter_chars += len(line)

    return counter_chars

# --- Create Processes Function --- #

sem = Semaphore(1)                              # Semaphore to help synch
def createProcesses(arguments, file_list, start, end):
    """
    Reads the arguments passed to the command pwc and writes in the stdout
    the result of the line command passed by the user

    Requires: arguments - list, file_list - list of .txt files
    Ensures:
    """
    NUM_PROCESS = 1                              # Check variables
    NUM_FILE = len(file_list)
    NUM_ARGS = len(arguments)

    sem.acquire()
    processNumber.value += 1
    sem.release()

    for file in file_list:
        result_list = []                         # List that keeps all the results for each file
        PSTRING = ""                             # String that will be printed with the result of each read file

        if "-w" in arguments:
            if nProcessesBiggerThanFiles:
                result_list.append(str(countWords(file, start, end)))
            else:
                result_list.append(str(countWords(file, None, None)))

        elif "-l" in arguments:
            if nProcessesBiggerThanFiles:
                result_list.append(str(countLines(file, start, end)))
            else:
                result_list.append(str(countLines(file, None, None)))

            if "-L" in arguments:
                if nProcessesBiggerThanFiles:
                    result_list.append(str(biggestLine(file, start, end)))
                else:
                    result_list.append(str(biggestLine(file, None, None)))

        elif "-c" in arguments:
            if nProcessesBiggerThanFiles:
                result_list.append(str(countCharacters(file, start, end)))
            else:
                result_list.append(str(countCharacters(file, None, None)))

        if int(NUM_PROCESS) < int(NUM_FILE):
            if NUM_FILE == 1:
                 if NUM_ARGS > 1:
                     for number in range(len(result_list)):
                        division = int(number) % 2

                        if division == 0:
                            total[0] += int(result_list[number])
                        else:
                            if total[1] > int(result_list[number]):
                                continue
                            else:
                                total[1] = int(result_list[number])

            else:
                if NUM_ARGS > 1:
                    total[0] += int(result_list[-2])
                    result_number = int(result_list[-1])

                    if total[1] > int(result_number):
                        pass
                    else:
                        total[1] = int(result_number)

                else:
                    total[0] += int(result_list[-1])

        elif int(NUM_PROCESS) == int(NUM_FILE):
            if NUM_ARGS > 1:
                for number in range(len(result_list)):
                    division = int(number) % 2

                    if division == 0:
                        total[0] += int(result_list[number])
                    else:
                        if total[1] > int(result_list[number]):
                            continue
                        else:
                            total[1] = int(result_list[number])

            else:
                for number in result_list:
                    total[0] += int(number)

        for number in result_list:
            PSTRING += str(number) + " "

        PSTRING += file

        print(PSTRING)
        #sys.exit()


def controlC(sig, NULL):
    print("\nCarregou no ctrl+c e terminou a execução do programa")
    #print("Resultados correntes:")
    sys.exit()

# --- Process Distribution Function --- #

def processDistribution(number_processes, file_list):
    """
    Gives the number of files that each process is going to read
    represented by an array in which the number of positions are
    the number of processes and the index represents how many files
    each process is going to read

    Requires: number_processes - int, file_list - list of .txt files
    Ensures: returns a list with the distribution of the number of files
    to read per process
    """
    num_proc_list = []                           # list with the distribution for each process

    NUM_FILES = len(file_list)                   # check variables
    NUM_PROC_INT = NUM_FILES // number_processes
    NUM_PROC_TEST = NUM_FILES % number_processes
    number_Processes_perFile_int = number_processes // NUM_FILES

    if number_processes <= NUM_FILES:
        if NUM_PROC_TEST == 0:
            for number in range(number_processes):
                num_proc_list.append(NUM_PROC_INT)
        else:
            for number in range(number_processes):
                num_proc_list.append(NUM_PROC_INT)

            if sum(num_proc_list) < NUM_FILES:
                for number in range (NUM_FILES - sum(num_proc_list)):
                    num_proc_list[number] += 1
    else:
        for number in range(NUM_FILES):
            num_proc_list.append(number_Processes_perFile_int)
        if sum(num_proc_list) < number_processes:
            for number in range (number_processes - sum(num_proc_list)):
                num_proc_list[number] += 1

    return num_proc_list


# --- Main --- #

if __name__ == "__main__":                       # Variables are declared in "__main__"
    arguments = sys.argv[1:]                     # list with the arguments passed in the terminal
    args_list = []
    list_processes = []
    list_files = []
    total = Array("i", 2)                       # Shared memory variable
    processNumber = Value("i", 1)               # Shared memory variable
    nProcessesBiggerThanFiles = bool(Value("i", True).value)   #Shared memory variable
    NUM_FILES = 0                                # Check variables
    NUM_PROCESSES = 1
    INITIAL_INDEX = 0
    INITIAL_INDEX_LINES = 0
    iterate = 0
    SIGNAL_TEMP = 0
    FILE_HISTORY = ""

    TOTAL_STR = ""                               # Variable with the final resultS

    signal.signal(signal.SIGINT, controlC)

    for arg in arguments:                        # Adds the .txt files to the list_files
        if arg.endswith('.txt'):
            list_files.append(arg)
            NUM_FILES += 1

    if len(list_files) == 0:                     # Checks if the files are going to be read from the stdin
        list_files = sys.stdin.readline().split(" ")

        try:
            if "\n" not in list_files:
                NUM_FILES = len(list_files)

            else:
                raise IOError("Error receiving the files")

        except IOError as error:
            print('Caught this error: ' + repr(error))
            sys.exit()

    for arg in arguments:                        # Gathers
        if arg == "-w":
            args_list.append(arg)

        elif arg == "-c":
            args_list.append(arg)

        elif arg == "-l":
            args_list.append(arg)

        if arg == "-L":
            args_list.append(arg)

        if arg == "-p":
            NUM_PROCESSES = int(arguments[arguments.index("-p")+1])

        if arg == "-a":
            SIGNAL_TEMP = int(arguments[arguments.index("-a")+1])

        if arg == "-f":
            FILE_HISTORY = arguments[arguments.index("-f")+1]

    checkArguments(args_list)                    # verify if the arguments passed meet the requirements

    process_distributionAux = processDistribution(NUM_PROCESSES, list_files)   # calculates the distribuition of processes per file/s
    process_distribution = Array("i", len(process_distributionAux))            # creates an Array for shared memory to use in the read of the amount of lines necessary
    for n in range(len(process_distributionAux)):
        process_distribution[n] = process_distributionAux[n]

    if NUM_PROCESSES > NUM_FILES:
        nProcessesBiggerThanFiles = True
        while True:
            time.sleep(2)
            for index_process in range (process_distribution[INITIAL_INDEX]):
                fileLines = linesCountingAux(list_files[INITIAL_INDEX], process_distribution[INITIAL_INDEX])
                process_child = Process(target = createProcesses, args = (args_list, list_files[INITIAL_INDEX : INITIAL_INDEX + 1], INITIAL_INDEX_LINES, fileLines[iterate]))
                list_processes.append(process_child)
                process_child.start()
                INITIAL_INDEX_LINES += fileLines[iterate]
                iterate += 1
                if processNumber.value == process_distribution[INITIAL_INDEX]:
                    processNumber.value = 0
                    INITIAL_INDEX_LINES = 0
                    iterate = 0
                    INITIAL_INDEX += 1
            if INITIAL_INDEX == len(process_distribution):
                break


    elif NUM_PROCESSES == NUM_FILES:               # depending on the number of files and processes, creates and starts them
        nProcessesBiggerThanFiles = False
        #time.sleep(2)
        for index_process in range (NUM_FILES):
            process_child = Process(target = createProcesses, args = (args_list, list_files[INITIAL_INDEX : index_process + 1], None, None,))
            list_processes.append(process_child)
            time.sleep(2)
            process_child.start()

            INITIAL_INDEX = index_process + 1

    elif NUM_PROCESSES == 1:
        nProcessesBiggerThanFiles = False
        time.sleep(2)
        createProcesses(args_list, list_files, None, None)

    else:
        nProcessesBiggerThanFiles = False
        time.sleep(2)
        for index_process in range (NUM_PROCESSES):
            process_child = Process(target = createProcesses, args = (args_list, list_files[INITIAL_INDEX : INITIAL_INDEX + process_distribution[index_process]], None, None,))
            list_processes.append(process_child)

            process_child.start()

            INITIAL_INDEX = process_distribution[index_process]

    for process in list_processes:               # processes are joined
        process.join()

    for number in total:                         # prints the final total
        if number == 0:
            continue
        else:
            TOTAL_STR += str(number) + ' '

    TOTAL_STR += 'total'

    if TOTAL_STR == 'total':
        pass
    else:
        print(TOTAL_STR)
