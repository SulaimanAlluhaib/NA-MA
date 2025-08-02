from openai import OpenAI
import json
import re
from datetime import datetime, timedelta
import os

class AIFinancialAdvisor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def categorize_transaction(self, description, amount, currency='SAR'):
        """Categorize a single transaction using AI"""
        try:
            prompt = f"""
            Categorize this Saudi Arabian transaction and extract merchant information:
            
            Description: {description}
            Amount: {amount} {currency}
            
            Categories to choose from:
            - Food & Dining (restaurants, cafes, food delivery)
            - Groceries & Supermarkets (grocery stores, markets)
            - Shopping & Retail (clothing, electronics, general shopping)
            - Transportation (gas, uber, parking, public transport)
            - Entertainment (movies, games, streaming services)
            - Bills & Utilities (electricity, water, internet, phone)
            - Healthcare & Medical (hospitals, clinics, pharmacy)
            - Education (schools, courses, books)
            - Travel & Hotels (flights, hotels, travel agencies)
            - Banking & Finance (bank fees, transfers, ATM)
            - Government & Services (government fees, official services)
            - Other
            
            Also extract:
            - Merchant name (if identifiable)
            - Transaction type (purchase, withdrawal, transfer, etc.)
            
            Respond in JSON format:
            {{
                "category": "category_name",
                "merchant": "merchant_name",
                "transaction_type": "type",
                "confidence": 0.95
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Categorization error: {e}")
            return {
                "category": "Other",
                "merchant": "Unknown",
                "transaction_type": "unknown",
                "confidence": 0.0
            }
    
    def generate_financial_advice(self, user_profile, message_history, current_message):
        """Generate personalized financial advice"""
        try:
            # Prepare user context
            context = f"""
            User Financial Profile:
            - Total Balance: {user_profile.get('total_balance', 0)} SAR
            - Monthly Income: {user_profile.get('monthly_income', 0)} SAR
            - Monthly Spending: {user_profile.get('monthly_spending', 0)} SAR
            - Top Spending Categories: {json.dumps(user_profile.get('top_categories', []), indent=2)}
            - Recent Transactions: {json.dumps(user_profile.get('recent_transactions', []), indent=2)}
            - Number of Accounts: {user_profile.get('accounts_count', 0)}
            - Savings Rate: {user_profile.get('savings_rate', 0)}%
            """
            
            system_prompt = f"""
            You are Nama'aAI (نماء), an intelligent bilingual (Arabic/English) financial advisor specializing in Saudi Arabian personal finance.
            
            Your capabilities:
            - Provide personalized budgeting advice
            - Suggest investment opportunities (Saudi market focus)
            - Analyze spending patterns
            - Recommend savings strategies
            - Offer Islamic finance-compliant solutions
            - Support both Arabic and English languages
            
            User Context:
            {context}
            
            Guidelines:
            - Be conversational and supportive
            - Provide actionable advice
            - Consider Saudi cultural context
            - Include Islamic finance principles when relevant
            - Be concise but comprehensive
            - Use emojis appropriately
            - Respond in the language the user prefers
            """
            
            # Build conversation history
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add recent message history (last 5 exchanges)
            for msg in message_history[-10:]:
                messages.append(msg)
            
            # Add current message
            messages.append({"role": "user", "content": current_message})
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"AI advice error: {e}")
            return "عذراً، حدث خطأ في النظام. حاول مرة أخرى.\nSorry, there was a system error. Please try again."
    
    def generate_investment_advice(self, user_profile, investment_amount, risk_tolerance):
        """Generate personalized investment advice"""
        try:
            prompt = f"""
            Create comprehensive investment advice for a Saudi investor:
            
            User Profile:
            - Total Balance: {user_profile.get('total_balance', 0)} SAR
            - Monthly Income: {user_profile.get('monthly_income', 0)} SAR
            - Monthly Spending: {user_profile.get('monthly_spending', 0)} SAR
            - Investment Amount: {investment_amount} SAR
            - Risk Tolerance: {risk_tolerance}
            - Age Group: {user_profile.get('age_group', 'adult')}
            
            Provide detailed advice including:
            1. Asset Allocation Recommendations (percentages)
            2. Specific Investment Options (Saudi-focused):
               - Tadawul stocks (mention specific sectors)
               - Islamic funds and sukuk
               - Real estate investment trusts (REITs)
               - International diversification options
            3. Risk Assessment and Mitigation
            4. Timeline Recommendations
            5. Expected Returns (realistic estimates)
            6. Action Steps
            
            Consider:
            - Islamic finance compliance (Sharia-compliant investments)
            - Saudi Vision 2030 opportunities
            - Local market conditions
            - Diversification principles
            
            Format as structured advice with clear sections.
            Use both Arabic and English for key terms.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Investment advice error: {e}")
            return "Unable to generate investment advice. Please try again."
    
    def suggest_spending_alternatives(self, category, spending_amount, location="Saudi Arabia"):
        """Suggest cheaper alternatives for spending categories"""
        try:
            prompt = f"""
            Suggest 5 cost-effective alternatives for the spending category "{category}" in {location}:
            
            Current monthly spending: {spending_amount} SAR
            
            For each alternative, provide:
            - Name/Service
            - Description (Arabic and English)
            - Estimated monthly savings (SAR and percentage)
            - Type (app, service, store, strategy)
            - Ease of implementation (1-5 scale)
            - Availability in Saudi Arabia
            
            Focus on:
            - Local Saudi options
            - Digital solutions and apps
            - Practical and realistic alternatives
            - Cultural appropriateness
            
            Format as JSON array:
            [
                {{
                    "name": "Alternative Name",
                    "description_en": "English description",
                    "description_ar": "الوصف بالعربية",
                    "estimated_savings_sar": 100,
                    "estimated_savings_percent": 15,
                    "type": "app/service/store/strategy",
                    "ease_score": 4,
                    "availability": "Available nationwide"
                }}
            ]
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=600
            )
            
            alternatives = json.loads(response.choices[0].message.content)
            return alternatives
            
        except Exception as e:
            print(f"Alternatives suggestion error: {e}")
            return []
    
    def analyze_spending_patterns(self, transactions, timeframe_days=30):
        """Analyze spending patterns and provide insights"""
        try:
            # Group transactions by category and merchant
            category_analysis = {}
            merchant_analysis = {}
            daily_spending = {}
            
            for trans in transactions:
                category = trans.get('category', 'Other')
                merchant = trans.get('merchant', 'Unknown')
                amount = abs(float(trans.get('amount', 0)))
                date = trans.get('transaction_date', '')
                
                # Category analysis
                if category not in category_analysis:
                    category_analysis[category] = {'total': 0, 'count': 0, 'transactions': []}
                category_analysis[category]['total'] += amount
                category_analysis[category]['count'] += 1
                category_analysis[category]['transactions'].append(trans)
                
                # Merchant analysis
                if merchant not in merchant_analysis:
                    merchant_analysis[merchant] = {'total': 0, 'count': 0}
                merchant_analysis[merchant]['total'] += amount
                merchant_analysis[merchant]['count'] += 1
                
                # Daily spending
                day = date.split('T')[0] if date else 'unknown'
                if day not in daily_spending:
                    daily_spending[day] = 0
                daily_spending[day] += amount
            
            # Generate insights using AI
            analysis_data = {
                'categories': category_analysis,
                'merchants': merchant_analysis,
                'daily_spending': daily_spending,
                'total_transactions': len(transactions),
                'timeframe_days': timeframe_days
            }
            
            prompt = f"""
            Analyze this spending data and provide actionable insights:
            
            {json.dumps(analysis_data, indent=2)}
            
            Provide insights in Arabic and English covering:
            1. Spending patterns and trends
            2. Areas for potential savings
            3. Unusual or concerning patterns
            4. Recommendations for better financial management
            5. Budget allocation suggestions
            
            Be specific and actionable. Format as structured text with clear sections.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=700
            )
            
            return {
                'insights': response.choices[0].message.content,
                'raw_analysis': analysis_data
            }
            
        except Exception as e:
            print(f"Spending analysis error: {e}")
            return {
                'insights': 'Unable to analyze spending patterns.',
                'raw_analysis': {}
            }
    
    def generate_budget_plan(self, income, current_spending, financial_goals):
        """Generate a personalized budget plan"""
        try:
            prompt = f"""
            Create a comprehensive monthly budget plan for a Saudi resident:
            
            Financial Information:
            - Monthly Income: {income} SAR
            - Current Monthly Spending: {current_spending} SAR
            - Financial Goals: {json.dumps(financial_goals, indent=2)}
            
            Create a budget following these principles:
            - 50/30/20 rule adaptation for Saudi context
            - Islamic finance principles
            - Emergency fund priority
            - Practical and achievable targets
            
            Provide:
            1. Detailed budget breakdown by category (SAR and percentages)
            2. Savings targets and timeline
            3. Emergency fund recommendations
            4. Investment allocation suggestions
            5. Monthly monitoring plan
            6. Tips for staying on budget
            
            Format as structured plan with clear action items.
            Include both Arabic and English for key terms.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Budget planning error: {e}")
            return "Unable to generate budget plan. Please try again."