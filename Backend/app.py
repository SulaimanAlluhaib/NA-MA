from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import requests
import re
from openai import OpenAI
import json

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///namaai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)

db = SQLAlchemy(app)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Tarabut API configuration
TARABUT_BASE_URL = "https://api.sau.sandbox.tarabutgateway.io"
TARABUT_TOKEN_URL = "https://oauth.tarabutgateway.io/sandbox/token"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_user_id = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tarabut_access_token = db.Column(db.String(500))

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    account_id = db.Column(db.String(100), nullable=False)
    account_name = db.Column(db.String(100))
    account_type = db.Column(db.String(50))
    bank_name = db.Column(db.String(100))
    provider_id = db.Column(db.String(10))
    balance = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='SAR')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    transaction_id = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='SAR')
    credit_debit = db.Column(db.String(10))
    transaction_date = db.Column(db.DateTime)
    category = db.Column(db.String(50))
    merchant = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)
    messages = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def get_tarabut_token():
    """Get access token from Tarabut API"""
    try:
        # Check if environment variables are set
        client_id = os.getenv('TARABUT_CLIENT_ID')
        client_secret = os.getenv('TARABUT_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            print("Missing Tarabut credentials in environment variables")
            return None
        
        payload = {
            "clientId": client_id,
            "clientSecret": client_secret,
            "grantType": "client_credentials"
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-TG-CustomerUserId': 'namaai-user'
        }
        
        print(f"Requesting token from: {TARABUT_TOKEN_URL}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(TARABUT_TOKEN_URL, json=payload, headers=headers)
        
        print(f"Token response status: {response.status_code}")
        print(f"Token response: {response.text}")
        
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            print(f"Token error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

def categorize_transaction(description, amount):
    """Categorize transaction using AI"""
    try:
        prompt = f"""
        Categorize this transaction:
        Description: {description}
        Amount: {amount} SAR
        
        Categories to choose from:
        - Food & Dining
        - Shopping
        - Transportation
        - Entertainment
        - Bills & Utilities
        - Healthcare
        - Education
        - Travel
        - Groceries
        - Gas & Fuel
        - Banking & Finance
        - Other
        
        Also extract the merchant name if possible.
        
        Respond in JSON format:
        {{"category": "category_name", "merchant": "merchant_name"}}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get('category', 'Other'), result.get('merchant', 'Unknown')
    except Exception as e:
        print(f"Categorization error: {e}")
        return 'Other', 'Unknown'

@app.route('/api/providers', methods=['GET'])
def get_providers():
    """Get available bank providers"""
    try:
        # For demo purposes, return static Saudi bank data if Tarabut fails
        static_providers = {
            "providers": [
                {
                    "providerId": "SNB",
                    "name": "Saudi National Bank",
                    "displayName": "SNB",
                    "logoUrl": "https://tg-external-entities-prod.s3.me-south-1.amazonaws.com/SNB.png",
                    "countryCode": "SAU",
                    "aisStatus": "AVAILABLE",
                    "pisStatus": "UNAVAILABLE"
                },
                {
                    "providerId": "SABR-SAU",
                    "name": "Saudi British Bank",
                    "displayName": "SABB",
                    "logoUrl": "https://tg-external-entities-prod.s3.me-south-1.amazonaws.com/SABR-SAU.png",
                    "countryCode": "SAU",
                    "aisStatus": "AVAILABLE",
                    "pisStatus": "AVAILABLE"
                },
                {
                    "providerId": "RIBL",
                    "name": "Riyad Bank",
                    "displayName": "Riyad Bank",
                    "logoUrl": "https://tg-external-entities-prod.s3.me-south-1.amazonaws.com/RIBL.png",
                    "countryCode": "SAU",
                    "aisStatus": "AVAILABLE",
                    "pisStatus": "UNAVAILABLE"
                },
                {
                    "providerId": "ANBB",
                    "name": "Arab National Bank",
                    "displayName": "ANB",
                    "logoUrl": "https://tg-external-entities-prod.s3.me-south-1.amazonaws.com/ANBB.png",
                    "countryCode": "SAU",
                    "aisStatus": "AVAILABLE",
                    "pisStatus": "UNAVAILABLE"
                }
            ]
        }
        
        token = get_tarabut_token()
        if not token:
            print("Using static provider data due to token failure")
            return jsonify(static_providers)
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{TARABUT_BASE_URL}/v1/providers", headers=headers)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            print(f"Providers API error: {response.status_code} - {response.text}")
            print("Falling back to static provider data")
            return jsonify(static_providers)
    except Exception as e:
        print(f"Error in get_providers: {e}")
        # Return static data as fallback
        return jsonify({
            "providers": [
                {
                    "providerId": "SNB",
                    "name": "Saudi National Bank",
                    "displayName": "SNB",
                    "logoUrl": "",
                    "countryCode": "SAU",
                    "aisStatus": "AVAILABLE",
                    "pisStatus": "UNAVAILABLE"
                }
            ]
        })

@app.route('/api/register', methods=['POST'])
def register_user():
    """Register a new user"""
    data = request.get_json()
    
    try:
        user = User(
            customer_user_id=data['customerUserId'],
            first_name=data['firstName'],
            last_name=data['lastName'],
            email=data['email'],
            phone=data.get('phone', '')
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'userId': user.id,
            'message': 'User registered successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create-intent', methods=['POST'])
def create_intent():
    """Create Tarabut intent for bank connection"""
    data = request.get_json()
    token = get_tarabut_token()
    
    if not token:
        return jsonify({'error': 'Failed to get access token'}), 500
    
    try:
        payload = {
            "user": {
                "customerUserId": data['customerUserId'],
                "firstName": data['firstName'],
                "lastName": data['lastName'],
                "email": data['email']
            },
            "redirectUrl": data.get('redirectUrl', 'https://namaai.app/callback')
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{TARABUT_BASE_URL}/accountInformation/v1/intent",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Failed to create intent'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/accounts/<user_id>', methods=['GET'])
def get_user_accounts(user_id):
    """Get user accounts with balances"""
    token = get_tarabut_token()
    if not token:
        return jsonify({'error': 'Failed to get access token'}), 500
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Get accounts from Tarabut
        response = requests.get(f"{TARABUT_BASE_URL}/accountInformation/v2/accounts", headers=headers)
        
        if response.status_code == 200:
            accounts_data = response.json()
            
            # Store/update accounts in database
            user = User.query.get(user_id)
            if user:
                for acc_data in accounts_data.get('accounts', []):
                    account = Account.query.filter_by(
                        user_id=user_id,
                        account_id=acc_data.get('accountId')
                    ).first()
                    
                    if not account:
                        account = Account(
                            user_id=user_id,
                            account_id=acc_data.get('accountId'),
                            account_name=acc_data.get('accountName'),
                            account_type=acc_data.get('accountType'),
                            bank_name=acc_data.get('bankName'),
                            provider_id=acc_data.get('providerId')
                        )
                        db.session.add(account)
                    
                    # Update balance
                    balance_response = requests.get(
                        f"{TARABUT_BASE_URL}/accountInformation/v2/accounts/{account.account_id}/balances",
                        headers=headers
                    )
                    
                    if balance_response.status_code == 200:
                        balance_data = balance_response.json()
                        if balance_data.get('balances'):
                            account.balance = float(balance_data['balances'][0].get('amount', {}).get('value', 0))
                            account.currency = balance_data['balances'][0].get('amount', {}).get('currency', 'SAR')
                    
                    account.last_updated = datetime.utcnow()
                
                db.session.commit()
            
            return jsonify(accounts_data)
        else:
            return jsonify({'error': 'Failed to fetch accounts'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions/<account_id>', methods=['GET'])
def get_account_transactions(account_id):
    """Get account transactions and categorize them"""
    token = get_tarabut_token()
    if not token:
        return jsonify({'error': 'Failed to get access token'}), 500
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Get date range (last 3 months)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        params = {
            'fromBookingDateTime': start_date.isoformat() + 'Z',
            'toBookingDateTime': end_date.isoformat() + 'Z'
        }
        
        response = requests.get(
            f"{TARABUT_BASE_URL}/accountInformation/v2/accounts/{account_id}/transactions",
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            transactions_data = response.json()
            
            # Process and categorize transactions
            processed_transactions = []
            category_totals = {}
            
            for trans in transactions_data.get('transactions', []):
                description = trans.get('transactionDescription', '')
                amount = float(trans.get('amount', {}).get('value', 0))
                
                # Categorize transaction
                category, merchant = categorize_transaction(description, amount)
                
                # Store in database
                account = Account.query.filter_by(account_id=account_id).first()
                if account:
                    transaction = Transaction(
                        account_id=account.id,
                        transaction_id=trans.get('transactionId'),
                        description=description,
                        amount=amount,
                        currency=trans.get('amount', {}).get('currency', 'SAR'),
                        credit_debit=trans.get('creditDebitIndicator'),
                        transaction_date=datetime.fromisoformat(trans.get('transactionDateTime', '').replace('Z', '+00:00')),
                        category=category,
                        merchant=merchant
                    )
                    
                    db.session.merge(transaction)
                
                # Calculate category totals (for debit transactions only)
                if trans.get('creditDebitIndicator') == 'Debit':
                    if category not in category_totals:
                        category_totals[category] = 0
                    category_totals[category] += amount
                
                processed_transactions.append({
                    **trans,
                    'category': category,
                    'merchant': merchant
                })
            
            db.session.commit()
            
            # Sort categories by spending
            top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return jsonify({
                'transactions': processed_transactions,
                'categoryTotals': dict(category_totals),
                'topCategories': top_categories
            })
        else:
            return jsonify({'error': 'Failed to fetch transactions'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/send', methods=['POST'])
def chat_with_ai():
    """Chat with AI financial advisor"""
    data = request.get_json()
    user_id = data.get('userId')
    message = data.get('message')
    session_id = data.get('sessionId', 'default')
    
    try:
        # Get user's financial data
        user = User.query.get(user_id)
        accounts = Account.query.filter_by(user_id=user_id).all()
        
        # Prepare context
        financial_context = {
            'total_balance': sum(acc.balance for acc in accounts),
            'accounts_count': len(accounts),
            'currency': accounts[0].currency if accounts else 'SAR'
        }
        
        # Get recent transactions for context
        recent_transactions = []
        for account in accounts:
            transactions = Transaction.query.filter_by(account_id=account.id)\
                .order_by(Transaction.transaction_date.desc())\
                .limit(10).all()
            
            for trans in transactions:
                recent_transactions.append({
                    'description': trans.description,
                    'amount': trans.amount,
                    'category': trans.category,
                    'date': trans.transaction_date.isoformat() if trans.transaction_date else None
                })
        
        # Create AI prompt
        system_prompt = f"""
        You are Nama'aAI (نَماء), an intelligent Arabic-English bilingual financial advisor.
        
        User's Financial Profile:
        - Total Balance: {financial_context['total_balance']} {financial_context['currency']}
        - Number of Accounts: {financial_context['accounts_count']}
        
        Recent Transactions Context:
        {json.dumps(recent_transactions[:5], indent=2)}
        
        Provide personalized financial advice, budgeting tips, and investment suggestions.
        Be concise but helpful. Support both Arabic and English.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        
        # Store chat session
        chat_session = ChatSession.query.filter_by(
            user_id=user_id,
            session_id=session_id
        ).first()
        
        if not chat_session:
            chat_session = ChatSession(
                user_id=user_id,
                session_id=session_id,
                messages=json.dumps([])
            )
            db.session.add(chat_session)
        
        # Update messages
        messages = json.loads(chat_session.messages)
        messages.extend([
            {"role": "user", "content": message, "timestamp": datetime.utcnow().isoformat()},
            {"role": "assistant", "content": ai_response, "timestamp": datetime.utcnow().isoformat()}
        ])
        chat_session.messages = json.dumps(messages)
        
        db.session.commit()
        
        return jsonify({
            'response': ai_response,
            'sessionId': session_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/investment-advice', methods=['POST'])
def get_investment_advice():
    """Get personalized investment advice"""
    data = request.get_json()
    user_id = data.get('userId')
    risk_tolerance = data.get('riskTolerance', 'moderate')
    investment_amount = data.get('investmentAmount', 0)
    
    try:
        # Get user's financial profile
        user = User.query.get(user_id)
        accounts = Account.query.filter_by(user_id=user_id).all()
        total_balance = sum(acc.balance for acc in accounts)
        
        # Get spending patterns
        transactions = db.session.query(Transaction.category, db.func.sum(Transaction.amount))\
            .filter(Transaction.credit_debit == 'Debit')\
            .group_by(Transaction.category)\
            .all()
        
        monthly_spending = sum(amount for _, amount in transactions) / 3  # 3 months average
        
        # Create investment advice prompt
        prompt = f"""
        Create personalized investment advice for a Saudi user:
        
        Financial Profile:
        - Total Balance: {total_balance} SAR
        - Monthly Spending: {monthly_spending} SAR
        - Available for Investment: {investment_amount} SAR
        - Risk Tolerance: {risk_tolerance}
        
        Provide:
        1. Asset allocation recommendations
        2. Specific investment options (Saudi market focus)
        3. Risk assessment
        4. Timeline recommendations
        
        Format as JSON with sections for each recommendation.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        advice = response.choices[0].message.content
        
        return jsonify({
            'investmentAdvice': advice,
            'userProfile': {
                'totalBalance': total_balance,
                'monthlySpending': monthly_spending,
                'riskTolerance': risk_tolerance
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alternatives/<category>', methods=['GET'])
def get_spending_alternatives(category):
    """Get cheaper alternatives for spending categories"""
    try:
        # This would integrate with Tivaly API for local alternatives
        # For now, using AI to suggest alternatives
        
        prompt = f"""
        Suggest 3-5 cheaper alternatives for the category "{category}" in Saudi Arabia.
        Focus on local options, apps, or services that could help save money.
        
        Format as JSON array with:
        - name: Alternative name
        - description: Brief description
        - estimatedSavings: Percentage savings
        - type: "app", "service", "store", etc.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        alternatives = json.loads(response.choices[0].message.content)
        
        return jsonify({'alternatives': alternatives})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/insights/dashboard/<user_id>', methods=['GET'])
def get_dashboard_data(user_id):
    """Get comprehensive dashboard data"""
    try:
        # Get user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user accounts
        accounts = Account.query.filter_by(user_id=user_id).all()
        total_balance = sum(acc.balance for acc in accounts) if accounts else 0.0
        
        # Generate some demo data for hackathon
        if not accounts:
            # Create demo account
            demo_account = Account(
                user_id=user_id,
                account_id=f"DEMO_{user_id}",
                account_name="Demo Account",
                account_type="current",
                bank_name="Saudi National Bank",
                provider_id="SNB",
                balance=15000.0,
                currency="SAR"
            )
            db.session.add(demo_account)
            db.session.commit()
            
            # Create demo transactions
            demo_transactions = [
                {
                    'description': 'Supermarket Purchase',
                    'amount': 250.0,
                    'category': 'Groceries',
                    'credit_debit': 'Debit'
                },
                {
                    'description': 'Restaurant Bill',
                    'amount': 180.0,
                    'category': 'Food & Dining',
                    'credit_debit': 'Debit'
                },
                {
                    'description': 'Gas Station',
                    'amount': 120.0,
                    'category': 'Transportation',
                    'credit_debit': 'Debit'
                },
                {
                    'description': 'Online Shopping',
                    'amount': 350.0,
                    'category': 'Shopping',
                    'credit_debit': 'Debit'
                },
                {
                    'description': 'Salary Credit',
                    'amount': 8000.0,
                    'category': 'Income',
                    'credit_debit': 'Credit'
                }
            ]
            
            for trans_data in demo_transactions:
                transaction = Transaction(
                    account_id=demo_account.id,
                    transaction_id=f"DEMO_{len(demo_transactions)}_{user_id}",
                    description=trans_data['description'],
                    amount=trans_data['amount'],
                    currency='SAR',
                    credit_debit=trans_data['credit_debit'],
                    transaction_date=datetime.now() - timedelta(days=5),
                    category=trans_data['category'],
                    merchant='Demo Merchant'
                )
                db.session.add(transaction)
            
            db.session.commit()
            accounts = [demo_account]
            total_balance = demo_account.balance
        
        # Get spending by category (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        category_spending = db.session.query(
            Transaction.category,
            db.func.sum(Transaction.amount).label('total'),
            db.func.count(Transaction.id).label('count')
        ).filter(
            Transaction.credit_debit == 'Debit',
            Transaction.transaction_date >= thirty_days_ago
        ).group_by(Transaction.category).all()
        
        # Get recent transactions
        recent_transactions = Transaction.query\
            .order_by(Transaction.transaction_date.desc())\
            .limit(10).all()
        
        # Calculate monthly income and spending
        monthly_income = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.credit_debit == 'Credit',
            Transaction.transaction_date >= thirty_days_ago
        ).scalar() or 0
        
        monthly_spending = sum(float(amount) for _, amount, _ in category_spending)
        savings_rate = ((monthly_income - monthly_spending) / monthly_income * 100) if monthly_income > 0 else 0
        
        return jsonify({
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            },
            'totalBalance': total_balance,
            'accountsCount': len(accounts),
            'accounts': [{
                'id': acc.id,
                'account_id': acc.account_id,
                'account_name': acc.account_name,
                'balance': acc.balance,
                'bank_name': acc.bank_name,
                'currency': acc.currency
            } for acc in accounts],
            'monthlyIncome': float(monthly_income),
            'monthlySpending': monthly_spending,
            'savingsRate': max(0, savings_rate),
            'categorySpending': [
                {
                    'category': cat if cat else 'Other',
                    'amount': float(amount),
                    'count': count,
                    'percentage': (float(amount) / monthly_spending * 100) if monthly_spending > 0 else 0
                }
                for cat, amount, count in category_spending
            ],
            'recentTransactions': [{
                'id': trans.id,
                'description': trans.description,
                'amount': trans.amount,
                'category': trans.category,
                'credit_debit': trans.credit_debit,
                'date': trans.transaction_date.isoformat() if trans.transaction_date else None
            } for trans in recent_transactions]
        })
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/create-test-user', methods=['POST'])
def create_test_user():
    """Create a test user for debugging"""
    try:
        # Check if test user already exists
        test_user = User.query.filter_by(email='test@namaai.com').first()
        
        if not test_user:
            test_user = User(
                customer_user_id='test_user_123',
                first_name='Test',
                last_name='User',
                email='test@namaai.com',
                phone='966501234567'
            )
            db.session.add(test_user)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'userId': test_user.id,
            'message': 'Test user created/found',
            'user': {
                'id': test_user.id,
                'email': test_user.email,
                'first_name': test_user.first_name,
                'last_name': test_user.last_name
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/env', methods=['GET'])
def debug_env():
    """Debug endpoint to check environment variables"""
    return jsonify({
        'tarabut_client_id_set': bool(os.getenv('TARABUT_CLIENT_ID')),
        'tarabut_client_secret_set': bool(os.getenv('TARABUT_CLIENT_SECRET')),
        'openai_key_set': bool(os.getenv('OPENAI_API_KEY')),
        'tarabut_base_url': TARABUT_BASE_URL,
        'tarabut_token_url': TARABUT_TOKEN_URL,
        'flask_env': os.getenv('FLASK_ENV', 'not_set'),
        'database_url': app.config['SQLALCHEMY_DATABASE_URI']
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)