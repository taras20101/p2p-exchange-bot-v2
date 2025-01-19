import logging
import requests
from config import BINANCE_API_URL, USDT_UAH_SYMBOL

class BinanceAPI:
    @staticmethod
    def get_p2p_offers(side='BUY', fiat='UAH', asset='USDT', rows=10, verified_only=False, limit_amount=0, transaction_amount=0):
        try:
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json',
                'Origin': 'https://p2p.binance.com',
                'Pragma': 'no-cache',
                'Referer': 'https://p2p.binance.com/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            payload = {
                "page": 1,
                "rows": rows,
                "asset": asset,
                "fiat": fiat,
                "tradeType": side,
                "payTypes": [],
                "transAmount": str(transaction_amount) if transaction_amount > 0 else ""
            }
            
            response = requests.post(
                'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search',
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
                if verified_only and not item['advertiser']['verified']:
                    continue
                    
                amount = float(item['adv']['surplusAmount'])
                if limit_amount > 0 and amount < limit_amount:
                    continue
                    
                offer = {
                    'price': float(item['adv']['price']),
                    'amount': amount,
                    'merchant': item['advertiser']['nickName'],
                    'completion': f"{float(item['advertiser']['monthFinishRate']) * 100:.2f}%",
                    'payment_methods': [method['identifier'] for method in item['adv']['tradeMethods']],
                    'exchange': 'Binance'
                }
                offers.append(offer)
            
            offers.sort(key=lambda x: x['price'], reverse=(side == 'SELL'))
            
            return offers[:3]

        except Exception as e:
            logging.error(f"Помилка отримання P2P пропозицій: {e}")
            return []

    @staticmethod
    def get_buy_offers(amount_uah=0, context=None):
        # Отримуємо налаштування з контексту
        verified_only = context.user_data.get('verified_only', False) if context else False
        limit_amount = context.user_data.get('limit_amount', 0) if context else 0
        transaction_amount = context.user_data.get('transaction_amount', 0) if context else 0
        
        return BinanceAPI.get_p2p_offers(
            side='BUY',
            verified_only=verified_only,
            limit_amount=limit_amount,
            transaction_amount=transaction_amount
        )

    @staticmethod
    def get_sell_offers(amount_usdt=0, context=None):
        # Отримуємо налаштування з контексту
        verified_only = context.user_data.get('verified_only', False) if context else False
        limit_amount = context.user_data.get('limit_amount', 0) if context else 0
        transaction_amount = context.user_data.get('transaction_amount', 0) if context else 0
        
        return BinanceAPI.get_p2p_offers(
            side='SELL',
            verified_only=verified_only,
            limit_amount=limit_amount,
            transaction_amount=transaction_amount
        )

    @staticmethod
    def get_usdt_price():
        try:
            response = requests.get(
                f"{BINANCE_API_URL}/api/v3/ticker/price", 
                params={"symbol": USDT_UAH_SYMBOL},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            logging.info(f"Отримано курс від Binance: {data}")
            return float(data["price"])
        except Exception as e:
            logging.error(f"Помилка запиту до Binance API: {e}")
            return None

    @staticmethod
    def get_spread():
        try:
            book = requests.get(
                f"{BINANCE_API_URL}/api/v3/ticker/bookTicker", 
                params={"symbol": USDT_UAH_SYMBOL},
                timeout=10
            )
            book.raise_for_status()
            data = book.json()
            logging.info(f"Отримано дані спреду від Binance: {data}")
            
            return {
                "bid": float(data["bidPrice"]),
                "ask": float(data["askPrice"]),
                "spread": float(data["askPrice"]) - float(data["bidPrice"])
            }
        except Exception as e:
            logging.error(f"Помилка запиту до Binance API: {e}")
            return None 