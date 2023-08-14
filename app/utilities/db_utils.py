
import os
import asyncpg
import redis

# PostgreSQL related functions
async def get_tasks_from_db():
    tasks = []
    conn = await asyncpg.connect(
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME'),
        host=os.environ.get('DB_HOST')
    )
    rows = await conn.fetch('SELECT id, title, status FROM tasks')
    for row in rows:
        tasks.append({
            "id": row[0],
            "title": row[1],
            "status": row[2]
        })
    await conn.close()
    return tasks

# Redis related functions
def get_total_tasks_from_redis():
    r = redis.Redis(
        host=os.environ.get('REDIS_HOST'),
        port=int(os.environ.get('REDIS_PORT')),
        db=int(os.environ.get('REDIS_DB'))
    )
    return int(r.get('total_tasks'))

def get_recent_tasks_from_redis(N=5):
    r = redis.Redis(
        host=os.environ.get('REDIS_HOST'),
        port=int(os.environ.get('REDIS_PORT')),
        db=int(os.environ.get('REDIS_DB'))
    )
    recent_tasks = []
    total_tasks = get_total_tasks_from_redis()
    for i in range(total_tasks, total_tasks - N, -1):
        task = r.hgetall(f'task_{i}')
        if task:
            recent_tasks.append(task)
    return recent_tasks
