# Nama'aAI | نَماء - Intelligent Financial Advisor

> **🏆 Hackathon-Ready POC** - AI-powered financial advisor leveraging real banking data through Tarabut API integration

An intelligent bilingual (Arabic/English) financial advisor that analyzes users' banking data, provides personalized budgeting insights, and offers Sharia-compliant investment recommendations tailored for Saudi Arabian users.

## 🚀 **Live Demo**

- **Frontend:** `http://localhost:3000` (Next.js)
- **Backend API:** `http://localhost:3000` (Flask)
- **Status:** ✅ **Fully Functional**

## 🎯 **Key Features**

### 💰 **Smart Financial Dashboard**
- Real-time balance display from connected Saudi banks
- Interactive spending categorization with AI-powered insights
- Visual spending breakdown with clickable categories
- Alternative suggestions for expensive spending habits

### 🤖 **Bilingual AI Advisor**
- Natural language chat in Arabic and English
- Personalized financial advice based on real transaction data
- Investment recommendations with Sharia-compliance focus
- Context-aware responses using user's actual financial profile

### 🏦 **Real Banking Integration**
- Secure connection to major Saudi banks (SNB, SABB, Riyad Bank, ANB)
- Live transaction categorization and analysis
- Account balance synchronization
- Transaction history with AI-enhanced categorization

### 📊 **Advanced Analytics**
- Spending pattern analysis and trends
- Budget recommendations based on actual spending
- Savings rate calculation and optimization tips
- Investment portfolio suggestions for Saudi market

## 🛠️ **Technology Stack**

### **Backend (Flask)**
```
Python 3.9+
├── Flask                    # Web framework
├── SQLAlchemy              # Database ORM
├── OpenAI GPT-4           # AI financial advisor
├── Tarabut Gateway        # Saudi banking API
├── Flask-CORS             # Cross-origin requests
└── SQLite                 # Database (dev) / PostgreSQL (prod)
```

### **Frontend (Next.js)**
```
Next.js 14 + TypeScript
├── React 18               # UI framework
├── Tailwind CSS          # Styling
├── Recharts              # Data visualization
├── Axios                 # HTTP client
├── Lucide React          # Icons
└── js-cookie             # Session management
```

### **APIs & Services**
- **🏦 Tarabut Gateway:** Banking data and account information
- **🤖 OpenAI GPT-4:** AI-powered financial analysis and advice
- **🔍 Tivaly:** Local alternatives and recommendations (planned)

## 📁 **Current Project Structure**

```
namaai/
├── backend/
│   ├── app.py                    # 🔥 Main Flask app (monolithic)
│   ├── models.py                 # 📊 Database models (detailed)
│   ├── tarabut_service.py        # 🏦 Banking API service
│   ├── ai_service.py             # 🤖 AI financial advisor
│   ├── routes.py                 # 🛣️ API route blueprints (alternative)
│   ├── test_tarabut.py           # 🧪 Comprehensive API tester
│   ├── requirements.txt          # 📦 Python dependencies
│   ├── .env.example              # ⚙️ Environment template
│   └── namaai.db                 # 💾 SQLite database
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx            # 🎨 Main app layout
│   │   ├── page.tsx              # 🏠 Home dashboard
│   │   ├── globals.css           # 🎨 Global styles (Tailwind)
│   │   ├── auth/
│   │   │   ├── register/page.tsx # 📝 User registration
│   │   │   └── connect-bank/page.tsx # 🏦 Bank connection
│   │   ├── chat/page.tsx         # 💬 AI chat interface
│   │   └── profile/page.tsx      # 👤 User profile
│   ├── package.json              # 📦 Dependencies
│   ├── next.config.js            # ⚙️ Next.js config
│   ├── tailwind.config.js        # 🎨 Tailwind config
│   ├── postcss.config.js         # 🎨 PostCSS config
│   └── .env.local                # ⚙️ Environment variables
│
└── README.md                     # 📖 This file
```

## ⚡ **Quick Start**

### **Prerequisites**
- Python 3.9+
- Node.js 18+
- Tarabut API credentials (from Tarabut Portal)
- OpenAI API key

### **1. Backend Setup**

```bash
# Navigate to backend
cd backend/

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys:
# TARABUT_CLIENT_ID=your_client_id
# TARABUT_CLIENT_SECRET=your_client_secret
# OPENAI_API_KEY=your_openai_key

# Test Tarabut API connection
python test_tarabut.py

# Run the Flask server
python app.py
```

**Expected output:**
```
🏦 Nama'aAI - Complete Tarabut API Tester
✅ All tests passed! Your Tarabut API is working correctly.

* Running on all addresses (0.0.0.0)
* Running on http://192.168.5.38:3000
```

### **2. Frontend Setup**

```bash
# Navigate to frontend
cd frontend/

# Install dependencies
npm install

# Set up environment variables
# Create .env.local with:
echo "NEXT_PUBLIC_API_URL=http://192.168.5.38:3000" > .env.local

# Run the development server
npm run dev
```

**Expected output:**
```
▲ Next.js 14.0.4
- Local: http://localhost:3000
✓ Ready in 569ms
```

### **3. Test the Application**

1. **Open browser:** `http://localhost:3000`
2. **Register new user:** Fill out the registration form
3. **Connect bank:** Select a Saudi bank from the list
4. **View dashboard:** See your financial overview
5. **Chat with AI:** Ask questions about your finances

## 🔧 **Configuration**

### **Backend Environment Variables**

Create `backend/.env`:
```bash
# Required - Tarabut API
TARABUT_CLIENT_ID=your_tarabut_client_id
TARABUT_CLIENT_SECRET=your_tarabut_client_secret

# Required - OpenAI
OPENAI_API_KEY=your_openai_api_key

# Optional - Flask settings
FLASK_ENV=development
SECRET_KEY=nama-ai-secret-key-2024

# Optional - Database
DATABASE_URL=sqlite:///namaai.db
```

### **Frontend Environment Variables**

Create `frontend/.env.local`:
```bash
# Required - API endpoint
NEXT_PUBLIC_API_URL=http://192.168.5.38:3000

# Optional - Environment
NEXT_PUBLIC_ENVIRONMENT=development
```

## 🧪 **Testing**

### **Test Tarabut API Integration**
```bash
cd backend/
python test_tarabut.py
```

### **Test Backend Endpoints**
```bash
# Test environment setup
curl http://192.168.5.38:3000/api/debug/env

# Test user registration
curl -X POST http://192.168.5.38:3000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "customerUserId": "test_123",
    "firstName": "Ahmed",
    "lastName": "Al-Rashid",
    "email": "ahmed@test.com"
  }'

# Test bank providers
curl http://192.168.5.38:3000/api/accounts/providers
```

### **Test Frontend**
1. Open `http://localhost:3000` in browser
2. Check browser console (F12) for any errors
3. Test registration flow
4. Verify API calls in Network tab

## 📊 **API Endpoints**

### **Authentication**
- `POST /api/register` - Register new user
- `GET /api/debug/env` - Environment status

### **Banking**
- `GET /api/accounts/providers` - Available Saudi banks
- `POST /api/accounts/create-intent` - Bank connection
- `GET /api/accounts/<user_id>` - User accounts
- `GET /api/transactions/<account_id>` - Account transactions

### **AI Services**
- `POST /api/chat/send` - Chat with AI advisor
- `POST /api/investment-advice` - Investment recommendations
- `GET /api/alternatives/<category>` - Spending alternatives

### **Analytics**
- `GET /api/insights/dashboard/<user_id>` - Dashboard data

## 🎨 **Demo Features**

### **Real Saudi Banks Supported**
- Saudi National Bank (SNB)
- Saudi British Bank (SABB)
- Riyad Bank
- Arab National Bank (ANB)
- Bank AlJazira
- Alinma Bank
- Banque Saudi Fransi (BSF)

### **AI-Powered Insights**
- Transaction categorization (Food, Transportation, Shopping, etc.)
- Spending pattern analysis
- Budget recommendations
- Investment advice with Sharia compliance
- Alternative suggestions for expensive habits

### **Bilingual Support**
- Arabic and English UI
- Seamless language switching
- Cultural context awareness in AI responses

## 🚀 **Deployment**

### **Backend (Heroku/Railway)**
```bash
# Build for production
pip freeze > requirements.txt

# Deploy to Heroku
heroku create namaai-backend
git push heroku main
```

### **Frontend (Vercel/Netlify)**
```bash
# Build for production
npm run build

# Deploy to Vercel
vercel deploy --prod
```

## 🔒 **Security & Privacy**

- **🔐 Bank-grade Security:** All API communications encrypted
- **🛡️ Data Protection:** User data never shared with third parties
- **🔄 Secure Tokens:** Temporary access tokens with automatic expiration
- **📋 Compliance:** Follows Saudi data protection regulations
- **🚫 No Storage:** Banking credentials never stored locally

## 🎯 **Hackathon Highlights**

### **✅ Completed Features**
- ✅ Real banking API integration (Tarabut)
- ✅ AI-powered financial analysis (OpenAI GPT-4)
- ✅ Bilingual chat interface (Arabic/English)
- ✅ Interactive dashboard with visualizations
- ✅ Transaction categorization and insights
- ✅ Investment recommendations
- ✅ User registration and onboarding
- ✅ Mobile-responsive design

### **🚀 Demo-Ready**
- Real API data (not mock data)
- Functional user registration
- Live bank connection simulation
- Working AI chat with financial context
- Interactive spending analysis

### **🏆 Innovation Points**
- First bilingual AI financial advisor for Saudi market
- Real-time banking integration with cultural awareness
- Sharia-compliant investment recommendations
- AI-powered spending alternatives discovery

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📞 **Support & Contact**

- **Email:** support@namaai.app
- **Demo:** [Live Demo Link]
- **Documentation:** [API Docs Link]
- **Issues:** [GitHub Issues](https://github.com/your-repo/namaai/issues)

## 🙏 **Acknowledgments**

- **Tarabut Gateway** for providing Saudi banking API access
- **OpenAI** for GPT-4 AI capabilities
- **Saudi Vision 2030** for inspiring fintech innovation
- **Hackathon Organizers** for the opportunity to innovate

---

**Nama'aAI | نَماء** - *Empowering Financial Growth with AI Intelligence*

Built with ❤️ for the Saudi fintech ecosystem
