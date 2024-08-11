from openai import OpenAI
# from main import Record

def get_codes(descr, dir, record, i):
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

  # advisor_template
  with open("templates/coder_template.txt", "r") as file:
    coder_template = file.read()
  
  with open("log/coder/{id}_query.log".format(id=id), "w") as file:
    file.write(coder_template.format(task=current_task, description=descr, modification_direction=dir, origin_target_code=original_target_code, origin_key_code=original_key_code, other_tips="\n"))

  try:
    completion = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": "You are a SAT solver researcher trying to write the {task} to help the SAT solver escape from the local optimum.".format(task=current_task)},
        {"role": "system", "content": "Past modifications with its analysis and evaluation metric (smaller is better) are as follows:\n{f}".format(f=f)},
        {"role": "user", "content": coder_template.format(task=current_task, description=descr, modification_direction=dir, origin_target_code=original_target_code, origin_key_code=original_key_code, other_tips="\n")}
      ]
    )
  except:
    completion = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": "You are a SAT solver researcher trying to write the {task} to help the SAT solver escape from the local optimum.".format(task=current_task)},
        {"role": "system", "content": "Past modifications with its analysis and evaluation metric (smaller is better) are as follows:\n{f}".format(f=f)},
        {"role": "user", "content": coder_template.format(task=current_task, description=descr, modification_direction=dir, origin_target_code=original_target_code, origin_key_code=original_target_code, other_tips="\n")}
      ]
    )

  with open("log/coder/{id}_response.txt".format(id=id), "w") as file:
    file.write(completion.choices[0].message.content)

  with open("log/coder/{id}_response.txt".format(id=id), "r") as file:
    code = file.read()
    return code
