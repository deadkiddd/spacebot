#!/usr/bin/env python3
import os
import time
import json
import requests
import threading
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

class RenderTelegramBot:
    def __init__(self):
        self.token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.admin_id = os.environ.get('ADMIN_ID')
        self.offset = 0
        self.running = False
        
    def send_message(self, chat_id, text, keyboard=None):
        data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
        if keyboard:
            data['reply_markup'] = json.dumps(keyboard)
        try:
            response = requests.post(f'https://api.telegram.org/bot{self.token}/sendMessage', json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def handle_start(self, chat_id, user_name):
        welcome = f"""🤖 Welcome {user_name}!

Payment Bot is online and ready.

Available options:
• Digital Products: $29.99, $49.99, $99.99
• Services: Twitter, ChatGPT, YouTube
• Payment: Cards, Crypto, RUB

Choose an option below:"""
        
        keyboard = {'inline_keyboard': [
            [{'text': '🛍️ Shop Products', 'callback_data': 'products'}],
            [{'text': '💼 Services', 'callback_data': 'services'}],
            [{'text': '❓ Help', 'callback_data': 'help'}]
        ]}
        
        success = self.send_message(chat_id, welcome, keyboard)
        if chat_id != self.admin_id:
            self.send_message(self.admin_id, f"New user: {user_name} (ID: {chat_id})")
        return success
    
    def handle_pay(self, chat_id):
        products = """🛍️ Digital Products:

1. **Premium Software License** - $29.99
   ✓ Lifetime access to all features
   
2. **Digital Course Bundle** - $49.99
   ✓ 5 premium courses with certificates
   
3. **VIP Membership** - $99.99
   ✓ Exclusive premium content access

Select a product to purchase:"""
        
        keyboard = {'inline_keyboard': [
            [{'text': 'Software License $29.99', 'callback_data': 'buy_software'}],
            [{'text': 'Course Bundle $49.99', 'callback_data': 'buy_courses'}],
            [{'text': 'VIP Membership $99.99', 'callback_data': 'buy_vip'}],
            [{'text': '🔙 Main Menu', 'callback_data': 'menu'}]
        ]}
        
        return self.send_message(chat_id, products, keyboard)
    
    def handle_services(self, chat_id):
        services = """💼 Professional Services:

🐦 **Twitter Services**
• Account management and growth
• Content creation and strategy

💬 **ChatGPT Services**
• Premium access and integrations
• Custom bot development

📺 **YouTube Services**
• Channel optimization
• Analytics and growth strategy

Contact admin for custom pricing and requirements."""
        
        keyboard = {'inline_keyboard': [
            [{'text': '🐦 Twitter', 'callback_data': 'service_twitter'}],
            [{'text': '💬 ChatGPT', 'callback_data': 'service_chatgpt'}],
            [{'text': '📺 YouTube', 'callback_data': 'service_youtube'}],
            [{'text': '🔙 Main Menu', 'callback_data': 'menu'}]
        ]}
        
        return self.send_message(chat_id, services, keyboard)
    
    def handle_help(self, chat_id):
        help_text = """❓ Bot Help:

**Available Commands:**
/start - Main menu and welcome
/pay - Browse digital products
/services - Professional services
/help - This help message

**Payment Methods:**
💳 Credit/Debit Cards (Visa, MasterCard)
₿ Cryptocurrency (SOL, BSC, EVM, TRX)
💰 RUB payments

**Support:**
Contact admin for assistance with orders or questions."""
        
        keyboard = {'inline_keyboard': [
            [{'text': '🛍️ Products', 'callback_data': 'products'}],
            [{'text': '💼 Services', 'callback_data': 'services'}],
            [{'text': '🔙 Main Menu', 'callback_data': 'menu'}]
        ]}
        
        return self.send_message(chat_id, help_text, keyboard)
    
    def handle_callback(self, chat_id, data, user_name):
        if data == 'products':
            return self.handle_pay(chat_id)
        elif data == 'services':
            return self.handle_services(chat_id)
        elif data == 'help':
            return self.handle_help(chat_id)
        elif data == 'menu':
            return self.handle_start(chat_id, user_name)
        elif data.startswith('buy_'):
            return self.handle_purchase(chat_id, data, user_name)
        elif data.startswith('service_'):
            return self.handle_service_inquiry(chat_id, data, user_name)
    
    def handle_purchase(self, chat_id, product_data, user_name):
        products = {
            'buy_software': {'name': 'Premium Software License', 'price': 29.99},
            'buy_courses': {'name': 'Digital Course Bundle', 'price': 49.99},
            'buy_vip': {'name': 'VIP Membership', 'price': 99.99}
        }
        
        if product_data in products:
            product = products[product_data]
            purchase_msg = f"""💳 Purchase Request: {product['name']}
Price: ${product['price']}

Payment methods available:
💳 Card payments (secure processing)
₿ Cryptocurrency (multiple coins)
💰 RUB payments

Admin will contact you shortly to complete the payment process."""
            
            keyboard = {'inline_keyboard': [
                [{'text': '💬 Contact Admin', 'callback_data': 'contact_admin'}],
                [{'text': '🔙 Back to Products', 'callback_data': 'products'}]
            ]}
            
            self.send_message(chat_id, purchase_msg, keyboard)
            
            admin_msg = f"""🛒 Purchase Request:
Product: {product['name']}
Price: ${product['price']}
Customer: {user_name} (ID: {chat_id})
Time: {datetime.now().strftime('%H:%M %d/%m/%Y')}

Contact customer to complete payment."""
            
            return self.send_message(self.admin_id, admin_msg)
    
    def handle_service_inquiry(self, chat_id, service_data, user_name):
        services = {
            'service_twitter': 'Twitter Services',
            'service_chatgpt': 'ChatGPT Services',
            'service_youtube': 'YouTube Services'
        }
        
        service_name = services.get(service_data, 'Service')
        
        inquiry_msg = f"""💼 {service_name} Inquiry

Thank you for your interest in our {service_name.lower()}!

Our team will contact you within 24 hours to discuss:
• Your specific requirements
• Custom pricing options
• Project timeline
• Payment methods

Admin has been notified of your inquiry."""
        
        keyboard = {'inline_keyboard': [
            [{'text': '💬 Contact Admin', 'callback_data': 'contact_admin'}],
            [{'text': '🔙 Back to Services', 'callback_data': 'services'}]
        ]}
        
        self.send_message(chat_id, inquiry_msg, keyboard)
        
        admin_msg = f"""💼 Service Inquiry:
Service: {service_name}
Customer: {user_name} (ID: {chat_id})
Time: {datetime.now().strftime('%H:%M %d/%m/%Y')}

Contact customer for requirements and pricing."""
        
        return self.send_message(self.admin_id, admin_msg)
    
    def process_update(self, update):
        try:
            if 'message' in update:
                message = update['message']
                chat_id = str(message['chat']['id'])
                user_name = message['from'].get('first_name', 'User')
                
                if 'text' in message:
                    text = message['text'].strip().lower()
                    
                    if text.startswith('/start'):
                        self.handle_start(chat_id, user_name)
                    elif text.startswith('/pay'):
                        self.handle_pay(chat_id)
                    elif text.startswith('/services'):
                        self.handle_services(chat_id)
                    elif text.startswith('/help'):
                        self.handle_help(chat_id)
                    else:
                        self.send_message(chat_id, "Use /start to see available options and commands.")
            
            elif 'callback_query' in update:
                callback = update['callback_query']
                chat_id = str(callback['message']['chat']['id'])
                data = callback['data']
                user_name = callback['from'].get('first_name', 'User')
                
                self.handle_callback(chat_id, data, user_name)
                
                requests.post(f'https://api.telegram.org/bot{self.token}/answerCallbackQuery',
                            json={'callback_query_id': callback['id']}, timeout=5)
                
        except Exception as e:
            print(f"Error processing update: {e}")
    
    def poll_updates(self):
        while self.running:
            try:
                response = requests.get(f'https://api.telegram.org/bot{self.token}/getUpdates',
                                     params={'offset': self.offset, 'timeout': 30}, timeout=35)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok') and data.get('result'):
                        updates = data['result']
                        
                        for update in updates:
                            self.process_update(update)
                            self.offset = update['update_id'] + 1
                        
                        if updates:
                            print(f"Processed {len(updates)} updates")
                
            except Exception as e:
                print(f"Polling error: {e}")
                time.sleep(5)
    
    def start_polling(self):
        if not self.running:
            self.running = True
            polling_thread = threading.Thread(target=self.poll_updates, daemon=True)
            polling_thread.start()
            
            if self.admin_id:
                self.send_message(self.admin_id, "Bot deployed on Render.com and active!")
            
            print("Bot polling started on Render.com")
    
    def stop_polling(self):
        self.running = False

telegram_bot = RenderTelegramBot()

@app.route('/')
def health():
    return jsonify({'status': 'online', 'bot_active': telegram_bot.running, 'timestamp': datetime.now().isoformat()})

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        if update:
            telegram_bot.process_update(update)
        return "OK"
    except Exception as e:
        print(f"Webhook error: {e}")
        return "Error", 500

@app.route('/start_bot', methods=['POST'])
def start_bot():
    telegram_bot.start_polling()
    return jsonify({'status': 'Bot started'})

@app.route('/stop_bot', methods=['POST'])
def stop_bot():
    telegram_bot.stop_polling()
    return jsonify({'status': 'Bot stopped'})

if __name__ == '__main__':
    telegram_bot.start_polling()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
