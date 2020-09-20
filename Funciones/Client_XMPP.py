import sleekxmpp

import logging

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout
from sleekxmpp.xmlstream.stanzabase import ET, ElementBase
from sleekxmpp.plugins.xep_0096 import stanza, File

class Client_XMPP(ClientXMPP):

    """
    Constructor
    Parametros: username, password y resource
    """
    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)

        #Eventos a utilizar
        self.add_event_handler("session_start", self.session_start)

        #Plugins
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0045') # Mulit-User Chat (MUC)
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0077') # In-band Registration
        self.register_plugin('xep_0066') # Out-of-band Data
        self.register_plugin('xep_0096') # File transfer 

    """
    Función: session_start
    Parametros: -
    ¿Que hace? cierra sesion
    """
    def session_start(self, event):
        try:
            log = logging.getLogger("XMPP")
            self.send_presence()
            print('Se ha logeado correctamente')
        except IqError as e:
            print("Error: %s" % e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            print("El server se ha tardado")
            self.disconnect()
