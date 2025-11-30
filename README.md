# 📄 Document Upload & Viewer Web App

A clean and simple **Flask-based document management system**.  
Admins can upload files, rename them, delete them, and the public can view or download the documents.

Designed to be fast, mobile-friendly, and easy to use.

---

## 🚀 Features

### 🔒 Admin Panel
- Login system (password protected)
- Upload any document type (PDF, JPG, PNG, DOCX, PPTX, ZIP, etc.)
- Auto-rename file to prevent overwriting
- Edit document display name
- Delete documents
- Clean UI with responsive design

### 🌍 Public Interface
- View all uploaded documents
- Download any file
- Mobile-friendly buttons (View / Download)
- Automatically displays upload date & time (IST)

### 🧠 Backend
- Flask + SQLAlchemy
- Secure file handling with `werkzeug`
- Uses SQLite database (lightweight & portable)

---

## 🛠 Tech Stack

| Component | Technology |
|----------|------------|
| Backend | Python (Flask) |
| Database | SQLite + SQLAlchemy ORM |
| Frontend | HTML, Bootstrap 5, CSS |
| File Storage | Local `/uploads` folder |
| Authentication | Simple password-based session login |
