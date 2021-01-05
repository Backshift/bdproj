def setup_pckges(packages):
    for package in packages:
        if isinstance(package, list):
            try:
                __import__(package[0])
                print("Successfully imported", package[0])
            except ModuleNotFoundError:
                import subprocess
                import sys
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package[1]])
        else:
            try:
                __import__(package)
                print("Successfully imported", package)
            except ModuleNotFoundError:
                print("except")
                import subprocess
                import sys
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])


if __name__ == "__main__":
    needed_packages = list()
    needed_packages.append('wheel')
    needed_packages.append('requests')
    needed_packages.append('urllib')
    needed_packages.append('ssl')
    needed_packages.append('json')
    needed_packages.append('re')
    needed_packages.append(['sqlite3', 'pysqlite'])
    needed_packages.append('concurrent.futures')
    needed_packages.append('multiprocessing')
    needed_packages.append('threading')
    needed_packages.append('joblib')
    needed_packages.append('os')
    needed_packages.append('math')
    needed_packages.append('datetime')
    needed_packages.append('time')
    needed_packages.append('numpy')
    needed_packages.append('pandas')
    needed_packages.append('plotly')
    needed_packages.append('dash')
    needed_packages.append(['progressbar', 'progessbar2'])

    setup_pckges(needed_packages)
