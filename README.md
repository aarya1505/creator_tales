# 🌟 Creator Tales: AI-Powered LinkedIn Content Platform

Creator Tales is a full-stack web application designed to help LinkedIn content creators, students, job seekers, and professionals rapidly build and manage a powerful digital personal brand using advanced AI-powered tools.

## ✨ Features

Creator Tales provides a comprehensive suite of AI tools powered by the **Google Gemini API** to streamline LinkedIn content creation and profile optimization.

### 🤖 AI Content Generation Tools

| Tool | Description |
| :--- | :--- |
| **Post Generator** | Creates high-performing LinkedIn posts with optimized hooks, body content, and clear Calls-to-Action (CTAs). |
| **Content Rewriter** | Transforms rough drafts into professional, engaging, and LinkedIn-optimized content with enhanced tone. |
| **Carousel Generator** | Generates a 5-slide outline (Hook, Problem, Insight, Solution, CTA) with design tips for viral carousels. |
| **Profile Optimizer** | Suggests improvements for the About section, headline, and experience (using the STAR method) for better visibility. |
| **Message Generator** | Crafts personalized networking, referral, recruiter outreach, and client pitch messages. |
| **Content Calendar** | Produces weekly or monthly content plans with specific topics, post types, and **IST**-optimized posting times. |

---

### 📈 Analytics Module

* **Data Upload**: Users can upload LinkedIn analytics CSV/Excel files.
* **Visualization**: Generates charts (using Matplotlib) to visualize key metrics like impressions, engagement, and top-performing days. 
* **AI Recommendations**: Provides strategic, AI-powered insights and actionable recommendations based on the user's past performance data.

---

## 💻 Technology Stack

| Category | Technology | Notes |
| :--- | :--- | :--- |
| **Backend** | Python 3.10+, Flask, SQLAlchemy ORM | Lightweight and powerful framework. |
| **Database** | **MySQL** | Robust, external relational database named `creatortalesdb`. |
| **AI** | **Google Gemini API** (via `google-genai` SDK) | Powers all content and analytics generation features. |
| **Frontend** | HTML5, CSS3, JavaScript | Responsive and user-friendly interface. |
| **Authentication** | Flask-Login, `bcrypt` | Secure session management and password hashing. |

---

## ⚙️ Setup and Installation

Follow these steps to get a copy of the project running on your local machine.

### Prerequisites

* Python 3.10+
* A running **MySQL server** instance.
* A Google Gemini API Key.

### 1. Clone the Repository

# Bash
git clone <repository-url>
cd creator-tales

### 2. Set up a Virtual Environment
## Bash

python -m venv venv
source venv/bin/activate   # On Linux/macOS
.\venv\Scripts\activate  # On Windows

### 3. Install Dependencies
Install all required Python packages, including the necessary driver for MySQL (PyMySQL).

## Bash

pip install -r requirements.txt

### 4. Configure Environment Variables
Create a file named .env in the root directory and populate it with your configuration details.

Note: The database named creatortalesdb and a dedicated user must be set up on your MySQL server prior to running the app.

### Code snippet

## Flask Configuration
SESSION_SECRET=your_long_random_secret_key
FLASK_DEBUG=True

## Google Gemini API Key
GEMINI_API_KEY=YOUR_GOOGLE_GEMINI_API_KEY_HERE

## MySQL Database Configuration
## Format: mysql+pymysql://<user>:<password>@<host>/creatortalesdb
SQLALCHEMY_DATABASE_URI=mysql+pymysql://creator_tales_user:secure_password@localhost/creatortalesdb

### 5. Initialize and Run the Application
The application will connect to your MySQL server using the URI, create the necessary database tables, and start the web server.

## Bash

python app.py
The application will be running at http://127.0.0.1:5000/.
