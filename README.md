# 🧠 Social Keep - Survey Management System

**Social Keep** is a full-stack survey management web application built with **Flask**, **MySQL**, and **HTML/CSS/JavaScript**. It supports two roles: **Admin** and **Participant**. Admins manage users and surveys, while participants complete surveys and track their rewards.

---

## 🚀 Key Features

### 🔑 Authentication & Access Control
- **Admin-Only User Creation**: Participants are added only by Admins.
- **Email Password Delivery**: Participants receive a randomly generated password via email.
- **Password Reset**: Participants can securely change their password anytime after logging in.

### 👨‍💼 Admin Dashboard
- **Create Surveys**: Daily or Biweekly, with custom questions (radio, checkbox, descriptive).
- **Survey Scheduling**: Set future start times, automatically transition from upcoming to current.
- **Track Activation**: Monitor if participants have activated their accounts.
- **Survey Completion Report**: See who completed which surveys.
- **Pending Surveys**: Track incomplete surveys per user.
- **Error Detection**: Alerts if surveys expire with no responses.
- **Reward System**: Optionally assign token rewards per survey.

### 👤 Participant Dashboard
- **Available Surveys**: Access and complete active surveys.
- **Upcoming Surveys**: View surveys scheduled for future.
- **Survey Schedule**: Check planned surveys with their start time.
- **Payout Details**: Track total tokens earned and reward history.
- **Help Section**: FAQs or support info.
- **Reset Password**: Secure password change with email verification.

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Python (Flask)
- **Database**: MySQL
- **Email Service**: SMTP (for password delivery)
- **Utilities**: Token-based session management, datetime scheduling logic and etc

---


