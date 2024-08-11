import os
import subprocess

def run_codes(codes):

    metrics = []
    commands = os.listdir('benchmarks')

    # List of commands to run sequentially
    for i in range(len(commands)):
        commands[i] = 'easysat/EasySAT benchmarks/' + commands[i]

    # modify EasySAT.cpp
    for code in codes:
        # Remove leading newline characters
        code = str.lstrip(code)

        with open("easysat/EasySAT.cpp", "r") as file:
            lines = file.readlines()
        
        with open("easysat/EasySAT.cpp", "w") as file:
            modifying = False
            for i in range(len(lines)):
                if "start bump variables" in lines[i]:
                    modifying = True
                elif "end bump variables" in lines[i]:
                    modifying = False
                    file.write("{code}\n".format(code=code))
                    continue
          
                if modifying:
                    continue
                else:
                    file.write(lines[i])

        try:
            # Compile the code
            os.chdir('easysat')
            result = subprocess.run('make', shell=True, capture_output=True, text=True)
            print(result)
            os.chdir('../')
            print(commands)

            solved_times = []
            # Run benchmarks
            for cmd in commands:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                print(result)
                solved_times.append(float(result.stdout))
            
            # Calculate the PAR-2 Score
            for time in solved_times:
                if time > 1499:
                    time = 3000
            
            # Append the final PAR-2 Score to the metrics list
            metrics.append(sum(solved_times) / len(solved_times))
        except:
            metrics.append(0) # If the code fails to compile, return a PAR-2 Score of 0, which indicates a failure
    
    return metrics