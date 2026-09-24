"""
=============================================================
Sistema de Administración y Reserva de Motel (ver. 1.0)
=============================================================
Lenguaje de programación: Python

Descripción general:
Software de escritorio desarrollado en Python. Su función principal es la 
gestión en tiempo real de un complejo de 13 habitaciones (divididas en 
sencillas, suites y VIP), permitiendo el control de estados (Disponible, 
Ocupado, En espera), cálculo de tarifas por hora, registro de clientes 
con códigos únicos, control de tiempos y un módulo de administración 
protegido por contraseña.

Interfaz Gráfica (GUI):
De momento, la interfaz gráfica de usuario (GUI) está construida íntegramente 
utilizando la librería nativa Tkinter de Python, estructurando un mapa 
interactivo con Canvas, paneles laterales e inferiores de control.

Arquitectura de Software (Patrón MVC):
El sistema se encuentra estructurado bajo el patrón Modelo-Vista-Controlador:
- Modelo (MotelModelo): Gestiona la lógica de datos, los estados de las 
  habitaciones, los registros de usuarios y las credenciales de acceso.
- Vista (MotelVista): Renderiza la interfaz gráfica de usuario (GUI), 
  incluyendo el plano interactivo (Canvas), paneles y elementos visuales.
- Controlador (MotelControlador): Actúa como intermediario gestionando 
  eventos de usuario, lógica de negocio y el bucle de actualización en vivo.

Versión: 1.0
=============================================================
"""