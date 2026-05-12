Se tiene la arquitectura basica de una aplicación django con sus template boostrap.

El sistema manejará el control de acceso al aula de computación y el control de pagos en la cafetereia

Su arquitectura está pensada para funcionar con 2 sistemas independientes: control de acceso y control de pagos
realizados con esp32 y rfid, los sistemas esp32 tendrán la nomenclatura esp32door y esp32cafe

El sistema integrerá la tecnología nfc vía MQTT y sistema en tiempo real con django Channels 

Los usuarios que interactuan con el sistema son:

- Alumnos
- Docentes
- Personal de administración
- Dirección
- Cafetereia
- Representante

Se requiere optimizar el modelo del user y crear 2 aplicaciones:

# Aplicacion Control de acceso: 

- El usuario debe estar regsitrado en el sistema con el ID de su tarjeta NFC, vía MQTT
- Maneja los siguientes tópicos:
    - Topic esp32door/rfid/uid hace la lectura y lo envía al servidor MQTT
    - Topic esp32door/rfid/auth hace la valizacion y envía "autorizado-nombre" si el usuario tiene acceso al  laboratorio y "no autorizado" en el caso que noo existe en la base de datos o tiene el acceso restringido
- Debe crear una tabla para guardar los logs de acceso:
    - id
    - rfid
    - fecha
    - hora
    - estado
    - usuario (ForeignKey al modelo User)

- Debe implementar un web socket para mostrar en tiempo real los logs de acceso realizados, debe mostrar: 
    - nombre
    - fecha
    - hora
    - estado
    - anno_grado
    - sección
- El flujo de trabajo de los administradores es el siguiente:
    - El usuario presenta su tarjeta NFC en el lector
    - el lector envía el ID de la tarjeta al servidor MQTT
    - el servidor MQTT envía el ID de la tarjeta al servidor django
    - el servidor django valida el id y el estado y envía un mensaje al servidor MQTT
- Los administradores deben poder agregar, editar y eliminar usuarios, y deben tener acceso al panel de control
- el panel de control muestra:
    - logs de acceso en tiempo real
    - usuarios registrados
    - usuarios bloqueados
    - usuarios eliminados
    - usuarios editados
    - usuarios agregados

# Aplicacion Control de pagos en la cafetereia

Esta aplicacieon esta mas cruda a nivel de topicos MQTT, lo cuales debe implementar un modelo similar al de la aplicacion control de acceso por lo que se requiere hacer un estudio de los topicos necesarios para implementar esta funcionalidad
    - Topic esp32cafe/amount/set establece el monto a pagar
    - Topic esp32cafe/rfid/uid hace la lectura y lo envía al servidor MQTT
    - Topic esp32cafe/rfid/auth verifica que el usuario tenga saldo suficiente y realiza la transaccion
- El usuario podrá ver su saldo disponible y recargar su tarjeta
- Los representantes podrán ver el saldo disponible de sus representados y recargar su tarjeta
- El cafetin cargara el monto a pagar y el sistema descontará de la tarjeta del usuario
- el sistema debe tener una tabla para guardar los logs de pago
    - id
    - rfid
    - fecha
    - hora
    - estado
    - usuario (ForeignKey al modelo User)
- el flujo de pago es el siguiente:
    - El cafetin introduce el monto a pagar y presiona un boton para iniciar el pago
    - el usuario presenta su tarjeta NFC en el lector
    - el lector envía el ID de la tarjeta al servidor MQTT
    - el servidor MQTT envía el ID de la tarjeta al servidor django
    - el servidor django envía lee el saldo del usuario y valida que tenga fondos suficientes
    - el servidor django envía un mensaje al servidor MQTT para descontar el monto de la tarjeta del usuario
    - el servidor django envía un mensaje al servidor MQTT para actualizar el saldo del usuario
    - el servidor django envía un mensaje al servidor MQTT para actualizar el log de pago
    - el servidor django envía un mensaje al servidor MQTT para mostrar el resultado del pago en tiempo real
- El flujo de trabajo de los administradores es el siguiente:
    - El usuario presenta su tarjeta NFC en el lector
    - el lector envía el ID de la tarjeta al servidor MQTT
    - el servidor MQTT envía el ID de la tarjeta al servidor django
    - el servidor django valida el id y el estado y envía un mensaje al servidor MQTT
- Los administradores deben poder agregar, editar y eliminar usuarios, y deben tener acceso al panel de control
- el panel de control muestra:
    - logs de acceso en tiempo real
    - usuarios registrados
    - usuarios bloqueados
    - usuarios eliminados
    - usuarios editados
    - usuarios agregados
- los representantes podrán ver el saldo disponible de sus representados y recargar su tarjeta

Se solicita implementar esta nueva funcionalidad en la aplicación, manteniendo la arquitectura actual y siguiendo las buenas prácticas de desarrollo.