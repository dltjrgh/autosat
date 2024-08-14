from openai import OpenAI

def get_codes(descr, dir, record, i):
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
  elif record.get_phase() == 2:
    current_task = "rephase function"
    func = "rephase"

  # Load target code
  with open("templates/{func}.txt".format(func=func), "r") as file:
    original_target_code = file.read()

  # Load full EasySAT code
  with open("templates/full_code.txt", "r") as file:
    original_key_code = file.read()

  # Load Coder template
  with open("templates/coder_template.txt", "r") as file:
    coder_template = file.read()
  
  # Write query log
  with open("log/coder/{id}_query.log".format(id=id), "w") as file:
    file.write("You are a SAT solver researcher trying to write the {task} to help the SAT solver escape from the local optimum.\n".format(task=current_task))
    file.write("Past modifications with its analysis and evaluation metric (smaller is better) are as follows:\n{f}".format(f=f))
    file.write(coder_template.format(task=current_task, description=descr, modification_direction=dir, origin_target_code=original_target_code, origin_key_code=original_key_code, other_tips="\n"))

  # Try with giving the ChatGPT entire solver code (origin_key_code=key_code on the 3rd message)
  try:
    completion = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": "You are a SAT solver researcher trying to write the {task} to help the SAT solver escape from the local optimum.".format(task=current_task)},
        {"role": "system", "content": "Past modifications with its analysis and evaluation metric (smaller is better) are as follows:\n{f}".format(f=f)},
        {"role": "user", "content": coder_template.format(task=current_task, description=descr, modification_direction=dir, origin_target_code=original_target_code, origin_key_code=original_key_code, other_tips="\n")}
      ]
    )
  # If it fails (Token limitation), just give only the target function code (origin_key_code=original_target_code in 3rd message)
  except:
    completion = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": "You are a SAT solver researcher trying to write the {task} to help the SAT solver escape from the local optimum.".format(task=current_task)},
        {"role": "system", "content": "Past modifications with its analysis and evaluation metric (smaller is better) are as follows:\n{f}".format(f=f)},
        {"role": "user", "content": coder_template.format(task=current_task, description=descr, modification_direction=dir, origin_target_code=original_target_code, origin_key_code=original_target_code, other_tips="\n")}
      ]
    )

  # Write log for responses
  with open("log/coder/{id}_response.txt".format(id=id), "w") as file:
    file.write(completion.choices[0].message.content)

  # Return modified code:str
  with open("log/coder/{id}_response.txt".format(id=id), "r") as file:
    code = file.read()
    return code
