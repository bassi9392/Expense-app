# 💰 Expense Tracker

A full-stack Personal Expense Tracker application built with the MERN stack (Node.js, Express, React, and SQLite/MongoDB). This application allows users to manage their daily finances with a focus on security, dynamic data retrieval, and insightful analytics.

## 🚀 Features

### 🔐 Authentication
* **Secure Onboarding:** User registration and login functionality.
* **Session Management:** Persistent login using JWT (JSON Web Tokens) and LocalStorage.
* **Protected Routes:** Unauthorized users are redirected to the login page.

### 📝 Transaction Management
* **Full CRUD:** Add, Edit, View, and Delete transactions.
* **Detailed Records:** Track title, amount, category, date, and optional notes.
* **Dynamic Feedback:** Instant UI updates upon data modification.

### 🔍 Transaction Explorer
* **Dynamic Search:** Real-time text search for transaction titles.
* **Scalable Browsing:** Designed to handle large histories with smooth navigation.
* **Category Filtering:** Quickly isolate spending by groups (e.g., Food, Rent, Transport).
* **Empty State Handling:** Graceful UI displays when no results match search criteria.

### 📊 Dashboard
* **Spending Summary:** Quick view of the total amount spent.
* **Visual Analytics:** Interactive Category-based breakdown using Recharts.
* **Recent Activity:** A quick preview of the latest financial entries.

---

## 🛠️ Tech Stack

**Frontend:**
* React.js (Functional Components, Hooks)
* React Router DOM (Navigation & Protected Routes)
* Context API (Global State Management)
* Recharts (Data Visualization)
* Axios (API Communication)

**Backend:**
* Node.js & Express
* JWT (Authentication)
* Sequelize (ORM) / SQLite (Database)
* Bcryptjs (Password Hashing)

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone 
