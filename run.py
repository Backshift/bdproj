import os

if __name__ == '__main__':
    file_path = os.path.dirname(os.path.realpath(__file__))
    file_path += "\\Code\\"

    for file in os.listdir(file_path):
        if file[(len(file)-3):len(file)] == ".py":
            exec(open(file_path+file).read())
