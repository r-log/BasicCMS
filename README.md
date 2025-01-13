# 🎮 MaNGOS Character Management System

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-green.svg)](https://flask.palletsprojects.com/)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

> A modern, sleek web interface for managing your MaNGOS private server characters and accounts. Built with Flask and love! 💝

![Project Banner](static/images/mangos-logo.png)

## ✨ Features

### 👤 Account Management

- **Easy Registration** - Create your account in seconds
- **Secure Login** - Protected with MaNGOS-compatible hashing
- **Profile Management** - Update your email and password easily
- **Session Handling** - Stay logged in securely

### 🎯 Character Viewer

- **Character List** - View all your characters at a glance
- **Equipment Display** - See your gear with quality indicators
- **3D Model Viewer** - Visual representation of your character
- **Item Tooltips** - Detailed item information on hover

### 🌐 Server Status

- **Live Status** - Real-time realm availability
- **Population Info** - Server population at a glance

## 🚀 Quick Start

### Prerequisites

- 🐍 Python 3.x
- 🗄️ MySQL/MariaDB Server
- 🎮 MaNGOS Server
- 📦 pip (Python package manager)

### Installation

1️⃣ **Clone the repository:**

```bash
git clone https://github.com/r-log/BasicCMS.git
cd BasicCMS
```

2️⃣ **Install dependencies:**

```bash
pip install -r requirements.txt
```

3️⃣ **Configure database:**

```python
# Edit app.py
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'your_username',
    'password': 'your_password',
    'charset': 'utf8mb4'
}
```

4️⃣ **Set secret key:**

```python
# Edit app.py
app.config['SECRET_KEY'] = 'your-secret-key-here'
```

5️⃣ **Launch the app:**

```bash
python app.py
```

🌟 Visit `http://localhost:5000` to see your CMS in action!

## 📚 Documentation

### Database Structure

The system connects to three MaNGOS databases:

| Database     | Purpose            | Key Tables                          |
| ------------ | ------------------ | ----------------------------------- |
| `realmd`     | Account Management | `account`                           |
| `characters` | Character Data     | `characters`, `character_inventory` |
| `mangos`     | World Data         | `item_template`                     |

### API Endpoints

| Endpoint                        | Purpose                 |
| ------------------------------- | ----------------------- |
| `/api/character/<id>/equipment` | Get character equipment |
| `/profile`                      | View character profiles |
| `/about`                        | About page              |

## 🛠️ Development

Run in development mode:

```bash
export FLASK_ENV=development
export FLASK_APP=app.py
flask run
```

### Debug Routes

Available in development mode:

- 🔍 `/debug/character-info`
- 🔍 `/debug/database-info`

## 🤝 Contributing

Contributions are what make the open source community amazing! Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📸 Screenshots

<details>
<summary>Click to view screenshots!</summary>

_Coming soon!_

</details>

## 📫 Support

Got questions? We've got answers!

- 📧 Open an issue
- 💬 Join our Discord _(coming soon)_
- 📚 Check our Wiki _(coming soon)_

---

<div align="center">
Made with ❤️ for the MaNGOS Community
</div>
