# BKMS ↔ Coda Attendance Automation Bot

This project automates the process of syncing attendance from a **Coda-based roster** to the **BKMS (BAPS Kishore Management System)** website using a full-stack solution with **React**, **FastAPI**, **Selenium**, and **Coda API**.

## 🔍 Overview

- 🧠 **Purpose:** Eliminate manual entry by pulling attendance data from Coda, determining who attended a sabha, and auto-filling the BKMS form with the correct kishores marked.
- 🔄 **Flow:** 
  1. User selects sabha group, date (restricted to recent Sundays), and setup options.
  2. Bot fetches attendance from Coda for the selected sabha and date.
  3. Bot opens BKMS and automates the submission of attendance using Selenium.  
     > ⚠️ **CAPTCHA Notice:** After login, a CAPTCHA **must be solved manually within 30 seconds**, or the submission will fail.
  4. Telegram notification confirms successful submission.

## 🧱 Tech Stack

- **Frontend:** React
- **Backend:** FastAPI
- **Automation:** Selenium WebDriver (Chrome)
- **Data:** Coda API, Pandas
- **Messaging:** Telegram Bot

## 🚀 Running Locally

1. Clone the repo
2. Install frontend and backend dependencies
3. Run backend: `PYTHONPATH=. uvicorn backend.index:app --reload` (make sure you're not in backend folder)
4. Run frontend: `npm install && npm start`
5. Open: `http://localhost:3000`

Ensure you have the correct `.env` secrets set for **Backend**:
- `CODA_API_KEY`
- `TELEGRAM_TOKEN`
- BKMS login credentials (currently hardcoded for testing)

## ✅ Collaboration Guidelines

- **Branching:**  
  All branches **must start with `feature/`**, e.g.:
  - `feature/add-datepicker-validation`
  - `feature/improve-telegram-alert`

- **Testing Requirements:**  
  All changes must be tested **locally** and confirmed to work before submitting a PR.
  - Add a **screenshot or short video** showing your feature in action.

- **Date Selection for Testing:**  
  Use the **closest recent Sunday** you attended sabha for the most accurate and working test scenario. Data from that date should exist in Coda for your group.

- **Pull Request Template:**  
  Please include:
  - A brief summary of your changes
  - A screenshot/video of your feature working
  - Any edge cases or limitations to be aware of

## 📦 Deployment

To deploy:
- Push to `main` (or your production branch)
- The backend can be hosted on AWS, Render, or Railway
- The frontend can be deployed via Vercel, Netlify, or Amplify

---

👋 Feel free to contribute! Reach out with any questions before diving in.
