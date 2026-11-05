import os, tempfile
from fastapi import FastAPI, UploadFile
from fastapi.responses import HTMLResponse
from .ayikla import isle

app = FastAPI(title="Fatura / Evrak Ayıklayıcı")


@app.post("/ayikla")
async def ayikla(dosya: UploadFile):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as t:
        t.write(await dosya.read())
        yol = t.name
    try:
        return isle(yol)
    finally:
        os.remove(yol)


@app.get("/", response_class=HTMLResponse)
def ui():
    return open(os.path.join(os.path.dirname(__file__), "ui.html"), encoding="utf-8").read()
