from system_almacen.bbdd_function import conectar, desconectar
from system_almacen.password_funct import hash_password



# Función para crear la tabla 'usuarios' si no existe
def datos_usuarios():
    conexion = conectar()
    if not conexion:
        return

    try:
        with conexion.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre_usuario VARCHAR(255) NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    es_admin BOOLEAN NOT NULL,
                    UNIQUE (nombre_usuario)
                )
            ''')

    except Exception as e:
        print(f"Error al ejecutar la consulta: {str(e)}")

    finally:
        desconectar(conexion)



def crear_usuario(nombre_usuario, password, es_admin):
    conexion = conectar()
    # Nombre de usuario y contraseña para el nuevo usuario
    username = nombre_usuario

    # Hashear la contraseña con bcrypt y agregar sal
    hashed_password = hash_password(password)
    
    tipo_usuario = 0
    
    if es_admin == 'Administrador':
        tipo_usuario =+ 1
        
    try:
        with conexion.cursor() as cursor:
            # Insertar el nuevo usuario en la base de datos
            query = "INSERT INTO usuarios (nombre_usuario, password, es_admin) VALUES (%s, %s, %s)"
            data = (username, hashed_password, tipo_usuario)
            cursor.execute(query, data)
            conexion.commit()
            return True
    except Exception as e:
        # Eleva error al crear usuario
        raise e

    finally:
        desconectar(conexion)
        
        