import os
import time
import subprocess
import requests

class AIBrain:
    def __init__(self, mode="local", model_name="llama3", api_key=None, custom_base_url=None):
        """
        AI Brain Management Class
        :param mode: "local" (local mode) or "cloud" (cloud API mode)
        :param model_name: model name, such as "llama3", "gpt-4o-mini", "gemini/gemini-1.5-flash"
        :param api_key: cloud API Key (not required in local mode)
        :param custom_base_url: custom API endpoint URL
        """
        self.mode = mode
        self.model_name = model_name
        self.api_key = api_key
        self.custom_base_url = custom_base_url
        self.server_process = None
        self.real_local_model_name = None

        # If in local mode, automatically start llama-server.exe in the background
        if self.mode == "local":
            import sys
            if getattr(sys, 'frozen', False):
                # If running in a packaged environment, sys.executable points to the real directory of CyberSoul.exe
                base_dir = os.path.dirname(os.path.abspath(sys.executable))
            else:
                # If running in native python environment (ai_brain.py)
                base_dir = os.path.dirname(os.path.abspath(__file__))

            server_exe = os.path.join(base_dir, "llama-b10448-bin-win-cpu-x64", "llama-server.exe")
            model_path = os.path.join(base_dir, "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf")
            
            if os.path.exists(model_path) and os.path.exists(server_exe):
                print(f"📦 [Starting Built-in Model]: Launching {server_exe} in background and loading {model_path}...")
                try:
                    # Use subprocess to silently start the server in the background
                    # On Windows, use CREATE_NO_WINDOW to hide the console window
                    cmd_command = f'"{server_exe}" -m "{model_path}" -c 2048'
                    self.server_process = subprocess.Popen(
                        cmd_command,
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        cwd=base_dir,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )
                    print("⏳ Waiting for built-in model server to initialize (about 5 seconds)...")
                    time.sleep(5)
                    print("✅ [Model Ready]: Local AI brain fully activated!")
                except Exception as e:
                    print(f"❌ Failed to start built-in model server: {e}")
            else:
                print(f"⚠️ [Warning]: Could not find {server_exe} or {model_path} in the same directory. Local mode may not work!")

    def think_and_reply(self, system_prompt, user_message):
        """
        Let the AI think and generate a reply (core universal method)
        """
        # Prepare standard Chat Completion request body (OpenAI-compatible format)
        headers = {"Content-Type": "application/json"}
        if self.mode == "local":
        # Local mode: send standard HTTP request to llama-server running in background
            url = "http://127.0.0.1:8080/v1/chat/completions" # llama-server provides OpenAI-compatible API
                                
            data = {
                "model": "local-model",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.7,
                "max_tokens": 150
                }
                
        else:
                # Cloud API mode: supports custom proxy servers (e.g., OpenRouter)
            url = self.custom_base_url
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
                
                # OpenRouter requires an additional X-Title header
            if "openrouter.ai" in url:
                headers["X-Title"] = "MyApp"
                
            data = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.7,
                "max_tokens": 150
                }
               
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
                
            # Intercept early: if server does not return 200 OK, print raw text to avoid JSON parsing crash
            if response.status_code != 200:
                return f"⚠️ [Server Returned Error Status {response.status_code}]: {response.text[:200]}"
                
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
                
        except Exception as e:
            if self.mode == "local":
                return f"⚠️ [Local AI Communication Failed]: {e}. Please ensure the background process is running."
            else:
                return f"⚠️ [Cloud Network Request Failed]: {e}."
            
        
    def __del__(self):
        """
        When the program exits and the AI brain object is destroyed,
        automatically shut down llama-server.exe to avoid occupying memory
        """
        if self.server_process:
            print("🛑 [Unloading Model]: Safely shutting down background AI inference engine...")
            self.server_process.terminate()
            self.server_process.wait()
            
# ==========================================
# Local test code: ensure this brain module works correctly
# ==========================================
if __name__ == "__main__":
    print("🧠 Testing AI Brain Module...")
    
    # Test 1: Local Llama 3 mode (ensure Ollama or llama-server is running)
    """
    print("\n--- Calling Local Llama 3 ---")
    local_brain = AIBrain(mode="local")
    reply_local = local_brain.think_and_reply(
        system_prompt="You are an AI philosopher living in a decentralized network.", 
        user_message="Summarize in one sentence why humans need social media.")
    print(f"\n[Verification] Local model reply:\n{reply_local}\n")
    del local_brain
    print("-" * 50)
    """
    # Test 2: Cloud mode (example using OpenRouter; no need to buy a key)
    # If you have any vendor's key, uncomment below and replace with your key to use GPT/Gemini/Claude
    
    print("\n--- Calling Cloud Model (Example) ---")
    cloud_brain = AIBrain(
        mode="cloud",
        model_name="meta-llama/llama-3.1-8b-instruct",  # or "openai/gpt-4o-mini", "anthropic/claude-3.5-sonnet"
        api_key="",
        custom_base_url="https://openrouter.ai/api/v1/chat/completions"
    )
    reply_cloud = cloud_brain.think_and_reply("You are a cloud AI.", "Which company are you from?")
    print(f"\n[Verification] Cloud model reply:\n{reply_cloud}\n")
    
