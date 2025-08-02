import requests
import os
from datetime import datetime, timedelta
import json

class TarabutService:
    def __init__(self):
        self.base_url = "https://api.sau.sandbox.tarabutgateway.io"
        self.token_url = "https://oauth.tarabutgateway.io/sandbox/token"
        self.client_id = os.getenv('TARABUT_CLIENT_ID')
        self.client_secret = os.getenv('TARABUT_CLIENT_SECRET')
        self.access_token = None
        
    def get_access_token(self):
        """Get access token from Tarabut API"""
        try:
            payload = {
                "clientId": self.client_id,
                "clientSecret": self.client_secret,
                "grantType": "client_credentials"
            }
            
            headers = {
                'Content-Type': 'application/json',
                'X-TG-CustomerUserId': 'namaai-system'
            }
            
            response = requests.post(self.token_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                return self.access_token
            else:
                print(f"Token error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting token: {e}")
            return None
    
    def get_headers(self):
        """Get headers with authorization token"""
        if not self.access_token:
            self.get_access_token()
            
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_providers(self):
        """Get list of available bank providers"""
        try:
            headers = self.get_headers()
            response = requests.get(f"{self.base_url}/v1/providers", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Providers error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting providers: {e}")
            return None
    
    def create_intent(self, user_data):
        """Create intent for bank connection"""
        try:
            headers = self.get_headers()
            
            payload = {
                "user": {
                    "customerUserId": user_data['customerUserId'],
                    "firstName": user_data['firstName'],
                    "lastName": user_data['lastName'],
                    "email": user_data['email']
                },
                "redirectUrl": user_data.get('redirectUrl', 'https://namaai.app/callback')
            }
            
            response = requests.post(
                f"{self.base_url}/accountInformation/v1/intent",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Intent creation error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error creating intent: {e}")
            return None
    
    def get_intent(self, intent_id):
        """Get intent details"""
        try:
            headers = self.get_headers()
            response = requests.get(f"{self.base_url}/accountInformation/v1/intent/{intent_id}", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Get intent error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting intent: {e}")
            return None
    
    def get_accounts(self):
        """Get user accounts"""
        try:
            headers = self.get_headers()
            response = requests.get(f"{self.base_url}/accountInformation/v2/accounts", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Accounts error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting accounts: {e}")
            return None
    
    def get_account_balance(self, account_id):
        """Get balance for specific account"""
        try:
            headers = self.get_headers()
            response = requests.get(
                f"{self.base_url}/accountInformation/v2/accounts/{account_id}/balances",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Balance error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting balance: {e}")
            return None
    
    def refresh_account_balance(self, account_id):
        """Refresh balance for specific account"""
        try:
            headers = self.get_headers()
            response = requests.get(
                f"{self.base_url}/accountInformation/v2/accounts/{account_id}/balances/refresh",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Refresh balance error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error refreshing balance: {e}")
            return None
    
    def get_account_transactions(self, account_id, from_date=None, to_date=None, page=1):
        """Get transactions for specific account"""
        try:
            headers = self.get_headers()
            
            # Default to last 3 months if no dates provided
            if not from_date:
                from_date = datetime.now() - timedelta(days=90)
            if not to_date:
                to_date = datetime.now()
            
            params = {
                'fromBookingDateTime': from_date.isoformat() + 'Z',
                'toBookingDateTime': to_date.isoformat() + 'Z',
                'page': page
            }
            
            response = requests.get(
                f"{self.base_url}/accountInformation/v2/accounts/{account_id}/transactions",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Transactions error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return None
    
    def get_account_raw_transactions(self, account_id, from_date=None, to_date=None):
        """Get raw transactions for specific account"""
        try:
            headers = self.get_headers()
            
            # Default to last 3 months if no dates provided
            if not from_date:
                from_date = datetime.now() - timedelta(days=90)
            if not to_date:
                to_date = datetime.now()
            
            params = {
                'fromBookingDateTime': from_date.isoformat() + 'Z',
                'toBookingDateTime': to_date.isoformat() + 'Z'
            }
            
            response = requests.get(
                f"{self.base_url}/accountInformation/v2/accounts/{account_id}/rawtransactions",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Raw transactions error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting raw transactions: {e}")
            return None
    
    def refresh_account_transactions(self, account_id):
        """Refresh transactions for specific account"""
        try:
            headers = self.get_headers()
            response = requests.get(
                f"{self.base_url}/accountInformation/v2/accounts/{account_id}/rawtransactions/refresh",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Refresh transactions error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error refreshing transactions: {e}")
            return None
    
    def categorize_transactions(self, transactions, account_id, provider_id):
        """Categorize transactions using Tarabut's categorization API"""
        try:
            headers = self.get_headers()
            
            # Convert transactions to the format expected by Tarabut API
            formatted_transactions = []
            for trans in transactions:
                formatted_trans = {
                    "transactionId": trans.get('transactionId', str(len(formatted_transactions) + 1)),
                    "transactionDescription": trans.get('description', ''),
                    "amount": {
                        "value": trans.get('amount', 0),
                        "currency": trans.get('currency', 'SAR')
                    },
                    "creditDebitIndicator": trans.get('creditDebitIndicator', 'Debit'),
                    "transactionDateTime": trans.get('transactionDateTime', datetime.now().isoformat() + 'Z')
                }
                formatted_transactions.append(formatted_trans)
            
            payload = {
                "transactions": formatted_transactions,
                "accountId": account_id,
                "accountProductType": "account",
                "providerId": provider_id
            }
            
            response = requests.post(
                f"{self.base_url}/ingest/v1/categorise-transactions",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Categorization error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error categorizing transactions: {e}")
            return None
    
    def get_salary_insights(self, months=3):
        """Get salary insights"""
        try:
            headers = self.get_headers()
            params = {'months': months}
            
            response = requests.get(
                f"{self.base_url}/insights/v1/salary",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Salary insights error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting salary insights: {e}")
            return None
    
    def get_income_insights(self, months=3, detailed=False):
        """Get income insights"""
        try:
            headers = self.get_headers()
            params = {'months': months}
            
            # For KSA, the endpoint is different from Bahrain
            endpoint = "/insights/v1/income/details" if detailed else "/insights/v1/income"
            
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Income insights error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting income insights: {e}")
            return None
    
    def verify_account(self, iban, identifier):
        """Verify account with IBAN and identifier (KSA specific)"""
        try:
            headers = self.get_headers()
            
            payload = {
                "iban": iban,
                "identifier": identifier
            }
            
            response = requests.post(
                f"{self.base_url}/accountverification/v1/verify",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Account verification error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error verifying account: {e}")
            return None
    
    def match_identifier(self, identifier):
        """Match IBAN identifier"""
        try:
            headers = self.get_headers()
            
            payload = {
                "identifier": identifier
            }
            
            response = requests.post(
                f"{self.base_url}/accountVerification/v1/matchIdentifier",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"IBAN match error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error matching identifier: {e}")
            return None
    
    def create_consent_dashboard(self, user_data):
        """Create consent dashboard"""
        try:
            headers = self.get_headers()
            
            payload = {
                "user": {
                    "customerUserId": user_data['customerUserId'],
                    "firstName": user_data['firstName'],
                    "lastName": user_data['lastName'],
                    "email": user_data['email']
                },
                "redirectUrl": user_data.get('redirectUrl', 'https://namaai.app/callback')
            }
            
            response = requests.post(
                f"{self.base_url}/consentInformation/v1/dashboard",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Consent dashboard error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error creating consent dashboard: {e}")
            return None
    
    def get_all_consents(self):
        """Get all consents"""
        try:
            headers = self.get_headers()
            response = requests.get(f"{self.base_url}/consentInformation/v1/consents", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Get consents error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting consents: {e}")
            return None
    
    def get_consent_details(self, consent_id):
        """Get consent details"""
        try:
            headers = self.get_headers()
            response = requests.get(f"{self.base_url}/consentInformation/v1/consents/{consent_id}", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Get consent details error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting consent details: {e}")
            return None
    
    def revoke_consent(self, consent_id):
        """Revoke consent"""
        try:
            headers = self.get_headers()
            response = requests.delete(f"{self.base_url}/consentInformation/v1/consents/{consent_id}", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Revoke consent error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error revoking consent: {e}")
            return None