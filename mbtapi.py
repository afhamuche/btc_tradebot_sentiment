import hashlib
import hmac
import json
import time

from http import client
from urllib.parse import urlencode

class Tapi:
    def __init__(self, tapi_method, quantity, limit_price):
        # Variables
        self.tapi_method = tapi_method
        self.quantity = str(quantity)
        self.limit_price = str(limit_price)

        # Constantes
        self.MB_TAPI_ID = 'ID'
        self.MB_TAPI_SECRET = 'SECRET'
        self.REQUEST_HOST = 'www.mercadobitcoin.net'
        self.REQUEST_PATH = '/tapi/v3/'

        # Nonce
        # Para obter variação de forma simples
        # timestamp pode ser utilizado:
        self.tapi_nonce = str(int(time.time()))
        #tapi_nonce = 1

    def generate_params(self):
        # Parâmetros
        params = {
            'tapi_method': self.tapi_method,
            'tapi_nonce': self.tapi_nonce,
            'coin_pair': 'BRLBTC',
            'quantity': self.quantity,
            'limit_price': self.limit_price,
            'async': 'true'
        }
        params = urlencode(params)
        return params

    def generate_mac(self, params):
        # Gerar MAC
        params_string = self.REQUEST_PATH + '?' + params
        H = hmac.new(bytes(self.MB_TAPI_SECRET, encoding='utf8'), digestmod=hashlib.sha512)
        H.update(params_string.encode('utf-8'))
        tapi_mac = H.hexdigest()
        return tapi_mac

    def generate_headers(self, tapi_mac):
        # Gerar cabeçalho da requisição
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'TAPI-ID': self.MB_TAPI_ID,
            'TAPI-MAC': tapi_mac
        }
        return headers

    def generate_post(self, params, headers):
        # Realizar requisição POST
        try:
            conn = client.HTTPSConnection(self.REQUEST_HOST)
            conn.request("POST", self.REQUEST_PATH, params, headers)

            # Print response data to console
            response = conn.getresponse()
            response = response.read()

            response_json = json.loads(response)
            print('status: {}'.format(response_json['status_code']))
            print(json.dumps(response_json, indent=4))
        finally:
            if conn:
                conn.close()

