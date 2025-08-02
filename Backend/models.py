from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_user_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    national_id = db.Column(db.String(20))
    preferred_language = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    accounts = db.relationship('Account', backref='user', lazy=True, cascade='all, delete-orphan')
    chat_sessions = db.relationship('ChatSession', backref='user', lazy=True, cascade='all, delete-orphan')
    financial_goals = db.relationship('FinancialGoal', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_user_id': self.customer_user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'preferred_language': self.preferred_language,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

class BankProvider(db.Model):
    __tablename__ = 'bank_providers'
    
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(100))
    logo_url = db.Column(db.String(200))
    country_code = db.Column(db.String(10))
    ais_status = db.Column(db.String(20))  # AVAILABLE, UNAVAILABLE
    pis_status = db.Column(db.String(20))  # AVAILABLE, UNAVAILABLE
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'provider_id': self.provider_id,
            'name': self.name,
            'display_name': self.display_name,
            'logo_url': self.logo_url,
            'country_code': self.country_code,
            'ais_status': self.ais_status,
            'pis_status': self.pis_status
        }

class Account(db.Model):
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.String(100), nullable=False, index=True)
    account_name = db.Column(db.String(100))
    account_type = db.Column(db.String(50))
    account_subtype = db.Column(db.String(50))
    bank_name = db.Column(db.String(100))
    provider_id = db.Column(db.String(20))
    iban = db.Column(db.String(50))
    balance = db.Column(db.Float, default=0.0)
    available_balance = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='SAR')
    status = db.Column(db.String(20), default='ACTIVE')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='account', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'account_name': self.account_name,
            'account_type': self.account_type,
            'bank_name': self.bank_name,
            'provider_id': self.provider_id,
            'iban': self.iban,
            'balance': self.balance,
            'available_balance': self.available_balance,
            'currency': self.currency,
            'status': self.status,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    transaction_id = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='SAR')
    credit_debit = db.Column(db.String(10))  # Credit, Debit
    transaction_date = db.Column(db.DateTime, index=True)
    booking_date = db.Column(db.DateTime)
    value_date = db.Column(db.DateTime)
    
    # Categorization fields
    category = db.Column(db.String(50), index=True)
    subcategory = db.Column(db.String(50))
    merchant = db.Column(db.String(100), index=True)
    merchant_category = db.Column(db.String(50))
    
    # AI analysis fields
    confidence_score = db.Column(db.Float)
    is_recurring = db.Column(db.Boolean, default=False)
    is_essential = db.Column(db.Boolean)
    
    # Reference fields
    reference_number = db.Column(db.String(100))
    balance_after = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'description': self.description,
            'amount': self.amount,
            'currency': self.currency,
            'credit_debit': self.credit_debit,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'category': self.category,
            'subcategory': self.subcategory,
            'merchant': self.merchant,
            'merchant_category': self.merchant_category,
            'is_recurring': self.is_recurring,
            'is_essential': self.is_essential,
            'confidence_score': self.confidence_score
        }

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False, index=True)
    title = db.Column(db.String(200))
    messages = db.Column(db.Text)  # JSON string
    context_data = db.Column(db.Text)  # JSON string for context
    total_messages = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def get_messages(self):
        if self.messages:
            return json.loads(self.messages)
        return []
    
    def add_message(self, role, content):
        messages = self.get_messages()
        messages.append({
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat()
        })
        self.messages = json.dumps(messages)
        self.total_messages = len(messages)
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'title': self.title,
            'messages': self.get_messages(),
            'total_messages': self.total_messages,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class FinancialGoal(db.Model):
    __tablename__ = 'financial_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    goal_type = db.Column(db.String(50))  # saving, investment, debt_payoff, etc.
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    target_date = db.Column(db.Date)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    status = db.Column(db.String(20), default='active')  # active, completed, paused
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def progress_percentage(self):
        if self.target_amount > 0:
            return min((self.current_amount / self.target_amount) * 100, 100)
        return 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'goal_type': self.goal_type,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'priority': self.priority,
            'status': self.status,
            'progress_percentage': self.progress_percentage(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    total_income = db.Column(db.Float, default=0.0)
    total_budgeted = db.Column(db.Float, default=0.0)
    total_spent = db.Column(db.Float, default=0.0)
    categories = db.Column(db.Text)  # JSON string with category budgets
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='budgets')
    
    def get_categories(self):
        if self.categories:
            return json.loads(self.categories)
        return {}
    
    def set_categories(self, categories_dict):
        self.categories = json.dumps(categories_dict)
    
    def to_dict(self):
        return {
            'id': self.id,
            'month': self.month,
            'year': self.year,
            'total_income': self.total_income,
            'total_budgeted': self.total_budgeted,
            'total_spent': self.total_spent,
            'categories': self.get_categories(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Insight(db.Model):
    __tablename__ = 'insights'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    insight_type = db.Column(db.String(50), nullable=False)  # spending_pattern, budget_alert, etc.
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    data = db.Column(db.Text)  # JSON string with insight data
    priority = db.Column(db.String(20), default='medium')
    is_read = db.Column(db.Boolean, default=False)
    is_actionable = db.Column(db.Boolean, default=True)
    action_taken = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    def get_data(self):
        if self.data:
            return json.loads(self.data)
        return {}
    
    def set_data(self, data_dict):
        self.data = json.dumps(data_dict)
    
    def to_dict(self):
        return {
            'id': self.id,
            'insight_type': self.insight_type,
            'title': self.title,
            'description': self.description,
            'data': self.get_data(),
            'priority': self.priority,
            'is_read': self.is_read,
            'is_actionable': self.is_actionable,
            'action_taken': self.action_taken,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

class Investment(db.Model):
    __tablename__ = 'investments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    investment_type = db.Column(db.String(50), nullable=False)  # stocks, funds, sukuk, etc.
    symbol = db.Column(db.String(20))
    name = db.Column(db.String(200))
    quantity = db.Column(db.Float, default=0.0)
    purchase_price = db.Column(db.Float)
    current_price = db.Column(db.Float)
    currency = db.Column(db.String(10), default='SAR')
    purchase_date = db.Column(db.Date)
    is_sharia_compliant = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def current_value(self):
        if self.current_price and self.quantity:
            return self.current_price * self.quantity
        return 0.0
    
    def total_return(self):
        if self.purchase_price and self.current_price and self.quantity:
            return (self.current_price - self.purchase_price) * self.quantity
        return 0.0
    
    def return_percentage(self):
        if self.purchase_price and self.current_price:
            return ((self.current_price - self.purchase_price) / self.purchase_price) * 100
        return 0.0
    
    def to_dict(self):
        return {
            'id': self.id,
            'investment_type': self.investment_type,
            'symbol': self.symbol,
            'name': self.name,
            'quantity': self.quantity,
            'purchase_price': self.purchase_price,
            'current_price': self.current_price,
            'currency': self.currency,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'is_sharia_compliant': self.is_sharia_compliant,
            'current_value': self.current_value(),
            'total_return': self.total_return(),
            'return_percentage': self.return_percentage(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }