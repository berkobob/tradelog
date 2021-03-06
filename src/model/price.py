from src.model.model import Model
import requests, json

class Price(Model):
    """
    Represents the price of each stock
    """
    collection = "prices"
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/get-quotes"
    params = {
        "region":"GB",
        "lang":"en",
        "symbols": '',
        }
    headers = {
        'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
        'x-rapidapi-key': "eb592d6f74msh1fdca4824b15878p1afbc3jsn261d349004d2",
        'params': ''
        }

    def __init__(self, stock):
        self._id = stock['_id']
        self.price = stock['price']
        self.yahoo = stock['yahoo']
        self.name = stock['name']
        self.currency = stock['currency']

    @classmethod
    def new(cls, trade):
        if cls.get(trade.stock): return

        symbol = trade.stock
        if trade.trade['currency'] == '£':
            symbol = trade.stock[0:-1].replace('.', '-') + trade.stock[-1]
            if symbol[-1] != '.': symbol += '.' 
            symbol += 'L'

        cls({
            '_id': trade.stock,
            'price': trade.trade['price'] if trade.trade['asset'] == 'STK' else 0.0,
            'yahoo': symbol,
            'name': "Update price for name",
            'currency': trade.trade['currency'],

        }).create()

    @classmethod
    def update_prices(cls):
        symbols = []
        for stock in cls.read({}, True):
            symbols.append(stock.yahoo + ',')

        factor = 50
        count = len(symbols)
        iters = count // factor
        for i in range(0, iters):
            fifty = ''
            for j in range(factor*i, factor*i+(factor)):
                fifty += symbols[j]
            cls._API(fifty)

        fifty = ''
        for i in range(factor*iters, count):
            fifty += symbols[i]
        cls._API(fifty)

    @classmethod
    def delete_price(cls, stock):
        cls.read({'_id': stock}).delete()

    @classmethod
    def get_price(cls, positions):
        prices = cls.read({}, True)
        message = []

        for position in positions:
            if 'shares' in position.position:
                _prices = [price for price in prices if price._id == position.stock]
                if len(_prices) == 0: 
                    price = 0
                    currency = ''
                else: 
                    price = _prices[0].price
                    currency = _prices[0].currency
                percent = (price-position.risk_per) / position.risk_per if position.risk_per != 0 else 0
                message.append({
                    'stock': position.stock,
                    'cost': position.risk_per,
                    'price': price,
                    'percent': percent,
                    'value': price * position.quantity,
                    'currency': currency,
                })
        return message

    @classmethod
    def _API(cls, symbols):
        cls.params['symbols'] = symbols
        response = requests.request('GET', cls.url, headers=cls.headers, params=cls.params)
        data = json.loads(response.text)
        results = data['quoteResponse']['result']

        for result in results:
            price = cls.read({'yahoo': result['symbol']})
            if 'regularMarketPrice' in result.keys():
                price.price = result['regularMarketPrice']
                if price.currency == '£': price.price /= 100
            else:
                price.price = 0
                print(f'No price for {result["symbol"]}')
            if 'shortName' in result.keys(): price.name = result['shortName']
            else: price.name = 'Not found'
            price.update()
            print(result['symbol'],': ', price.price)
