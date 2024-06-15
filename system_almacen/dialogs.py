from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QWidget, QTableWidget,QTableWidgetItem
from PySide6.QtCore import Signal, QStringListModel
from PySide6.QtWidgets import QWidget, QComboBox,QVBoxLayout, QLabel, QLineEdit, QPushButton
from system_almacen.bbdd_function import armar_producto,conectar, desconectar, buscar_descripcion, buscar_codigo,  conectar_y_consultar,agregar_a_tabla_compras
from system_almacen.password_funct import verificar_permisos,verificar_contrasena
from system_almacen.user_function import crear_usuario
import functools

class DialogoCantidad(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cantidad producto")

        self.cantidad = QtWidgets.QSpinBox()
        self.cantidad.setRange(1, 999)

        # Etiquetas para los campos

        label_cantidad = QtWidgets.QLabel("Cantidad:")


        # Botones para agregar o cancelar
        boton_agregar = QtWidgets.QPushButton("Agregar")
        boton_cancelar = QtWidgets.QPushButton("Cancelar")
        

        # Diseño del diálogo
        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(label_cantidad, 1, 0)
        layout.addWidget(self.cantidad, 1, 1)
        layout.addWidget(boton_agregar, 3, 0)
        layout.addWidget(boton_cancelar, 3, 1)

        boton_agregar.clicked.connect(self.aceptar)
        boton_cancelar.clicked.connect(self.reject)

        # Centrar el diálogo en la pantalla
        self.resize(300, 100)  # Establecer un tamaño inicial para el diálogo
        self.center_on_screen()

    def resizeEvent(self, event):
        # Llamado cuando el diálogo cambia de tamaño
        self.center_on_screen()

    def center_on_screen(self):
        # Obtener la pantalla principal
        screen = QtWidgets.QApplication.primaryScreen()

        # Obtener la geometría de la pantalla
        screen_geometry = screen.geometry()

        # Calcular la posición central del diálogo
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2

        # Establecer la posición del diálogo
        self.setGeometry(x, y, self.width(), self.height())
        
    def aceptar(self):
        cantidad = self.cantidad.value()
        # Agregar lógica para guardar la cantidad en la lista
        self.accept()
        
class DialogoAgregarProducto(QtWidgets.QDialog):
    cargar_datos_tabla_compra_signal = Signal()
    
    
    def __init__(self):
        
        
        super().__init__()

        self.setWindowTitle("Agregar Producto")

        # Campos de entrada para el nuevo producto
        self.codigo_ean = QtWidgets.QLineEdit()
        self.descripcion = QtWidgets.QLineEdit()
        
       

        # Etiquetas para los campos
        label_codigo = QtWidgets.QLabel("Codigo:")
        label_descripcion = QtWidgets.QLabel("Descripción:")

        # Botones para agregar o cancelar
        boton_agregar = QtWidgets.QPushButton("Agregar")
        boton_cancelar = QtWidgets.QPushButton("Cancelar")

        # Layout para los campos de entrada
        layout_campos = QtWidgets.QGridLayout()
        layout_campos.addWidget(label_codigo, 0, 0)
        layout_campos.addWidget(self.codigo_ean, 0, 1)
        layout_campos.addWidget(label_descripcion, 1, 0)
        layout_campos.addWidget(self.descripcion, 1, 1)
       

        # Layout principal
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(layout_campos)

        # Layout para la tabla
        tabla_layout = QtWidgets.QVBoxLayout()
        self.tabla_productos = QtWidgets.QTableWidget()
        self.tabla_productos.setColumnCount(2)  # Dos columnas: Descripción y Precio
        self.tabla_productos.setHorizontalHeaderLabels(["Descripcion","Codigo"])
        tabla_layout.addWidget(self.tabla_productos)
        
        # Configurar las celdas para que no sean editables
        self.tabla_productos.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        main_layout.addLayout(tabla_layout)
        main_layout.addWidget(boton_agregar)
        main_layout.addWidget(boton_cancelar)

        boton_agregar.clicked.connect(self.aceptar)
        boton_cancelar.clicked.connect(self.reject)

        self.setMinimumSize(600, 300)
        
        self.codigo_ean.textChanged.connect(self.busqueda_por_codigo)
        

        # Conexión de la señal textChanged para buscar coincidencias
        self.descripcion.textChanged.connect(self.autocompletar_descripcion)
        
        self.tabla_productos.cellClicked.connect(self.tabla_celda_clicked)
    
    
    def keyPressEvent(self, event):
        
        # Tecla enter
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            # Obtener la celda actual
            current_item = self.tabla_productos.currentItem()
            if current_item is not None:
                row = current_item.row()
                column = current_item.column()
                if column == 1:  # Columna de la cantidad
                    self.handle_cell_changed(row, column)
                    
                    
    def handle_cell_changed(self, row, column):
        # Maneja el cambio de cantidad de un producto
        if column == 1:  # Cantidad
            codigo_ean = self.tabla_productos.item(row, column).text()
            self.agregar_producto(codigo_ean)
            self.close()
            
            print(f"Código EAN seleccionado: {codigo_ean}")

    def tabla_celda_clicked(self, row, column):
        if column == 1:  # Si se hizo clic en la columna del código EAN
            codigo_ean = self.tabla_productos.item(row, column).text()
            self.agregar_producto(codigo_ean)
            self.close()
            print(f"Código EAN seleccionado: {codigo_ean}")
            
    def agregar_producto(self, codigo):
        producto = conectar_y_consultar(codigo)
        if producto is not None:
            producto_final = armar_producto(producto)
            ean = producto_final['ean']
            descripcion = producto_final['descripcion']
            precio = producto_final['precio']
            cantidad = producto_final['cantidad']
            producto_armado = agregar_a_tabla_compras(ean,descripcion, precio,cantidad)
            self.cargar_datos_tabla_compra_signal.emit()
       
    def aceptar(self):
        
        # Agregar lógica para guardar el nuevo producto en la lista o base de datos
        self.accept()
        
    def autocompletar_descripcion(self, texto_ingresado):
        # Realizar la búsqueda en la base de datos para encontrar coincidencias
        # y establecer las sugerencias de autocompletar
        # Supongamos que tienes una función para buscar en la base de datos llamada buscar_descripcion
        if len(texto_ingresado) >= 4:
            sugerencias = buscar_descripcion(texto_ingresado)[:20] 
            self.actualizar_tabla(sugerencias)
            
    def busqueda_por_codigo(self, ean):
        # Realizar la búsqueda en la base de datos para encontrar coincidencias
        # y establecer las sugerencias de autocompletar
        # Supongamos que tienes una función para buscar en la base de datos llamada buscar_descripcion
        
        sugerencias = buscar_codigo(ean)[:20] 
        self.actualizar_tabla(sugerencias)
    

            
    def actualizar_tabla(self, sugerencias):
        
        print(f'SUGERENCIAS{sugerencias}')
        
        self.tabla_productos.setRowCount(len(sugerencias))
        for i, (nombre, ean) in enumerate(sugerencias):
            # Crear objetos QTableWidgetItem con la descripción y el precio del producto
            descripcion_item = QTableWidgetItem(nombre)
            ean_item = QTableWidgetItem(ean)
            
            # Establecer los elementos en las columnas correspondientes de la fila actual
            self.tabla_productos.setItem(i, 0, descripcion_item)
            self.tabla_productos.setItem(i, 1, ean_item)
        # Ajustar el ancho de la columna de descripción para que se ajuste al contenido
        self.tabla_productos.resizeColumnsToContents()


class AgregarUsuarioDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agregar Usuario")

        # Crear widgets para el formulario
        self.label_nombre_usuario = QtWidgets.QLabel("Nombre de usuario:")
        self.input_nombre_usuario = QtWidgets.QLineEdit()
        self.label_contrasena = QtWidgets.QLabel("Contraseña:")
        self.input_contrasena = QtWidgets.QLineEdit()
        self.input_contrasena.setEchoMode(QtWidgets.QLineEdit.Password)  # Configurar el campo de contraseña
        self.label_comprobar_contrasena = QtWidgets.QLabel("Comprobar contraseña:")
        self.input_comprobar_contrasena = QtWidgets.QLineEdit()
        self.input_comprobar_contrasena.setEchoMode(QtWidgets.QLineEdit.Password)  # Configurar el campo de contraseña
        self.boton_agregar = QtWidgets.QPushButton("Agregar usuario")

        # Crear un combo box para seleccionar el tipo de usuario
        self.combo_tipo_usuario = QComboBox()
        self.combo_tipo_usuario.addItems(["Administrador", "Cajero"])
        
        
        
        # Configurar el diseño del formulario
        layout = QtWidgets.QVBoxLayout()
        # User
        layout.addWidget(self.label_nombre_usuario)
        layout.addWidget(self.input_nombre_usuario)
        # Password
        layout.addWidget(self.label_contrasena)
        layout.addWidget(self.input_contrasena)
        layout.addWidget(self.label_comprobar_contrasena)
        layout.addWidget(self.input_comprobar_contrasena)
        # Agregar el combo box a la interfaz
        layout.addWidget(self.combo_tipo_usuario)
        # Boton agregar
        layout.addWidget(self.boton_agregar)
        
        # Establece los widgets anteriores
        self.setLayout(layout)
        
        # Conectar el clic del botón al método para agregar usuario
        self.boton_agregar.clicked.connect(self.agregar_usuario_signal)
        
        self.setMinimumSize(300, 300)
        
       
    def agregar_usuario_signal(self):
        # Solo debe agregar al usuario si tiene los permisos de admin
        dialog = PasswordCheck()
        dialog.autenticacion_exitosa.connect(lambda: self.agregar_usuario())
        dialog.exec_()
    
    
    def agregar_usuario(self):
        # Obtener los datos ingresados
        nombre_usuario = self.input_nombre_usuario.text()
        contrasena = self.input_contrasena.text()
        comprobar_contrasena = self.input_comprobar_contrasena.text()
        
        if not nombre_usuario:
            QtWidgets.QMessageBox.warning(self, "Error", "Por favor ingresa un nombre de usuario.")
            return
        
        elif not (contrasena and comprobar_contrasena) or contrasena != comprobar_contrasena:
            QtWidgets.QMessageBox.warning(self, "Error", "Las contraseñas deben coincidir.")
            return
        

        # Obtener el tipo de usuario seleccionado
        tipo_usuario = self.combo_tipo_usuario.currentText()
        
        # Llamar a la función para crear usuario con los datos ingresados
        try:
            if crear_usuario(nombre_usuario, contrasena, tipo_usuario):
                QtWidgets.QMessageBox.information(self, "Éxito", "Usuario agregado con éxito.")
                # Cierra la ventana
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Puede que el usuario ya exista. \nError especifico: {str(e)}")
        finally:
            self.close()
            
        

class EliminarUsuarioDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Eliminar Usuario")

        # Crear una tabla para mostrar los usuarios
        self.tabla_usuarios = QtWidgets.QTableWidget()
        self.tabla_usuarios.setColumnCount(2)  # Nombre de usuario y botón de eliminar
        self.tabla_usuarios.setHorizontalHeaderLabels(["Nombre de usuario", "Eliminar"])
        self.tabla_usuarios.horizontalHeader().setStretchLastSection(True)
        
        # Ajustar el ancho de las columnas al contenido de los títulos
        self.tabla_usuarios.resizeColumnsToContents()

        # Crear un botón para cerrar el diálogo
        self.boton_cerrar = QtWidgets.QPushButton("Cerrar")

        # Configurar el diseño del diálogo
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.tabla_usuarios)
        layout.addWidget(self.boton_cerrar)
        self.setLayout(layout)

        # Conectar clics de botón a métodos
        self.boton_cerrar.clicked.connect(self.close)

        # Cargar usuarios al iniciar el diálogo
        self.cargar_usuarios()
    
        
        # Establecer tamaño mínimo y máximo del diálogo
        self.setMinimumSize(400, 300)
        self.setMaximumSize(500, 500)
        
        
    def eliminar_usuario2(self, nombre_usuario):
        # Solo debe eliminar al usuario si tiene los permisos de admin
        dialog = PasswordCheck()
        dialog.autenticacion_exitosa.connect(lambda: self.eliminar_usuario(nombre_usuario))
        dialog.exec_()
    
    def eliminar_usuario(self, nombre_usuario):
        # Conectar a la base de datos
        conexion = conectar()
        
        try:
            with conexion.cursor() as cursor:
                # Consulta para eliminar el usuario
                consulta = "DELETE FROM usuarios WHERE nombre_usuario = %s"
                cursor.execute(consulta, (nombre_usuario,))
                # Confirmar la eliminación
                conexion.commit()
                print("Usuario eliminado:", nombre_usuario)
                QtWidgets.QMessageBox.information(self, "Éxito", "Usuario eliminado con éxito.")
                
                
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Error al eliminar usuario: {str(e)}")
        finally:
            # Cerrar la conexión a la base de datos
            desconectar(conexion)
            self.close()



    def cargar_usuarios(self):
        conexion = conectar()
        
        try:
            with conexion.cursor() as cursor:
                consulta = "SELECT nombre_usuario FROM usuarios"
                cursor.execute(consulta)
                usuarios = cursor.fetchall()

                self.tabla_usuarios.setRowCount(len(usuarios))
                for i, usuario in enumerate(usuarios):
                    nombre_usuario = usuario[0]
                    self.tabla_usuarios.setItem(i, 0, QtWidgets.QTableWidgetItem(nombre_usuario))
                    boton_eliminar = QtWidgets.QPushButton("Eliminar")
                    boton_eliminar.clicked.connect(functools.partial(self.eliminar_usuario2, nombre_usuario))
                    self.tabla_usuarios.setCellWidget(i, 1, boton_eliminar)
                    
                    boton_eliminar.setStyleSheet("""
                    QPushButton {
                        background-color: #8B0000;
                        color: white;
                    }
                    QPushButton:hover {
                        background-color: red;
                            }
                """)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Error al eliminar usuario: {str(e)}")
        finally:
            desconectar(conexion)
            
            

class PasswordCheck(QtWidgets.QDialog):
    autenticacion_exitosa = Signal()
    
    def __init__(self,):
        super().__init__()
        
        
        self.setWindowTitle('Comprobacion de Administrador')

        self.label_usuario = QLabel('Usuario:')
        self.input_usuario = QLineEdit()
        self.label_contrasena = QLabel('Contraseña:')
        self.input_contrasena = QLineEdit()
        self.input_contrasena.setEchoMode(QLineEdit.Password)

        self.btn_ingresar = QPushButton('Ingresar')
        self.btn_ingresar.clicked.connect(self.verificar_ingreso)
        
        
        self.widget_usuario_estandar = QWidget(self)
        self.widget_usuario_estandar.setWindowTitle("Nuevo Widget")
        self.widget_usuario_estandar.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label_usuario)
        layout.addWidget(self.input_usuario)
        layout.addWidget(self.label_contrasena)
        layout.addWidget(self.input_contrasena)
        layout.addWidget(self.btn_ingresar)
        
        
        # Establecer tamaño mínimo y máximo del diálogo
        self.setMinimumSize(400, 200)
        self.setMaximumSize(450, 250)
        
    def verificar_ingreso(self):
        nombre_usuario = self.input_usuario.text()
        

        if verificar_permisos(nombre_usuario):
            tipo_usuario = verificar_contrasena(nombre_usuario, self.input_contrasena.text())
            if tipo_usuario is not None:
                print(f'TIPO DE USUARIO: {tipo_usuario}')
                self.autenticacion_exitosa.emit()  # Emitir la señal de autenticación exitosa
                self.accept()  # Cerrar el diálogo
            else:
                QtWidgets.QMessageBox.warning(self, 'Error de autenticación', 'Credenciales incorrectas.')
                return




