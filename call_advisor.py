from openai import OpenAI
import json

def get_advice(record):
  client = OpenAI(api_key = "sk-proj-7HyMsTDmzxf3nsOhAXpNT3BlbkFJTos4MEyT2gvHRha5wo1s")

  # ids are only used to index queries and responses for logging
  id = record.get_id()
  f = record.get_rec()

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

  # Load template
  with open("templates/advisor_template.txt", "r") as file:
    advisor_template = file.read()

  # Load full code of EasySAT
  with open("templates/full_code.txt", "r") as file:
    key_code = file.read()

  # Load target function code (original version)
  with open("templates/{func}.txt".format(func=func), "r") as file:
    original_target_code = file.read()
  
  # Write query log
  with open("log/advisor/{id}_query.log".format(id=id), "w") as file:
    file.write("You are a SAT solver researcher trying to write the {task} to help the SAT solver escape from the local optimum.\n".format(task=current_task))
    file.write("Past modifications with its analysis and evaluation metric (smaller is better) are as follows:\n{f}".format(f=f))
    file.write(advisor_template.format(task=current_task, origin_key_code=key_code, other_tips=""))
  
  # Try with giving the ChatGPT entire solver code (origin_key_code=key_code on the 3rd message)
  try:
    completion = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": "You are a SAT solver researcher trying to write the {task} to help the SAT solver escape from the local optimum.".format(task=current_task)},
        {"role": "system", "content": "Past modifications with its analysis and evaluation metric (smaller is better) are as follows:\n{f}".format(f=f)},
        {"role": "user", "content": advisor_template.format(task=current_task, origin_key_code=key_code, other_tips="\n")}
      ]
    )
  # If it fails (Token limitation), just give only the target function code (origin_key_code=original_target_code in 3rd message)
  except:
    completion = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": "You are a SAT solver researcher trying to write the {task} to help the SAT solver escape from the local optimum.".format(task=current_task)},
        {"role": "system", "content": "Past modifications with its analysis and evaluation metric (smaller is better) are as follows:\n{f}".format(f=f)},
        {"role": "user", "content": advisor_template.format(task=current_task, origin_key_code=original_target_code, other_tips="\n")}
      ]
    )

  # Write log of the response
  with open("log/advisor/{id}_response.json".format(id=id), "w") as file:
    file.write(completion.choices[0].message.content)

  # Return description:str, modification_direction:list(str)
  with open("log/advisor/{id}_response.json".format(id=id), "r") as file:
    data = json.load(file)
    return data['description'], data['modification_direction']