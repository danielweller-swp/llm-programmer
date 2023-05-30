from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import os
import subprocess
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

from functools import partial

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
   "last_error": None,
   "log": []
}

stdout_handler = StdOutCallbackHandler()

@app.post("/task")
def run_task(task: Task, background_tasks: BackgroundTasks):
#async def run_task(task: Task):

  async def do_task(agent, state, input, stdout_handler):
    def on_log(state, event: dict):
      state['log'].append(event)

    my_handler = MyCallbackHandler(partial(on_log, state))
    callbacks = [stdout_handler, my_handler]
    #callbacks = [stdout_handler]
    #callbacks = [my_handler]
    state["is_coding"] = True
    state["log"] = []
    def f(agent, input, callbacks):
       return agent.run(input=input, callbacks=callbacks)
    try:
      with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, f, agent, input, callbacks)
    except Exception as e:
        print("error executing agent!")
    os.system("/usr/bin/git add -N .")
    state["is_coding"] = False

  if state["is_coding"]:
    raise HTTPException(status_code=400, detail="Already working on a task.")  
  
  #background_tasks.add_task(do_task, agent, state, task.description, [stdout_handler, my_handler])
  background_tasks.add_task(do_task, agent, state, task.description, stdout_handler)
  
  #os.system("git add .")
  #os.system(f"git commit -m '{task.commitMessage}'")
  return "Task started"

@app.get("/log")
async def get_log():
     return state["log"]

@app.get("/diff")
async def get_diff_html():
   return HTMLResponse(content=subprocess.check_output("git diff | diff2html -i stdin -o stdout", shell=True))

