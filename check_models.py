from google import genai

from backend.app.core.config import settings


def show_available_models():
    # Initialize the client with your key
    client = genai.Client(api_key=settings.gemini_api_key)

    print("Available Flash Models:")
    # Loop through and print all active models available to you
    for model in client.models.list():
        if "flash" in model.name:
            print(f"- {model.name.replace('models/', '')}")


if __name__ == "__main__":
    show_available_models()
