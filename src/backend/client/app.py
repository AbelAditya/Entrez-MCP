import sys
from dotenv import load_dotenv

from client.ai_mode import ai_mode
from client.examples import run_client
from client.interactive import interactive_mode

load_dotenv()

async def main():
    args = sys.argv[1:]
    
    if len(args) > 0 and args[0] == "--interactive":
        await interactive_mode()
    elif len(args) > 0 and args[0] == "--ai":
        await ai_mode()
    else:
        print("Running basic examples...")
        await run_client()

