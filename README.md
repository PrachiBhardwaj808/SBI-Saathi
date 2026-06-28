# SBI Saathi

**SBI Saathi** is an AI-powered government benefit discovery and eligibility assistant. Designed with a mobile-first approach, it helps users (especially rural and semi-urban banking customers) discover government welfare schemes they qualify for, apply for them, track applications, and receive personalized SBI product recommendations.

## 🌟 Features

*   **AI Eligibility Engine**: Rule-based mock AI engine that evaluates user profiles against 15+ government schemes (e.g., PM Kisan, PMAY, Ayushman Bharat) and provides natural language reasoning for eligibility.
*   **Bilingual Voice AI Chatbot**: Interactive chat interface supporting English and Hindi. Includes browser-native Speech-to-Text (Voice input) and Text-to-Speech integration.
*   **Application Tracker**: Dynamic tracking system that simulates application statuses (Applied → In Progress → Approved/Rejected) with a visual timeline.
*   **SBI Product Cross-Sell**: Smart recommendations for SBI products (like Kisan Credit Card or Home Loans) based on the user's profile and scheme applications.
*   **Master Dashboard**: A comprehensive overview featuring hero stats, recent activity, top recommended schemes, and quick actions.
*   **PWA Ready**: Progressive Web App manifest and Framer Motion transitions for a premium, native-app feel.
*   **Mobile-First Design**: Fully responsive interface tailored for 375px mobile screens, styled with SBI's trustworthy corporate brand colors.

## 🛠️ Tech Stack

### Frontend
*   **Framework**: Next.js 14 (App Router)
*   **Language**: TypeScript
*   **Styling**: Tailwind CSS v3, `shadcn/ui` components
*   **State Management**: Zustand
*   **Animations**: Framer Motion
*   **PWA**: `next-pwa`

### Backend
*   **Framework**: FastAPI (Python)
*   **Database**: SQLite via SQLAlchemy & Alembic
*   **Validation**: Pydantic models
*   **Security**: JWT-based stateless authentication

## 🚀 Getting Started

### Prerequisites
*   Node.js (v18+)
*   Python (3.10+)

### 1. Backend Setup

Navigate to the backend directory and set up the Python environment:

```bash
cd backend
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
uvicorn app.main:app --reload
```
The backend will run on `http://127.0.0.1:8000`. On the first startup, it will automatically initialize the database and seed it with 15 government schemes.

### 2. Frontend Setup

Open a new terminal, navigate to the frontend directory, and install dependencies:

```bash
cd frontend
npm install

# Run the frontend development server
npm run dev
```
The frontend will run on `http://localhost:3000`.

## 🧪 Testing the Prototype

1.  Open `http://localhost:3000` in your browser.
2.  Log in using any 10-digit mobile number (e.g., `9876543210`).
3.  Check the console/terminal for the mock OTP (or just use `123456`).
4.  Complete your profile (ensure you try different occupations like "Farmer" to see specific schemes like PM Kisan).
5.  Navigate to the **Dashboard** to view your eligible schemes.
6.  Click **Apply** on a scheme, then go to the **Applications** tab to watch the simulated status timeline advance automatically.
7.  Try the **AI Chat** feature by clicking the microphone icon to use voice input.

## 📜 License

This project is licensed under the MIT License.
