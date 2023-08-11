
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import asyncpg
import redis
import asyncio

# Dummy data for tasks
tasks = [
    {"id": 1, "title": "Setup Qlik Cloud instance", "status": "Pending"},
    {"id": 2, "title": "Configure user permissions", "status": "Completed"},
    {"id": 3, "title": "Review usage metrics", "status": "In Progress"}
]

async def populate_postgres():
    conn = await asyncpg.connect(user=os.environ.get('DB_USER'), password=os.environ.get('DB_PASSWORD'), database=os.environ.get('DB_NAME'), host=os.environ.get('DB_HOST'))
    for task in tasks:
        await conn.execute('''
            INSERT INTO tasks(id, title, status) VALUES($1, $2, $3)
        ''', task['id'], task['title'], task['status'])
    await conn.close()

def populate_redis():
    r = redis.Redis(host=os.environ.get('REDIS_HOST'), port=int(os.environ.get('REDIS_PORT')), db=int(os.environ.get('REDIS_DB')))
    r.set('total_tasks', len(tasks))
    for task in tasks:
        r.hmset(f'task_{task["id"]}', task)

if __name__ == os.environ.get("__main__"):
    asyncio.run(populate_postgres())
    populate_redis()
    