# Код для Bitget API 

import logging
import requests
import time
from .api_utils import make_request

logger = logging.getLogger(__name__)

class BitgetAPI:
    def __init__(self):
        self.base_url = "https://api.bitget.com"
        
    async def get_p2p_orders(self, side: str = "BUY") -> dict:
        try:
            url = f"{self.base_url}/api/mix/v1/market/p2p/advertisements"
            params = {
                "fiatCurrency": "UAH",
                "cryptoCurrency": "USDT",
                "side": side,
                "pageSize": 10,
                "pageNo": 1
            }
            
            response = await make_request(url, params=params)
            if response:
                return response
            return {"error": "Не вдалося отримати дані"}
            
        except Exception as e:
            logger.error(f"Помилка отримання P2P пропозицій Bitget: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def get_p2p_offers(side='BUY', fiat='UAH', asset='USDT', rows=10, verified_only=False, limit_amount=0, transaction_amount=0):
        try:
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'uk-UA',
                'Content-Type': 'application/json',
                'Origin': 'https://www.bitget.com',
                'Referer': 'https://www.bitget.com/p2p/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            payload = {
                "fiatCurrency": fiat,
                "cryptoCurrency": asset,
                "tradeType": "BUY" if side == 'SELL' else "SELL",
                "page": 1,
                "rows": rows,
                "paymentMethod": "",
                "amount": str(transaction_amount) if transaction_amount > 0 else ""
            }
            
            response = requests.post(
                'https://api.bitget.com/api/v2/p2p/advertisement/list',
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if not data or 'data' not in data or 'items' not in data['data']:
                return []
            
            offers = []
            for item in data['data']['items']:
                try:
                    amount = float(item['availableAmount'])
                    if limit_amount > 0 and amount < limit_amount:
                        continue
                        
                    if verified_only and not item['merchant'].get('verified'):
                        continue
                        
                    offer = {
                        'price': float(item['price']),
                        'amount': amount,
                        'merchant': item['merchant']['nickName'],
                        'completion': f"{float(item['merchant'].get('finishRate', 0)) * 100:.2f}%",
                        'payment_methods': [method['name'] for method in item['payments']],
                        'exchange': 'Bitget'
                    }
                    offers.append(offer)
                except Exception as e:
                    logging.error(f"Помилка обробки пропозиції Bitget: {e}")
                    continue
            
            offers.sort(key=lambda x: x['price'], reverse=(side == 'SELL'))
            return offers[:3]

        except Exception as e:
            logging.error(f"Помилка отримання P2P пропозицій Bitget: {e}")
            return []

    @staticmethod
    def get_buy_offers(context=None):
        verified_only = context.user_data.get('verified_only', False) if context else False
        limit_amount = context.user_data.get('limit_amount', 0) if context else 0
        transaction_amount = context.user_data.get('transaction_amount', 0) if context else 0
        
        return BitgetAPI.get_p2p_offers(
            side='BUY',
            verified_only=verified_only,
            limit_amount=limit_amount,
            transaction_amount=transaction_amount
        )

    @staticmethod
    def get_sell_offers(context=None):
        verified_only = context.user_data.get('verified_only', False) if context else False
        limit_amount = context.user_data.get('limit_amount', 0) if context else 0
        transaction_amount = context.user_data.get('transaction_amount', 0) if context else 0
        
        return BitgetAPI.get_p2p_offers(
            side='SELL',
            verified_only=verified_only,
            limit_amount=limit_amount,
            transaction_amount=transaction_amount
        ) 