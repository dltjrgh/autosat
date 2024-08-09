from openai import OpenAI
from run_code import *
from call_advisor import *

id = 0
f = []

def main():
  

  file = open("autosat/test.log", "w")
  x = get_advice(id)
  print(x)
  file.write(x['description'])
  file.write(x['modification_direction'])
  file.close()

if __name__ == "__main__":
  main()