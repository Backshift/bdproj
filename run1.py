import os

if __name__ == '__main__':
    file_path = os.path.dirname(os.path.realpath(__file__))
    file_path += "\\Code\\"
    print("Available programs:")
    i=1
    programs = list()
    for file in os.listdir(file_path):
        if file[(len(file)-3):len(file)] == ".py":
            print(str(i)+")", file)
            programs.append(file_path+file)
            i+=1

    while True:
        inp = input("Choose which program to run\n")
        try:
            inp = int(inp)
            if inp >= len(os.listdir(file_path)):
                continue
            break
        except:
            continue

    exec(open(programs[inp-1]).read())
