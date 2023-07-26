from typing import List
from langchain.tools import BaseTool
from langchain.agents import AgentType
from typing import Optional, Type
from pydantic import BaseModel, Field
from langchain.agents import create_sql_agent, AgentExecutor
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain import SQLDatabase, SQLDatabaseChain

class SQLQueryCheckInput(BaseModel):
    """Input for Stock ticker check. for percentage check"""

    query: str = Field(...,
                             description="SQL query to select data or statistic result from database")

class SQLQueryTool(BaseTool):
    name = "execute_sql_query"
    description = "Execute a SQL query on mySQL database"

    def _run(self, query: str, db_url: str, llm):
        db = SQLDatabase.from_uri(db_url)
        db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)
        result = db_chain.run(query)
        return result

    def _arun(self, query: str):
        raise NotImplementedError("This tool dose not support async")