import httpx  
from aiogram.types import Message  
from openai import AsyncOpenAI, beta, api_key
import asyncio
from config import * 
import time
from bot import client_gpt
from utils.utils import *
from bot import redis


async def get_thread_id(user_id, client) -> str:
    thread_id = await redis.get(f"user:{user_id}:thread_id")
    if thread_id:
        return thread_id

    thread = await client.beta.threads.create()
    await redis.setex(f"user:{user_id}:thread_id", 18000, thread.id)

    return thread.id

async def get_gpt_client():
    http_client = httpx.AsyncClient(  
    limits=httpx.Limits(max_connections=150, max_keepalive_connections=20)  
    )  
    client = AsyncOpenAI(  
        api_key=settings.openai_api_key,  
        http_client=http_client,  
        base_url="https://api.openai.com/v1",  
        
    )
    return client

async def get_chat_completion_cons(message: Message):
    client = await get_gpt_client()
    thread_id = await get_thread_id(message.from_user.id, client)

    run = await client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id="ur assistant id"
    )

    while True:
        run = await client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        if run.status == "completed":
            break

    messages = client.beta.threads.messages.list(thread_id=thread_id)
    async for message in messages:
        if message.role == "assistant":
            return message.content[0].text.value