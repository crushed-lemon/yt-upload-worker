from fastapi import FastAPI

app = FastAPI()

# Health controller
@app.get("/")
async def root():
    return {"message": "Hello World"}
