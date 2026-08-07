import httpx

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "saptarshi@example.com"  # <-- Change this to your user's email
PASSWORD = "password"  # <-- Change this to your user's password


def run():
    print("🚀 Booting up Client...")
    with httpx.Client() as client:
        # 1. Authenticate to get our JWT Token
        # Note: FastAPI's OAuth2 uses form data, not JSON, for login!
        auth_response = client.post(
            f"{BASE_URL}/auth/login", data={"username": EMAIL, "password": PASSWORD}
        )

        if auth_response.status_code != 200:
            print("❌ Login failed! Check your email and password.")
            return

        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create a new Conversation
        conv_response = client.post(
            f"{BASE_URL}/conversations/",
            json={"title": "Streaming Test"},
            headers=headers,
        )
        conv_id = conv_response.json()["id"]

        # 3. Stream the AI's Response
        prompt = "Explain how a Transformer Neural Network works, but explain it like I am a 10-year-old."
        print(f"\n👤 You: {prompt}\n")
        print("🤖 AI: ", end="", flush=True)

        # We use client.stream() to keep the connection open and read chunks as they arrive
        with client.stream(
            "POST",
            f"{BASE_URL}/conversations/{conv_id}/messages/stream",
            json={"content": prompt},
            headers=headers,
        ) as response:
            # Read the SSE stream line-by-line
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Strip the "data: " prefix

                    # Ignore the JSON metadata payloads (user_message & completed)
                    if data.startswith("{"):
                        continue

                    # Print the raw text chunks to the terminal in real-time!
                    print(data, end="", flush=True)

        print("\n\n✅ [Stream Completed and Saved to PostgreSQL]")


if __name__ == "__main__":
    run()
