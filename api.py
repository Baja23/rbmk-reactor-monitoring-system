from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uvicorn
from redis_client import r
from redis.exceptions import ConnectionError as RedisConnectionError
from dotenv import load_dotenv
import os

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    '''Delete leftover data on startup'''

    r.delete("rods_movement")
    r.delete("water_flow")
    r.delete("in_water_temp")
    r.delete("az5")
    yield

# This disables public documentation generation. Other people will not be able to see the API points.
app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

API_KEY = os.getenv("X_API_KEY")

# BaseModel enables automatic parsing, validation and generating documentation
class GrafanaData(BaseModel):

    value: int | None = None
    name: str | None = None
    key: str | None = None


def verify_button_header(data:GrafanaData):
    '''Verify API key send in payload from Grafana'''

    if data.key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized access")

# Launches a function that verifies API key
@app.post("/webhook", dependencies=[Depends(verify_button_header)])
async def grafana_webhook(data: GrafanaData):
    '''Accept data of attributes from Grafana'''

    print(f"Otrzymano wartości z Grafana przez POST - {data.name}: {data.value}")
    try:
        if data.value is None:
            return("Value is None.")
        r.lpush(f"{data.name}", data.value)
    except RedisConnectionError:
        raise HTTPException(status_code=503, detail="Redis database is unavailable!")




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
