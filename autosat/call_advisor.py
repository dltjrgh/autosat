from openai import OpenAI
import json

def get_advice(id, f = []):
  client = OpenAI(api_key = "sk-proj-7HyMsTDmzxf3nsOhAXpNT3BlbkFJTos4MEyT2gvHRha5wo1s")

  # Parameters
  current_task = "bump variables function"

  file = open("autosat/templates/advisor_template.txt", "r")
  advisor_template = file.read()
  file.close()

  file = open("autosat/templates/bump_variables.txt", "r")
  key_code = file.read()
  file.close()

  file = open("autosat/log/advisor/{id}_query.log".format(id=id), "w")
  file.write(advisor_template.format(task=current_task, origin_key_code=key_code, other_tips=""))
  file.close()
  
  completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
      {"role": "system", "content": "You are a SAT solver researcher trying to write the {task} to help the SAT solver escape from the local optimum.".format(task=current_task)},
      {"role": "user", "content": advisor_template.format(task=current_task, origin_key_code=key_code, other_tips="\n")}
    ]
  )

  file = open("autosat/log/advisor/{id}_response.json".format(id=id), "w")
  file.write(completion.choices[0].message.content)
  file.close()

  with open("autosat/log/advisor/{id}_response.json".format(id=id), "r") as file:
    data = json.load(file)
    return data