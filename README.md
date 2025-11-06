# 🏦 MODULO_BANK

> **Empowering Secure Banking Through Innovation and Trust**

[![Last Commit](https://img.shields.io/github/last-commit/CodeByPerumal/Modulo_Bank)](https://github.com/CodeByPerumal/Modulo_Bank/commits/main)
![Python](https://img.shields.io/badge/python-81.1%25-blue)
![Languages](https://img.shields.io/github/languages/count/CodeByPerumal/Modulo_Bank)
![Django](https://img.shields.io/badge/Django-REST%20Framework-0C4B33?logo=django)
![SQLite](https://img.shields.io/badge/Database-SQLite3-lightgrey)
![JWT](https://img.shields.io/badge/Auth-JWT%20Token-orange)
![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7)
![License](https://img.shields.io/badge/license-MIT-green)

---

### 🧰 Built With
![Gunicorn](https://img.shields.io/badge/-Gunicorn-499848?logo=gunicorn&logoColor=white)
![Django](https://img.shields.io/badge/-Django-092E20?logo=django&logoColor=white)
![Pytest](https://img.shields.io/badge/-Pytest-0A9EDC?logo=pytest&logoColor=white)
![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white)
![YAML](https://img.shields.io/badge/-YAML-CB171E?logo=yaml&logoColor=white)

---

## 📚 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Setup](#environment-setup)
  - [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Deployment](#deployment)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)
- [Live Demo & Repository](#live-demo--repository)

---

## 🧾 Overview
**Modulo Bank** is a secure and modular banking backend built using **Django REST Framework**.  
It provides APIs for **user management, account creation, fund transfers, loan processing, audit logging**, and **fraud detection** — designed for scalability and reliability.

> 🖥️ Live Demo: [https://modulo-bank.onrender.com/](https://modulo-bank.onrender.com/)  
> 📦 Source Code: [https://github.com/CodeByPerumal/Modulo_Bank.git](https://github.com/CodeByPerumal/Modulo_Bank.git)

---

## 🚀 Features

- 🔐 **JWT Authentication** with Role-based Access Control (Customer, Admin, Auditor)
- 💰 **Account Management** – Create and manage multiple account types (Savings, Current, FD)
- 💸 **Transactions** – Deposit, Withdraw, and Transfer between accounts
- 🧮 **Loan Processing** – EMI calculation, approval workflow, and status tracking
- 🧠 **Fraud Detection** – Detect suspicious transactions (Isolation Forest-based)
- 🧾 **Audit Logs** – Track every action with timestamp, user, and IP address
- 📊 **Reports & Dashboard** – Transaction summaries, trends, and insights

---

## 🧑‍💻 Tech Stack

| Layer | Technologies Used |
|-------|--------------------|
| Backend | Python, Django REST Framework |
| Database | SQLite3 (Local) |
| Authentication | JWT (SimpleJWT) |
| Deployment | Render |
| Testing | Pytest, Django Test Framework |
| Utilities | Django Environ, Faker |

---

## 🧠 System Architecture

