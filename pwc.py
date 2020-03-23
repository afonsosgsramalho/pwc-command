import os, sys, pickle, time, signal, datetime, struct

from itertools import islice
from multiprocessing import Process, Array, Value, Semaphore, Queue


# ----- SUPPORT FUNCTIONS ----- #

# --- Check Arguments Function --- #

def checkArguments(arguments):
    """
    Checks the arguments passed to the command pwc to verify if they obey
    the requirements
    """

    try:                                         # Checks the arguments
        if len(arguments) == 0:
            raise ValueError("Missing option arguments: Please pass at least 1 option [-c|-w|-l [-L]]")

        elif len(arguments) == 1:
            for arg in arguments:

                if arg.isdigit() == True:
                    raise ValueError(arg, "is not a valid option, please pass at least 1 option [-c|-w|-l [-L]]")
                else:
                    if not arg.startswith("-"):
                        raise ValueError(arg, "is not a valid option, please pass at least 1 option [-c|-w|-l [-L]]")

        elif '-p' in arguments and len(arguments) == 2:

            if ('-w' not in arguments or '-c' not in arguments or '-l' not in arguments):
                raise ValueError("No arguments have been passed, except the number of processes to be created")

        elif '-l' in arguments and '-L' in arguments:

            if '-p' not in arguments:

                if '-a' not in arguments and '-f' not in arguments:
                    if len(arguments) >= 3:
                        raise ValueError("Too many arguments have been passed")

                elif ('-a' in arguments or '-f' not in arguments) or ('-a' not in arguments or '-f' in arguments):
                    if len(arguments) >= 6:
                        raise ValueError("Too many arguments have been passed")

                else:
                    if len(arguments) >= 9:
                        raise ValueError("Too many arguments have been passed")

            else:
                if '-a' not in arguments and '-f' not in arguments:
                    if len(arguments) >= 5:
                        raise ValueError("Too many arguments have been passed")

                elif '-a' not in arguments or '-f' not in arguments:
                    if len(arguments) >= 8:
                        raise ValueError("Too many arguments have been passed")

                else:
                    if len(arguments) >= 11:
                        raise ValueError("Too many arguments have been passed")

        elif '-l' in arguments and '-L' not in arguments:

            if '-p' not in arguments:

                if '-a' not in arguments and '-f' not in arguments:
                    if len(arguments) >= 2:
                        raise ValueError("Too many arguments have been passed")

                elif ('-a' in arguments or '-f' not in arguments) or ('-a' not in arguments or '-f' in arguments):
                    if len(arguments) >= 4:
                        raise ValueError("Too many arguments have been passed")

                else:
                    if len(arguments) >= 6:
                        raise ValueError("Too many arguments have been passed")

            else:
                if '-a' not in arguments and '-f' not in arguments:
                    if len(arguments) >= 4:
                        raise ValueError("Too many arguments have been passed")

                elif ('-a' in arguments or '-f' not in arguments) or ('-a' not in arguments or '-f' in arguments):
                    if len(arguments) >= 7:
                        raise ValueError("Too many arguments have been passed")

                else:
                    if len(arguments) >= 10:
                        raise ValueError("Too many arguments have been passed")

        elif '-l' not in arguments and '-L' in arguments:
            raise ValueError("-L argument cannot be passed, expected -l argument to pass -L argument")

        else:
            if '-p' not in arguments:
                if ('-w' not in arguments or '-c' not in arguments or '-l' not in arguments) and len(arguments) > 1:
                    raise ValueError("Error receiving the options")

            elif '-p' in arguments and len(arguments) >= 9:
                raise ValueError("Too many arguments have been passed")

    except ValueError as error:                  # If any error is raised, prints it into the stout
        print('Caught this error: ' + repr(error))
        sys.exit()

# --- Write Function --- #

def writeBinary(file_name, date, duration, proc_file_list):
    '''
    Writes into a file the processes information
    and what they have processed in binary
    '''

    b_array = bytearray()

    string = 'Início da execução da pesquisa: ' + str(date) + '\n' \
            + 'Duração da execução: ' + str(duration)

    for proc in proc_file_list:
        for k, v in proc.items():
            string += '\nProcesso: ' + str(k) + '\n' \
                + '\tFicheiro: ' + str(v[0]) +'\n' \
                + '\t\tTempo de Pesquisa: ' + str(v[3]) + '\n' \
                + '\t\tDimensão do Ficheiro: ' + str(v[1]) + '\n' \
                + '\t\tNúmero de [' + str(v[2][0]) + ']: '+ str(v[2][1]) + '\n'

    str_bytes = bytes(string, 'utf-8')

    with open(file_name, "wb") as outFile:
        pickle.dump(struct.pack("I%ds" % (len(str_bytes),), len(str_bytes), str_bytes), outFile)

# --- Convert Function --- #

def convert_timedelta(duration):
    '''
    Converts a given duration to a date
    '''

    days, seconds = duration.days, duration.seconds

    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    microseconds = (seconds * 1000000)

    return hours, minutes, seconds, microseconds

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
    """
    NUM_PROCESS = 1                              # Check variables
    NUM_FILE = len(file_list)
    NUM_ARGS = len(arguments)

    proc_info = {}

    sem.acquire()
    processNumber.value += 1
    sem.release()

    for file in file_list:
        statinfo = os.stat(file)
        size = str(statinfo.st_size)
        proc_info.update({os.getpid():[file, size[:-1]]})

        result_list = []                         # List that keeps all the results for each file
        PSTRING = ""                             # String that will be printed with the result of each read file

        date_beg = datetime.datetime.now()

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

        if "-l" in arguments:
            proc_info[os.getpid()].append(["linhas", result_list[0]])
        elif "-c" in arguments:
            proc_info[os.getpid()].append(["caracteres", result_list[0]])
        elif "-w" in arguments:
            proc_info[os.getpid()].append(["palavras", result_list[0]])

        PSTRING += file
        print(PSTRING)

        date_end = datetime.datetime.now()
        duration = date_end - date_beg
        hours, minutes, seconds, microseconds = convert_timedelta(duration)
        time_str = str(hours) + ":" + str(minutes) + ":" + str(seconds) + ":" + str(microseconds)

        proc_info[os.getpid()].append(time_str)

        queue_proc.put(proc_info)

# --- SIGINT function --- #

def controlC(sig, NULL):
    '''
    Checks if the CTRL+C is pressed
    '''

    print("\nPressed CTRL+C - The execution of the program has finished")
    print("Current Results:")

    if total[1] == 0:
        print(str(total[0]) + " total")

    else:
        print(str(total[0]) + " " + str(total[1]) + " total")

    sys.exit()

# --- Alarm function --- #

def alarm(sig, NULL):
    '''
    If the -a option is passed, it creates an alarm with a given time duration
    '''

    timeAlarm = timeSinceStartInc.value

    print("\n--- Alarm ---")

    if total[1] == 0:
        print("--- " + str(total[0]) + " total ---")
        print("--- Already processed " + str(nFilesProcessed.value) + " files ---")
        print("--- Time elapsed since start of execution: " + str(timeSinceStart.value * 1000000) + " microseconds ---\n")

    else:
        print("--- " + str(total[0]) + " " + str(total[1]) + " total ---")
        print("--- Already processed " + str(nFilesProcessed.value) + " files ---")
        print("--- Time elapsed since start of execution: " + str(timeSinceStart.value * 1000000) + " microseconds ---\n")

    timeSinceStart.value += timeAlarm

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


# --- MAIN --- #

if __name__ == "__main__":                       # Variables are declared in "__main__"
    date_beginning = datetime.datetime.now()

    arguments = sys.argv[1:]                     # list with the arguments passed in the terminal
    args_list = []
    list_processes = []
    list_files = []
                                                 # Shared memory variables
    total = Array("i", 2)
    processNumber = Value("i", 1)
    nProcessesBiggerThanFiles = bool(Value("i", True).value)
    nFilesProcessed = Value("i", 0)
    timeSinceStart = Value("i", 0)
    timeSinceStartInc = Value("i", 0)

    NUM_FILES = 0                               # Check variables
    NUM_PROCESSES = 1
    INITIAL_INDEX = 0
    INITIAL_INDEX_LINES = 0
    initialTime = 0
    endTime = 0
    SIGNAL_TEMP = 0

    FILE_HISTORY = ""                            # -f option file name

    queue_proc = Queue()                         # Queue to store the info for each process

    list_infos = []

    TOTAL_STR = ""                               # Variable with the final resultS

    signal.signal(signal.SIGINT, controlC)

    for arg in arguments:
        if arg == "-f":
            FILE_HISTORY = arguments[arguments.index("-f") + 1]
            arguments.remove(arguments[arguments.index("-f") + 1])

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

    for arg in arguments:                        # Gathers the option arguments (-w or -c or -l [-L])
                                                 # Passes those arguments to the counting functions
        if arg == "-w":
            args_list.append(arg)

        elif arg == "-c":
            args_list.append(arg)

        elif arg == "-l":
            args_list.append(arg)

        if arg == "-L":
            args_list.append(arg)

        if arg == "-p":
            NUM_PROCESSES = int(arguments[arguments.index("-p") + 1])

        if arg == "-a":
            SIGNAL_TEMP = int(arguments[arguments.index("-a") + 1])
            signal.signal(signal.SIGALRM, alarm)
            signal.setitimer(signal.ITIMER_REAL, SIGNAL_TEMP, SIGNAL_TEMP)
            timeSinceStart.value = SIGNAL_TEMP
            timeSinceStartInc.value = SIGNAL_TEMP   # Increments in the alarm function

    checkArguments(args_list)                    # Verify if the arguments passed meet the requirements

    process_distributionAux = processDistribution(NUM_PROCESSES, list_files)   # Calculates the distribuition of processes per file/s
    process_distribution = Array("i", len(process_distributionAux))   # Creates an array for shared memory to use in the read of the amount of lines necessary

    for n in range(len(process_distributionAux)):
        process_distribution[n] = process_distributionAux[n]

    if NUM_PROCESSES > NUM_FILES:
        nProcessesBiggerThanFiles = True

        while True:
            time.sleep(2)

            for index_process in range (process_distribution[INITIAL_INDEX]):
                fileLines = linesCountingAux(list_files[INITIAL_INDEX], process_distribution[INITIAL_INDEX])
                process_child = Process(target = createProcesses, args = (args_list, list_files[INITIAL_INDEX : INITIAL_INDEX + 1], INITIAL_INDEX_LINES, fileLines[index_process] + INITIAL_INDEX_LINES))
                list_processes.append(process_child)
                process_child.start()

                INITIAL_INDEX_LINES += fileLines[index_process]
                if processNumber.value == process_distribution[INITIAL_INDEX]:
                    processNumber.value = 0
                    INITIAL_INDEX_LINES = 0
                    INITIAL_INDEX += 1
                    nFilesProcessed.value += 1

            if INITIAL_INDEX == len(process_distribution):
                break

    elif NUM_PROCESSES == NUM_FILES:             # Depending on the number of files and processes, creates and starts them
        nProcessesBiggerThanFiles = False

        for index_process in range (NUM_FILES):
            process_child = Process(target = createProcesses, args = (args_list, list_files[INITIAL_INDEX : index_process + 1], None, None,))
            list_processes.append(process_child)
            time.sleep(2)
            process_child.start()

            INITIAL_INDEX = index_process + 1
            nFilesProcessed.value += 1

    elif NUM_PROCESSES == 1:
        nProcessesBiggerThanFiles = False
        time.sleep(2)
        createProcesses(args_list, list_files, None, None)
        nFilesProcessed.value = 1

    else:
        nProcessesBiggerThanFiles = False

        for index_process in range (NUM_PROCESSES):
            time.sleep(2)
            process_child = Process(target = createProcesses, args = (args_list, list_files[INITIAL_INDEX : INITIAL_INDEX + process_distribution[index_process]], None, None,))
            list_processes.append(process_child)
            process_child.start()

            INITIAL_INDEX = process_distribution[index_process]
            nFilesProcessed.value += INITIAL_INDEX


    for process in list_processes:               # Processes are joined
        process.join()

    for i in range(queue_proc.qsize()):
        list_infos.append(queue_proc.get())

    for number in total:
        if number == 0:
            continue
        else:
            TOTAL_STR += str(number) + ' '

    TOTAL_STR += 'total'

    if TOTAL_STR == 'total':
        pass
    else:
        print(TOTAL_STR)                         # Prints the final total

    date_ending = datetime.datetime.now()
    duratn = date_ending - date_beginning
    hours, minutes, seconds, microseconds = convert_timedelta(duratn)
    duratn_str = str(hours) + ":" + str(minutes) + ":" + str(seconds) + ":" + str(microseconds)

    if not FILE_HISTORY == "":
        writeBinary(FILE_HISTORY, date_beginning, duratn_str, list_infos)   # Writes the processes info into the binary data file
