
# UltimAI

UltimAI is an intelligent agent designed to help players, coaches, and fans answer questions and clarify rules about **Ultimate Frisbee**.

---

## 🚀 Tech Stack

- **Python** — Core programming language for the backend.
- **FastAPI** — High-performance, modern web framework for building robust APIs.
- **LangChain** — For chaining and managing language models.
- **Google Gemini** — Main LLM to power conversations and rule clarifications.
- **PostgreSQL** — Relational database to store user data and interactions.
- **Docker** — Containerization for easy deployment and reproducible environments.

---

## 🌍 Multilingual Support

UltimAI currently supports:
- **English**
- **Spanish**
- **French**

---

## ✅ Current Features

- Answers common questions about Ultimate Frisbee rules.
- Detects keywords and generates clarifications.
- Multi-language support out of the box.

---

## 🗂️ Upcoming To-Do

- Fine-tune with gathered answers to improve accuracy.
- Improve prompts for **Ultimate Frisbee signals** generation.
- Add a **Nuxt** application for a modern frontend.
- Implement **user registration** and account management.
- Provide an official translation of Ultimate Frisbee rules in all supported languages.

---

## ⚙️ Setup & Configuration

### 📌 Prerequisites

Before you start, make sure you have **Docker** and **Docker Compose** installed on your machine.

- [Get Docker](https://www.docker.com/get-started/)
- [Get Docker Compose](https://docs.docker.com/compose/install/)

To run **UltimAI** locally, follow these steps:

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/ultimai.git
cd ultimai
```

---

### 2️⃣ Configure environment variables

In the root of the project, you’ll find a `.env.example` file. Copy it and rename it to `.env`:

```bash
cp .env.example .env
```

Edit the `.env` file with your own credentials:

```dotenv
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_NAME=your_db_name

PGADMIN_USER=your_pgadmin_user
PGADMIN_PASSWORD=your_pgadmin_password

LANGSMITH_API_KEY=your_langsmith_api_key  # Optional
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=UltimAI

GOOGLE_API_KEY=your_google_gemini_api_key  # Required
```

⚠️ **Important Notes:**
- **PostgreSQL and PgAdmin:** You **must** replace the default credentials with your own. It is **strongly discouraged** to use the example values.
- **LANGSMITH_API_KEY:** This is **optional** but recommended if you want advanced tracing and debugging with LangChain.
- **GOOGLE_API_KEY:** This is **required** to use Google Gemini.

👉 **Generate your API keys here:**
- [🔑 Get a Google Gemini API Key](https://aistudio.google.com/app/apikey)
- [🔑 Get a LangSmith API Key](https://smith.langchain.com/)

---

### 3️⃣ Create the PostgreSQL database manually

Before creating the database, you must **start the containers** so that **PostgreSQL** and **PgAdmin** are running.

Run:

```bash
docker compose up -d postgres pgadmin
```

By default, **PgAdmin** will be available at [http://localhost:8080](http://localhost:8080).

Log in with the credentials you defined in your `.env` file (`PGADMIN_USER` and `PGADMIN_PASSWORD`), then create a new server connection and your database, making sure the name matches `DATABASE_NAME`.

---

### 4️⃣ Run the application

Run the app using **Docker Compose**:

```bash
docker compose up --build
```

Once running:
- The APP will be available at [http://localhost:8000](http://localhost:8000).
- PgAdmin will be available at [http://localhost:8080](http://localhost:8080).

---

## 🤝 Contributing

Contributions are welcome! Please submit issues and pull requests to help improve **UltimAI**.

---

## 📄 License

This project is licensed under the **MIT License**.

---

**UltimAI — Your Ultimate Frisbee Assistant 🥏🤝**