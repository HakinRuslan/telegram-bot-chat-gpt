
from config import *
from bot import *
import asyncio

async def check_user_delay(user_id: int):  
    last_message_time = await redis.get(f"users:{user_id}")  
    if last_message_time:  
        time_since_last_message = asyncio.get_event_loop().time() - float(  
            last_message_time  
        )
    else:
        await redis.setex(  
            f"users:{user_id}", 8, asyncio.get_event_loop().time(), 
        )
        return True
    if time_since_last_message <  4:  
        return False  
    return True