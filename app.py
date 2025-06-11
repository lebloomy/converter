from flask import Flask, render_template, request, jsonify
import requests
from models import db, ExchangeRate  
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///currency.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    print("База данных инициализирована")  
API_KEY = 'b498530742bde72a21e8e12061bc2ac2'
BASE_URL = 'https://api.exchangeratesapi.io/latest' 

@app.route('/update_rates', methods=['POST'])
def update_rates():
    try:
        response = requests.get(f"{BASE_URL}?access_key={API_KEY}")
        response.raise_for_status()
        data = response.json()

        rate_entry = ExchangeRate.query.first()
        if not rate_entry:
            rate_entry = ExchangeRate(base_currency=data['base'], rates=data['rates'])
            db.session.add(rate_entry)
        else:
            rate_entry.base_currency = data['base']
            rate_entry.rates = data['rates']
        rate_entry.updated_at = datetime.datetime.now(datetime.timezone.utc)
        db.session.commit()

        print("Данные сохранены в БД:", ExchangeRate.query.first().rates)
        return jsonify({"success": True, "message": "Курсы обновлены"})
    except Exception as e:
        db.session.rollback()
        print("Ошибка сохранения в БД:", str(e))
        return jsonify({"success": False, "error": f"Ошибка сохранения: {str(e)}"})

@app.route('/last_updated', methods=['GET'])
def last_updated():
    rate_entry = ExchangeRate.query.first()
    if rate_entry:
        return jsonify({"updated_at": rate_entry.updated_at.strftime("%Y-%m-%d %H:%M:%S")})
    return jsonify({"updated_at": "Нет данных"})

@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.json
        from_curr = data['from']
        to_curr = data['to']
        amount = float(data['amount'])  

        rate_entry = ExchangeRate.query.first()
        if not rate_entry:
            return jsonify({"error": "Курсы не загружены. Нажмите 'Обновить курсы'."})

        print("Полученные данные:", data)
        print("Доступные валюты:", list(rate_entry.rates.keys()))

        if from_curr not in rate_entry.rates or to_curr not in rate_entry.rates:
            return jsonify({"error": f"Валюта не найдена: {from_curr} → {to_curr}"})

        rate_from = rate_entry.rates[from_curr]
        rate_to = rate_entry.rates[to_curr]

        if rate_from == 0:
            return jsonify({"error": "Курс для исходной валюты равен нулю"})

        converted = amount * (rate_to / rate_from)
        return jsonify({"result": round(converted, 2)})
    except Exception as e:
        print("Ошибка конвертации:", str(e))
        return jsonify({"error": f"Ошибка сервера: {str(e)}"})

@app.route('/currencies', methods=['GET'])
def get_currencies():
    rate_entry = ExchangeRate.query.first()
    if not rate_entry:
        default_currencies = ['USD', 'CNY', 'RUB']
        return jsonify({"currencies": default_currencies})
    
    currencies = list(rate_entry.rates.keys())
    return jsonify({"currencies": currencies})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/debug', methods=['GET'])
def debug():
    rate_entry = ExchangeRate.query.first()
    if rate_entry:
        return jsonify({
            "base": rate_entry.base_currency,
            "rates_count": len(rate_entry.rates),
            "updated_at": rate_entry.updated_at.isoformat()
        })
    return jsonify({"error": "Данные в БД отсутствуют"})

if __name__ == '__main__':
    with app.app_context():
        update_rates()  
    app.run(debug=True)