import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import MAX_CHARS, WORKING_DIR, LOOP_LIMIT
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python import run_python_file


def main():
    load_dotenv()

    verbose = "--verbose" in sys.argv or "--v" in sys.argv
    args = sys.argv[1:]

    if not args:
        print ("Error - no prompt provided")
        print ('Usage: python main.py "prompt1" "prompt2" "etc..."')
        print ('For verbose response, add --verbose or --v at the end')
        print ('Usage: python main.py "prompt1" "prompt2" --verbose')
        sys.exit(1)    

    # Variables and Prompts
    prompt_args = [arg for arg in args if arg not in ["--verbose", "--v"]]
    user_prompts = " ".join(prompt_args)
    model_name = "gemini-2.0-flash-001"
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories
    - Read file contents
    - Execute Python files with optional arguments
    - Write or overwrite files

    You should use the available functions to explore files and answer questions. Do not ask the user for file names—use your tools to find out!

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

    def call_function(function_call_part, verbose=False):
        function_map = {
            "get_files_info": get_files_info,
            "get_file_content": get_file_content,
            "run_python_file": run_python_file,
            "write_file": write_file,
        }
        args_dict = dict(function_call_part.args)
        args_dict["working_directory"] = WORKING_DIR

        function_name = function_call_part.name

        if verbose:
            print(f"Calling function: {function_call_part.name}({function_call_part.args})")
        else:
            print(f" - Calling function: {function_call_part.name}")

        if function_name not in function_map:
            return types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=function_name,
                        response={"error": f"Unknown function: {function_name}"},
                    )
                ],
            )

        selected_function = function_map[function_name]
        function_result = selected_function(**args_dict)

        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": function_result},
                )
            ],
        )

    # Main Loop Logic
    break_counter = 0
    while True:
        # Generating the Response
        response = client.models.generate_content(
            model=model_name,
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions], system_instruction=system_prompt
            )
        )

        # Add the model's response to messages
        for candidate in response.candidates:
            messages.append(candidate.content)
            if verbose:
                print(f"\nModel ({candidate.content.role}): {candidate.content.parts[0].text}")

        # Check if there are function calls to process
        function_calls_made = False
        if response.function_calls:
            function_calls_made = True
            for function_call_part in response.function_calls:
                function_call_result = call_function(function_call_part, verbose)
                messages.append(function_call_result)

                if verbose:
                    for part in function_call_result.parts:
                        print(f"-> {part.function_response.response}")

        # If no function calls were made, we're done
        if not function_calls_made:
            if verbose:
                print("No more function calls")
            break

        break_counter += 1
        if break_counter >= LOOP_LIMIT:
            if verbose:
                print("Exceeded break_counter limit")
            break


    # Verbose Tokens
    prompt_tokens_used = response.usage_metadata.prompt_token_count
    response_tokens_used = response.usage_metadata.candidates_token_count

    if verbose:
        print()
        print("Verbose Mode")
        print(f"User prompt: {user_prompts}")
        print(f"Prompt tokens: {prompt_tokens_used}")
        print(f"Response tokens: {response_tokens_used}")

    # Output
    print()
    print("Final Response:")
    print(response.text)
    print()

if __name__ == "__main__":
    main()
