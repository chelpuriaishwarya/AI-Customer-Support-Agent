# AI Customer Support Agent

An AI-powered customer support system that provides personalized assistance by combining conversational AI with customer-specific memory.

## Overview

The AI Customer Support Agent is a web-based customer support application built with Flask. It allows support agents to interact with customers through a chat interface while maintaining customer-specific information and conversation context.

The system integrates **Ollama** for local AI processing and **Hindsight** for long-term customer memory, allowing responses to be more relevant to each customer's history and information.

## Features

* Customer-specific support conversations
* Personalized customer information
* Customer-specific memory
* AI-powered responses using Ollama
* Long-term memory using Hindsight
* Customer selection from the sidebar
* Conversation history
* Customer details and order information
* Memory management
* Support dashboard
* Local fallback responses when AI services are unavailable
* Responsive web interface

## Technology Stack

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Python
* Flask

### AI & Memory

* Ollama
* Llama 3.2
* Hindsight

### Development

* Git
* GitHub
* Docker

## System Architecture

```text
                 ┌──────────────────────┐
                 │     User / Agent     │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │    Flask Web App     │
                 │       app.py         │
                 └──────────┬───────────┘
                            │
                 ┌──────────┴───────────┐
                 │                      │
                 ▼                      ▼
        ┌─────────────────┐    ┌─────────────────┐
        │     Ollama      │    │    Hindsight    │
        │    Llama 3.2    │    │ Customer Memory │
        └─────────────────┘    └─────────────────┘
                 │                      │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Personalized Support │
                 │       Response       │
                 └──────────────────────┘
```

## How It Works

1. The support agent selects a customer from the sidebar.
2. The agent enters a question or support message.
3. The Flask backend processes the request.
4. Customer-specific information and memory are retrieved.
5. Relevant customer context is used to generate a response.
6. The response is displayed in the support chat interface.
7. Customer conversations and relevant information can be retained for future interactions.

## Project Structure

```text
AI-Customer-Support-Agent/
│
├── app.py
├── .gitignore
├── templates/
│   └── index.html
├── README.md
└── demo_memory.json
```

> `demo_memory.json` is used for local development and is excluded from GitHub using `.gitignore`.

## Requirements

* Python 3.x
* Flask
* Ollama
* Docker
* Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/chelpuriaishwarya/AI-Customer-Support-Agent.git
cd AI-Customer-Support-Agent
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

For Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

For Windows Command Prompt:

```cmd
venv\Scripts\activate.bat
```

### 4. Install Dependencies

```bash
pip install flask
```

## Ollama Setup

Install Ollama and make sure it is running.

Pull the required model:

```bash
ollama pull llama3.2:3b
```

Verify that the model is available:

```bash
ollama list
```

## Hindsight Setup

Hindsight is used to provide customer-specific long-term memory.

The application expects Hindsight to be available at:

```text
http://localhost:8888
```

The Hindsight URL can be configured using:

```text
HINDSIGHT_URL=http://localhost:8888
```

## Running the Application

Start the Flask application:

```bash
python app.py
```

Then open the following address in your browser:

```text
http://127.0.0.1:5000
```

## Customer-Specific Memory

Each customer has a separate memory bank.

Examples:

```text
customer-support-sam
customer-support-rahul-verma
customer-support-sneha-reddy
```

This keeps customer information and conversation context separated between customers.

## Data and Privacy

Local development data is kept on the user's machine.

The following files and folders are excluded from Git:

```text
venv/
__pycache__/
*.pyc
.env
demo_memory.json
```

This prevents the Python virtual environment, environment variables, and local customer memory data from being committed to the repository.

## Use Cases

The AI Customer Support Agent can be used for:

* Customer account assistance
* Order-related questions
* Personalized customer support
* Previous conversation lookup
* Customer information retrieval
* Support history management
* Context-aware customer interactions

## Future Improvements

* User authentication
* Database integration
* Real-time customer data
* Ticket management
* Email integration
* Customer sentiment analysis
* Automated ticket classification
* Support analytics
* Role-based access control
* Production deployment
* Improved conversation summarization

## License

This project is currently not distributed under an open-source license.

