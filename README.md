# Cardio-Renal-Metabolic (CRM) Analysis Platform - Backend

This project is a high-performance backend for a CRM Analysis application, built with **FastAPI**, **Supabase (PostgreSQL)**, and **ML Models (scikit-learn)** for risk prediction.

## 🚀 One-Click Setup

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- A [Supabase](https://supabase.com/) account for database hosting.

### 1. Simple Run (Docker)
The easiest way to run the project on any machine is using Docker Compose:

1. **Clone the project** and navigate into the directory.
2. **Setup environment**: Rename `.env.example` to `.env` and fill in your Supabase credentials.
3. **Launch**:
   ```bash
   docker-compose up --build
   ```
   The API will be live at `http://localhost:8000`.

---

### 2. Local Python Run
If you prefer to run it directly on your system:

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Database Setup**: Execute `schema.sql` in your Supabase SQL Editor.
3. **Run Server**:
   ```bash
   python -m app.main
   ```

---

## 🛠️ Manual Testing Guide

Once the server is running, you can test all features using the **Swagger UI**.

### Step 1: Open Documentation
Go to: [http://localhost:8000/docs](http://localhost:8000/docs)

### Step 2: User Account Setup
1. Find the `POST /api/v1/auth/register` endpoint.
2. Click **Try it out** and submit a user JSON (email, password, etc.).
3. Go to `POST /api/v1/auth/login` and submit your credentials.
4. **Copy the `access_token`** from the response.

### Step 3: Authorize
1. Scroll to the top of the Swagger page and click the **Authorize** lock button.
2. Paste your `access_token` and click **Authorize**.

### Step 4: Submit Health Data
1. Find `POST /api/v1/health/data`.
2. Submit a JSON with your health metrics (Blood pressure, glucose, etc.).
3. **Copy the `id`** of the newly created health record.

### Step 5: Trigger ML Analysis
1. Find `POST /api/v1/analysis/trigger`.
2. Paste the `health_data_id` you just copied.
3. This will start the background risk assessment.

### Step 6: View Full Risk Profile
1. Find `GET /api/v1/analysis/profile`.
2. This returns your Cardiac, Renal, and Metabolic risk levels, plus clinician-tailored recommendations.

---

## ✨ Features
- **ML Integration**: Real-world scikit-learn models for predictive healthcare.
- **Portability**: Fully containerized environment with Docker.
- **Security**: JWT tokens, bcrypt hashing, and audit logs.
- **Documentation**: Professional Swagger and ReDoc interfaces.
