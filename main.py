from Funciones.Register import *
from Funciones.Client_XMPP import *

if __name__ == '__main__':
    server = '@redes2020.xyz'

    menu = True
    login = False
    group_joined = False

    print("*"*12,"BIENVENIDO USUARIO","*"*12)

    menu_not_log = """\nAun no esta logeado, estas son sus opciones:
    1. Registrar un usuario
    2. Log in
    99. Salir
    """
    
    menu_log = """\nUsted se encuentra logeado, estas son sus opciones:
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
            if (not(login)):
                print ('\n*************opcion 1*************\nEn esta opcion se crea un nuevo usuario')
                username = input('Ingrese username: ')
                password = input('Ingrese password: ')
                jid = username + server
                register = Register(jid, password)
                if register.connect():
                    register.process(block=True)
                else:
                    print("Error")
            else: 
                print('Si ya esta logeado, no puede crear otra cuenta')
            
        #Iniciar sesion o cerrar sesion
        elif (opcion == '2'):
            print ('\n*************opcion 2*************\nEn esta opcion se inicia o cierra sesion')
            #Si el usuario no se ha logeado, pide usuario y password
            if not(login):
                username = input('Ingrese username: ')
                password = input('Ingrese password: ')
                jid = username + server
                cliente = Client_XMPP(jid, password)
                if cliente.connect():
                    cliente.process()
                    print("Se ha logeado correctamente")
                    login = True
                else:
                    print('Error')
            else:
                if cliente.connect():
                    cliente.logout()
                    login = False

        #Mostrar cuentas
        elif opcion == '3':
            print ('\n*************opcion 3*************\nEn esta opcion se muestran cuentas')

        #Eliminar cuenta
        elif opcion == '4':
            print ('\n*************opcion 4*************\nEliminar cuenta')
            if login:
                cliente.delete_Account()
                login = False
            else:
                print('No ha iniciado sesion')
        
        #Eliminar cuenta
        elif opcion == '5':
            print ('\n*************opcion 5*************\nAgregar usuarios como contacto')
            if login:
                pass
            else:
                print('No ha iniciado sesion')

        #Mostrar detalles de una cuenta
        elif opcion == '6':
            print ('\n*************opcion 6*************\nMostrar detalles de una cuenta')
            if login:
                pass
            else:
                print('No ha iniciado sesion')

        #Enviar mensaje (Mensaje directo)
        elif opcion == '7':
            print ('\n*************opcion 7*************\nEnviar mensaje (Mensaje directo)')
            if login:
                jid = input("Destinatario: ")
                message = input("Ingrese el mensaje que desea enviarle:\n")
                cliente.send_Direct_Msg(jid, server, message)
            else:
                print('No ha iniciado sesion')

        #Enviar mensaje (Mensaje grupal)
        elif opcion == '8':
            print ('\n*************opcion 8*************\nEnviar mensaje (Mensaje grupal)')
            if login:
                if group_joined:
                    print('Pertenece a un grupo, puede enviar un mensaje')
                    new_group = input('¿Desea ingresar a uno nuevo? \n1. si \n2. no')

                    if new_group == '1':
                        room = input("Ingrese el room al que desee entrar. Si este existe, se creara uno nuevo con ese nombre.\nnombre:")
                        nickname = input ("Ingrese el nickname con el que desea presentarse")
                        cliente.createRoom(room+'@conference.redes2020.xyz',nickname)
                    elif new_group == '2':
                        room = input("Ingrese el room al que desee entrar: ")
                        msg = input("Ingrese el mensaje que desea enviarle al grupo:\n")
                        cliente.send_Msg_group(room+'@conference.redes2020.xyz',message)                    
                else:
                    print('Aun no pertenece a ningun grupo, entre a uno primero')
                    room = input("Ingrese el room al que desee entrar. Si este existe, se creara uno nuevo con ese nombre.\nnombre:")
                    nickname = input ("Ingrese el nickname con el que desea presentarse")
                    cliente.createRoom(room+'@conference.redes2020.xyz',nickname)
                    group_joined = True

            else:
                print('No ha iniciado sesion')

        #Definir mensaje de presencia
        elif opcion == '9':
            print ('\n*************opcion 9*************\nDefinir mensaje de presencia')
            if login:
                status = input('Elija su estado \n1. away\n2. chat\n3. xa\n 4. dnd\n')
                status=int(status)
                msg_status = input('Ingrese su mensaje del status\n')
                cliente.change_Status(msg_status,status)
            else:
                print('No ha iniciado sesion')

        #Terminar programa
        elif (opcion == '99'):
            if cliente.connect():
                    cliente.logout()
                    login = False 
            print ('\nHa elegido salir. Gracias por utilizar el programa')
            menu = False
        else:
            print('\nEligió la opcion '+opcion+'. Esta opcion no es valida')
