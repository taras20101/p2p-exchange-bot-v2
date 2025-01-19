# Код для MEXC API 

import logging
import requests
import time
from .api_utils import make_request

logger = logging.getLogger(__name__)

class MexcAPI:
    def __init__(self):
        self.base_url = "https://api.mexc.com"
        
    async def get_p2p_orders(self, side: str = "BUY") -> dict:
        try:
            url = f"{self.base_url}/api/v3/p2p/advertisements"
            params = {
                "fiatCurrency": "UAH",
                "cryptoCurrency": "USDT",
                "side": side,
                "page": 1,
                "rows": 10
            }
            
            response = await make_request(url, params=params)
            if response:
                return response
            return {"error": "Не вдалося отримати дані"}
            
        except Exception as e:
            logger.error(f"Помилка отримання P2P пропозицій MEXC: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def get_p2p_offers(side='BUY', fiat='UAH', asset='USDT', rows=10, verified_only=False, limit_amount=0, transaction_amount=0):
        try:
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'uk-UA',
                'Content-Type': 'application/json',
                'Origin': 'https://p2p.mexc.com',
                'Referer': 'https://p2p.mexc.com/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            payload = {
                "page": 1,
                "rows": rows,
                "asset": asset,
                "fiat": fiat,
                "trade_type": side.lower(),
                "payment_method": [],
                "amount": str(transaction_amount) if transaction_amount > 0 else ""
            }
            
            response = requests.post(
                'https://p2p.mexc.com/api/p2p/market/trade/list',
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if not data or 'data' not in data:
                return []
            
            offers = []
            for item in data['data']:
                try:
                    amount = float(item['amount'])
                    if limit_amount > 0 and amount < limit_amount:
                        continue
                        
                    if verified_only and not item['user'].get('verified'):
                        continue
                        
                    offer = {
                        'price': float(item['price']),
                        'amount': amount,
                        'merchant': item['user']['nickname'],
                        'completion': f"{float(item['user'].get('completion_rate', 0)) * 100:.2f}%",
                        'payment_methods': [method['name'] for method in item['payments']],
                        'exchange': 'MEXC'
                    }
                    offers.append(offer)
                except Exception as e:
                    logging.error(f"Помилка обробки пропозиції MEXC: {e}")
                    continue
            
            offers.sort(key=lambda x: x['price'], reverse=(side == 'SELL'))
            return offers[:3]

        except Exception as e:
            logging.error(f"Помилка отримання P2P пропозицій MEXC: {e}")
            return []

    @staticmethod
    def get_buy_offers(context=None):
        verified_only = context.user_data.get('verified_only', False) if context else False
        limit_amount = context.user_data.get('limit_amount', 0) if context else 0
        transaction_amount = context.user_data.get('transaction_amount', 0) if context else 0
        
        return MexcAPI.get_p2p_offers(
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
        
        return MexcAPI.get_p2p_offers(
            side='SELL',
            verified_only=verified_only,
            limit_amount=limit_amount,
            transaction_amount=transaction_amount
        ) 