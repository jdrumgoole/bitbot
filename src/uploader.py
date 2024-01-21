from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import hashlib

app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), checksum: str = Form(...)):
    hash_sha256 = hashlib.sha256()
    try:
        while content := await file.read(1024):  # Read the file in chunks
            hash_sha256.update(content)  # Update the hash with the file content
        file_checksum = hash_sha256.hexdigest()
        if file_checksum != checksum:
            raise HTTPException(status_code=400, detail="Checksum does not match")
        return {"filename": file.filename, "checksum": file_checksum, "status": "Success"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"An error occurred: {str(e)}"})

