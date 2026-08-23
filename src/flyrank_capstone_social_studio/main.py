from fastapi import FastAPI
import uvicorn
from flyrank_capstone_social_studio.api.v1 import api_router



app = FastAPI(
    title="FlyRank Social Media Studio",
    version="0.1.0",
)


app.include_router(
    api_router,
    prefix="/api/v1",
)


#health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}




#Run the Uvicorn server
def run():
    uvicorn.run(
        "flyrank_capstone_social_studio.main:app",
        host = "127.0.0.1",
        port = 8000,
        reload = True
    )