import pymysql

# Funciones relacionadas a la base de datos, como su conexion y desconexion,
#  consultar por un producto, crear tabla de compras, agregar a compras, eliminar productos.



# Función para conectar a la base de datos
def conectar():
    host = 'localhost' 
    usuario = 'usuario'
    contrasena = 'contraseña'
    base_datos = 'productosDeAlmacen'

    try:
        conexion = pymysql.connect(
            host=host,
            user=usuario,
            password=contrasena,
            database=base_datos
        )
        return conexion
    except Exception as e:
        print(f"Error de conexión: {str(e)}")
        return None

# Función para desconectar de la base de datos
def desconectar(conexion):
    if conexion and conexion.open:
        conexion.close()



# Función para consultar un producto por su código EAN
def conectar_y_consultar(codigo_ean):
    conexion = conectar()
    if not conexion:
        return None

    try:
        with conexion.cursor() as cursor:
            consulta = f"SELECT * FROM lista_de_productos WHERE ean = '{codigo_ean}'"
            cursor.execute(consulta)
            fila = cursor.fetchone()

            if fila:
                nombres_columnas = ['id', 'ean', 'descripcion', 'cantidad', 'unidad', 'precio']
                dict_resultados = dict(zip(nombres_columnas, fila))
                return dict_resultados
            else:
                return None

    except Exception as e:
        print(f"Error al ejecutar la consulta: {str(e)}")
        return None

    finally:
        desconectar(conexion)



# Función para crear la tabla 'compra' si no existe
def tabla_compra():
    conexion = conectar()
    if not conexion:
        return

    try:
        with conexion.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS compra (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ean VARCHAR(255) NOT NULL,
                    descripcion VARCHAR(255) NOT NULL,
                    precio_unitario DECIMAL(10, 2) NOT NULL,
                    cantidad INT NOT NULL,
                    precio_total DECIMAL(10, 2) NOT NULL
                )
            ''')

    except Exception as e:
        print(f"Error al ejecutar la consulta: {str(e)}")

    finally:
        desconectar(conexion)
        


# Función para agregar un producto a la tabla 'compra'
def agregar_a_tabla_compras(ean, descripcion, precio_unitario, cantidad):
    conexion = conectar()
    if not conexion:
        return

    try:
        precio_total = precio_unitario * cantidad

        with conexion.cursor() as cursor:
            cursor.execute('''
                INSERT INTO compra (ean, descripcion, precio_unitario, cantidad, precio_total)
                VALUES (%s, %s, %s, %s, %s)
            ''', (ean, descripcion, precio_unitario, cantidad, precio_total))

        conexion.commit()
        print(f'Producto con EAN {ean} agregado a la tabla compra.')

    except Exception as error:
        print(f'Error al agregar producto a la tabla compra: {error}')

    finally:
        desconectar(conexion)



# Función para eliminar todos los productos de la tabla 'compra'
def eliminar_todos_los_productos():
    conexion = conectar()
    if not conexion:
        return

    try:
        with conexion.cursor() as cursor:
            cursor.execute('DELETE FROM compra')
        conexion.commit()
        print('Todos los elementos de la tabla compra han sido eliminados.')

    except Exception as error:
        print(f'Error al eliminar elementos de la tabla compra: {error}')

    finally:
        desconectar(conexion)


def imprimir_factura():
    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute('SELECT * FROM compra')
            compra = cursor.fetchall()
            print('Gracias por su compra.\n ')

            total = 0
            for producto in compra:
                # Imprime toda la tupla sin desempaquetar
                #print(f'Producto: {producto}')

                # Si necesitas desempaquetar valores específicos, ajusta según la estructura real de tu base de datos
                # Por ejemplo, si la tupla tiene más de 4 elementos y solo necesitas los primeros 4, puedes hacer:
                id, ean, descripcion, precio, cantidad, precio_total, *_ = producto
                print(f'{descripcion} ${precio} | Cantidad: {cantidad} | Precio Total: ${precio_total} \n')

                total += precio_total
            print(f'Total: {total}')
    except Exception as error:
        print(f'Error imprimir factura: {error}')
    finally:
        desconectar(conexion)
        
        
def buscar_descripcion(texto_ingresado):
    try:
        # Conectar a la base de datos
        conexion = conectar()
        
        
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor()

        # Preparar la consulta SQL para buscar coincidencias en palabrasClave usando Full-text search
        query = "SELECT nameComplete, ean  FROM lista_de_productos WHERE MATCH(nameComplete) AGAINST (%s IN BOOLEAN MODE)"
        
        
        # Ejecutar la consulta SQL
        cursor.execute(query, (texto_ingresado,))
        
        # Obtener los resultados de la consulta
        resultados = cursor.fetchall()[:20] 
        
        
        return resultados

    except Exception as e:
        print(f"Error al buscar descripción en la base de datos: {e}")
        return []
    finally:
        desconectar(conexion)
        
        
def buscar_codigo(ean):
    try:
        # Conectar a la base de datos
        conexion = conectar()
        
        
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor()

        query = "SELECT nameComplete, ean  FROM lista_de_productos WHERE ean LIKE %s"
        
         # Agregar comodines alrededor del código EAN para la búsqueda parcial
        ean_parcial = f"%{ean}%"
        
        
        # Ejecutar la consulta SQL
        cursor.execute(query, (ean_parcial,))
        
        # Obtener los resultados de la consulta
        resultados = cursor.fetchall()[:20] 
        
        print(resultados)
        
        
        return resultados

    except Exception as e:
        print(f"Error al buscar descripción en la base de datos: {e}")
        return []
    finally:
        desconectar(conexion)
        


def armar_producto(diccionario_producto):
    ean = diccionario_producto['ean']
    descripcion = diccionario_producto['descripcion']
    precio = float(diccionario_producto['precio'])
    cantidad = 1
    
    producto_final = {'ean':ean, 'descripcion': descripcion, 'precio': precio, 'cantidad':cantidad}
    
    return producto_final


