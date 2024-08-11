from openai import OpenAI
from run_code import *
from call_advisor import *
from call_coder import *
from call_evaluator import *
import random, heapq, argparse

# Set up the argument parser
parser = argparse.ArgumentParser()
parser.add_argument('--batch_size', help=' : Batch Size', type=int)
parser.add_argument('--iteration_size', help=' : Iteration Size', type=int)
args = parser.parse_args()

class Record:
  def __init__(self):
    self.rec = []
    self.hq = []
  
  def get_rec(self):
    return self.rec
  
  def get_id(self):
    return len(self.rec)

  def get_index(self, id):
    return self.rec[id]

  def add_rec(self, code, metric, analysis):
    heapq.heappush(self.hq, (metric, len(self.rec)))
    self.rec.append({"code":code, "PAR-2 Score":metric, "Analysis":analysis})

  def get_best_index(self):
    return self.hq[0][1]
  
def main(args):
  M = args.batch_size
  N = args.iteration_size

  # Initialize the record
  record = Record()

  for i in range(N):

    # Getting advice from the advisor
    if i == 0:
      # Add baseline code to the record
      with open('templates/bump_variables.txt', 'r') as file:
        baseline_code = file.read()
      
      metric = run_codes([baseline_code])
      descr, dir = get_advice(record)
      record.add_rec(baseline_code, metric, descr)

    # Revise Advice if recent results are not satisfactory
    elif record.get_best_index() <= record.get_id() - 2 * M:
      descr, dir = get_advice(record)


    batch_codes = []
    batch_eval = []
    batch_metric = []
    for i in range(M):
      target_dir = dir[random.randint(0, len(dir)-1)]
      code = get_codes(descr, target_dir, record, i)
      eval_type, analysis = get_eval(descr, target_dir, code, record, i)
      metric = run_codes([code])

      if eval_type == "No Modification" or metric == 0:
        code = get_codes(descr, target_dir, record, i)
        eval_type, analysis = get_eval(descr, target_dir, code, record, i)
        metric = run_codes([code])
      
      batch_codes.append(code)
      batch_eval.append("Type:\n" + eval_type + "\nExtra Analysis:\n" + analysis)
      batch_metric.append(metric)

    for i in range(M):
      if batch_metric[i] == 0:
        record.add_rec(batch_codes[i], "", "Analysis: Erroneous Code")
      else:
        record.add_rec(batch_codes[i], batch_metric[i], batch_eval[i])

  with open('log/final/record.txt', 'w') as file:
    rec = record.get_rec()
    for i in range(len(rec)):
      file.write('-------------Record ' + str(i) + '----------------\n')
      file.write('Code : \n' + str(rec[i]['code']) + '\n')
      file.write('PAR-2 : \n' + str(rec[i]['PAR-2 Score']) + '\n')
      file.write('Analysis : \n' + str(rec[i]['Analysis']) + '\n')

if __name__ == "__main__":
  main(args)