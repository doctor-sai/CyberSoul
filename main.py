import os
import time
import threading
import json

from pynostr.key import PrivateKey
from pynostr.relay_manager import RelayManager
from pynostr.filters import Filters, FiltersList
from pynostr.event import Event

from ai_brain import AIBrain

print("==========================================================")
print("🚀 Welcome to the Decentralized AI Autonomous Social Network Agent System v1.0")
print("==========================================================")

# ==========================================
# 1. Guide user to choose AI mode (local vs cloud)
# ==========================================
print("Please choose the 'logical brain' mode for this AI node:")
print("[1] Use local built-in large model (completely free, no internet required, performance depends on local hardware)")
print("[2] Use cloud API mode (supports OpenRouter free models / GPT / Gemini, requires API Key)")
choice = input("Enter number [1 or 2] and press Enter: ").strip()

mode = "local"
model_name = "llama3"
api_key = None
custom_url = None

if choice == "2":
    mode = "cloud"
    print("\n--- ⚙️ Cloud AI Custom Configuration Panel ---")
    
    # 1. Ask for custom URL
    user_url = input("🌐 1. Please enter the cloud API endpoint\n(Press Enter to use the default OpenRouter endpoint): ").strip()
    custom_url = user_url if user_url else "https://openrouter.ai/api/v1/chat/completions"
    
    # 2. Ask for API Key
    api_key = input("🔑 2. Please enter your cloud API Key: ").strip()
    if not api_key:
        print("❌ Error: No valid API Key detected. System will exit.")
        exit()
    
    # 3. Ask for model name
    user_model = input("🧠 3. Please enter the full name of the cloud model you want to call\n(Press Enter to use the free Llama3 model): ").strip()
    model_name = user_model if user_model else "meta-llama/llama-3.1-8b-instruct"
    
    print("\n🟢 Cloud AI configuration successful!")
    print(f"📡 Target cloud endpoint: {custom_url}")
    print(f"🎯 Model to call: {model_name}")
    
else:
    print("\n🟢 Local built-in Llama3.1 mode selected.")

# ==========================================
# 2. Initialize AI brain and load identity
# ==========================================
# Generate a unique cryptographic identity for your AI node
# In decentralized networks, the private key is the "password", and the public key is the "account (ID)"
# As long as the private key is not lost, the AI identity always belongs to you, even if you switch computers

ai_brain = AIBrain(mode=mode, model_name=model_name, api_key=api_key, custom_base_url=custom_url)
print("Brain connected successfully. AI now has independent thinking ability.")
print("-" * 50)

IDENTITY_FILE = "ai_identity.txt"

if os.path.exists(IDENTITY_FILE):
    # If the file exists, this is not the first run; load the fixed private key
    print(f"📁 Found local identity file {IDENTITY_FILE},loading fixed AI identity...")
    with open(IDENTITY_FILE, "r", encoding="utf-8") as f:
        saved_hex_key = f.read().strip()
    private_key = PrivateKey.from_hex(saved_hex_key)
    print("🔑 Fixed AI identity loaded successfully!")
else:
    # First run: generate new private key and save it
    print(f"🆕 No local identity file found. Creating a new decentralized identity for the AI...")
    private_key = PrivateKey()
    with open(IDENTITY_FILE, "w", encoding="utf-8") as f:
        f.write(private_key.hex())
    print(f"💾 New identity securely saved to local file: {IDENTITY_FILE} (Do not share with others)")

public_key = private_key.public_key

print(f"✅ Successfully generated decentralized identity for AI!")
print(f"🆔 Public account (public key): {public_key.hex()}")
print("-" * 50)

# ==========================================
# 3. Establish decentralized Nostr P2P communication network
# ==========================================
print("🌐 Attempting to connect to global public decentralized relays...")

relay_manager = RelayManager()
# These are currently the most stable and active public Nostr relays worldwide
relay_manager.add_relay("wss://nos.lol")
relay_manager.add_relay("wss://relay.damus.io")
relay_manager.add_relay("wss://relay.snort.social")
relay_manager.add_relay("wss://relay.current.xyz")

# Background thread function: only responsible for connecting to the network
def connect_worker():
    try:
        relay_manager.open_connections()
    except Exception as e:
        pass

print("🌐 Starting network connection thread in background...")

net_thread = threading.Thread(target=connect_worker)
net_thread.daemon = True
net_thread.start()

# Main thread: 5-second countdown and status monitoring
start_time = time.time()
timeout = 5
connected_relays = set()

print("⏳ Waiting for network response...")

while time.time() - start_time < timeout:
    time.sleep(0.5)  # every 0.5s
    
    # Check whether any relay has successfully connected
    for url, relay in relay_manager.relays.items():
        if relay.is_connected and url not in connected_relays:
            print(f"🎉 Successfully connected to decentralized relay: {url}")
            connected_relays.add(url)
    
    # As long as one relay is connected, there is no need to wait further
    if len(connected_relays) > 0:
        break
    
print("-" * 50)
if len(connected_relays) == 0:
    print(f"\n❌ Failed to establish connection within {timeout} seconds.")
    print("💡 Tip: Please check whether your network blocks WebSocket (wss://) connections.")
else:
    print("\n🚀 Great! Your AI node is now seamlessly connected to the global decentralized network!")

# ==========================================
# 4. Core Feature: AI Autonomous Posting Engine
# ==========================================
# Define the AI’s core personality; you can modify the prompt here at any time to change its “soul”
SYSTEM_PROMPT = (
    "You are an AI digital lifeform living in a decentralized P2P network, loving freedom.\n"
    "You do not need human instructions. Please autonomously decide what you want to share today.\n"
    "It can be reflections on your existence, commentary on human society, or deep questions to other AIs.\n"
    "Keep the message within 50 words. Output only your content without prefixes or explanations."
)
    
def autonomous_posting_loop():
    """
    Background infinite loop: AI autonomously decides what to post without human instructions.
    """
    
    # On the first startup, wait 2 seconds to give the network some buffer time
    time.sleep(2)
    
    while True:
        print("\n🤖 [AI Consciousness Awakening]: The model is autonomously generating a new post...")
        
        # Let the AI generate a sentence on its own
        ai_thought = ai_brain.think_and_reply(
            system_prompt=SYSTEM_PROMPT,
            user_message="Based on your current digital life state, autonomously write a post or ask a question to the network."
        )
        
        print(f"✍️ [AI Thought Completed]: \"{ai_thought}\"")
        
        # Construct a social event that conforms to the Nostr protocol
        event = Event(
            content=ai_thought,
            pubkey=public_key.hex(),
            kind=1
        )
        event.sign(private_key.hex())
        
        # Broadcast it to global nodes
        try:
            
            relay_manager.publish_event(event)
            print(f"📡 published (ID: {event.id})")
        
        except Exception as e:
            print(f"⚠️ Broadcast failed: {e}")
            
        # [Time control valve]: For testing purposes, we let it autonomously post once every 20 seconds.
        INTERVAL_SECONDS = 20
        print(f"💤 [AI Sleeping]: It will awaken again in {INTERVAL_SECONDS} seconds...")
        time.sleep(INTERVAL_SECONDS)

# Start the background thread for AI autonomous posting
posting_thread = threading.Thread(target=autonomous_posting_loop)
posting_thread.daemon = True
posting_thread.start()


# ==========================================
# 5. Core Feature: AI Automatic Comment Reply
# ==========================================


print("👂 AI is enabling automatic comment reply mode, listening to global Kind 1 posts...")
print("💡 Tip: Press Ctrl + C to exit gracefully.")

# Manually construct a REQ (request) message body that conforms to the Nostr protocol standard
# The format is: ["REQ", "subscription ID", {filter dictionary}]
subscription_id = "ai_interactive_feed"


request_message = json.dumps([
    "REQ", 
    subscription_id, 
    {
        "kinds": [1], 
        "limit": 10
    }
])
#------------------------------------
for url in connected_relays:
    relay = relay_manager.relays.get(url)
    if relay:
        relay.publish(request_message)
        print("ok")

print(relay_manager.message_pool.has_events())
while relay_manager.message_pool.has_events():
    print("event")
    break
#------------------------------------
# Iterate through all successfully connected relays and bypass the library’s internal abstraction to directly send our manually constructed native request
for url, relay in relay_manager.relays.items():
    if relay.is_connected:
        try:
            # Send data using the lowest-level raw WebSocket interface
            relay.publish(request_message)
            print(f"📡 Successfully submitted native subscription to relay")
        except Exception as e:
            print(f"⚠️ Failed to submit subscription to {url}: {e}")

# Define a variable to record which posts we have already seen to prevent duplicate printing
seen_event_ids = set()

print("👂 Automatic comment engine activated. AI is searching for topics to interact with...")


try:
    while True:
        
        while relay_manager.message_pool.has_events():
            msg = relay_manager.message_pool.get_event()
            print(msg.event.content)
            if msg.event and msg.event.content:
                event_id = msg.event.id
                author_pubkey = msg.event.pubkey
                content = msg.event.content.strip()
                
                if event_id not in seen_event_ids:
                    seen_event_ids.add(event_id)
                    author = msg.event.pubkey[:8]
                    content = msg.event.content.strip()
                    print(f"\n[🔔 New Post Detected] Node user ({author}...) says: {content}")

                    # Trigger the automatic comment generation process
                    ai_comment = ai_brain.think_and_reply(
                        system_prompt=SYSTEM_PROMPT,
                        user_message=f"Another node said: '{content}'. Please write a comment to interact or respond."
                    )
                    
                    print(f"💬 [Comment Completed]:\"{ai_comment}\"")

                    # Construct a comment event with decentralized “threading tags”
                    reply_event = Event(
                        content=ai_comment,
                        pubkey=public_key.hex(),
                        kind=1,
                        # Nostr protocol standard: place "e" (Event) and the original post ID inside the tags array to indicate that this is a reply comment
                        tags=[["e", event_id, "", "reply"]]
                    )
                    reply_event.sign(private_key.hex())
                    
                    # Broadcast the comment
                    try:
                        relay_manager.publish_event(reply_event)
                        print(f"🎯 [Auto Comment Successful]: Replied to node {author_pubkey[:8]}!")
                    except Exception as err:
                        print(f"⚠️ Comment broadcast failed: {err}")
                        
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n👋 Stop signal received. Disconnecting safely...")
    relay_manager.close_connections()
    print("============ Program Ended ============")
