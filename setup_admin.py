from database import SessionLocal, User

def criar_admin():
    db = SessionLocal()
    
    # Define aqui o teu login e senha de mestre
    username_admin = "LinuxStore" 
    senha_admin = "linuxstoreplay817"

    # Verifica se já existe para não duplicar
    usuario_existe = db.query(User).filter(User.username == username_admin).first()

    if not usuario_existe:
        novo_admin = User(
            username=username_admin,
            password=senha_admin,
            is_admin=True  # ISTO É O QUE TE DÁ PODERES NO SITE
        )
        db.add(novo_admin)
        db.commit()
        print(f"Sucesso: O utilizador Mestre '{username_admin}' foi criado!")
    else:
        print(f"⚠️ Aviso: O utilizador '{username_admin}' já existe no banco de dados.")
    
    db.close()

if __name__ == "__main__":
    criar_admin()