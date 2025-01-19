import logging
import requests
import time

class OkxAPI:
    @staticmethod
    def get_p2p_offers(side='BUY', fiat='UAH', asset='USDT', rows=10, verified_only=False, limit_amount=0, transaction_amount=0):
        try:
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'uk-UA',
                'Content-Type': 'application/json',
                'Origin': 'https://www.okx.com',
                'Referer': 'https://www.okx.com/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            payload = {
                "quoteCurrency": "UAH",
                "baseCurrency": "USDT",
                "side": side.lower(),
                "paymentMethod": None,
                "userType": "certified" if verified_only else None,
                "showTotalOrderCount": True,
                "showCompleteOrderRate": True,
                "showOriginalAmount": True
            }

            response = requests.post(
                'https://www.okx.com/v3/c2c/tradingOrders/books',
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if not data or 'data' not in data:
                logging.error(f"Неправильна відповідь від OKX API: {data}")
                return []

            offers = []
            for item in data['data']:
                try:
                    amount = float(item['availableAmount'])
                    if limit_amount > 0 and amount < limit_amount:
                        continue

                    if transaction_amount > 0:
                        min_amount = float(item['minAmount'])
                        max_amount = float(item['maxAmount'])
                        if transaction_amount < min_amount or transaction_amount > max_amount:
                            continue

                    offer = {
                        'price': float(item['price']),
                        'amount': amount,
                        'merchant': item['nickName'],
                        'completion': f"{float(item['completedRate']) * 100:.0f}%",
                        'payment_methods': [pm['name'] for pm in item['paymentMethods']],
                        'exchange': 'OKX'
                    }
                    offers.append(offer)
                except Exception as e:
                    logging.error(f"Помилка обробки пропозиції OKX: {e}")
                    continue

            # Сортуємо за ціною
            offers.sort(key=lambda x: x['price'], reverse=(side == 'SELL'))
            
            return offers[:3]

        except Exception as e:
            logging.error(f"Помилка отримання P2P пропозицій OKX: {e}")
            return []

    @staticmethod
    def get_buy_offers(context=None):
        verified_only = context.user_data.get('verified_only', False) if context else False
        limit_amount = context.user_data.get('limit_amount', 0) if context else 0
        transaction_amount = context.user_data.get('transaction_amount', 0) if context else 0
        
        return OkxAPI.get_p2p_offers(
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
        
        return OkxAPI.get_p2p_offers(
            side='SELL',
            verified_only=verified_only,
            limit_amount=limit_amount,
            transaction_amount=transaction_amount
        ) 