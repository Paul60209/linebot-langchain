# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import os
import sys
import json
import aiohttp
from fastapi import Request, FastAPI, HTTPException
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentType
from langchain.agents import initialize_agent, Tool
from langchain.schema import HumanMessage
from stock_price import StockPriceTool
from stock_peformace import StockPercentageChangeTool, StockGetBestPerformingTool
from sql_query import SQLQueryTool
from linebot import (
    AsyncLineBotApi, WebhookParser
)
from linebot.aiohttp_async_http_client import AiohttpAsyncHttpClient
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())  # read local .env file

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('ChannelSecret', None)
channel_access_token = os.getenv('ChannelAccessToken', None)
open_ai_key = os.getenv('OPENAI_API_KEY', None)
db_url = os.getenv('CLEARDB_DATABASE_URL', None)



if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

app = FastAPI()
session = aiohttp.ClientSession()
async_http_client = AiohttpAsyncHttpClient(session)
line_bot_api = AsyncLineBotApi(channel_access_token, async_http_client)
parser = WebhookParser(channel_secret)

# Langchain (you must use 0613 model to use OpenAI functions.)
model = ChatOpenAI(model="gpt-3.5-turbo-0613")


tools = [StockPriceTool(), StockPercentageChangeTool(),
         StockGetBestPerformingTool(), SQLQueryTool()]

open_ai_agent = initialize_agent(tools,
                                 model,
                                 agent=AgentType.OPENAI_FUNCTIONS,
                                 verbose=False)

# llm = OpenAI(temperature=0, openai_api_key=open_ai_key, model_name='gpt-3.5-turbo')
# db = SQLDatabase.from_uri(db_url)
# toolkit = SQLDatabaseToolkit(db=db, llm=llm)
# agent_executor = create_sql_agent(
#     llm=gpt,
#     toolkit=toolkit,
#     verbose=True,
#     agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
# )



@app.post("/callback")
async def handle_callback(request: Request):
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = await request.body()
    body = body.decode()

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        print(f'MESSAGE={event.message.text}')

        # tool_result = agent_executor.run(event.message.text)
        tool_result = open_ai_agent.run(event.message.text)

        print(f'RESULT={tool_result}')
        # if event.message.text[2]=='/s':
        #     tool_result = open_ai_agent.run(event.message.text)
        # elif event.message.text[2]=='/q':
        #     tool_result = agent_executor.run(event.message.text)

        await line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=tool_result)
        )

    return 'OK'
