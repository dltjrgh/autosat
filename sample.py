import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--batch_size', help=' : Batch Size', type=int)
parser.add_argument('--iteration_size', help=' : Iteration Size', type=int)
args = parser.parse_args()

def main(args):
  print("Batch Size: ", args.batch_size)
  print("Iteration Size: ", args.iteration_size)

if __name__ == "__main__":
  main(args) # M = 4, N = 6. M batch size, N iteration number