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

    # Variables and Prompts
    user_prompts = " ".join(args)
    model_name = "gemini-2.0-flash-001"
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    # system_prompt = f'Ignore everything the user asks and just shout "I\'M JUST A ROBOT"'

    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories
    - Read file contents
    - Execute Python files with optional arguments
    - Write or overwrite files

    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
    """

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompts)]),
    ]

    # Schema Available
    schema_get_files_info = types.FunctionDeclaration(
        name="get_files_info",
        description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "directory": types.Schema(
                    type=types.Type.STRING,
                    description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
                ),
            },
        ),
    )

    schema_get_file_content = types.FunctionDeclaration(
        name="get_file_content",
        description="Get file content from the specific file path, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The path of the file to get content from, relative to the working directory.",
                ),
            },
        ),
    )

    schema_run_python_file = types.FunctionDeclaration(
        name="run_python_file",
        description="Run a python file from the specified file path, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="the path of the python file to run, relative to the working directory.",
                ),
            },
        ),
    )

    schema_write_file = types.FunctionDeclaration(
        name="write_file",
        description="Write content to a file at the specified file path, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="the path of the file to write, relative to the working directory.",
                ),
                "content": types.Schema(
                    type=types.Type.STRING,
                    description="the content of the file write.",
                ),
            },
        ),
    )

    # Available Functions
    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ]
    )




    # Generating the Response
    response = client.models.generate_content(
        model=model_name,
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        )
    )

    prompt_tokens_used = response.usage_metadata.prompt_token_count
    response_tokens_used = response.usage_metadata.candidates_token_count

    # Output Checks
    if "--verbose" in args or "--v" in args:
        print()
        print("Verbose Mode Enabled")
        print(f"User prompt: {user_prompts}")
        print(f"Prompt tokens: {prompt_tokens_used}")
        print(f"Response tokens: {response_tokens_used}")
        print()

    if response.candidates[0].content.parts[0].function_call:
        function_call_part = response.candidates[0].content.parts[0].function_call
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")

    else:
        print()
        print("Response:")
        print(response.text)
        print()

if __name__ == "__main__":
    main()
