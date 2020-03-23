import os, pickle, sys, struct


# ----- FUNCTIONS ----- #

# --- Read File Function --- #

def hpwc(filename):
    """
    Reads a binary file and prints the content to the stout
    in utf-8 coding
    """

    with open(filename, 'rb') as inFile:
        str_ser = pickle.load(inFile)
        string = unpack_helper("I", str_ser)

        return(string[1].decode("utf-8"))

def unpack_helper(fmt, data):
    '''
    Helps the hpwc function by calculating the size of the binary
    to alocate the space needed by each data
    '''

    size = struct.calcsize(fmt)
    
    return struct.unpack(fmt, data[:size]), data[size:]

# ----- MAIN ----- #

if __name__ == "__main__":                       # Variables are declared in "__main__"
    file_lst = sys.argv[1:]

    print(hpwc(file_lst[0]))

