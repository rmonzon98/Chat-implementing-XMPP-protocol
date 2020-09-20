from Register import *

if __name__ == '__main__':
    server = '@redes2020.xyz'
    username = 'raulinho'
    password = 'notedigo'

    menu = True
    login = False

    print("*"*12,"BIENVENIDO USUARIO","*"*12)

    menu_not_log = """Aun no esta logeado, estas son sus opciones:
    1. Registrar un usuario
    2. Log in
    99. Salir
    """
    
    menu_log = """Usted se encuentra logeado, estas son sus opciones:
    1. Registrar un usuario
    2. Log out
    3. Mostrar cuentas
    4. Eliminar cuenta
    5. Agregar usuario como contacto
    6. Mostrar detalles de una cuenta
    7. Enviar mensaje (Mensaje directo)
    8. Enviar mensaje (Mensaje de grupo)
    9. Definir mensaje de presencia
    99. Salir
    """

    while menu:

        #Dependiendo del estadode login, se muestran dos menus distintos
        if not(login):
            opcion = input(menu_not_log)
        else:
            opcion = input(menu_log)

        #Registrar usuario
        if (opcion == '1'): 
            print ('\n*************opcion 1*************\nEn esta opcion se crea un nuevo usuario')
            username = input('Ingrese username: ')
            password = input('Ingrese password: ')
            jid = username+server
            register = Register(jid, password)
            if register.connect():
                register.process(block=True)
            else:
                print("Error")
            

        #Iniciar sesion o cerrar sesion
        elif (opcion == '2'):
            print ('\n*************opcion 2*************\nEn esta opcion se inicia o cierra sesion')
        
        #Terminar programa
        elif (opcion == '99'):
            print ('Ha elegido salir. Gracias por utilizar el programa')
            menu = False
        else:
            print('Eligió la opcion '+opcion+'. Esta opcion no es valida')
