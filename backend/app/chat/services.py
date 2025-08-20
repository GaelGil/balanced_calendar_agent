from app.chat.utils.tool_definitions import tool_definitions
from app.chat.utils.prompts import AGENT_PROMPT
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
from composio import Composio
import os
import logging

# logging stuff
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
# load env
load_dotenv(Path("../../.env"))


class ChatService:
    def __init__(self):
        self.chat_history: list[dict] = []
        self.model_name: str = "gpt-4.1-mini"
        self.llm: OpenAI
        self.tools = tool_definitions
        self.composio = Composio()
        self.user_id = "0000-1111-2222"

    def init_chat_services(self):
        """
        Initialize the chat services
        Args:
            None
        Returns:
            None
        """
        print("Initializing OpenAI client ...")
        self.llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.add_chat_history(role="developer", message=AGENT_PROMPT)

    def add_chat_history(self, role: str, message: str):
        """Adds a message to the chat history

        Args:
            role (str): The role of the message sender
            message (str): The message content
        Returns:
            None
        """
        self.chat_history.append({"role": role, "content": message})
