from fastapi import FastAPI
from pydantic import BaseModel

import os
from langchain import OpenAI
from langchain.agents.agent_toolkits import FileManagementToolkit

from initialize import initialize_agent
from developer_agent import DeveloperAgent
from execute_bash_tool import ExecuteBashTool


def setupOpenAIOpenAI():
  from dotenv import load_dotenv
  load_dotenv()

  return OpenAI(
     openai_api_key=os.getenv("OPENAI_API_KEY"),
     model_name="gpt-3.5-turbo")    

llm = setupOpenAIOpenAI()

working_directory = "/home/frain/gpt-program"
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

class Task(BaseModel):
    commitMessage: str
    description: str

@app.post("/task")
def run_task(task: Task):
    try:
      result = agent.run(input=task.description)
    except:
       result = "Error"
    os.system("git add .")
    os.system(f"git commit -m '{task.commitMessage}'")
    return result
