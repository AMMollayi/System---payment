import json
from tonclient.client import TonClient
from tonclient.types import ParamsOfEncodeMessage, Abi

class TonProcessor:
    def __init__(self):
        self.client = TonClient(config={
            'network': {
                'server_address': Config.TON_RPC_URL,
                'api_key': Config.TON_API_KEY
            }
        })
        with open(Config.TON_ABI_PATH, 'r') as f:
            self.contract_abi = Abi.from_json(json.load(f))
        self.contract_address = Config.TON_CONTRACT_ADDRESS

    def transfer(self, receiver, amount):
        # ایجاد تراکنش و ارسال به بلاکچین
        message = self.create_message(receiver, amount)
        params = ParamsOfEncodeMessage(message=message, abi=self.contract_abi)
        encoded_message = self.client.abi.encode_message(params)
        result = self.client.network.send_message(params=encoded_message)
        return result['transaction']['id']
