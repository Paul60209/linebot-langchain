from typing import List
from langchain.tools import BaseTool
from langchain.agents import AgentType
from typing import Optional, Type
from pydantic import BaseModel, Field
from langchain.agents import create_sql_agent, AgentExecutor
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain import SQLDatabase, SQLDatabaseChain
from langchain.chat_models import ChatOpenAI
from langchain.llms.openai import OpenAI
import os




class SQLQueryCheckInput(BaseModel):
    """Input for Stock ticker check. for percentage check"""

    query: str = Field(...,
                             description="SQL query to select data or statistic result from database")

class SQLQueryTool(BaseTool):
    name = "execute_sql_query"
    description = "Execute a SQL query on mySQL database"


    def _run(self, query: str):
        db_url = os.getenv('CLEARDB_DATABASE_URL', None)
        open_ai_key = os.getenv('OPENAI_API_KEY', None)
        llm = OpenAI(temperature=0, openai_api_key=open_ai_key, model_name='gpt-3.5-turbo')

        db = SQLDatabase.from_uri(db_url)
        db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)
        result = db_chain.run(query)
        return result

    def _arun(self, query: str):
        raise NotImplementedError("This tool dose not support async")