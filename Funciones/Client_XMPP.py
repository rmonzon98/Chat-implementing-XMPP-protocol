import sleekxmpp

import logging
import threading
from tabulate import tabulate
import sys
import base64

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout
from sleekxmpp.xmlstream.stanzabase import ET, ElementBase
from sleekxmpp.plugins.xep_0096 import stanza, File

class Client_XMPP(ClientXMPP):

    """
    Constructor
    Parametros: jid,password
    """
    def __init__(self, jid, password, username):
        ClientXMPP.__init__(self, jid, password)
        self.nick = username

        #Eventos a utilizar
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler('message', self.message)
        self.add_event_handler("changed_status", self.wait_for_presences)
        self.add_event_handler('presence_subscribe',self.new_user_suscribed)
        self.add_event_handler("changed_subscription", self.friend_notification)

        self.received = set()
        self.contacts = []
        self.presences_received = threading.Event()

        #Plugins
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0045') # Mulit-User Chat (MUC)
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0077') # In-band Registration
        self.register_plugin('xep_0066') # Out-of-band Data
        self.register_plugin('xep_0096') # File transfer 
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0047', {
            'auto_accept': True
        })

    """
    Funcion extraida de:
    https://github.com/fritzy/SleekXMPP/blob/develop/examples/roster_browser.py  
    """
    def wait_for_presences(self, pres):
        """
        Track how many roster entries have received presence updates.
        """
        if pres['from'].bare != self.boundjid.bare:
            print("\nNUEVA NOTIFICACION\nHA LLEGADO UN MENSAJE TIPO")
            print(pres['from'].bare + " ha cambiado su estado a:  " + pres['status'])
        self.received.add(pres['from'].bare)
        if len(self.received) >= len(self.client_roster.keys()):
            self.presences_received.set()
        else:
            self.presences_received.clear()

    """
    Funcion: session_start
    Parametros: -
    ¿Que hace? inicia sesion
    """
    def session_start(self, event):
        try:
            log = logging.getLogger("XMPP")
            self.send_presence(pstatus='Conectado')
            roster = self.get_roster()
            for r in roster['roster']['items'].keys():
                self.contacts.append(r)              
        except IqError as e:
            print("Error: %s" % e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            print("El server se ha tardado")
            self.disconnect()
    
    """
    Funcion: session_end
    Parametros: -
    ¿Que hace? cierra sesion
    """
    def logout(self):
        self.disconnect(wait=True)

    """
    Funcion: delete_Account
    Parametros: -
    ¿Que hace? eliminar cuenta
    """
    def delete_Account(self):
        """
        query extraído de:
        https://stackoverflow.com/questions/24023051/xmppframework-delete-a-registered-user-account 
        """
        #create an iq stanza type 'set'
        iq_stanza = self.make_iq_set(ito='redes2020.xyz',ifrom=self.boundjid.user)
        item = ET.fromstring("<query xmlns='jabber:iq:register'> \
                                        <remove/> \
                                    </query>")
        iq_stanza.append(item)
        ans = iq_stanza.send()
        if ans['type'] == 'result':
            print("SU cuetna ha sido elimanada con exito")
        
    """
    Funcion: change_Status
    Parametros: msg_status (mensaje para el status), status
    ¿Que hace? cambiar status
    """
    def change_Status(self, msg_status, status):
        text = ""
        if(status == 1):
            text = "chat"
        elif(status == 2):
            text = "away"
        elif(status == 3):
            text = "xa"
        elif(status == 4):
            text = "dnd"
        self.send_presence(pshow=text, pstatus=msg_status)

    """
    Funcion: message
    Parametros: msg (mensaje que recibe)
    ¿Que hace? interpretar el mensaje que ha recibido
    """
    def message(self, msg):
        if str(msg['type']) == 'groupchat':
            if msg['mucnick'] != self.nick:
                print("\nNUEVA NOTIFICACION\nHA LLEGADO UN MENSAJE TIPO %s" % msg['type'])
                table_info = []
                table_info.append((str(msg['from']), str(msg['body'])))
                table = tabulate(table_info, headers=['From', 'Message'], tablefmt='grid')
                print(table)
        elif str(msg['type']) == 'chat':
            print("\nNUEVA NOTIFICACION\nHA LLEGADO UN MENSAJE TIPO %s" % msg['type'])
            if len(msg['body']) > 3000:
                image_rec = msg['body'].encode('utf-8')
                image_rec = base64.decodebytes(image_rec)
                with open("imagenrecibida.png", "wb") as fh:
                    fh.write(image_rec)
                print("Imagen recibida")
            else:
                table_info = []
                table_info.append((str(msg['from']), str(msg['body'])))
                table = tabulate(table_info, headers=['From', 'Message'], tablefmt='grid')
                print(table)
        
    """
    Funcion: send_Direct_Msg
    Parametros: jid,server, msg
    ¿Que hace? enviar mensaje
    """
    def send_Direct_Msg(self, jid, server, msg):
        try:
            user_recipient = jid + server
            self.send_message(mto= user_recipient, mbody=msg, mfrom=self.boundjid.user, mtype='chat')
            print("\nMensaje enviado a: "+jid)
        except IqError:
            print("No se ha recibido respuesta del server")
    
    """
    Funcion: send_Msg_group
    Parametros: room,message
    ¿Que hace? enviar mensaje a un grupo
    """
    def send_Msg_group(self, room, msg):
        try:
            room = room + '@conference.redes2020.xyz'
            self.send_message(mto= room, mbody=msg, mtype='groupchat')
            print("\nMensaje enviado a: "+room)
        except IqError:
            print("No se ha recibido respuesta del server")
    
    """
    Funcion: show_Rooms
    Parametros: -
    ¿Que hace? Muestra los grupos creados
    """
    def show_Rooms(self):
        """
        función extraída de:
        https://stackoverflow.com/questions/39426720/sleekxmpp-muc-room-list-and-discovering
        """
        result = self['xep_0030'].get_items(jid='conference.redes2020.xyz', iterator=True)
        print("\nLos grupos existentes son estos: ")
        for room_name in result['disco_items']:
            print(room_name['jid'])


    """
    Funcion: createRoom
    Parametros: room, nickname
    ¿Que hace? entrar/crear room y establecer el nickname
    """
    def create_Room(self, room):
        """
        función extraída de:
        https://stackoverflow.com/questions/24133662/sleekxmpp-automatically-accept-all-chat-room-invites
        """
        room_wished = room + '@conference.redes2020.xyz'
        exists = False
        result = self['xep_0030'].get_items(jid='conference.redes2020.xyz', iterator=True)
        for room_name in result['disco_items']:
            if room_wished == room_name['jid']:
                exists = True
        if exists:
            print("Se unira al grupo: %s" % room_wished)
            msg_status = 'Grupo listo para ser utilizado'
            self.plugin['xep_0045'].joinMUC(room_wished, self.nick, pstatus=msg_status, pfrom=self.boundjid.full, wait=True)
        else:
            print("Se creara el grupo: %s" % room_wished)
            msg_status= 'Listo para chatear en grupo'
            self.plugin['xep_0045'].joinMUC(room_wished, self.nick, pstatus=msg_status, pfrom=self.boundjid.full, wait=True)
            self.plugin['xep_0045'].setAffiliation(room_wished, self.boundjid.full, affiliation='owner')
            self.plugin['xep_0045'].configureRoom(room_wished, ifrom=self.boundjid.full)      
    
    """
    Funcion: add_Contact
    Parametros: user
    ¿Que hace? envia subscripcion 
    """
    def add_Contact(self, user):
        try:
            self.send_presence_subscription(pto=user)
            print("usuario agregado")
        except IqError:
            print("No se ha podido agregar como contacto")
        except IqTimeout:
            print("No se recibio respuesta de server") 
    
    """
    Funcion: show_Users
    Parametros: -
    ¿Que hace? imprime a los usuarios
    """
    def show_Users(self):
        iq_stanza = self.Iq()
        iq_stanza['type'] = 'set'
        iq_stanza['id'] = 'search_result'
        iq_stanza['to'] = 'search.redes2020.xyz'
        iq_stanza['from'] = self.boundjid.bare
        que = ET.fromstring("<query xmlns='jabber:iq:search'> \
                                <x xmlns='jabber:x:data' type='submit'> \
                                    <field type='hidden' var='FORM_TYPE'> \
                                        <value>jabber:iq:search</value> \
                                    </field> \
                                    <field var='Username'> \
                                        <value>1</value> \
                                    </field> \
                                    <field var='search'> \
                                        <value>*</value> \
                                    </field> \
                                </x> \
                              </query>")
        iq_stanza.append(que)
        try:
            users = iq_stanza.send()
            cont = 0
            data= []
            users_info = []
            for i in users.findall('.//{jabber:x:data}value'):
                cont += 1
                user_data = ''
                if i.text != None:
                    user_data = i.text
                data.append(user_data)
                if cont == 4:
                    cont = 0
                    users_info.append(data)
                    data=[]
            return users_info
        except IqError as err:
            print('No se pueden mostrar: %s' % err)
        except IqTimeout:
            print('No se recibe respeusta del servidor')

    """
    Funcion: show_one
    Parametros: JID
    ¿Que hace? imprime a info de un usuario
    """
    def show_one(self, JID):
        iq_stanza = self.Iq()
        iq_stanza['type'] = 'set'
        iq_stanza['id'] = 'search_result'
        iq_stanza['to'] = 'search.redes2020.xyz'
        iq_stanza['from'] = self.boundjid.bare
        que = ET.fromstring("<query xmlns='jabber:iq:search'> \
                                <x xmlns='jabber:x:data' type='submit'> \
                                    <field type='hidden' var='FORM_TYPE'> \
                                        <value>jabber:iq:search</value> \
                                    </field> \
                                    <field var='Username'> \
                                        <value>1</value> \
                                    </field> \
                                    <field var='search'> \
                                        <value>"+JID+"</value> \
                                    </field> \
                                </x> \
                              </query>")
        iq_stanza.append(que)
        try:
            users = iq_stanza.send()
            cont = 0
            data= []
            users_info = []
            for i in users.findall('.//{jabber:x:data}value'):
                cont += 1
                user_data = ''
                if i.text != None:
                    user_data = i.text
                data.append(user_data)
                if cont == 4:
                    cont = 0
                    users_info.append(data)
                    data=[]
            return users_info
        except IqError as err:
            print('No se pueden mostrar: %s' % err)
        except IqTimeout:
            print('No se recibe respeusta del servidor')
            
    """
    Funcion: friend_notification
    parametros: -
    ¿que hace? actualiza el roster
    """
    def friend_notification(self):
        self.get_roster()

    """
    Funcion: show_Friends
    Parametros: -
    ¿Que hace? muestra a los contactos agregados
    """
    def show_Friends(self):
        try:
            self.get_roster()
        except IqError as err:
            print('Error: %s' % err.iq['error']['condition'])
        except IqTimeout:
            print('No se recibio respuesta del server')
        self.send_presence()
        self.presences_received.wait(5)
        friends = self.client_roster.groups()
        list_friends = []
        for friend in friends:
            for jid in friends[friend]:
                self.contacts.append(jid)
                sub = self.client_roster[jid]['subscription']
                connections = self.client_roster.presence(jid)
                status = ''
                show = ''
                for res, pres in connections.items():
                    if pres['show']:
                        show = pres['show']
                    if pres['status']:
                        status = pres['status']
                if(jid != self.boundjid.user+'@redes2020.xyz'):
                    list_friends.append((jid,sub))
        return list_friends

    """
    Funcion: send_file
    Parametros: recipient, server, filename
    ¿Que hace? Codifica el archivo y lo envia como mensaje 
    """
    def send_File(self, recipient, server, filename):
        message = ''
        with open(filename, "rb") as img_file:
            message = base64.b64encode(img_file.read()).decode('utf-8')
        try:
            recipient = recipient + server
            self.send_message(mto=recipient,mbody=message,mtype="chat")
            print("Imagen enviada a ",recipient)
        except IqError:
            print("Error al enviar imagen")
        except IqTimeout:
            print("No se ha recibido respuesta del server")
    

    def new_user_suscribed(self,presence):
        print("\nNUEVA NOTIFICACION\nAlguien te ha agregado")
        print(str(presence['from'])+' y vos son amigos ahora ')