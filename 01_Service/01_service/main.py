from fastapi import FastAPI

app: FastAPI = FastAPI(root_path="/service01")


@app.get("/")
def get_data():
    return {"message": "Hello World From Service 01"}
