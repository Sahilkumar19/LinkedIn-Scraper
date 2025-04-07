import os
from browser_use import Agent, BrowserContextConfig
from dotenv import load_dotenv
from langchain.memory.token_buffer import ConversationTokenBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
llm=ChatGoogleGenerativeAI(
    model='gemini-2.0-flash-exp', 
    api_key=SecretStr(api_key)
)
class ContextManagedAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory = ConversationTokenBufferMemory(
            llm=llm,
            max_token_limit=3000,
            return_messages=True,
            memory_key="chat_history"
        )
        self.step_count = 0
        
    async def process_dom(self, dom: str) -> str:
        """Truncate DOM for LLM context"""
        return self._filter_interactive_elements(dom)[:2000]

    def _filter_interactive_elements(self, dom: str) -> str:
        return "\n".join([
            el for el in dom.split("\n") 
            if any(tag in el for tag in ['button', 'a', 'input'])
        ])

    async def run_step(self):
        # Reset context every 5 steps
        if self.step_count % 5 == 0:
            await self.browser_context.reload()
            self.memory.clear()
            
        return await super().run_step()

# Configure browser for optimal context
context_config = BrowserContextConfig(
    viewport_expansion=0,  # Only visible elements
    wait_for_network_idle_page_load_time=3.0,  # Allow full loading
    minimum_wait_page_load_time=1.0,
    highlight_elements=True  # Helps model focus
)