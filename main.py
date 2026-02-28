from fastapi import FastAPI, Request, Form, Response, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import database 

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- HOME ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    autenticado = request.cookies.get("autenticado")
    
    if not user_id or autenticado != "true":
        return RedirectResponse(url="/login")

    user = db.query(database.User).filter(database.User.id == int(user_id)).first()
    if not user:
        return RedirectResponse(url="/login")

    meus_clientes = db.query(database.Cliente).filter(database.Cliente.owner_id == user.id).all()
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "clientes": meus_clientes,
        "is_admin": user.is_admin,
        "user_valor_ativo": user.valor_ativo # <--- ENVIANDO PARA O HTML
    })

# --- SALVAR VALOR DO ATIVO ---
@app.post("/salvar_ativo")
async def salvar_ativo(request: Request, valor: float = Form(...), db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id: return RedirectResponse(url="/login", status_code=303)

    user = db.query(database.User).filter(database.User.id == int(user_id)).first()
    if user:
        user.valor_ativo = valor
        db.commit()
    return RedirectResponse(url="/", status_code=303)

# --- ADICIONAR CLIENTE (COM CAMPO USUÁRIO) ---
@app.post("/adicionar_cliente")
async def add_cliente(
    request: Request,
    nome: str = Form(...), 
    usuario: str = Form(...), # <--- NOVO
    valor: float = Form(...), 
    db: Session = Depends(get_db)
):
    user_id = request.cookies.get("user_id")
    if not user_id: return RedirectResponse(url="/login", status_code=303)

    novo = database.Cliente(
        nome=nome, 
        usuario=usuario, # <--- NOVO
        valor=valor, 
        status="receber", 
        owner_id=int(user_id)
    )
    db.add(novo)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

# --- STATUS E DELETAR (IGUAIS) ---
@app.get("/status/{cliente_id}")
async def alternar_status(request: Request, cliente_id: int, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    dado = db.query(database.Cliente).filter(database.Cliente.id == cliente_id, database.Cliente.owner_id == int(user_id)).first()
    if dado:
        dado.status = "pago" if dado.status == "receber" else "receber"
        db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/deletar/{cliente_id}")
async def deletar_cliente(request: Request, cliente_id: int, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    dado = db.query(database.Cliente).filter(database.Cliente.id == cliente_id, database.Cliente.owner_id == int(user_id)).first()
    if dado:
        db.delete(dado)
        db.commit()
    return RedirectResponse(url="/", status_code=303)

# --- LOGIN / LOGOUT / REGISTRAR (SEM ALTERAÇÕES) ---
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request): return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(database.User).filter(database.User.username == username, database.User.password == password).first()
    if user:
        resp = RedirectResponse(url="/", status_code=303)
        resp.set_cookie(key="autenticado", value="true", httponly=True)
        resp.set_cookie(key="user_id", value=str(user.id), httponly=True)
        return resp
    return RedirectResponse(url="/login?erro=1", status_code=303)

@app.get("/logout")
async def logout():
    resp = RedirectResponse(url="/login")
    resp.delete_cookie("autenticado")
    resp.delete_cookie("user_id")
    return resp

@app.get("/registrar", response_class=HTMLResponse)
async def registrar_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    user = db.query(database.User).filter(database.User.id == int(user_id)).first()
    if not user or not user.is_admin: return RedirectResponse(url="/")
    return templates.TemplateResponse("registrar.html", {"request": request})

@app.post("/registrar")
async def register(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    admin_id = request.cookies.get("user_id")
    admin = db.query(database.User).filter(database.User.id == int(admin_id)).first()
    if not admin or not admin.is_admin: return RedirectResponse(url="/", status_code=303)
    novo_usuario = database.User(username=username, password=password, is_admin=False)
    db.add(novo_usuario)
    db.commit()
    return RedirectResponse(url="/", status_code=303)