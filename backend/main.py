from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import os
import subprocess

from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_toolkits import FileManagementToolkit
from langchain.callbacks import StdOutCallbackHandler

from initialize import initialize_agent
from developer_agent import DeveloperAgent
from execute_bash_tool import ExecuteBashTool
from my_callback_handler import MyCallbackHandler

def setupOpenAIOpenAI():
  from dotenv import load_dotenv
  load_dotenv()

  return ChatOpenAI(
     openai_api_key=os.getenv("OPENAI_API_KEY"),
     model_name="gpt-3.5-turbo")    

llm = setupOpenAIOpenAI()

working_directory = "/tmp/workspace"
os.chdir(working_directory)

tools = FileManagementToolkit(root_dir=working_directory).get_tools()
tools.append(ExecuteBashTool())

agent = initialize_agent(
    tools,
    llm,
    agent_cls=DeveloperAgent,
    verbose=True
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

class Task(BaseModel):
    description: str

state = {
   "is_coding": False,
   "log": []
}

stdout_handler = StdOutCallbackHandler()

def on_log(event: dict):
  state['log'].append(event)
my_handler = MyCallbackHandler(on_log)

callbacks = [stdout_handler, my_handler]

@app.post("/task")
def run_task(task: Task, background_tasks: BackgroundTasks):
  def do_task():
    state["is_coding"] = True
    state["log"] = []    
    try:
      agent.run(input=task.description, callbacks=callbacks)
    except Exception as e:
        print("error executing agent!")
        state['log'].append({ "type": "end", "msg": "Error executing agent" })
    os.system("/usr/bin/git add -N .")
    state["is_coding"] = False

  if state["is_coding"]:
    raise HTTPException(status_code=400, detail="Already working on a task.")
  
  background_tasks.add_task(do_task)

  return "Task started"

class Commit(BaseModel):
    msg: str

@app.get("/log")
async def get_log():
     return state["log"]

@app.get("/diff")
async def get_diff_html():
  try:
    content=subprocess.check_output("git diff | diff2html -i stdin -o stdout", shell=True)
  except subprocess.CalledProcessError as e:
    if e.returncode == 3:
      # Empty diff
      content=subprocess.check_output("echo "" | diff2html -i stdin -o stdout", shell=True)
    else:
       raise e
  return HTMLResponse(content=content)

@app.post("/revert")
def revert():
  if state["is_coding"]:
    raise HTTPException(status_code=400, detail="Already working on a task.")  
  os.system(f"/usr/bin/git clean -f .")


@app.post("/commit")
def commit(commit: Commit):
  if state["is_coding"]:
    raise HTTPException(status_code=400, detail="Already working on a task.")  
  os.system(f"/usr/bin/git add .")
  os.system(f"/usr/bin/git commit -m '{commit.msg}'")
