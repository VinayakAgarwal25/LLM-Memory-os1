import requests
import config
import os

print("LLM CLIENT LOADED FROM:", os.path.abspath(__file__))


class LLMClient:
    def __init__(self):
        self.base_url = config.OLLAMA_BASE_URL
        self.model = config.OLLAMA_MODEL
        self.embed_model = config.OLLAMA_EMBED_MODEL

    # ======================
    # TEXT GENERATION
    # ======================
    def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"

        response = requests.post(
            url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()
        return response.json()["response"]

    # ======================
    # CONTEXTUAL RESPONSE
    # ======================
    def respond_with_context(self, user_input: str, context_memories: list[str]) -> str:
        """
        Generates response using retrieved memory context.
        """

        # Safety check
        if not isinstance(context_memories, list):
            context_memories = []

        # Format memory block
        if context_memories:
            context_block = "\n".join([f"- {mem}" for mem in context_memories])
        else:
            context_block = "No relevant stored memories."

        prompt = f"""
You are an AI assistant with long-term memory.
Use memories ONLY when they are directly relevant to the current user message.
If memories are unrelated, ignore them and answer from the current message naturally.
Do not keep talking about old topics unless explicitly asked.

Relevant Memories:
{context_block}

User: {user_input}
Assistant:
"""

        return self.generate(prompt)

    # ======================
    # EMBEDDINGS
    # ======================
    def embed(self, text: str):
        url = f"{self.base_url}/api/embeddings"

        response = requests.post(
            url,
            json={
                "model": self.embed_model,
                "prompt": text
            },
            timeout=120
        )

        response.raise_for_status()
        return response.json()["embedding"]

    # ======================
    # CHAT COMPATIBILITY API
    # ======================
    def chat(self, system_prompt: str, user_message: str) -> str:
        prompt = f"{system_prompt}\n\nUser: {user_message}\nAssistant:"
        return self.generate(prompt)
