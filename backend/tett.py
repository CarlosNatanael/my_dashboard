from app import app
from models import db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # 1. Listar utilizadores existentes
    users = User.query.all()
    
    if not users:
        print("Nenhum utilizador encontrado. Criando um novo administrador...")
        # Altere 'carlos' e 'sua_senha_aqui' para o que desejar
        new_user = User(
            username='cnat', 
            password_hash=generate_password_hash('pko6032')
        )
        db.session.add(new_user)
        db.session.commit()
        print(f"Utilizador 'cnat' criado com a senha 'pko6032'!")
    else:
        print("Utilizadores encontrados no sistema:")
        for u in users:
            print(f"- Nome de utilizador: {u.username}")
        
        # Se quiser resetar a senha do primeiro que encontrou:
        user_to_fix = users[0]
        user_to_fix.password_hash = generate_password_hash('pko6032')
        db.session.commit()
        print(f"\nSenha do utilizador '{user_to_fix.username}' resetada para: pko6032")