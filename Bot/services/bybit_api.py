import logging
import requests
import time
import json

class BybitAPI:
    @staticmethod
    def get_p2p_offers(side='BUY', fiat='UAH', asset='USDT', rows=10, verified_only=False, limit_amount=0, transaction_amount=0):
        try:
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'uk-UA',
                'Content-Type': 'application/json',
                'Origin': 'https://www.bybit.com',
                'Referer': 'https://www.bybit.com/fiat/trade/otc/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'bybit-timezone': 'Europe/Kiev',
                'device-info': 'eyJzY3JlZW5fcmVzb2x1dGlvbiI6IjE5MjAsMTA4MCIsImF2YWlsYWJsZV9zY3JlZW5fcmVzb2x1dGlvbiI6IjE5MjAsMTA0MSIsInN5c3RlbV92ZXJzaW9uIjoiV2luZG93cyAxMCIsImJyYW5kX21vZGVsIjoidW5rbm93biIsInN5c3RlbV9sYW5nIjoidWstVUEiLCJ0aW1lem9uZSI6IkdNVCsyIiwidGltZXpvbmVPZmZzZXQiOi0xMjAsInVzZXJfYWdlbnQiOiJNb3ppbGxhLzUuMCAoV2luZG93cyBOVCAxMC4wOyBXaW42NDsgeDY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTIwLjAuMC4wIFNhZmFyaS81MzcuMzYiLCJsaXN0X3BsdWdpbiI6IkNocm9tZSBQREYgVmlld2VyLENocm9taXVtIFBERiBWaWV3ZXIsTWljcm9zb2Z0IEVkZ2UgUERGIFZpZXdlcixOUERGIFAtVmlld2VyIiwidGltZV9wbHVzIjowLCJzeXN0ZW1fdmVyIjoiV2luZG93cyAxMCIsInNjcmVlbl9yZXNvbHV0aW9uIjoiMTkyMCwxMDgwIiwib3NfbW9kdWxlIjoiV2luZG93cyIsImJyb3dzZXJfcGxhdGZvcm0iOiJXaW4zMiIsImJyb3dzZXJfbmFtZSI6IkNocm9tZSIsImJyb3dzZXJfdmVyc2lvbiI6IjEyMC4wLjAuMCIsImJyb3dzZXJfb25saW5lIjp0cnVlLCJicm93c2VyX2xhbmd1YWdlIjoidWstVUEiLCJicm93c2VyX2NvbmZpZyI6eyJwbGF0Zm9ybSI6IldpbjMyIiwibGFuZ3VhZ2UiOiJ1ay1VQSIsIm9ubGluZSI6dHJ1ZX19',
                'lang': 'uk-UA'
            }

            payload = {
                "userId": "",
                "tokenId": "USDT",
                "currencyId": "UAH",
                "payment": [],
                "side": 1 if side == 'BUY' else 2,
                "size": 50,
                "page": 1,
                "amount": str(transaction_amount) if transaction_amount > 0 else "",
                "authMaker": verified_only,
                "canTrade": True
            }

            response = requests.post(
                'https://api2.bybit.com/spot/api/otc/item/list',
                headers=headers,
                json=payload,
                timeout=10
            )
            
            # Додаємо логування відповіді для діагностики
            logging.info(f"Bybit API response: {response.text}")
            
            response.raise_for_status()
            data = response.json()

            if not data or 'result' not in data or 'items' not in data['result']:
                logging.error(f"Неправильна відповідь від Bybit API: {data}")
                return []

            offers = []
            for item in data['result']['items']:
                try:
                    amount = float(item['quantity'])
                    if limit_amount > 0 and amount < limit_amount:
                        continue

                    price = float(item['price'])
                    if transaction_amount > 0:
                        min_amount = float(item['minAmount'])
                        max_amount = float(item['maxAmount'])
                        if transaction_amount < min_amount or transaction_amount > max_amount:
                            continue

                    if verified_only and not item['advertiser'].get('isVerified'):
                        continue

                    offer = {
                        'price': price,
                        'amount': amount,
                        'merchant': item['advertiser']['nickName'],
                        'completion': f"{float(item['advertiser'].get('monthFinishRate', 0)) * 100:.0f}%",
                        'payment_methods': [method['identifier'] for method in item['adv']['tradeMethods']],
                        'exchange': 'Bybit'
                    }
                    offers.append(offer)
                except Exception as e:
                    logging.error(f"Помилка обробки пропозиції Bybit: {e}")
                    continue

            # Сортуємо за ціною
            offers.sort(key=lambda x: x['price'], reverse=(side == 'SELL'))
            
            return offers[:3]

        except Exception as e:
            logging.error(f"Помилка отримання P2P пропозицій Bybit: {e}")
            return []

    @staticmethod
    def get_buy_offers(context=None):
        verified_only = context.user_data.get('verified_only', False) if context else False
        limit_amount = context.user_data.get('limit_amount', 0) if context else 0
        transaction_amount = context.user_data.get('transaction_amount', 0) if context else 0
        
        return BybitAPI.get_p2p_offers(
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
        
        return BybitAPI.get_p2p_offers(
            side='SELL',
            verified_only=verified_only,
            limit_amount=limit_amount,
            transaction_amount=transaction_amount
        ) 