from system_almacen.bbdd_function import conectar, desconectar

import bcrypt


# Funciones relacionadas a las contraseñas y permisos.




# Función para generar un hash de la contraseña con sal utilizando bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


        
        

def verificar_contrasena(usuario, contrasena):
    try:
        conexion = conectar()

        with conexion.cursor() as cursor:

            # Consulta para obtener la contraseña hash y la sal del usuario
            consulta = "SELECT password FROM usuarios WHERE nombre_usuario = %s"
            cursor.execute(consulta, (usuario,))
            resultado = cursor.fetchone()

            if resultado:
                # Obtener la contraseña de la base de datos
                contrasena_hash = resultado[0]
                password_bytes = contrasena_hash.encode('utf-8')
                contraseña_hashed = contrasena.encode('utf-8')
                # Verificar si la contraseña ingresada es correcta
                if bcrypt.checkpw(contraseña_hashed, password_bytes):
                    return True
                else:
                    return None
                    
            else:
                print("Usuario no encontrado.")

            cursor.close()
            conexion.close()

    except conexion.Error as error:
        print("Error al conectar a la base de datos:", error)
    finally:
        desconectar(conexion)


def verificar_permisos(nombre_usuario):
    conexion = conectar()
    with conexion.cursor() as cursor:
        try:
            # Consulta para obtener la contraseña hash y la sal del usuario
            consulta = "SELECT es_admin FROM usuarios WHERE nombre_usuario = %s"
            cursor.execute(consulta, (nombre_usuario,))
            resultado = cursor.fetchone()
            if resultado is not None:
                resultado = resultado[0]
                if resultado > 0:
                    return True
            

        except conexion.Error as error:
            print("Error al conectar a la base de datos:", error)
            print('No tenes permiso pa')
        finally:
            desconectar(conexion)