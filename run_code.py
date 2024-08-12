import os
import subprocess

def run_codes(code, record, i=0):

    commands = os.listdir('benchmarks')
    id = record.get_id() + i

    if record.get_phase() == 0:
        func = 'bump variables'
    elif record.get_phase() == 1:
        func = 'restart'
    elif record.get_phase() == 2:
        func = 'rephase'

    # List of commands to run sequentially
    for i in range(len(commands)):
        commands[i] = 'easysat/EasySAT benchmarks/' + commands[i]

    # Remove leading newline characters
    code = str.lstrip(code)

    with open("easysat/EasySAT.cpp", "r") as file:
        lines = file.readlines()
        
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
    print(result)
    os.chdir('../')
    print(commands)

    with open('log/run_code/{id}_run.log'.format(id=id), "w") as file:
        file.write("Compilation: \n" + str(result))

    solved_times = []
    if result.stderr == '':
        # Run benchmarks
        for cmd in commands:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            print(result)
            solved_times.append(float(result.stdout))
            with open('log/run_code/{id}_run.log'.format(id=id), "a") as file:
                file.write("\nRun bench: \n" + str(result))
            
            # Calculate the PAR-2 Score
            for time in solved_times:
                if time > 1499:
                    time = 3000
            
            # Append the final PAR-2 Score to the metrics list
            metric = (sum(solved_times) / len(solved_times))
    else:
        metric = 0 # If the code fails to compile, return a PAR-2 Score of 0, which indicates a failure
    
    with open('log/run_code/{id}_run.log'.format(id=id), "a") as file:
        file.write("\nMetric: \n" + str(metric) + "\n" + str(solved_times))

    return metric