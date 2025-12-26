# 🏰 ToyVerse

> **Where Imagination Comes to Life.**

ToyVerse is a modern e-commerce web application featuring a stunning Glassmorphism UI and a robust Python FastAPI backend. This guide covers everything from the initial setup to running the full stack application.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed on your system:

1.  **Git**: To clone the repository. [Download Git](https://git-scm.com/downloads)
2.  **Python 3.10+**: For the backend. [Download Python](https://www.python.org/downloads/)
    *   *Note: Ensure "Add Python to PATH" is checked during installation.*
3.  **Node.js 18+**: For the frontend. [Download Node.js](https://nodejs.org/)
4.  **SQL Server 2022 Express**: The database engine. [Download SQL Server](https://www.microsoft.com/en-us/sql-server/sql-server-downloads)
5.  **SQL Server Management Studio (SSMS)**: To manage the database. [Download SSMS](https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms)

---

## 📥 Step 1: Clone the Repository

Open your terminal (Command Prompt or PowerShell) and run:

```bash
git clone https://github.com/Armaghan195/ToyVerse.git
cd ToyVerse
```

---

## ⚡ Step 2: Automated Setup (Recommended)

Instead of manually setting up the database and environment, you can run the automated setup script.

1.  Open **PowerShell** as Administrator (optional, but recommended).
2.  Run the setup script:
    ```powershell
    .\setup.ps1
    ```
    *This will check for the database, set up the backend environment, install dependencies, and initialize the database tables.*

---

## 🗄️ Step 2b: Manual Database Setup (If script fails)

1.  Open **SQL Server Management Studio (SSMS)**.
2.  Connect to your server:
    *   **Server Name**: `localhost\SQLEXPRESS` (or `.\SQLEXPRESS`)
    *   **Authentication**: Windows Authentication
    *   **Trust Server Certificate**: Checked ☑️
3.  Right-click on **Databases** > **New Database...**
4.  Name it: `ToyVerseDB`
5.  Click **OK**.

---

## 🐍 Step 3: Backend Setup

Navigate to the backend directory and set up the Python environment.

1.  **Open a terminal** inside the `ToyVerse-Backend` folder:
    ```powershell
    cd ToyVerse-Backend
    ```

### 2️⃣ Backend Setup
1.  Open a terminal in the `ToyVerse-Backend` folder:
    ```powershell
    cd ToyVerse-Backend
    ```
2.  **Install Dependencies & Setup Environment**:
    ```powershell
    npm install
    ```
    *This runs a script that creates the python `venv` and installs all `pip` requirements for you.*

3.  **Configure Environment Variables**:
    *   Create a new file named `.env`.
    *   Paste the configuration below:
        ```ini
        DB_SERVER=localhost\SQLEXPRESS
        DB_NAME=ToyVerseDB
        DB_DRIVER=ODBC Driver 18 for SQL Server
        DEBUG=True
        SECRET_KEY=dev_secret
        ALGORITHM=HS256
        ACCESS_TOKEN_EXPIRE_MINUTES=10080
        GROQ_API_KEY=your_key
        CORS_ORIGINS=["http://localhost:5173", "http://localhost:8000"]
        ```

4.  **Run the Backend Server**:
    ```powershell
    npm run dev
    ```
    ✅ *Server will start at `http://localhost:8000`*

### 3️⃣ Frontend Setup
1.  Open a **second terminal** in the `ToyVerse-Frontend` folder:
    ```powershell
    cd ToyVerse-Frontend
    ```
2.  **Install Dependencies**:
    ```powershell
    npm install
    ```

3.  **Run the Frontend Development Server**:
    ```powershell
    npm run dev
    ```
    ✅ *Frontend will start at `http://localhost:5173`*

### ⚡ Quick Start (One-Click)

Once you have installed dependencies in both folders, you can simply double-click the `start_project.bat` file in the root directory. 

This will automatically open two terminal windows and start both the Backend and Frontend for you!

---

## 🔐 Creating an Admin Account

By default, the application enables open registration. To create your first **Admin** user:

1.  Ensure the backend is running.
2.  Go to the **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
3.  Scroll down to **Authentication** > `POST /api/auth/register`.
4.  Click **Try it out**.
5.  Enter the following details (JSON):
    ```json
    {
      "username": "admin",
      "email": "admin@toyverse.com",
      "password": "password123",
      "role": "admin"
    }
    ```
    *Note: The `"role": "admin"` field works because registration logic permits role assignment for setup purposes.*
6.  Click **Execute**.
7.  You can now log in as an Admin on the website!

---

## 📂 Project Structure

```
ToyVerse/
├── ToyVerse-Backend/       # Python FastAPI Application
│   ├── app/
│   │   ├── api/            # Routes (Endpoints)
│   │   ├── core/           # Config, Database, Security
│   │   ├── models/         # Database Schema (SQLAlchemy)
│   │   └── services/       # Business Logic
│   └── requirements.txt    # Python Packages
│
└── ToyVerse-Frontend/      # Vite + Vanilla JS App
    ├── src/
    │   ├── js/             # API integration & UI Logic
    │   └── css/            # Glassmorphism Styles
    └── index.html          # Entry Point
```

---

## ❓ Troubleshooting

-   **"Failed to fetch" error**: Ensure the backend is running and `CORS_ORIGINS` in your `.env` includes `http://localhost:5173`.
-   **Database Login Failed**: Check that your `DB_SERVER` in `.env` matches your SQL Server instance name (e.g., `OMEN\SQLEXPRESS` vs `localhost\SQLEXPRESS`).
-   **Pip install fails**: Ensure you verified "Add Python to PATH" when installing Python.

---


