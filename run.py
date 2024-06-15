from PySide6 import QtWidgets
from PySide6.QtGui import QPalette, QColor
import sys
from system_almacen.widget_carrito import CarritoCompras, SignalManager
from system_almacen.bbdd_function import tabla_compra
from system_almacen.widget_usuario import InicioSesion



  


def main():
    print('Sistema de ventas en ejecucion..')
    
    # Creacion de la tabla compra
    tabla_compra()
    
    app = QtWidgets.QApplication([])
    
    # Estilo interfaz
    paleta = QPalette()
    paleta.setColor(QPalette.Window, QColor(22, 11, 11))
    paleta.setColor(QPalette.WindowText, QColor(211, 115, 45))
    app.setPalette(paleta)
    
    # Instancia - Manejador de señal
    signal_manager = SignalManager()
    
    # Instancia - Carrito
    carrito_windows = CarritoCompras()
    
    # Instancia - Sesion
    inicio_sesion = InicioSesion(carrito_windows)
    inicio_sesion.resize(350,150)
    inicio_sesion.show()
    
    # Conectar la señal al método que maneja los nuevos productos en CarritoCompras
    # Envia señal de nuevo elemento redis
    signal_manager.nuevo_elemento_signal.connect(carrito_windows.procesar_codigo_ean)
    
    
    # Iniciar el procesamiento de la cola en un hilo
    sys.exit(app.exec())
    
   

    

    






if __name__ == "__main__":
    main()