import requests
import time
import hashlib

from collections import OrderedDict


class Coinex:

    def __init__(self, access_id, secret_key):
        self.access_id = access_id
        self.secret_key = secret_key

    def generate_signature(self, params: dict = None):
        if params:
            params = OrderedDict(sorted(params.items()))
            data = '&'.join([key + '=' + str(params[key]) for key in sorted(params)])
            data = data + '&secret_key=' + self.secret_key
        else:
            data = 'secret_key=' + self.secret_key

        data = data.encode()
        return hashlib.md5(data).hexdigest().upper()

    def generate_headers(self, shit: dict = None, require_access_id: bool = False) -> dict:
        headers = {
            'authorization': self.generate_signature(shit),
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/39.0.2171.71 Safari/537.36',
        }

        if require_access_id is True:
            headers['AccessId'] = self.access_id

        return headers

    @staticmethod
    def market_statics(market: str) -> dict:
        market = market.lower()
        r = requests.get(f'https://api.coinex.com/v1/market/ticker?market={market}')
        obj = r.json()

        if r.status_code == 200:
            try:
                code = obj['code']
            except KeyError:
                raise KeyError

            if code == 0:
                return obj['data']

            else:
                msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
                raise Exception(msg)

        else:
            msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
            raise Exception(msg)

    def submit_withdrawal(self, coin_type: str, coin_address: str,
                          actual_amount: str, smart_contract_name: str = None) -> dict:

        params = {
            'access_id': self.access_id,
            'tonce': int(time.time()) * 1000,
            'coin_type': coin_type,
            'coin_address': coin_address,
            'transfer_method': "onchain",
            'actual_amount': actual_amount,
        }

        headers = self.generate_headers(params)

        # TODO smart_contract_name == TRC20 !!!!!!!!

        if smart_contract_name:
            params['smart_contract_name'] = smart_contract_name

        if coin_type == 'usdt' or coin_type == 'tether':
            params['smart_contract_name'] = 'TRC20'

        r = requests.post('https://api.coinex.com/v1/balance/coin/withdraw', headers=headers, json=params)
        obj = r.json()

        if r.status_code == 200:
            try:
                code = obj['code']
            except KeyError:
                raise KeyError

            if code == 0:
                return obj['data']

            else:
                msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
                raise Exception(msg)

        else:
            msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
            raise Exception(msg)

    def all_market_stats(self):
        try:
            r = requests.get("https://api.coinex.com/v1/market/ticker/all")
            return r.json()
        except Exception as e:
            print(e)

    def place_limit_order(self, market: str, side: str, amount: str, price: str,
                          source_id: str = None, option: str = None, account_id: int = None,
                          client_id: str = None) -> dict:

        payload = {
            "access_id": self.access_id,
            "market": market.upper(),
            "price": price,
            "tonce": int(time.time()) * 1000,
            "type": side,
            "amount": amount,
        }

        headers = self.generate_headers(payload)

        r = requests.post('https://api.coinex.com/v1/order/limit', headers=headers, json=payload)
        obj = r.json()

        if r.status_code == 200:
            try:
                code = obj['code']
            except KeyError:
                raise KeyError

            if code == 0:
                return obj['data']
            else:
                msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
                raise Exception(msg)

        else:
            msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
            raise Exception(msg)

    def open_orders_by_side(self, market, side):
        params = {
            "access_id": self.access_id,
            "market": market.upper(),
            "tonce": int(time.time()) * 1000,
            "type": side,
            "page": 1,
            "limit": 100,
        }

        headers = self.generate_headers(params)

        r = requests.get('https://api.coinex.com/v1/order/pending', headers=headers, params=params)
        obj = r.json()
        if r.status_code == 200:
            try:
                code = obj['code']
            except KeyError:
                raise KeyError
            if code == 0:
                return obj["data"]
            else:
                msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
                return Exception(msg)
        else:
            msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
            raise Exception(msg)

    def market_depth(self, market, merge=0, limit=20):
        params = {
            "market": market,
            "merge": merge,
            "limit": limit,
        }
        r = requests.get('https://api.coinex.com/v1/market/depth', params=params)
        obj = r.json()
        if r.status_code == 200:
            try:
                code = obj['code']
            except KeyError:
                raise KeyError

            if code == 0:
                return obj['data']
            else:
                msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
                raise Exception(msg)

        else:
            msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
            raise Exception(msg)

    def place_market_order(self, market: str, side: str, amount: str) -> dict:
        payload = {
            "access_id": self.access_id,
            "market": market.upper(),
            "tonce": int(time.time()) * 1000,
            "type": side,
            "amount": amount,
        }

        headers = self.generate_headers(payload)

        r = requests.post('https://api.coinex.com/v1/order/market', headers=headers, json=payload)
        obj = r.json()

        if r.status_code == 200:
            try:
                code = obj['code']
            except KeyError:
                raise KeyError

            if code == 0:
                return obj['data']
            else:
                msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
                raise Exception(msg)

        else:
            msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
            raise Exception(msg)

    def market_transaction_info(self):
        r = requests.get('https://api.coinex.com/v1/order/market/trade/info')
        obj = r.json()

        if r.status_code == 200:
            try:
                code = obj['code']
            except KeyError:
                raise KeyError

            if code == 0:
                return obj['data']
            else:
                msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
                raise Exception(msg)

        else:
            msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
            raise Exception(msg)

    def recent_transactions(self, page: str, market=None):
        if market:
            params = {
                'access_id': self.access_id,
                'page': page,
                'limit': 100,
                'market': market,
                'tonce': int(time.time()) * 1000,
            }
        else:
            params = {
                'access_id': self.access_id,
                'page': page,
                'limit': 100,
                'tonce': int(time.time()) * 1000,
            }

        headers = self.generate_headers(params)

        r = requests.get('https://api.coinex.com/v1/order/user/deals', params=params, headers=headers)
        obj = r.json()

        if r.status_code == 200:
            try:
                code = obj['code']
            except KeyError:
                raise KeyError

            if code == 0:
                return obj['data']
            else:
                msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
                raise Exception(msg)

        else:
            msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
            raise Exception(msg)

    def order_status(self, id_: int, market: str) -> dict:

        params = {
            'access_id': self.access_id,
            'id': id_,
            'market': market,
            'tonce': int(time.time()) * 1000,
        }

        headers = self.generate_headers(params)

        r = requests.get('https://api.coinex.com/v1/order/status', params=params, headers=headers)
        obj = r.json()

        if r.status_code == 200:
            try:
                code = obj['code']
            except KeyError:
                raise KeyError

            if code == 0:
                return obj['data']
            else:
                msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
                raise Exception(msg)

        else:
            msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
            raise Exception(msg)

    def cancel_order(self, id_: int, market: str) -> dict:
        params = {
            'access_id': self.access_id,
            'id': id_,
            'market': market,
            'tonce': int(time.time()) * 1000,
        }

        headers = self.generate_headers(params)

        r = requests.delete('https://api.coinex.com/v1/order/pending', params=params, headers=headers)
        obj = r.json()

        if r.status_code == 200:
            try:
                code = obj['code']
            except KeyError:
                raise KeyError

            if code == 0:
                return obj['data']
            else:
                msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
                raise Exception(msg)
        else:
            msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
            raise Exception(msg)

    def balance_info(self, coin) -> list:

        params = {
            'access_id': self.access_id,
            'tonce': int(time.time()) * 1000
        }

        headers = self.generate_headers(params)

        r = requests.get('https://api.coinex.com/v1/balance/info', params=params, headers=headers)
        obj = r.json()

        if r.status_code == 200:
            try:
                code = obj['code']
            except KeyError:
                raise KeyError

            if code == 0:
                data_dict = obj['data'][coin]
                return data_dict
                # available = float(data_dict[coin]["available"])
                # frozen = float(data_dict[coin]["frozen"])
                # sum_balance = available + frozen
                # return available, frozen, sum_balance
            else:
                msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
                raise Exception(msg)
        else:
            msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
            raise Exception(msg)

    def cancel_all_orders(self, market: str, account_id: int = 0) -> dict:

        params = {
            'access_id': self.access_id,
            'account_id': account_id,
            'market': market,
            'tonce': int(time.time()) * 1000
        }

        headers = self.generate_headers(params)

        r = requests.delete('https://api.coinex.com/v1/order/pending', params=params, headers=headers)
        obj = r.json()

        if r.status_code == 200:
            try:
                code = obj['code']
            except KeyError:
                raise KeyError

            if code == 0:
                return obj['data']
            else:
                msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
                raise Exception(msg)
        else:
            msg = f"""[Code: {obj['code']}]- [{obj['message']}] --> {obj['data']}"""
            raise Exception(msg)
