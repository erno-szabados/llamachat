import subprocess
import re
from colorama import Fore, Style, init

LLAMA_CPP_PATH="/usr/local/bin/llama-run"
MODEL_PATH="/home/eszabados/workspace/models/SmolLM2-360M-Instruct-Q8_0.gguf"
FLITE_VOICE="/home/eszabados/voices/cmu_us_clb.flitevox"

# Initialize colorama
init(autoreset=True)

history = []

def run_llama_cpp(prompt, history):
    full_prompt = "You are a helpful assistant. Answer briefly.\n"
    for turn in history:
        full_prompt += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"
    full_prompt += f"User: {prompt}\nAssistant:"
    
    try:
        #print(f"Running llama.cpp with prompt: {full_prompt}")
        process = subprocess.Popen(
            [LLAMA_CPP_PATH, MODEL_PATH, full_prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise RuntimeError(f"Error running llama.cpp: {stderr}")
            
        # Print raw output for debugging
        #print(f"Raw output: {stdout}")
        
        # Extract just the assistant's response
        if "Assistant:" in stdout:
            response = stdout.split("Assistant:")[-1].strip()
            return response
        else:
            return stdout.strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def speak_text(text, voice):
    # Clean the text to remove any unwanted characters at the end
    # that might be causing the "zero m" or "zero n" pronunciation
    cleaned_text = text.strip()
    
    # Ensure the text ends with proper punctuation to help speech synthesis
    if cleaned_text and cleaned_text[-1] not in '.!?':
        cleaned_text += '.'
        
    process = subprocess.Popen(
        ["flite", "-voice", voice, "-t", cleaned_text],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process.wait()

def clean_ansi_codes(text):
    """Remove ANSI escape sequences from text"""
    # This pattern matches common ANSI escape sequences including the "]0m" you're seeing
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~]|\].*?[a-zA-Z])')
    return ansi_escape.sub('', text)
    
if __name__ == "__main__":
    print(f"{Fore.CYAN}Interactive chat with {MODEL_PATH}")
    while True:
        user_input = input(f"{Fore.GREEN}You: {Style.RESET_ALL}")
        if user_input.strip().lower() == "exit":
            break
        
        assistant_response = run_llama_cpp(user_input, history)
        
        if assistant_response:
            # First remove ANSI escape sequences, then filter non-printable characters
            cleaned_response = clean_ansi_codes(assistant_response)
            clean_response = ''.join(char for char in cleaned_response if ord(char) >= 32)
            print(f"{Fore.YELLOW}Assistant: {clean_response}")
            speak_text(clean_response, FLITE_VOICE)
            history.append({"user": user_input, "assistant": clean_response})
        else:
            print(f"{Fore.RED}Error: no output from llama.cpp")






