from fastapi import FastAPI

app: FastAPI = FastAPI(root_path="/service02")


@app.get("/")
def get_data():
    return {"message": "Hello World From Service 02"}
