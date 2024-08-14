from run_code import *
from call_advisor import *
from call_coder import *
from call_evaluator import *
import random, heapq, argparse

# Set up the argument parser
parser = argparse.ArgumentParser()
parser.add_argument('--batch_size', help=' : Batch Size', type=int)
parser.add_argument('--ite_size', help=' : Iteration Size', type=int)
parser.add_argument('--mod_target', help=' : Modification Target Function. 0) bump_var 1) restart 2) rephase', type=int)
args = parser.parse_args()

class Record:
  def __init__(self, p):
    self.rec = []     # list of dictionaries. Each element (dict) contains 'code' (from coder), 'metric' (which is merely a PAR-2 score), and 'analysis' (from evaluator)
    self.hq = []      # MinHeap for maintaining/updating the index of the best code version (lowest PAR-2)
    self.phase = p    # Target Function for modification. 0) bump_var 1) restart 2) rephase
  
  def get_rec(self):
    return self.rec
  
  def get_id(self):
    return len(self.rec)

  def get_phase(self):
    return self.phase
  
  def get_index(self, id):
    return self.rec[id]

  def add_rec(self, code, metric, analysis):
    heapq.heappush(self.hq, (metric, len(self.rec)))
    self.rec.append({"code":code, "PAR-2 Score":metric, "Analysis":analysis})

  def set_phase(self, p):
    self.phase = p

  def get_best_index(self):
    return self.hq[0][1]
  
def main(args):
  # get arguments
  M = args.batch_size
  N = args.ite_size
  p = args.mod_target

  # Initialize the record
  record = Record(p)

  for i in range(N):

    # Getting advice from the advisor
    if i == 0:
      # Add baseline code to the record on the initial run of the iteration

      # Set phase
      if record.get_phase() == 0:
        current_task = "bump variables function"
        func = 'bump_variables'
      elif record.get_phase() == 1:
        current_task = "restart"
        func = 'restart'
      elif record.get_phase() == 2:
        current_task = "rephase"
        func = 'rephase'
      
      # Get target function code
      with open('templates/{func}.txt'.format(func=func), 'r') as file:
        baseline_code = file.read()
      
      # Get PAR-2 Score of the baseline
      metric = run_codes(baseline_code, record)
      # Get advices from advisor
      descr, dir = get_advice(record)
      # Add baseline function to the record
      record.add_rec(baseline_code, metric, descr)

    # Get new advices if recent results are not satisfactory (No better codes in past 2 iterations (2 * batches))
    # get_id() returns the current number of records accumulated.
    elif record.get_best_index() <= record.get_id() - 2 * M:
      descr, dir = get_advice(record)

    # lists for accumulating results.
    batch_codes = []
    batch_eval = []
    batch_metric = []

    # Start batch
    for i in range(M):
      # Get random modification, modified code, evaluation, and metric
      target_dir = dir[random.randint(0, len(dir)-1)]
      code = get_codes(descr, target_dir, record, i)
      eval_type, analysis = get_eval(code, record, i)
      metric = run_codes(code, record, i)

      # if no modification or erroneous code (which is indicated by metric == 0), give Coder one more chance
      if eval_type == "No Modification" or metric == 0:
        code = get_codes(descr, target_dir, record, i)
        eval_type, analysis = get_eval(code, record, i)
        metric = run_codes(code, record, i)
      
      # Append results to batch records
      batch_codes.append(code)
      batch_eval.append("Type:\n" + eval_type + "\nExtra Analysis:\n" + analysis)
      batch_metric.append(metric)

    for i in range(M):
      # If final code is erroneous, add it to the result with metric = 3000 & Analysis : Erroneous Code
      if batch_metric[i] == 0:
        record.add_rec(batch_codes[i], 3000, "Analysis: Erroneous Code")
      else:
        record.add_rec(batch_codes[i], batch_metric[i], batch_eval[i])

  # After iteration, modify the SAT Solver code with the best version
  best_code = record.get_index(record.get_best_index())['code']
  code = str.lstrip(best_code)

  with open("easysat/EasySAT.cpp", "r") as file:
    lines = file.readlines()
        
  with open("easysat/EasySAT.cpp", "w") as file:
    modifying = False
    for i in range(len(lines)):
      if "start {task}".format(task=current_task) in lines[i]:
        modifying = True
      elif "end {task}".format(task=current_task) in lines[i]:
        modifying = False
        file.write("{code}\n".format(code=code))
        continue
          
      if modifying:
        continue
      else:
        file.write(lines[i])

  # Write logs
  with open('log/final/record.txt', 'w') as file:
    rec = record.get_rec()
    for i in range(len(rec)):
      file.write('-------------Record ' + str(i) + '----------------\n')
      file.write('Code : \n' + str(rec[i]['code']) + '\n')
      file.write('PAR-2 : \n' + str(rec[i]['PAR-2 Score']) + '\n')
      file.write('Analysis : \n' + str(rec[i]['Analysis']) + '\n')

if __name__ == "__main__":
  main(args)