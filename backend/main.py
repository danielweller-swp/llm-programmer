from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import os
import subprocess

from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_toolkits import FileManagementToolkit
from langchain.callbacks import StdOutCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler

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
# tools.append(ExecuteBashTool())

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

# TODO: thread safety?
state = {
   "is_coding": False,
   "last_error": None,
   "log": []
}

stdout_handler = StdOutCallbackHandler()

def on_log(event: dict):
   state['log'].append(event)
   
my_handler = MyCallbackHandler(on_log)

@app.post("/task")
async def run_task(task: Task, background_tasks: BackgroundTasks):
  def do_task(input: str, callbacks: list[BaseCallbackHandler]):
     state["is_coding"] = True
     state["log"] = []
     agent.run(input=input, callbacks=callbacks)
     os.system("/usr/bin/git add -N .")
     state["is_coding"] = False

  if state["is_coding"]:
    raise HTTPException(status_code=400, detail="Already working on a task.")  
  
  background_tasks.add_task(do_task, input=task.description, callbacks=[stdout_handler, my_handler])
  
  #os.system("git add .")
  #os.system(f"git commit -m '{task.commitMessage}'")
  return "Task started"

@app.get("/log")
def get_log():
   return state["log"]

@app.get("/diff")
def get_diff_html():
   return subprocess.check_output("/usr/local/bin/diff2html -o stdout")


# agent.run(input="Create a program that prints the first n primes.", callbacks=[stdout_handler])