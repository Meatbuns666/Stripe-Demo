from faker import Faker
from flask import Flask, render_template, request, jsonify
import stripe
import requests

stripe.api_key = '你的sk'

TURNSTILE_SECRET_KEY = "你的TURNSTILE_SECRET_KEY"

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    try:
        # 获取前端发送的 Turnstile token
        data = request.json
        turnstile_token = data.get("turnstileToken")

        if not turnstile_token:
            return jsonify(error="未提供 Turnstile token"), 403

        # 验证 Turnstile token
        turnstile_response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": TURNSTILE_SECRET_KEY,
                "response": turnstile_token
            }
        )
        turnstile_result = turnstile_response.json()

        if not turnstile_result.get("success"):
            return jsonify(error="Turnstile 验证失败"), 403

        # 如果 Turnstile 验证通过，创建支付意图
        amount = 100
        fake = Faker('en_US')
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            payment_method_types=['card'],
            metadata={
                "first_name": fake.first_name(),
                "last_name": fake.last_name()
            }
        )
        return jsonify({'clientSecret': intent.client_secret})
    except Exception as e:
        return jsonify(error=str(e)), 403

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=2000, debug=False)
