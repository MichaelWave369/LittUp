from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"app": "LittUp Web Template", "status": "ok"}
