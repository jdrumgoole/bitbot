# Run: uvicorn main:app --reload
import hashlib

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from starlette.responses import JSONResponse
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id:int):
    return {"item_id": item_id}


@app.post("/upload/")
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), checksum: str = Form(...)):
    hash_sha256 = hashlib.sha256()
    size = 0
    try:
        while content := await file.read(1024):  # Read the file in chunks
            hash_sha256.update(content)  # Update the hash with the file content
            size = size + len(content)
        file_checksum = hash_sha256.hexdigest()
        if file_checksum != checksum:
            raise HTTPException(status_code=400, detail="Checksum does not match")
        return {"filename": file.filename, "checksum": file_checksum, "size": size, "status": "Success"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"An error occurred: {str(e)}"})

