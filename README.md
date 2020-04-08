# smtp2mqtt (used for Konx doorbell and home assistant integration)

This script simulate an SMTP server with AUTH (required by KONX doorbell) and public a message in MQTT everytime the doorbell rings. 

## Run

````
/home/jgonzalez/homeassistant-venv/bin/python3.7 /etc/home-assistance/smtp2mqtt.py \
          --mqtttopic "doorbell/entrada" \
          --mqtthost 127.0.0.1 --mqttport 1883 \
          --mqttusername myusername --mqttpassword mypassword \
          --smtphost 192.168.1.100 --smtpport 1125 \
          --smtpusername doorbell@domain.local --smtppassword secret
````

## Home-assistant configuration

### Sensor

````
sensor:
- platform: mqtt
  state_topic: "doorbell/entrada"
  name: doorbell_ring
  qos: 0
  value_template: '{% if value_json.bell == "on" %} on {% else %} off {% endif %}'
  icon: mdi:bell
````

### Automation for reset payload

````
automation: 
	alias: 'Enviar Payload a OFF al pulsar VideoPortero'
	
	initial_state: 'on'
	trigger:
	  - platform: state
	    entity_id: sensor.doorbell_ring
	    to: 'on'
	action:
	  - service: mqtt.publish
	    data:
	      topic: 'doorbell/entrada'
	      payload: '{"bell":"off"}'
````

### Automation for notification

````
alias: 'Notificar iOS al Pulsar VideoPortero'

initial_state: 'on'
trigger:
  - platform: state
    entity_id: sensor.doorbell_ring
    to: 'on'
action:
  - service: notify.iphone_todos
    data:
      message: "Llamada Videoportero"
      data:
        attachment:
          content-type: jpeg
        push:
          category: camera-doorbell
          thread-id: "doorbell-notification-group"
        entity_id: camera.calle
````
