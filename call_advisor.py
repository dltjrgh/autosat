from openai import OpenAI
# from main import Record
import json

def get_advice(record):
  id = record.get_id()
  f = record.get_rec()
  client = OpenAI(api_key = "sk-proj-7HyMsTDmzxf3nsOhAXpNT3BlbkFJTos4MEyT2gvHRha5wo1s")

  # Parameters
  current_task = "bump variables function"

  with open("templates/advisor_template.txt", "r") as file:
    advisor_template = file.read()

  with open("templates/full_code.txt", "r") as file:
    key_code = file.read()

  # origin_target_code
  with open("templates/bump_variables.txt", "r") as file:
    original_target_code = file.read()
  
  with open("log/advisor/{id}_query.log".format(id=id), "w") as file:
    file.write(advisor_template.format(task=current_task, origin_key_code=key_code, other_tips=""))
  
  try:
    completion = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": "You are a SAT solver researcher trying to write the {task} to help the SAT solver escape from the local optimum.".format(task=current_task)},
        {"role": "system", "content": "Past modifications with its analysis and evaluation metric (smaller is better) are as follows:\n{f}".format(f=f)},
        {"role": "user", "content": advisor_template.format(task=current_task, origin_key_code=key_code, other_tips="\n")}
      ]
    )
  except:
    completion = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": "You are a SAT solver researcher trying to write the {task} to help the SAT solver escape from the local optimum.".format(task=current_task)},
        {"role": "system", "content": "Past modifications with its analysis and evaluation metric (smaller is better) are as follows:\n{f}".format(f=f)},
        {"role": "user", "content": advisor_template.format(task=current_task, origin_key_code=original_target_code, other_tips="\n")}
      ]
    )

  with open("log/advisor/{id}_response.json".format(id=id), "w") as file:
    file.write(completion.choices[0].message.content)

  with open("log/advisor/{id}_response.json".format(id=id), "r") as file:
    data = json.load(file)
    return data['description'], data['modification_direction']