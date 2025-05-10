from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, StreamingResponse, FileResponse

from db import *


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    print("startup test")


@app.on_event("shutdown")
def shutdown_event():
    print("shutdown test")
    clear_temp()


@app.get("/")
async def root():
    return RedirectResponse(url='/docs')


@app.get("/media/all")
async def media_all():
    cur = get_all_media()
    return format_cursor(cur)


@app.get("/media/{media_id}")
async def get_id_media(media_id: int):
    cur = get_media_id(media_id)
    return format_cursor(cur)


@app.get("/media/search/filter")
async def search_file(name: str = None, tag: str = None, typ: str = None, location: str = None, date: str = None):
    cur = search(name, tag, typ, location, date)
    if cur:
        return format_cursor(cur)
    return {"message": 'Parameter not provided!'}


@app.post("/media/add")
async def add_media(data: Request):
    req_data = await data.json()
    media_id = insert_media(req_data)
    return {"media_id": int(media_id[0])}


@app.delete("/media/delete/{media_id}")
async def delete_media(media_id: int):
    delete_by_id(media_id)
    return {"message": "media deleted"}


@app.put("/media/update")
async def update_media(data: Request):
    req_data = await data.json()
    update_by_id(req_data)
    return {"message": "media successfully updated"}


@app.post("/media/upload/{media_id}")
async def receive_media(media_id: int, file: UploadFile = File()):
    content = await file.read()
    update_media_obj(media_id, content)
    cache_image_by_id(media_id)
    return {"message": "media successfully updated"}

@app.get("/media/download/{media_id}")
async def send_media(media_id: int):
    # res = stream_media_object(media_id)
    name = await get_media_object(media_id)
    if name:
        path = f'media_cache/temp/{name}'
        return FileResponse(path, media_type='application/octet-stream',filename=name)
    # return StreamingResponse(res)
    raise HTTPException(status_code=404, detail="media not found")

