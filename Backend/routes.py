from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from models import db, User, Account, Transaction, ChatSession, FinancialGoal, Budget, Insight
from services.tarabut_service import TarabutService
from services.ai_service import AIFinancialAdvisor
import json
import uuid

# Initialize services
tarabut_service = TarabutService()
ai_advisor = AIFinancialAdvisor()

# Create blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/api')
accounts_bp = Blueprint('accounts', __name__, url_prefix='/api/accounts')
transactions_bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')
insights_bp = Blueprint('insights', __name__, url_prefix='/api/insights')

# Authentication Routes
@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400
        
        # Create new user
        user = User(
            customer_user_id=data['customerUserId'],
            first_name=data['firstName'],
            last_name=data['lastName'],
            email=data['email'],
            phone=data.get('phone', ''),
            preferred_language=data.get('language', 'en')
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'userId': user.id,
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Account Routes
@accounts_bp.route('/providers', methods=['GET'])
def get_providers():
    """Get available bank providers"""
    try:
        providers_data = tarabut_service.get_providers()
        if providers_data:
            return jsonify(providers_data)
        else:
            return jsonify({'error': 'Failed to fetch providers'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@accounts_bp.route('/create-intent', methods=['POST'])
def create_intent():
    """Create Tarabut intent for bank connection"""
    try:
        data = request.get_json()
        intent_data = tarabut_service.create_intent(data)
        
        if intent_data:
            return jsonify(intent_data)
        else:
            return jsonify({'error': 'Failed to create intent'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@accounts_bp.route('/<int:user_id>', methods=['GET'])
def get_user_accounts(user_id):
    """Get user accounts with balances"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Get accounts from Tarabut
        accounts_data = tarabut_service.get_accounts()
        
        if accounts_data and 'accounts' in accounts_data:
            for acc_data in accounts_data['accounts']:
                # Check if account exists in database
                account = Account.query.filter_by(
                    user_id=user_id,
                    account_id=acc_data.get('accountId')
                ).first()
                
                if not account:
                    # Create new account
                    account = Account(
                        user_id=user_id,
                        account_id=acc_data.get('accountId'),
                        account_name=acc_data.get('accountName'),
                        account_type=acc_data.get('accountType'),
                        bank_name=acc_data.get('bankName'),
                        provider_id=acc_data.get('providerId'),
                        iban=acc_data.get('iban')
                    )
                    db.session.add(account)
                
                # Update balance
                balance_data = tarabut_service.get_account_balance(account.account_id)
                if balance_data and 'balances' in balance_data:
                    balance_info = balance_data['balances'][0]
                    account.balance = float(balance_info.get('amount', {}).get('value', 0))
                    account.available_balance = float(balance_info.get('availableAmount', {}).get('value', 0))
                    account.currency = balance_info.get('amount', {}).get('currency', 'SAR')
                
                account.last_updated = datetime.utcnow()
            
            db.session.commit()
            
            # Return updated accounts from database
            user_accounts = Account.query.filter_by(user_id=user_id).all()
            return jsonify({
                'accounts': [acc.to_dict() for acc in user_accounts],
                'totalBalance': sum(acc.balance for acc in user_accounts),
                'totalAccounts': len(user_accounts)
            })
        else:
            return jsonify({'accounts': [], 'totalBalance': 0, 'totalAccounts': 0})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@accounts_bp.route('/<int:account_db_id>/sync', methods=['POST'])
def sync_account(account_db_id):
    """Sync account data from bank"""
    try:
        account = Account.query.get_or_404(account_db_id)
        
        # Sync balance
        balance_data = tarabut_service.get_account_balance(account.account_id)
        if balance_data and 'balances' in balance_data:
            balance_info = balance_data['balances'][0]
            account.balance = float(balance_info.get('amount', {}).get('value', 0))
            account.available_balance = float(balance_info.get('availableAmount', {}).get('value', 0))
            account.last_updated = datetime.utcnow()
        
        # Sync recent transactions
        transactions_data = tarabut_service.get_account_transactions(account.account_id)
        if transactions_data and 'transactions' in transactions_data:
            for trans_data in transactions_data['transactions']:
                # Check if transaction exists
                existing_trans = Transaction.query.filter_by(
                    account_id=account.id,
                    transaction_id=trans_data.get('transactionId')
                ).first()
                
                if not existing_trans:
                    # Categorize transaction using AI
                    description = trans_data.get('transactionDescription', '')
                    amount = float(trans_data.get('amount', {}).get('value', 0))
                    
                    category_result = ai_advisor.categorize_transaction(description, amount)
                    
                    # Create new transaction
                    transaction = Transaction(
                        account_id=account.id,
                        transaction_id=trans_data.get('transactionId'),
                        description=description,
                        amount=amount,
                        currency=trans_data.get('amount', {}).get('currency', 'SAR'),
                        credit_debit=trans_data.get('creditDebitIndicator'),
                        transaction_date=datetime.fromisoformat(
                            trans_data.get('transactionDateTime', '').replace('Z', '+00:00')
                        ),
                        category=category_result.get('category'),
                        merchant=category_result.get('merchant'),
                        confidence_score=category_result.get('confidence', 0.0)
                    )
                    db.session.add(transaction)
        
        db.session.commit()
        return jsonify({
            'success': True,
            'account': account.to_dict(),
            'message': 'Account synced successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Transaction Routes
@transactions_bp.route('/account/<int:account_db_id>', methods=['GET'])
def get_account_transactions(account_db_id):
    """Get transactions for an account"""
    try:
        account = Account.query.get_or_404(account_db_id)
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        category = request.args.get('category')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        # Build query
        query = Transaction.query.filter_by(account_id=account.id)
        
        if category:
            query = query.filter(Transaction.category == category)
        
        if from_date:
            query = query.filter(Transaction.transaction_date >= datetime.fromisoformat(from_date))
        
        if to_date:
            query = query.filter(Transaction.transaction_date <= datetime.fromisoformat(to_date))
        
        # Order by date descending
        query = query.order_by(Transaction.transaction_date.desc())
        
        # Paginate
        transactions = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Calculate category totals for the filtered period
        category_totals = {}
        spending_by_category = db.session.query(
            Transaction.category,
            db.func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.account_id == account.id,
            Transaction.credit_debit == 'Debit'
        )
        
        if from_date:
            spending_by_category = spending_by_category.filter(
                Transaction.transaction_date >= datetime.fromisoformat(from_date)
            )
        if to_date:
            spending_by_category = spending_by_category.filter(
                Transaction.transaction_date <= datetime.fromisoformat(to_date)
            )
            
        spending_by_category = spending_by_category.group_by(Transaction.category).all()
        
        for cat, total in spending_by_category:
            if cat:
                category_totals[cat] = float(total)
        
        return jsonify({
            'transactions': [trans.to_dict() for trans in transactions.items],
            'pagination': {
                'page': transactions.page,
                'pages': transactions.pages,
                'per_page': transactions.per_page,
                'total': transactions.total,
                'has_next': transactions.has_next,
                'has_prev': transactions.has_prev
            },
            'categoryTotals': category_totals,
            'topCategories': sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transactions_bp.route('/categorize', methods=['POST'])
def categorize_transactions():
    """Manually categorize transactions"""
    try:
        data = request.get_json()
        transaction_ids = data.get('transaction_ids', [])
        new_category = data.get('category')
        
        if not transaction_ids or not new_category:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Update transactions
        updated = Transaction.query.filter(
            Transaction.id.in_(transaction_ids)
        ).update(
            {'category': new_category, 'updated_at': datetime.utcnow()},
            synchronize_session='fetch'
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'updated_count': updated,
            'message': f'Updated {updated} transactions'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Chat Routes
@chat_bp.route('/send', methods=['POST'])
def send_message():
    """Send message to AI financial advisor"""
    try:
        data = request.get_json()
        user_id = data.get('userId')
        message = data.get('message')
        session_id = data.get('sessionId', str(uuid.uuid4()))
        
        if not user_id or not message:
            return jsonify({'error': 'Missing required fields'}), 400
        
        user = User.query.get_or_404(user_id)
        
        # Get or create chat session
        chat_session = ChatSession.query.filter_by(
            user_id=user_id,
            session_id=session_id
        ).first()
        
        if not chat_session:
            chat_session = ChatSession(
                user_id=user_id,
                session_id=session_id,
                title=message[:50] + '...' if len(message) > 50 else message
            )
            db.session.add(chat_session)
        
        # Build user financial profile
        accounts = Account.query.filter_by(user_id=user_id).all()
        total_balance = sum(acc.balance for acc in accounts)
        
        # Get recent transactions for context
        recent_transactions = []
        for account in accounts:
            transactions = Transaction.query.filter_by(account_id=account.id)\
                .order_by(Transaction.transaction_date.desc())\
                .limit(10).all()
            
            for trans in transactions:
                recent_transactions.append(trans.to_dict())
        
        # Calculate monthly spending
        thirty_days_ago = datetime.now() - timedelta(days=30)
        monthly_spending = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.credit_debit == 'Debit',
            Transaction.transaction_date >= thirty_days_ago
        ).scalar() or 0
        
        # Get spending by category
        category_spending = db.session.query(
            Transaction.category,
            db.func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.credit_debit == 'Debit',
            Transaction.transaction_date >= thirty_days_ago
        ).group_by(Transaction.category).all()
        
        top_categories = [(cat, float(total)) for cat, total in category_spending]
        
        user_profile = {
            'total_balance': total_balance,
            'monthly_spending': float(monthly_spending),
            'accounts_count': len(accounts),
            'recent_transactions': recent_transactions[:5],
            'top_categories': top_categories[:5],
            'savings_rate': max(0, (total_balance - monthly_spending) / total_balance * 100) if total_balance > 0 else 0
        }
        
        # Get conversation history
        message_history = chat_session.get_messages()
        
        # Add user message
        chat_session.add_message('user', message)
        
        # Generate AI response
        ai_response = ai_advisor.generate_financial_advice(
            user_profile, message_history, message
        )
        
        # Add AI response
        chat_session.add_message('assistant', ai_response)
        
        db.session.commit()
        
        return jsonify({
            'response': ai_response,
            'sessionId': session_id,
            'messageCount': chat_session.total_messages
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/sessions/<int:user_id>', methods=['GET'])
def get_chat_sessions(user_id):
    """Get user's chat sessions"""
    try:
        sessions = ChatSession.query.filter_by(
            user_id=user_id,
            is_active=True
        ).order_by(ChatSession.updated_at.desc()).all()
        
        return jsonify({
            'sessions': [session.to_dict() for session in sessions]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/investment-advice', methods=['POST'])
def get_investment_advice():
    """Get personalized investment advice"""
    try:
        data = request.get_json()
        user_id = data.get('userId')
        investment_amount = data.get('investmentAmount', 0)
        risk_tolerance = data.get('riskTolerance', 'moderate')
        
        user = User.query.get_or_404(user_id)
        
        # Build user profile
        accounts = Account.query.filter_by(user_id=user_id).all()
        total_balance = sum(acc.balance for acc in accounts)
        
        # Calculate monthly spending
        thirty_days_ago = datetime.now() - timedelta(days=30)
        monthly_spending = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.credit_debit == 'Debit',
            Transaction.transaction_date >= thirty_days_ago
        ).scalar() or 0
        
        user_profile = {
            'total_balance': total_balance,
            'monthly_spending': float(monthly_spending),
            'accounts_count': len(accounts),
            'age_group': 'adult'  # Could be derived from date_of_birth
        }
        
        # Generate investment advice
        advice = ai_advisor.generate_investment_advice(
            user_profile, investment_amount, risk_tolerance
        )
        
        return jsonify({
            'investmentAdvice': advice,
            'userProfile': user_profile,
            'riskTolerance': risk_tolerance,
            'investmentAmount': investment_amount
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Insights Routes
@insights_bp.route('/dashboard/<int:user_id>', methods=['GET'])
def get_dashboard_insights(user_id):
    """Get comprehensive dashboard insights"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Get accounts
        accounts = Account.query.filter_by(user_id=user_id).all()
        total_balance = sum(acc.balance for acc in accounts)
        
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
        
        # Get monthly income (credit transactions)
        monthly_income = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.credit_debit == 'Credit',
            Transaction.transaction_date >= thirty_days_ago
        ).scalar() or 0
        
        # Calculate savings rate
        monthly_spending = sum(float(amount) for _, amount, _ in category_spending)
        savings_rate = ((monthly_income - monthly_spending) / monthly_income * 100) if monthly_income > 0 else 0
        
        # Get financial goals
        goals = FinancialGoal.query.filter_by(user_id=user_id, status='active').all()
        
        return jsonify({
            'user': user.to_dict(),
            'totalBalance': total_balance,
            'accountsCount': len(accounts),
            'accounts': [acc.to_dict() for acc in accounts],
            'monthlyIncome': float(monthly_income),
            'monthlySpending': monthly_spending,
            'savingsRate': savings_rate,
            'categorySpending': [
                {
                    'category': cat,
                    'amount': float(amount),
                    'count': count,
                    'percentage': (float(amount) / monthly_spending * 100) if monthly_spending > 0 else 0
                }
                for cat, amount, count in category_spending
            ],
            'recentTransactions': [trans.to_dict() for trans in recent_transactions],
            'financialGoals': [goal.to_dict() for goal in goals],
            'insights': _generate_dashboard_insights(user_id, category_spending, monthly_income, monthly_spending)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@insights_bp.route('/alternatives/<category>', methods=['GET'])
def get_spending_alternatives(category):
    """Get spending alternatives for a category"""
    try:
        # Get spending amount for this category
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id parameter required'}), 400
        
        # Calculate category spending
        thirty_days_ago = datetime.now() - timedelta(days=30)
        category_spending = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.category == category,
            Transaction.credit_debit == 'Debit',
            Transaction.transaction_date >= thirty_days_ago
        ).scalar() or 0
        
        # Generate alternatives using AI
        alternatives = ai_advisor.suggest_spending_alternatives(
            category, float(category_spending)
        )
        
        return jsonify({
            'category': category,
            'currentSpending': float(category_spending),
            'alternatives': alternatives
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _generate_dashboard_insights(user_id, category_spending, monthly_income, monthly_spending):
    """Generate personalized dashboard insights"""
    insights = []
    
    # High spending categories
    if category_spending:
        top_category, top_amount, _ = max(category_spending, key=lambda x: x[1])
        if float(top_amount) > monthly_income * 0.3:  # More than 30% of income
            insights.append({
                'type': 'warning',
                'title': f'High {top_category} Spending',
                'description': f'You\'re spending {float(top_amount):.0f} SAR on {top_category} this month, which is {(float(top_amount)/monthly_income*100):.1f}% of your income.',
                'actionable': True
            })
    
    # Savings rate insight
    savings_rate = ((monthly_income - monthly_spending) / monthly_income * 100) if monthly_income > 0 else 0
    if savings_rate < 10:
        insights.append({
            'type': 'alert',
            'title': 'Low Savings Rate',
            'description': f'Your current savings rate is {savings_rate:.1f}%. Consider aiming for at least 20% of your income.',
            'actionable': True
        })
    elif savings_rate > 20:
        insights.append({
            'type': 'success',
            'title': 'Great Savings!',
            'description': f'Excellent! You\'re saving {savings_rate:.1f}% of your income. Consider investing your surplus.',
            'actionable': True
        })
    
    return insights

# Register all blueprints
def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(accounts_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(insights_bp)