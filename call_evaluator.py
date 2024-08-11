from openai import OpenAI
# from main import Record
import json

def get_eval(descr, dir, code, record, i):
  client = OpenAI(api_key = "sk-proj-7HyMsTDmzxf3nsOhAXpNT3BlbkFJTos4MEyT2gvHRha5wo1s")
  # Parameters
  current_task = "bump variables function"
  f = record.get_rec()
  id = record.get_id() + i

  # origin_target_code
  with open("templates/bump_variables.txt", "r") as file:
    original_target_code = file.read()

  # origin_key_code
  with open("templates/full_code.txt", "r") as file:
    original_key_code = file.read()

  # evaluator_template
  with open("templates/evaluator_template.txt", "r") as file:
    evaluator_template = file.read()
  
  with open("log/evaluator/{id}_query.log".format(id=id), "w") as file:
    file.write(evaluator_template.format(task=current_task, origin_target_code=original_target_code, llm_generation=code, origin_key_code=original_key_code, other_tips="\n"))

  try:
    completion = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": "You are a SAT solver researcher trying to write the {task} to help the SAT solver escape from the local optimum.".format(task=current_task)},
        {"role": "system", "content": "Past modifications with its analysis and evaluation metric (smaller is better) are as follows:\n{f}".format(f=f)},
        {"role": "user", "content": evaluator_template.format(task=current_task, origin_target_code=original_target_code, llm_generation=code, origin_key_code=original_key_code, other_tips="\n")}
      ]
    )
  except:
    completion = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": "You are a SAT solver researcher trying to write the {task} to help the SAT solver escape from the local optimum.".format(task=current_task)},
        {"role": "system", "content": "Past modifications with its analysis and evaluation metric (smaller is better) are as follows:\n{f}".format(f=f)},
        {"role": "user", "content": evaluator_template.format(task=current_task, origin_target_code=original_target_code, llm_generation=code, origin_key_code=original_target_code, other_tips="\n")}
      ]
    )

  with open("log/evaluator/{id}_response.json".format(id=id), "w") as file:
    file.write(completion.choices[0].message.content)

  with open("log/evaluator/{id}_response.json".format(id=id), "r") as file:
    data = json.load(file)
    return data['type'], data['extra_analysis']
