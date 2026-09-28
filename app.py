import asyncio
import json
import os
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
HINDSIGHT_URL = os.getenv("HINDSIGHT_URL", "http://127.0.0.1:8888").rstrip("/")
BANK_PREFIX = "customer-support"

# IMPORTANT: this is the existing local memory file. Nothing in this version
# deletes, resets, or migrates it.
MEMORY_FILE = Path(__file__).with_name("demo_memory.json")

CUSTOMERS = {
    "Sam": {
        "phone": "+91 98765 43210",
        "email": "sam@example.com",
        "order_id": "#45678",
        "product": "Wireless Headphones",
        "price": "₹2,499",
        "issue": "Damaged item",
        "resolution": "Replacement",
        "status": "Open",
        "preview": "My order is damaged...",
        "time": "10:24 AM",
        "avatar": "S",
        "avatar_class": "",
    },
    "Rahul Verma": {
        "phone": "+91 98123 45678",
        "email": "rahul.verma@example.com",
        "order_id": "#78214",
        "product": "Smart Watch",
        "price": "₹3,799",
        "issue": "Refund pending",
        "resolution": "Refund",
        "status": "Processing",
        "preview": "When will my refund...",
        "time": "09:12 AM",
        "avatar": "R",
        "avatar_class": "alt",
    },
    "Sneha Reddy": {
        "phone": "+91 99001 23456",
        "email": "sneha.reddy@example.com",
        "order_id": "#61309",
        "product": "Cotton Kurta Set",
        "price": "₹1,299",
        "issue": "Change of size",
        "resolution": "Exchange",
        "status": "Open",
        "preview": "I want to change the...",
        "time": "Yesterday",
        "avatar": "S",
        "avatar_class": "teal",
    },
    "Arjun Mehta": {
        "phone": "+91 98450 76543",
        "email": "arjun.mehta@example.com",
        "order_id": "#90541",
        "product": "Mechanical Keyboard",
        "price": "₹4,499",
        "issue": "Warranty question",
        "resolution": "Support",
        "status": "Open",
        "preview": "Can you provide the...",
        "time": "Yesterday",
        "avatar": "A",
        "avatar_class": "",
    },
    "Neha Gupta": {
        "phone": "+91 98220 11223",
        "email": "neha.gupta@example.com",
        "order_id": "#34872",
        "product": "Bluetooth Speaker",
        "price": "₹2,199",
        "issue": "Delivery delayed",
        "resolution": "Delivery update",
        "status": "In transit",
        "preview": "Product not delivered...",
        "time": "2 days ago",
        "avatar": "N",
        "avatar_class": "orange",
    },
    "Kiran Das": {
        "phone": "+91 98661 22334",
        "email": "kiran.das@example.com",
        "order_id": "#52163",
        "product": "Laptop Stand",
        "price": "₹1,799",
        "issue": "Setup assistance",
        "resolution": "Guidance",
        "status": "Resolved",
        "preview": "Thanks for the help!",
        "time": "2 days ago",
        "avatar": "K",
        "avatar_class": "pink",
    },
    "Anaya Iyer": {
        "phone": "+91 98888 44556",
        "email": "anaya.iyer@example.com",
        "order_id": "#74625",
        "product": "Running Shoes",
        "price": "₹2,999",
        "issue": "Return policy",
        "resolution": "Return",
        "status": "Open",
        "preview": "Return policy question...",
        "time": "3 days ago",
        "avatar": "A",
        "avatar_class": "teal",
    },
    "Rohit Singh": {
        "phone": "+91 97777 55667",
        "email": "rohit.singh@example.com",
        "order_id": "#86420",
        "product": "USB-C Monitor",
        "price": "₹12,499",
        "issue": "Order status",
        "resolution": "Tracking",
        "status": "Shipped",
        "preview": "Order status update...",
        "time": "3 days ago",
        "avatar": "R",
        "avatar_class": "alt",
    },
}


def load_local_memory():
    """Read the existing local memory without changing its structure."""
    if not MEMORY_FILE.exists():
        return {}
    try:
        with MEMORY_FILE.open("r", encoding="utf-8") as f:
            value = json.load(f)
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_local_memory(customer, message):
    """Append to the existing local memory file; never clear existing entries."""
    data = load_local_memory()
    key = customer.strip().lower()
    existing = data.setdefault(key, [])
    if not isinstance(existing, list):
        existing = []
        data[key] = existing
    existing.append(message)
    with MEMORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_bank_id(customer):
    safe = re.sub(r"[^a-zA-Z0-9_-]", "-", customer.strip().lower())
    safe = re.sub(r"-+", "-", safe).strip("-") or "guest"
    return f"{BANK_PREFIX}-{safe[:50]}"


def http_json(url, method="GET", payload=None, timeout=4):
    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url, data=body, headers=headers, method=method)
    with urlopen(req, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
        return response.status, json.loads(raw) if raw else {}


def check_ollama():
    try:
        status, data = http_json(f"{OLLAMA_URL}/api/tags", timeout=3)
        models = [
            item.get("name", "")
            for item in data.get("models", [])
            if isinstance(item, dict)
        ]
        model_found = any(
            name == OLLAMA_MODEL or name.split(":")[0] == OLLAMA_MODEL.split(":")[0]
            for name in models
        )
        return {
            "connected": status == 200,
            "status": "connected" if status == 200 else "unavailable",
            "model": OLLAMA_MODEL,
            "model_available": model_found,
            "models": models,
            "detail": (
                f"{OLLAMA_MODEL} ready"
                if model_found
                else f"Ollama reachable; {OLLAMA_MODEL} not found"
            ),
        }
    except (URLError, HTTPError, TimeoutError, OSError, ValueError) as exc:
        return {
            "connected": False,
            "status": "unavailable",
            "model": OLLAMA_MODEL,
            "model_available": False,
            "models": [],
            "detail": f"Cannot reach Ollama ({type(exc).__name__})",
        }


def check_hindsight():
    # Hindsight documents /health/ready as the readiness endpoint (with /health
    # supported as its alias). Some local Docker versions do not require auth.
    for path in ("/health/ready", "/health"):
        try:
            status, _ = http_json(f"{HINDSIGHT_URL}{path}", timeout=3)
            if status == 200:
                return {
                    "connected": True,
                    "status": "connected",
                    "detail": "Hindsight API ready",
                }
        except (URLError, HTTPError, TimeoutError, OSError, ValueError):
            pass

    return {
        "connected": False,
        "status": "unavailable",
        "detail": "Cannot reach Hindsight readiness endpoint",
    }


def ollama_chat(customer, question, memories):
    profile = CUSTOMERS.get(customer, {})
    local_history = load_local_memory().get(customer.lower(), [])
    memory_text = "\n".join(str(x) for x in memories[:12])
    local_text = "\n".join(str(x) for x in local_history[-8:])

    prompt = f"""You are a helpful AI customer support agent.
Answer the customer's latest message politely and concisely.
Use only information supplied below. Do not invent order details, policies,
refund dates, tracking numbers, or actions that have not happened.
If the available information is insufficient, ask a useful follow-up question.

Customer profile:
{json.dumps(profile, ensure_ascii=False, indent=2)}

Relevant Hindsight memories:
{memory_text or "(none returned)"}

Recent local conversation memory:
{local_text or "(none)"}

Latest customer message:
{question}
"""

    status, data = http_json(
        f"{OLLAMA_URL}/api/chat",
        method="POST",
        payload={
            "model": OLLAMA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.2},
        },
        timeout=90,
    )
    if status != 200:
        raise RuntimeError(f"Ollama returned HTTP {status}")

    message = data.get("message", {})
    reply = message.get("content")
    if not reply:
        raise RuntimeError("Ollama returned no response text")
    return reply.strip()


async def run_hindsight(customer, question):
    """Store and recall through the customer's existing Hindsight bank."""
    from hindsight_client import Hindsight

    bank_id = get_bank_id(customer)
    async with Hindsight(base_url=HINDSIGHT_URL) as client:
        try:
            await client.create_bank(
                bank_id=bank_id,
                name=f"Customer Support - {customer}",
            )
        except Exception as exc:
            # Existing banks are expected. Do not delete/recreate them.
            print("Hindsight bank note:", str(exc))

        await client.aretain(
            bank_id=bank_id,
            content=f"Customer: {customer}\nMessage: {question}",
            context="Customer support conversation",
        )

        recalled = await client.arecall(
            bank_id=bank_id,
            query=question,
            budget="mid",
            max_tokens=2000,
        )
        memories = getattr(recalled, "results", recalled)
        if memories is None:
            memories = []
        if not isinstance(memories, list):
            memories = [memories]

        return memories


def memory_for_ui(memories):
    output = []
    for item in memories:
        if isinstance(item, str):
            output.append(item)
        else:
            text = getattr(item, "text", None)
            if text:
                output.append(text)
            elif isinstance(item, dict) and item.get("text"):
                output.append(str(item["text"]))
            else:
                output.append(str(item))
    return output[:12]


def local_demo_reply(customer, question, history):
    """Offline fallback only; Ollama is attempted first when available."""
    profile = CUSTOMERS.get(customer, {})
    q = question.lower()
    joined = " ".join(history).lower()

    if any(x in q for x in ("hello", "hi", "hey")):
        return f"Hello {customer}! How can I help you today?"
    if "order" in q or "order number" in q:
        return (
            f"Your current order is {profile.get('order_id', 'not available')} "
            f"for {profile.get('product', 'the listed product')} at "
            f"{profile.get('price', 'the listed price')}."
        )
    if any(x in q for x in ("problem", "issue", "damaged", "refund", "return", "delivery")):
        return (
            f"The current support record shows: {profile.get('issue', 'an open support issue')}. "
            f"The listed resolution is {profile.get('resolution', 'support assistance')}."
        )
    if "remember" in q and joined:
        return "I have information from this customer's previous local conversation memory."
    return (
        "Ollama is not available right now. I can still see the customer's saved "
        "support record, but please try again after Ollama is running."
    )


@app.route("/", methods=["GET"])
def home():
    return render_template(
        "index.html",
        customers=CUSTOMERS,
        customer_list=list(CUSTOMERS.keys()),
    )


@app.route("/api/health", methods=["GET"])
def health():
    ollama = check_ollama()
    hindsight = check_hindsight()
    return jsonify({
        "ollama": ollama,
        "hindsight": hindsight,
        "overall": "connected" if ollama["connected"] and hindsight["connected"] else "partial",
    })


@app.route("/api/customers", methods=["GET"])
def customers():
    return jsonify(CUSTOMERS)


@app.route("/api/customer/<path:customer>", methods=["GET"])
def customer_details(customer):
    profile = CUSTOMERS.get(customer)
    if not profile:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify(profile)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    customer = str(data.get("customer", "")).strip()
    question = str(data.get("message", "")).strip()

    if not customer or not question:
        return jsonify({"reply": "Please enter a customer name and message."}), 400

    if customer not in CUSTOMERS:
        # Allow user-created names, while giving them a safe generic profile.
        CUSTOMERS[customer] = {
            "phone": "Not provided",
            "email": "Not provided",
            "order_id": "Not provided",
            "product": "Not provided",
            "price": "Not provided",
            "issue": "New conversation",
            "resolution": "Pending",
            "status": "Active",
            "preview": question,
            "time": "Now",
            "avatar": customer[:1].upper() or "?",
            "avatar_class": "",
        }

    history = load_local_memory().get(customer.lower(), [])
    save_local_memory(customer, question)

    hindsight_ok = False
    memories = []
    hindsight_error = None

    try:
        memories = asyncio.run(run_hindsight(customer, question))
        hindsight_ok = True
    except Exception as exc:
        hindsight_error = repr(exc)
        print("Hindsight request failed:", hindsight_error)

    try:
        reply = ollama_chat(customer, question, memory_for_ui(memories))
        ollama_ok = True
        source = "ollama+hindsight" if hindsight_ok else "ollama+local"
    except Exception as exc:
        print("Ollama request failed:", repr(exc))
        ollama_ok = False
        reply = local_demo_reply(customer, question, history)
        source = "local_fallback"

    return jsonify({
        "reply": reply,
        "source": source,
        "ollama": ollama_ok,
        "hindsight": hindsight_ok,
        "memories": memory_for_ui(memories),
        "hindsight_error": hindsight_error,
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
