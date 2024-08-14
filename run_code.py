import os
import subprocess

def run_codes(code, record, i=0):

    # Parameter for logging
    id = record.get_id() + i

    # Get names of every file in benchmarks/ directory
    commands = os.listdir('benchmarks')

    # Set Phase
    if record.get_phase() == 0:
        func = 'bump variables'
    elif record.get_phase() == 1:
        func = 'restart'
    elif record.get_phase() == 2:
        func = 'rephase'

    # Set a list of commands to run sequentially
    for i in range(len(commands)):
        commands[i] = 'easysat/EasySAT benchmarks/' + commands[i]

    # Remove leading newline characters
    code = str.lstrip(code)

    with open("easysat/EasySAT.cpp", "r") as file:
        lines = file.readlines()

    # Modifying EasySAT.cpp
    # Three target functions (bump_var, restart, rephase) are identified by comments, as shown by an example below
    # // start bump variables function
    # codes...
    # // end bump variables function
    # Use this structure to identify where to start and end modification
    with open("easysat/EasySAT.cpp", "w") as file:
        modifying = False
        for i in range(len(lines)):
            if "start {func}".format(func=func) in lines[i]:
                modifying = True
            elif "end {func}".format(func=func) in lines[i]:
                modifying = False
                file.write("{code}\n".format(code=code))
                continue
          
            if modifying:
                continue
            else:
                file.write(lines[i])

    # Compile the code
    os.chdir('easysat')
    result = subprocess.run('make', shell=True, capture_output=True, text=True)
    os.chdir('../')

    # Log Compilation results
    with open('log/run_code/{id}_run.log'.format(id=id), "w") as file:
        file.write("Compilation: \n" + str(result))

    # List storing solved times for each benchmark instance
    solved_times = []

    # If the compilation was successful, run each benchmarks to calculate PAR-2.
    if result.stderr == '':
        # Run benchmarks
        for cmd in commands:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            solved_times.append(float(result.stdout))

            # Log benchmark solving results
            with open('log/run_code/{id}_run.log'.format(id=id), "a") as file:
                file.write("\nRun bench: \n" + str(result))
            
            # Calculate the PAR-2 Score
            for i in range(len(solved_times)):
                if solved_times[i] > 1499:
                    solved_times[i] = 3000
            
            # Append the final PAR-2 Score to the metrics list
            metric = (sum(solved_times) / len(solved_times))
    
    # If compilation failed, return metric = 0 , which indicates an error
    else:
        metric = 0 # If the code fails to compile, return a PAR-2 Score of 0, which indicates a failure
    
    # Log execution results
    with open('log/run_code/{id}_run.log'.format(id=id), "a") as file:
        file.write("\nMetric: \n" + str(metric) + "\n" + str(solved_times))

    # return metric(Par-2):float
    return metric