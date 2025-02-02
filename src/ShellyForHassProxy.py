import os
import socket
import struct
import logging

from datetime import datetime 

class ShellyProxy:
  def __init__(self, hass_ip, hass_port, coap_ip, coap_port, debug=None):
    self.hass_ip = hass_ip
    self.hass_port = hass_port
    self.coap_ip = coap_ip
    self.coap_port = coap_port
    self.debug = debug

    # configure logging
    logging.basicConfig(
      format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
      datefmt='%Y-%m-%d %H:%M:%S',
      level=logging.INFO)
    if self.debug and self.debug == 'yes':
      logging.getLogger().setLevel(logging.DEBUG)

  def run(self):
    # bind socket
    logging.info(f'Starting ShellyForHASS Proxy..')
    logging.info(f'Listener: {self.coap_ip}:{self.coap_port}')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', self.coap_port))
    mreq = struct.pack("4sl", socket.inet_aton(self.coap_ip), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # start loop
    logging.info(f'Forwarder: {self.hass_ip}:{self.hass_port}')
    while True:
      try:
        # Receive CoAP message
        data, addr = sock.recvfrom(10240)
        # Debug
        logging.debug(f'Got CoAP message from: {addr[0]}:{addr[1]}')
        # Tag and add device ip-address to message
        newdata = bytearray(b'prxy')
        newdata.extend(socket.inet_aton(addr[0]))
        newdata.extend(data)
        # Send to Shelly plugin
        sock.sendto(newdata, (self.hass_ip, self.hass_port))
      except Exception as e:
        logginf.error('exception ' + str(e))


def main():
  # fetch variables
  HOMEASSISTANT_IP = os.getenv('HASS_IP', '127.0.0.1')
  HOMEASSISTANT_PORT = int(os.getenv('HASS_PORT', default=5684))
  COAP_IP = os.getenv('COAP_IP', default='224.0.1.187')
  COAP_UDP_PORT = int(os.getenv('COAP_PORT', default=5683))
  PROXY_DEBUG = os.getenv('PROXY_DEBUG', default='no')

  # start shelly proxy
  sp = ShellyProxy(HOMEASSISTANT_IP, HOMEASSISTANT_PORT, COAP_IP, COAP_UDP_PORT, PROXY_DEBUG)
  sp.run()

if __name__ == '__main__':
  main()
