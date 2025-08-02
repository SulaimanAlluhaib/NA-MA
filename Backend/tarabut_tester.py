#!/usr/bin/env python3
"""
Tarabut API Test Script
Tests ALL endpoints used in Nama'aAI app
"""

import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Tarabut API Configuration
#!/usr/bin/env python3
"""
Tarabut API Test Script
Tests ALL endpoints used in Nama'aAI app
"""

import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

TARABUT_TOKEN_URL = "https://oauth.tarabutgateway.io/sandbox/token"
TARABUT_BASE_URL = "https://api.sau.sandbox.tarabutgateway.io"
TARABUT_CUSTOMER_USER_ID = "namaai-test-user"
TARABUT_REDIRECT_URL = os.getenv("TARABUT_REDIRECT_URL") or "http://localhost:3000/callback"

class TarabutTester:
    def __init__(self):
        self.client_id = os.getenv('TARABUT_CLIENT_ID')
        self.client_secret = os.getenv('TARABUT_CLIENT_SECRET')
        self.token = None
        self.intent_id = None
        self.test_account_id = None
        self.test_results = []

    def run_all_tests(self):
        print("\n🏦 Nama'aAI - Complete Tarabut API Tester")
        print("=" * 60)

        if not self.check_credentials():
            return False

        tests = [
            ("1️⃣ Get Access Token", self.test_get_token),
            ("2️⃣ Get Providers", self.test_get_providers),
            ("3️⃣ Create Intent", self.test_create_intent),
            ("4️⃣ Get Intent Details", self.test_get_intent),
            ("5️⃣ Get Accounts", self.test_get_accounts),
            ("6️⃣ Get Account Balance", self.test_get_account_balance),
            ("7️⃣ Get Account Transactions", self.test_get_transactions),
            ("8️⃣ Categorize Transactions", self.test_categorize_transactions),
            ("9️⃣ Get Salary Insights", self.test_salary_insights),
            ("🔟 Get Income Insights", self.test_income_insights),
            ("1️⃣1️⃣ Account Verification", self.test_account_verification),
            ("1️⃣2️⃣ IBAN Match", self.test_iban_match),
        ]

        for name, func in tests:
            print(f"\n{name}")
            print("-" * 40)
            success = func()
            self.test_results.append((name, success))
            if name == "1️⃣ Get Access Token" and not success:
                print("❌ Cannot continue without access token")
                break

        self.show_summary()
        return True

    def check_credentials(self):
        print("📋 Checking Credentials...")
        print(f"   Client ID: {'✅ Set' if self.client_id else '❌ Missing'}")
        print(f"   Client Secret: {'✅ Set' if self.client_secret else '❌ Missing'}")
        return bool(self.client_id and self.client_secret)

    def get_headers(self):
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    def test_get_token(self):
        if self.token:
            return self.token
        payload = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret,
            "grantType": "client_credentials"
        }
        headers = {
            'Content-Type': 'application/json',
            'X-TG-CustomerUserId': TARABUT_CUSTOMER_USER_ID
        }
        response = requests.post(TARABUT_TOKEN_URL, json=payload, headers=headers)
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            return self.token
        else:
            raise Exception(f"Failed to get token: {response.text}")

    def test_get_providers(self):
        try:
            headers = self.get_headers()
            response = requests.get(f"{TARABUT_BASE_URL}/v1/providers", headers=headers)
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 200:
                providers = response.json().get('providers', [])
                print(f"   ✅ Found {len(providers)} providers")
                return True
            print(f"   ❌ Error: {response.text}")
            return False
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return False
    def test_create_intent(self):
        """Create Intent and print connect URL"""
        self.test_get_token()  # Ensure token is available
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        payload = {
            "user": {
                "customerUserId": TARABUT_CUSTOMER_USER_ID,
                "email": "john@example.com",
                "firstName": "John",
                "lastName": "Doe"
            },
            "consent": {
                "providerId": "BLUE"
            },
            "redirectUrl": TARABUT_REDIRECT_URL
        }
        url = f"{TARABUT_BASE_URL}/accountInformation/v1/intent"
        response = requests.post(url, headers=headers, json=payload)
        print(f"\n➡️ POST {url}")
        print(f"   📊 Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            self.intent_id = data.get("intentId")
            connect_url = data.get("connectUrl")
            print(f"   ✅ Intent created: {self.intent_id}")
            print(f"   🔗 Connect user at: {connect_url}")
        else:
            print(f"   ❌ Error: {response.text}")

    def test_get_intent(self):
        if not self.intent_id:
            print("   ⏭️ Skipped - No intent ID")
            return False
        try:
            headers = self.get_headers()
            response = requests.get(
                f"{TARABUT_BASE_URL}/accountInformation/v1/intent/{self.intent_id}",
                headers=headers
            )
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Intent status: {response.json().get('status', 'Unknown')}")
                return True
            print(f"   ❌ Error: {response.text}")
            return False
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return False

    def test_get_accounts(self):
        try:
            headers = self.get_headers()
            response = requests.get(f"{TARABUT_BASE_URL}/accountInformation/v2/accounts", headers=headers)
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 200:
                accounts = response.json().get('accounts', [])
                print(f"   ✅ Found {len(accounts)} accounts")
                if accounts:
                    self.test_account_id = accounts[0].get('accountId')
                return True
            print(f"   ❌ Error: {response.text}")
            return False
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return False

    def test_get_account_balance(self):
        if not self.test_account_id:
            print("   ⏭️ Skipped - No account ID")
            return False
        try:
            headers = self.get_headers()
            response = requests.get(
                f"{TARABUT_BASE_URL}/accountInformation/v2/accounts/{self.test_account_id}/balances",
                headers=headers
            )
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Balance data retrieved")
                return True
            print(f"   ❌ Error: {response.text}")
            return False
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return False

    def test_get_transactions(self):
        if not self.test_account_id:
            print("   ⏭️ Skipped - No account ID")
            return False
        try:
            headers = self.get_headers()
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            params = {
                'fromBookingDateTime': start_date.isoformat() + 'Z',
                'toBookingDateTime': end_date.isoformat() + 'Z'
            }
            response = requests.get(
                f"{TARABUT_BASE_URL}/accountInformation/v2/accounts/{self.test_account_id}/transactions",
                headers=headers,
                params=params
            )
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Transaction data retrieved")
                return True
            print(f"   ❌ Error: {response.text}")
            return False
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return False

    def test_categorize_transactions(self):
        try:
            headers = self.get_headers()
            payload = {
                "transactions": [
                    {
                        "transactionId": "sample_txn_001",
                        "transactionDescription": "Sample Purchase",
                        "amount": {"value": 100, "currency": "SAR"},
                        "creditDebitIndicator": "Debit",
                        "transactionDateTime": "2025-01-01T00:00:00Z"
                    }
                ],
                "accountId": self.test_account_id or "DUMMY_ACCOUNT",
                "accountProductType": "account",
                "providerId": "SNB"
            }
            response = requests.post(
                f"{TARABUT_BASE_URL}/ingest/v1/categorise-transactions",
                headers=headers,
                json=payload
            )
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Categorization successful")
                return True
            print(f"   ❌ Error: {response.text}")
            return False
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return False

    def test_salary_insights(self):
        try:
            headers = self.get_headers()
            params = {"months": 3}
            response = requests.get(f"{TARABUT_BASE_URL}/insights/v1/salary", headers=headers, params=params)
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Salary insights retrieved")
                return True
            print(f"   ❌ Error: {response.text}")
            return False
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return False

    def test_income_insights(self):
        try:
            headers = self.get_headers()
            params = {"months": 3}
            response = requests.get(f"{TARABUT_BASE_URL}/insights/v1/income", headers=headers, params=params)
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Income insights retrieved")
                return True
            print(f"   ❌ Error: {response.text}")
            return False
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return False

    def test_account_verification(self):
        try:
            headers = self.get_headers()
            payload = {
                "iban": "SA6530400108071059170014",
                "identifier": "1098184854"
            }
            response = requests.post(f"{TARABUT_BASE_URL}/accountverification/v1/verify", headers=headers, json=payload)
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Account verification successful")
                return True
            print(f"   ❌ Error: {response.text}")
            return False
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return False

    def test_iban_match(self):
        try:
            headers = self.get_headers()
            payload = {"identifier": "SA6530400108071059170014"}
            response = requests.post(f"{TARABUT_BASE_URL}/accountVerification/v1/matchIdentifier", headers=headers, json=payload)
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ IBAN match successful")
                return True
            print(f"   ❌ Error: {response.text}")
            return False
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return False

    def show_summary(self):
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        passed = sum(1 for _, success in self.test_results if success)
        total = len(self.test_results)
        for test_name, success in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
        print("-" * 60)
        print(f"📈 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        if passed == total:
            print("🎉 All tests passed! Your Tarabut integration is working perfectly!")
        elif passed >= total * 0.5:
            print("⚠️ Some tests failed. Partial functionality verified.")
        else:
            print("❌ Many tests failed. Investigate your configuration.")

if __name__ == "__main__":
    tester = TarabutTester()
    tester.run_all_tests()
