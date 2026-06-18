from fastapi import FastAPI

app = FastAPI()

# root endpoint
@app.get("/")
def read_root():
    return {"Hello": "World"}



# health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}

