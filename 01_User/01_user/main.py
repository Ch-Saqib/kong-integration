from fastapi import FastAPI

app: FastAPI = FastAPI()


@app.get("/")
def get_data():
    return {"message": "Hello World From User Service 01"}
