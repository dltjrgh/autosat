from openai import OpenAI
import json

def get_eval(code, record, i):
  client = OpenAI(api_key = "sk-proj-7HyMsTDmzxf3nsOhAXpNT3BlbkFJTos4MEyT2gvHRha5wo1s")
  
  # Parameters
  f = record.get_rec()
  id = record.get_id() + i

  # Set Phase
  if record.get_phase() == 0:
    current_task = "bump variables function"
    func = "bump_variables"
  elif record.get_phase() == 1:
    current_task = "restart function"
    func = "restart"
  if record.get_phase() == 2:
    current_task = "rephase function"
    func = "rephase"

  # Load target function code
  with open("templates/{func}.txt".format(func=func), "r") as file:
    original_target_code = file.read()

  # Load full EasySAT code
  with open("templates/full_code.txt", "r") as file:
    original_key_code = file.read()

  # Load Evaluator template
  with open("templates/evaluator_template.txt", "r") as file:
    evaluator_template = file.read()
  
  # Write log for queries
  with open("log/evaluator/{id}_query.log".format(id=id), "w") as file:
    file.write("You are a SAT solver researcher trying to write the {task} to help the SAT solver escape from the local optimum.\n".format(task=current_task))
    file.write("Past modifications with its analysis and evaluation metric (smaller is better) are as follows:\n{f}".format(f=f))
    file.write(evaluator_template.format(task=current_task, origin_target_code=original_target_code, llm_generation=code, origin_key_code=original_key_code, other_tips="\n"))

  # Try with giving the ChatGPT entire solver code (origin_key_code=key_code on the 3rd message)
  try:
    completion = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": "You are a SAT solver researcher trying to write the {task} to help the SAT solver escape from the local optimum.".format(task=current_task)},
        {"role": "system", "content": "Past modifications with its analysis and evaluation metric (smaller is better) are as follows:\n{f}".format(f=f)},
        {"role": "user", "content": evaluator_template.format(task=current_task, origin_target_code=original_target_code, llm_generation=code, origin_key_code=original_key_code, other_tips="\n")}
      ]
    )
  # If it fails (Token limitation), just give only the target function code (origin_key_code=original_target_code in 3rd message)
  except:
    completion = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": "You are a SAT solver researcher trying to write the {task} to help the SAT solver escape from the local optimum.".format(task=current_task)},
        {"role": "system", "content": "Past modifications with its analysis and evaluation metric (smaller is better) are as follows:\n{f}".format(f=f)},
        {"role": "user", "content": evaluator_template.format(task=current_task, origin_target_code=original_target_code, llm_generation=code, origin_key_code=original_target_code, other_tips="\n")}
      ]
    )

  # Write log for response
  with open("log/evaluator/{id}_response.json".format(id=id), "w") as file:
    file.write(completion.choices[0].message.content)

  # Return 'type':str, 'extra_analysis':str
  with open("log/evaluator/{id}_response.json".format(id=id), "r") as file:
    data = json.load(file)
    return data['type'], data['extra_analysis']
