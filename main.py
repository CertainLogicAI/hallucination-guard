from fastapi import FastAPI
import redis
import os

app = FastAPI()

redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_client = redis.Redis(host=redis_host, port=redis_port)

@app.get("/validate")
def validate():
    try:
        redis_client.ping()
        return {"status": "OK", "redis_connected": True}
    except:
        return {"status": "ERROR", "redis_connected": False}

@app.get("/")
def root():
    return {"message": "Deterministic AI Brain API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)