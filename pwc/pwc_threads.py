import os, sys
from multiprocessing import Array
from threading import Thread


# --- Check Arguments Function --- #

def check_arguments(arguments):
    """
    Checks the arguments passed to the command pwc to see if any -p option was been passed
    Requires: arguments list
    Return: Boolean, if the number of processes was been passed returns True, else returns False
    """
    check_var = True

    try:
        if len(arguments) == 0:
            raise TypeError("Missing arguments")

        for index in range(len(arguments)):
            if arguments[index] == "-p":
                if int(arguments[index+1]) < 0:
                    raise TypeError("Cannot create negative number of processes")

    except ValueError:
        print("Cannot create processes: Enter a integer representing the number of processes to be created")
        check_var = False

    return check_var


# --- Read and Write Processes Function --- #

def read_write_processes(arguments, file_list):
    """
    Reads the arguments passed to the command pwc and writes in the stdout
    the result of the line command passed by the user
    Requires: arguments list, file_list .txt, total Array
    """
    number_process = 1
    number_file = len(file_list)
    number_args = 0

                                                           # checks if the arguments passed are correct
    if len(arguments) == 0:
         raise ValueError("Missing option arguments: Please pass at least 1 option [-c|-w|-l [-L]] [-p n]")
    
    elif '-p' in arguments and len(arguments) == 2:
        if ('-w' not in arguments or '-c' not in arguments or '-l' not in arguments):
            raise ValueError("No arguments have been passed, except the number of processes to be created")

    elif '-l' in arguments and '-L' in arguments:
        if '-p' not in arguments:
            if len(arguments) >= 3:
                raise ValueError("Too many arguments have been passed", len(arguments))
        else:
             if len(arguments) >= 5:
                raise ValueError("Too many arguments have been passed", len(arguments))

    elif '-l' in arguments and '-L' not in arguments:
        if '-p' not in arguments:
            if len(arguments) >= 2:
                raise ValueError("Too many arguments have been passed", len(arguments))
        else:
             if len(arguments) >= 4:
                raise ValueError("Too many arguments have been passed", len(arguments))

    elif '-l' not in arguments and '-L' in arguments:
        raise ValueError("-L argument cannot be passed, expected -l argument before")

    else:
        if '-p' not in arguments:
            if ('-w' not in arguments or '-c' not in arguments or '-l' not in arguments) and len(arguments) > 1:
                raise ValueError("Passed the number of processes but didn't pass the -p option")

        elif '-p' in arguments and len(arguments) >= 4:
            raise ValueError("Too many arguments have been passed", len(arguments))

    for arg in arguments:
        number_args += 1
        if arg == "-p":
            try:
                arguments.remove(arguments[arguments.index("-p")+1])
            except IndexError:
                pass
            arguments.remove("-p")
            number_args -= 1
    args_str = ""

    for arg in arguments:                                  # creates the arguments line to be passed to the wc
        args_str += str(arg) + " "

    for i in range (len(file_list)):
        args_str += file_list[i] + " "
    terminal_command = "wc " + args_str

    os.system(terminal_command)                            # passes the wc command line to the shell and runs it

    shell_line = os.popen(terminal_command)
    shell_line_str = shell_line.read()
    cmd_str = " ".join(shell_line_str.split())
    cmd_list = cmd_str.split(" ")                          # list containing the results of each wc command for each file, including the total of the files for each process created

    removingAfter = []                                     # this list corresponds to the elements that are going to be removed afterwards to only have the values to become total in the cmd_list
    for n in range(len(cmd_list)):                         # removes the .txt files from the list
        if cmd_list[n].endswith(".txt") or cmd_list[n] == "total":
            removingAfter.append(cmd_list[n])

    for n in removingAfter:                                # removing those values
        for x in cmd_list:
            if n == x:
                cmd_list.remove(x)

    cmd_list = list(map(int, cmd_list))                    # converts all the values inside the list to integers

    if int(number_process) < int(number_file):             # makes the calculations to make sure the total presented in the end is correct
        if number_file == 1:
            if number_args > 1:
                for number in range(len(cmd_list)):
                    division = number%2
                    if division == 0:
                        total[0] += cmd_list[number]
                    else:
                        if total[1] > cmd_list[number]:
                            continue
                        else:
                            total[1] = cmd_list[number]
        else:
            if number_args > 1:
                total[0] += cmd_list.pop(-2)
                result_number = cmd_list.pop(-1)

                if total[1] > result_number:
                    pass
                else:
                    total[1] = result_number
            else:
                cmd_list.pop(-1)
                for number in cmd_list:
                    total[0] += number

    elif int(number_process) == int(number_file):
        if number_args > 1:
            for number in range(len(cmd_list)):
                division = number%2
                if division == 0:
                    total[0] += cmd_list[number]
                else:
                    if total[1] > cmd_list[number]:
                        continue
                    else:
                        total[1] = cmd_list[number]
        else:
            for number in cmd_list:
                total[0] += number


def process_distribution(number_processes, file_list):
    """
    Gives the number of files that each process is going to read
    Represented by an array in wich the number of positions are
    the number of processes and the index represents how many files
    each process is going to read
    """
    number_files_perProcess_list = []
    number_files = len(file_list)
    number_Files_perProcess_int = number_files // number_processes
    number_Files_perProcess_test = number_files % number_processes

    if number_Files_perProcess_test == 0:
        for number in range(number_processes):
            number_files_perProcess_list.append(number_Files_perProcess_int)
    else:
        for number in range(number_processes):
            number_files_perProcess_list.append(number_Files_perProcess_int)
        if sum(number_files_perProcess_list) < number_files:
            for number in range (number_files - sum(number_files_perProcess_list)):
                number_files_perProcess_list[number] += 1

    return number_files_perProcess_list



# --- Main --- #

if __name__ == "__main__":                                 # variables are declared
    arguments = sys.argv[1:]
    args_passed = []
    list_files = []
    list_arguments = []
    number_processes = 1
    number_files = 0
    total = Array("i", 2)
    total_str = ""
    initialIndex = 0
    check_variable = check_arguments(arguments)

    if check_variable == False:
        raise ValueError("Error receiving the number of processes")

    for arg in arguments:                                  # adds the .txt files to the list_files                         
        if arg.endswith('.txt'):
            list_files.append(arg)
            number_files += 1

    if len(list_files) == 0:                               # checks if the files are going to be read from the stdin
        list_files = sys.stdin.readline().split(" ")
        number_files = len(list_files)
        args_passed = arguments
    else:
        args_passed = arguments[:-(number_files)]

    try:
        for arg in arguments:
            if arg == "-p":
                number_processes = int(arguments[arguments.index("-p")+1])

        if number_processes > number_files:
            number_processes = number_files

    except ValueError:
        pass

    processDistribution = process_distribution(number_processes, list_files) # calculates the distribuition of processes per file/s

    if number_processes == number_files:                   # depending on the number of files and processes, creates and starts them
        for index_process in range (number_files):
            process_child = Thread(target = read_write_processes, args = (args_passed, list_files[initialIndex : index_process + 1],))
            list_arguments.append(process_child)
            process_child.start()
            initialIndex = index_process + 1
    elif number_processes == 1:
        read_write_processes(args_passed, list_files)
    else:
        for index_process in range (number_processes):
            process_child = Thread(target = read_write_processes, args = (args_passed, list_files[initialIndex : initialIndex + processDistribution[index_process]],))
            list_arguments.append(process_child)
            process_child.start()
            initialIndex += processDistribution[index_process]

    for process in list_arguments:                         # processes are joined
        process.join()

    for number in total:                                   # prints the final total
        if number == 0:
            continue
        else:
            total_str += str(number) + ' '

    total_str += 'total'

    if total_str == 'total':
        pass
    else:
        print(total_str)
