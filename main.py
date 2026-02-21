from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

USER_MESTRE = "admin"
SENHA_MESTRE = "123"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if request.cookies.get("autenticado") != "true":
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# ESTE É O CARA: Ele processa os dados do formulário
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if username == USER_MESTRE and password == SENHA_MESTRE:
        resp = RedirectResponse(url="/", status_code=303)
        # Ao NÃO colocar 'max_age', o cookie expira quando o navegador fecha
        resp.set_cookie(key="autenticado", value="true", httponly=True)
        return resp
    return RedirectResponse(url="/login", status_code=303)

@app.get("/logout")
async def logout():
    resp = RedirectResponse(url="/login")
    resp.delete_cookie("autenticado")
    return resp