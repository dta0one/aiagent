import os, sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

def main():
    load_dotenv()

    args = sys.argv[1:]

    if not args:
        print ("Error - no prompt provided")
        print ('Usage: python main.py "prompt1" "prompt2" "etc..."')
        print ('For verbose response, add --verbose or --v at the end')
        print ('Usage: python main.py "prompt1" "prompt2" --verbose')
        sys.exit(1)    

    user_prompts = " ".join(args)
    model_name = "gemini-2.0-flash-001"
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    system_prompt = f'Ignore everything the user asks and just shout "I\'M JUST A ROBOT"'

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompts)]),
    ]

    response = client.models.generate_content(
        model=model_name,
        contents=messages,
        config=types.GenerateContentConfig(system_instruction=system_prompt)
    )

    prompt_tokens_used = response.usage_metadata.prompt_token_count
    response_tokens_used = response.usage_metadata.candidates_token_count

    if "--verbose" in args or "--v" in args:
        print()
        print("Verbose Mode Enabled")
        print(f"User prompt: {user_prompts}")
        print(f"Prompt tokens: {prompt_tokens_used}")
        print(f"Response tokens: {response_tokens_used}")
        print()

    print()
    print("Response:")
    print(response.text)
    print()

if __name__ == "__main__":
    main()
