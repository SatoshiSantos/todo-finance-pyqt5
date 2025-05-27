# Family To-Do & Financial Snapshot

#### Video Demo: <Coming Soon>
#### Author: Rafael Santos  
#### GitHub: [SatoshiSantos](https://github.com/SatoshiSantos)  
#### edX Username: SatoshiSantos  
#### Location: Florida, USA  
#### Date Recorded: May 26, 2025

---

## 📌 Description

This desktop application, developed in Python with PyQt5, provides a secure and user-friendly interface for families or individuals to manage daily to-dos and financial information. It includes task tracking, financial entry logging, credit card monitoring, and CSV export functionality for record-keeping and analysis.

The application was created as the final project for CS50's Introduction to Programming with Python (CS50P), fulfilling all course requirements including top-level functions, unit testing, GUI design, and data persistence.

---

## 🚀 Features

### ✅ To-Do Management
- Add tasks with due date, status, notes, and categories
- Filter by status, due date, task name, or category
- Visual color indicators based on task status
- All data saved persistently to `data.json`

### 💵 Financial Snapshot
- Log income, expenses, or accounts
- Each entry has a label and amount
- Summarized by account and by owner

### 💳 Credit Card Tracker
- Input cardholder, card name, limit, balance, available credit, and due date
- Automatically calculates:
  - Usage % per card
  - Total credit usage across all cards
  - Total and per-user debt
- Input validation ensures clean data entry

---

## 🧪 Testing

The app includes three top-level utility functions:
- `format_currency(amount)`
- `calculate_credit_usage(balance, limit)`
- `validate_float(value)`

These are covered with unit tests using `pytest`. Tests are found in `test_project.py`.

Run tests with:
```bash
pytest test_project.py

Install requirements with:
```bash
pip install -r requirements.txt
