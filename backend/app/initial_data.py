# backend/app/initial_data.py

from app.db.coneccion import SessionLocal
from app.services.rol_service import create_role, get_role_by_name
from app.services.usuario_service import create_user, assign_role_to_user
from app.schemas.rol_schema import RoleCreate
from app.schemas.usuario_schema import UserCreate
from app.models.usuario_model import Usuario

def initialize_data():
    """
    Verifica la existencia del rol 'admin' y del usuario administrador.
    Si no existen, los crea y asigna el rol correspondiente.
    """
    db = SessionLocal()
    try:
        # 1. Crear el rol 'admin' si no existe
        admin_role = get_role_by_name(db, "admin")
        if not admin_role:
            role_data = RoleCreate(nombre_rol="admin")
            admin_role = create_role(db, role_data)  # Crea el rol 'admin'

        # 2. Crear el usuario admin si no existe
        admin_email = "admin@example.com"
        existing_admin_user = db.query(Usuario).filter(Usuario.correo == admin_email).first()
        if not existing_admin_user:
            user_data = UserCreate(
                nombre="Admin",
                apellido="Master",
                correo=admin_email,
                password="admin123"  # Contraseña en texto plano (hasheada al crear)
            )
            admin_user = create_user(db, user_data)
        else:
            admin_user = existing_admin_user

        # 3. Asignar el rol 'admin' al usuario
        assign_role_to_user(db, admin_user.id, "admin")

    finally:
        db.close()
