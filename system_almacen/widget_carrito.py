from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QObject, Signal, Qt
import redis, json
from system_almacen.dialogs import DialogoAgregarProducto,DialogoCantidad, AgregarUsuarioDialog, EliminarUsuarioDialog
from system_almacen.bbdd_function import eliminar_todos_los_productos, conectar, conectar_y_consultar,agregar_a_tabla_compras, imprimir_factura 

redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)


##################      Manejador de señal     #######################

class SignalManager(QObject):
    # Definir una señal personalizada para notificar cambios
    nuevo_elemento_signal = Signal(str, dict)

    def __init__(self):
        super().__init__()

        # Conectar con Redis y suscribirse al canal específico
        self.redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.pubsub = self.redis_db.pubsub()
        self.pubsub.subscribe('cambios_estructura_datos')

        # Iniciar un hilo o bucle para escuchar mensajes en segundo plano
        self.pubsub.subscribe(**{'cambios_estructura_datos': self.manejar_mensaje})
        self.listen_thread = self.pubsub.run_in_thread(sleep_time=0.001, daemon=True)

    def manejar_mensaje(self, mensaje):
        if mensaje['type'] == 'message':
            datos_producto = mensaje['data'].decode('utf-8')

            try:
                producto = json.loads(datos_producto)
                clave_producto = producto['ean']
                self.nuevo_elemento_signal.emit(clave_producto, producto)
            except json.decoder.JSONDecodeError as e:
                print(f"Error al decodificar JSON: {e}")


    def cerrar_conexion(self):
        # Detener la suscripción y cerrar la conexión con Redis
        self.listen_thread.stop()
        self.pubsub.close()



################    Carrito de compras    #######################
class CarritoCompras(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()
        
         # Increase the font size of the table to 20
        font = QtGui.QFont()
        font.setPointSize(25)
        self.tabla_compra.setFont(font)
        self.installEventFilter(self)
        self.dialogo_agregar_producto = None
        

    def init_ui(self):
        # Configuración de la ventana principal
        self.setWindowTitle("Negocio")

        # Crear un widget para contener la tabla y los botones
        widget = QtWidgets.QWidget(self)
        self.setCentralWidget(widget)

        # Crear un menú desplegable en la barra de menú
        self.menu_bar = self.menuBar()
        self.admin_menu = self.menu_bar.addMenu("Usuarios")
        self.base_de_datos = self.menu_bar.addMenu("Base de datos")
        
        # Configurar la visibilidad inicial del menú
        self.menu_bar.setVisible(False)
        
        
        # Agregar acciones al menú desplegable
        self.opcion_admin_1 = self.admin_menu.addAction("Agregar usuarios")
        self.opcion_admin_1.triggered.connect(self.abrir_dialog_agregar_usuario)

        
        
        # Agregar acción al menú desplegable para eliminar usuarios
        self.eliminar_usuarios_action = self.admin_menu.addAction("Eliminar usuarios")
        self.eliminar_usuarios_action.triggered.connect(self.abrir_dialog_eliminar_usuario)

        self.abrir_base = self.base_de_datos.addAction("Abrir base de datos")
        
        
        # Crear un layout horizontal para el widget principal
        layout_principal = QtWidgets.QHBoxLayout(widget)

        # Crear un layout vertical para el widget de la izquierda (tabla)
        layout_izquierda = QtWidgets.QVBoxLayout()
        layout_principal.addLayout(layout_izquierda)

        # Agregar la tabla al layout vertical de la izquierda
        self.tabla_compra = QtWidgets.QTableWidget(widget)
        layout_izquierda.addWidget(self.tabla_compra)

        # Configurar las columnas de la tabla
        self.tabla_compra.setColumnCount(6)
        self.tabla_compra.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tabla_compra.setHorizontalHeaderLabels(['ID','EAN', 'Producto', 'Precio', 'Cantidad', 'Precio Total'])
        
        # Configurar las celdas para que no sean editables
        self.tabla_compra.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        
        
        # Adjust the width of the "Cantidad" column to fit its content
        header = self.tabla_compra.horizontalHeader()
        
        # Ajusta el ancho de la columna
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        
        
        # Ocultar las columnas de ID y EAN
        self.tabla_compra.setColumnHidden(0, True)  # Columna ID
        self.tabla_compra.setColumnHidden(1, True)  # Columna EAN

        
        # Supongamos que quieres establecer la altura de todas las filas a 50 píxeles
        height = 40  # Altura deseada en píxeles

        # Obtener el encabezado vertical
        vertical_header = self.tabla_compra.verticalHeader()

        # Establecer la altura predeterminada de todas las filas
        vertical_header.setDefaultSectionSize(height)


        # Crear un layout vertical para el widget de la derecha (botones y etiqueta)
        layout_derecha = QtWidgets.QVBoxLayout()
        layout_principal.addLayout(layout_derecha)

        # Botón para agregar un nuevo elemento
        boton_agregar = QtWidgets.QPushButton('Agregar Elemento', widget)
        boton_agregar.clicked.connect(self.boton_agregar_clicked)
        layout_derecha.addWidget(boton_agregar)

        # Botón para cerrar la compra
        boton_cerrar_compra = QtWidgets.QPushButton('Cerrar Compra', widget)
        boton_cerrar_compra.clicked.connect(self.cerrar_compra)
        layout_derecha.addWidget(boton_cerrar_compra)
        
        

        # Etiqueta para mostrar el total de la compra
        self.etiqueta_total = QtWidgets.QLabel("Total de la Compra: $0.00", widget)
        layout_derecha.addWidget(self.etiqueta_total)


        # Agrega el botón "Cancelar compra" aquí
        cancel_button = QtWidgets.QPushButton('Cancelar compra', widget)
        cancel_button.clicked.connect(self.cancelar_compra)
        layout_derecha.addWidget(cancel_button)
        
        
        # Aplicar estilos a la etiqueta
        self.etiqueta_total.setStyleSheet(
            "QLabel {"
            "    border: 2px solid #000000;"  # Borde de 2 píxeles en color negro
            "    font-size: 40px;"  # Tamaño de la fuente a 20 puntos
            "    font-weight: bold;"  # Texto en negrita
            "    color : white;"
            "}"
        )
        
        boton_cerrar_compra.setStyleSheet("""
            QPushButton {
                background-color: #8B0000;
                color: white;
                font-size: 20px;  /* Tamaño de la fuente */
                padding: 10px;    /* Espaciado interno para aumentar el tamaño del botón */
            }
            QPushButton:hover {
                background-color: red;
                    }
        """)
        boton_agregar.setStyleSheet("""
            QPushButton {
                background-color: green;
                color: white;
                font-size: 20px;  /* Tamaño de la fuente */
                padding: 10px;    /* Espaciado interno para aumentar el tamaño del botón */
            }
            QPushButton:hover {
                background-color: #2E8B57;
                    }
        """)
        
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #003366;
                color: white;
                font-size: 20px;  /* Tamaño de la fuente */
                padding: 10px;    /* Espaciado interno para aumentar el tamaño del botón */
            }
            QPushButton:hover {
                background-color: blue;
                font-weight: bold;
                    }
        """)
        
                
                # Crear un layout vertical para el widget de la izquierda (tabla)

        # Configurar el ancho del layout de la izquierda en una relación de 3:1 respecto al layout de la derecha
        layout_principal.setStretch(0, 3)
        layout_izquierda.setStretch(0, 3)

        # Crear un layout vertical para el widget de la derecha (botones y etiqueta)

        # Configurar el ancho del layout de la derecha en una relación de 1:1 respecto al layout de la izquierda
        layout_principal.setStretch(1, 1)
        layout_derecha.setStretch(0, 1)
        
        
        # Cargar datos desde la base de datos y mostrarlos en la tabla
        self.cargar_datos_tabla_compra() 
        
        self.setFocus()
    
    def abrir_dialog_agregar_producto(self):
        
        # Si no está visible o no está creado, lo creamos
        self.dialogo_agregar_producto = DialogoAgregarProducto()
        self.dialogo_agregar_producto.finished.connect(self.dialogo_cerrado)
        self.dialogo_agregar_producto.show()
        # Verificamos si el diálogo ya está creado y aún está visible
        if self.dialogo_agregar_producto and self.dialogo_agregar_producto.isVisible():
            # Si está visible, lo traemos al frente y no creamos uno nuevo
            self.dialogo_agregar_producto.raise_()
            self.dialogo_agregar_producto.activateWindow()

           

    def dialogo_cerrado(self):
        # Este método se llama cuando el diálogo se cierra
        # Aquí puedes realizar acciones necesarias
        # Por ejemplo, limpiar campos o realizar alguna otra operación
        # También puedes restablecer el diálogo a None para permitir que se cree uno nuevo la próxima vez que se abra
        self.dialogo_agregar_producto = None
        self.abrir_dialog_agregar_producto()

    def abrir_dialog_agregar_producto(self):
        
        dialog = DialogoAgregarProducto()
        dialog.cargar_datos_tabla_compra_signal.connect(self.cargar_datos_tabla_compra)
        dialog.exec_()
        
        
    def abrir_dialog_eliminar_usuario(self):
        dialog = EliminarUsuarioDialog()
        dialog.exec_()
        
    # Metodos del carrito
    
    def abrir_dialog_agregar_usuario(self):
        dialog = AgregarUsuarioDialog()
        dialog.exec_()
    
    def keyPressEvent(self, event):
        
        # Tecla enter
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            # Obtener la celda actual
            current_item = self.tabla_compra.currentItem()
            if current_item is not None:
                row = current_item.row()
                column = current_item.column()
                if column == 4:  # Columna de la cantidad
                    self.handle_cell_changed(row, column)
        elif event.key() == QtCore.Qt.Key_Plus:
            self.boton_agregar_clicked()
        
        # Tecla suprimir
        elif event.key() == QtCore.Qt.Key_Delete:
            current_item = self.tabla_compra.currentItem()
            if current_item is not None:
                row = current_item.row()
                self.eliminar_producto(row)
                
                
    def boton_agregar_clicked(self):
        self.abrir_dialog_agregar_producto()
            
    
    def cargar_datos_tabla_compra(self):
        
        try:
            conexion = conectar()

            # Crear un cursor para ejecutar consultas
            cursor = conexion.cursor()

            # Obtener los datos de la tabla 'compra'
            cursor.execute('SELECT id,ean, descripcion, precio_unitario, cantidad, precio_total FROM compra')
            resultados = cursor.fetchall()

            # Configurar el número de filas en la tabla
            self.tabla_compra.setRowCount(len(resultados))

            # Llenar la tabla con los datos
            for fila, datos_fila in enumerate(resultados):
                for columna, valor in enumerate(datos_fila):
                    item = QtWidgets.QTableWidgetItem(str(valor))
                    self.tabla_compra.setItem(fila, columna, item)
            
             # Calcular el total de la compra
            total_compra = sum(float(datos_fila[5]) for datos_fila in resultados)
            total = round(total_compra,2)
            self.etiqueta_total.setText(f"Total ${total}")

        except Exception as error:
            print(f'Error al cargar datos en la tabla de compra: {error}')

        finally:
        # Asegurarse de cerrar el cursor y la conexión, incluso en caso de excepción
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'connection' in locals() and conexion:
                conexion.close()
    

    
    def cantidad_producto(self):
        dialogo = DialogoCantidad()
        if dialogo.exec() == QtWidgets.QDialog.Accepted:
            cantidad = dialogo.cantidad.value()
            return cantidad
        else:
            return None
        
            
    
    def eliminar_producto(self, row):
        conexion = conectar()  
        try:
            cursor = conexion.cursor()
            id = self.tabla_compra.item(row, 0).text()
            cursor.execute('DELETE FROM compra WHERE id = %s', (id,))
            conexion.commit()
            
        except Exception as e:
            print(f"Error al eliminar producto: {e}")
        finally:
            print(f'Producto con codigo {id}, eliminado de la compra')
            self.cargar_datos_tabla_compra()
            conexion.close()
    
    
    
    def cancelar_compra(self):
        
        # Crear un cuadro de diálogo de confirmación
        confirm_dialog = QMessageBox(self)
        confirm_dialog.setIcon(QMessageBox.Question)
        confirm_dialog.setWindowTitle("Confirmación de Cancelación")
        confirm_dialog.setText("¿Desea cancelar la compra?")
        confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        confirm_dialog.setDefaultButton(QMessageBox.Cancel)
        
        # Mostrar el cuadro de diálogo y esperar la respuesta del usuario
        respuesta = confirm_dialog.exec_()
        
        # Comprobar la respuesta del usuario
        if respuesta == QMessageBox.Yes:
            # Si el usuario elige 'Sí', cancelar la compra
            eliminar_todos_los_productos()

            # Actualiza contenido de la interfaz
            self.cargar_datos_tabla_compra()
        else:
            # Si el usuario elige 'Cancelar' o cierra el cuadro de diálogo, no hacer nada
            pass
            
        
        
    
    
    def handle_cell_changed(self, row, column):
        # Maneja el cambio de cantidad de un producto
        if column == 4:  # Cantidad
            new_quantity = self.cantidad_producto()
            if new_quantity:
                self.tabla_compra.item(row, column).setText(str(new_quantity))
                self.update_quantity(row, new_quantity)
        # Se podria agregar funcionalidad para otras columnas


    # Actualiza cantidad de un producto
    def update_quantity(self, row, new_quantity):
        conexion = conectar()
        try:
            cursor = conexion.cursor()
            id = self.tabla_compra.item(row, 0).text()
            
             # Obtener el precio unitario actual
            cursor.execute("SELECT precio_unitario FROM compra WHERE id = %s", (id,))
            precio_unitario = cursor.fetchone()[0]
            
            # Calcular el nuevo precio total
            nuevo_precio_total = new_quantity * precio_unitario
            
            # Actualiza la cantidad de un producto
            cursor.execute("UPDATE compra SET cantidad = %s WHERE id = %s", (new_quantity, id))
            
            # Actualizar el precio total en la tabla 'compra'
            cursor.execute("UPDATE compra SET precio_total = %s WHERE id = %s", (nuevo_precio_total, id))
            
            conexion.commit()
        except Exception as e:
            print(f"Error al actualizar la cantidad: {e}")
        finally:
            self.cargar_datos_tabla_compra()
            conexion.close()

    


            
    def cerrar_compra(self):
        print('Cerrando venta \n')      
                   
        # Elimina codigo de redis
        redis_db.flushall()
        
        # Imprime factura de compra
        imprimir_factura()
        
        # Elimina contenido de la tabla compra
        eliminar_todos_los_productos()
        
        print('Sistema listo para nueva compra')
        
        # Actualiza contenido de la interfaz
        self.cargar_datos_tabla_compra()
    
        
    def armar_producto_final(self,dict_productos):
        ean = dict_productos['ean']
        descripcion = dict_productos['descripcion']
        precio = float(dict_productos['precio'])
        cantidad = self.cantidad_producto()
        
        producto_final = {'ean':ean, 'descripcion': descripcion, 'precio': precio, 'cantidad':cantidad}
        
        return producto_final
        
    
    def procesar_codigo_ean(self, ean):
        # Consulta en base de datos por el codigo de producto
        dict_productos = conectar_y_consultar(ean)
        
        # Crea el producto con la cantidad
        producto_final = self.armar_producto_final(dict_productos)        
        ean = producto_final['ean']
        descripcion = producto_final['descripcion']
        precio = producto_final['precio']
        cantidad = producto_final['cantidad']
        
        # Agrega a tabla de compras solo si hay una cantidad
        if cantidad is not None:
            agregar_a_tabla_compras(ean, descripcion, precio, cantidad)
        
        self.cargar_datos_tabla_compra()
        
        return producto_final




    
            




