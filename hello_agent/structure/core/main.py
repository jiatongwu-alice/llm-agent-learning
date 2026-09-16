# my_main.py
from dotenv import load_dotenv
from llm import MyLLM # Note: Import our own class here

# Load environment variables
load_dotenv()

# Instantiate our overridden client and specify provider
llm = MyLLM(provider="modelscope")

# Prepare messages
messages = [{"role": "user", "content": "Hello, please introduce yourself."}]

# Make the call, think and other methods are inherited from parent class, no need to override
response_stream = llm.think(messages)

# Print response
print("ModelScope Response:")
for chunk in response_stream:
    # Chunk already printed in my_llm, just pass here
    # print(chunk, end="", flush=True)
    pass
