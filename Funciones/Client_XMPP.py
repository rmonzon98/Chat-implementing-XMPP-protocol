import sleekxmpp

import logging

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout
from sleekxmpp.xmlstream.stanzabase import ET, ElementBase
from sleekxmpp.plugins.xep_0096 import stanza, File

class Client_XMPP(ClientXMPP):

    """
    Constructor
    Parametros: jid,password
    """
    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)

        #Eventos a utilizar
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler('message', self.message)

        #Plugins
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0045') # Mulit-User Chat (MUC)
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0077') # In-band Registration
        self.register_plugin('xep_0066') # Out-of-band Data
        self.register_plugin('xep_0096') # File transfer 

    """
    Funcion: session_start
    Parametros: -
    ¿Que hace? inicia sesion
    """
    def session_start(self, event):
        try:
            log = logging.getLogger("XMPP")
            self.send_presence()      
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
        que = ET.fromstring("<query xmlns='jabber:iq:register'>\<remove/>\</query>")
        #create an iq stanza type 'set'
        iq_stanza = self.make_iq_set(ito='redes2020.xyz', ifrom=self.boundjid.user)
        iq_stanza.append(que)
        iq_stanza.send()
        
    """
    Funcion: change_Status
    Parametros: msg_status (mensaje para el status), status
    ¿Que hace? cambiar status
    """
    def change_Status(self, msg_status, status):
        if status == 1:
            status = "away"
        elif status == 2:
            status = "chat"
        elif status == 3:
            status = "xa"
        elif status == 4:
            status = "dnd"
        self.send_presence(pshow = status, pstatus = msg_status)   

    """
    Funcion: message
    Parametros: msg (mensaje que recibe)
    ¿Que hace? interpretar el mensaje que ha recibido
    """
    def message(self, msg):
        print("Ha llegado un mensaje")
        if str(msg['type']) == 'chat':
            print("\nMensaje de parte de ",msg['from'],":\n",msg['body'])
        elif str(msg['type']) == 'groupchat':
            print('Mensaje grupal de parte de %(from)s:\n%(body)s' %(msg))
    
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
            self.send_message(mto= room+'@conference.redes2020.xyz', mbody=msg, mtype='groupchat')
            print("\nMensaje enviado a: "+room+'@conference.redes2020.xyz')
        except IqError:
            print("No se ha recibido respuesta del server")

    """
    Funcion: createRoom
    Parametros: room, nickname
    ¿Que hace? entrar/crear room y establecer el nickname
    """
    def createRoom(self, room, nickname):
        """
        función extraída de:
        https://stackoverflow.com/questions/24133662/sleekxmpp-automatically-accept-all-chat-room-invites
        """
        self.plugin['xep_0045'].joinMUC(room+'@conference.redes2020.xyz', nickname, wait=True)
        self.nick = nickname
    
