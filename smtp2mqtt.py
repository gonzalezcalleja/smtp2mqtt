import json
import paho.mqtt.client as mqtt
import argparse
import email
import logging

from secure_smtpd import SMTPServer, LOG_NAME

parser = argparse.ArgumentParser()
parser.add_argument("-N", "--mqtttopic", help="mqtt topic", default="doorbell/entrada")
parser.add_argument("-M", "--mqtthost", help="mqtt host", default="127.0.0.1")
parser.add_argument("-P", "--mqttport", help="mqtt port", type=int, default="1883")
parser.add_argument("-U", "--mqttusername", help="mqtt username")
parser.add_argument("-W", "--mqttpassword", help="mqtt password")

parser.add_argument("-T", "--smtphost", help="smtp host", default="0.0.0.0")
parser.add_argument("-S", "--smtppassword", help="smtp password", default="password")
parser.add_argument("-O", "--smtpusername", help="smtp username", default="doorbell@blanco.local")
parser.add_argument("-Y", "--smtpport", help="smtp port", type=int, default=1125)
args = parser.parse_args()


class SMTPServer(SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, message_data):
        print("Processing message ...")

        msg = email.message_from_string(message_data)

        # Save 3 img attachments from KONX doorbell
        attachment = msg.get_payload()[1]
        open('/var/www/html/doorbell/doorbell-1.jpg', 'wb').write(attachment.get_payload(decode=True))
        attachment = msg.get_payload()[2]
        open('/var/www/html/doorbell/doorbell-2.jpg', 'wb').write(attachment.get_payload(decode=True))
        attachment = msg.get_payload()[3]
        open('/var/www/html/doorbell/doorbell-3.jpg', 'wb').write(attachment.get_payload(decode=True))

class FakeCredentialValidator(object):
    def validate(self, username, password):
       if username == args.smtpusername and password == args.smtppassword:
         print("Login successfull")

         ## MQTT publish notification
         client = mqtt.Client(client_id="", clean_session=True, userdata=None,
                         protocol=mqtt.MQTTv311)
         client.username_pw_set(args.mqttusername, args.mqttpassword)
         client.connect(args.mqtthost, args.mqttport, 60)
         client.loop_start()

         data = {}
         data['mailfrom'] = username
         data['bell'] = 'on'
         json_data = json.dumps(data)

         client.publish(args.mqtttopic, json_data, qos=0)
         client.disconnect()
         
         print("Published in: %s:%s - %s" % (args.mqtthost, args.mqttport, args.mqtttopic))

         return True
       else:
         print("Login failed!")
         return False

logging.getLogger( LOG_NAME )
logging.basicConfig(level=logging.DEBUG)

server = SMTPServer(
    (args.smtphost, args.smtpport),
    None,
    require_authentication=True,
    ssl=False,
    credential_validator=FakeCredentialValidator(),
    process_count=5,
    maximum_execution_time = 30
)

print('Server running on %s:%d for username/password: %s/%s' % (args.smtphost, args.smtpport, args.smtpusername, args.smtppassword))
server.run()