from fastapi import FastAPI

app: FastAPI = FastAPI()


@app.get("/")
def get_data():
    return {"message": "Hello World From Product Service 02"}
