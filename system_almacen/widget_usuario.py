from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from system_almacen.password_funct import verificar_contrasena, verificar_permisos



class InicioSesion(QWidget):
    def __init__(self, carrito_compras,parent=None):
        super().__init__(parent)
        
        self.carrito_compras = carrito_compras
        
        self.setWindowTitle('Inicio de Sesión')

        self.label_usuario = QLabel('Usuario:')
        self.input_usuario = QLineEdit()
        self.label_contrasena = QLabel('Contraseña:')
        self.input_contrasena = QLineEdit()
        self.input_contrasena.setEchoMode(QLineEdit.Password)

        self.btn_ingresar = QPushButton('Ingresar')
        self.btn_ingresar.clicked.connect(self.verificar_ingreso)
        
        
        self.widget_usuario_estandar = QWidget(self)
        self.widget_usuario_estandar.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label_usuario)
        layout.addWidget(self.input_usuario)
        layout.addWidget(self.label_contrasena)
        layout.addWidget(self.input_contrasena)
        layout.addWidget(self.btn_ingresar)



    def verificar_ingreso(self):
        nombre_usuario = self.input_usuario.text()
        
        # Autentificacion de usuario
        es_admin = verificar_contrasena(nombre_usuario, self.input_contrasena.text())

        if es_admin is not None:
            # Verifica los permisos del usuario
            es_admin = verificar_permisos(nombre_usuario) 
            # Agregar funcion que determina la interfaz en base a si es admin o cajero
            self.abrir_interfaz(es_admin)
            self.carrito_compras.setWindowTitle(f"Negocio - Usuario: {nombre_usuario}")
        else:
            QMessageBox.warning(self, 'Error de autenticación', 'Credenciales incorrectas.')



    # Interfaz grafica para usuario admin y cajero
    def abrir_interfaz(self, es_admin):
        # Si es admin, se muestra la barra de menu
        self.carrito_compras.showMaximized()
        if es_admin:   
            self.carrito_compras.menu_bar.setVisible(True)  # Mostrar menú para admin
        self.close()  
 
    
    

