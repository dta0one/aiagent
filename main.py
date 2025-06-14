import os, sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

def main():
    load_dotenv()

    if len(sys.argv) < 2:
        print ("No prompt provided")
        sys.exit(1)    

    user_prompts = sys.argv[1:]
    ai_model = "gemini-2.0-flash-001"

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompts)]),
    ]

    api_key = os.environ.get("GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=ai_model,
        contents=messages
    )

    prompt_tokens_used = response.usage_metadata.prompt_token_count
    response_tokens_used = response.usage_metadata.candidates_token_count

    print()
    print(f"Prompt tokens: {prompt_tokens_used}")
    print(f"Response tokens: {response_tokens_used}")
    print()
    print("Response:")
    print(response.text)
    print()

if __name__ == "__main__":
    main()
