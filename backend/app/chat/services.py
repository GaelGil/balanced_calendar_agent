from app.chat.utils.tool_definitions import tool_definitions
from app.chat.utils.prompts import AGENT_PROMPT
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
from composio import Composio
import os
import logging
import json

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
        self.tools = tool_definitions
        self.composio = Composio()
        self.user_id = "0000-1111-2222"
        self.llm: OpenAI = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not self.chat_history:
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

    def process_message_stream(self, message: str):
        """Processes a message

        Args:
            message (str): The message to process

        Returns:
            None

        """
        print("HELLLOOOO")
        print(f"LLM: {self.llm}")
        # add user message to chat history
        self.add_chat_history(role="user", message=message)
        # log the message
        logger.info(f"process_message called with message: {message}")
        # stream the response
        stream = self.llm.responses.create(
            model=self.model_name,
            input=self.chat_history,
            tools=self.tools,
            tool_choice="auto",
            stream=True,
        )

        # keep track of tool calls
        tool_calls = {}

        # initial call
        for event in stream:
            print(
                f"\n[DEBUG EVENT] type={event.type}, idx={getattr(event, 'output_index', None)}, delta={getattr(event, 'delta', None)}"
            )

            # if there is text, print it
            if event.type == "response.output_text.delta":
                # yield the text
                yield json.dumps({"type": "init_response", "text": event.delta})
                logger.info(f"response.output_text.delta: {event.delta}")
                print(event.delta, end="", flush=True)
            # if there is no text, print a newline
            elif event.type == "response.output_text.done":
                print()

            # else if there is a tool call
            # name of the tool is in response.output.item
            elif event.type == "response.output_item.added":
                # output_index is the index of the tool call
                # because they come in chunks we need to keep track of the index
                idx = getattr(event, "output_index", 0)
                if idx not in tool_calls:
                    # if the index is not in the tool calls dict, add it
                    tool_calls[idx] = {
                        "name": None,
                        "arguments_fragments": [],
                        "arguments": None,
                        "done": False,
                    }
                    logger.info(f"[DEBUG] Added tool call slot idx={idx}")
                tool_calls[idx]["name"] = event.item.name  # get the name of the tool

            # else if there is a tool argument (they come in chunks as strings)
            elif event.type == "response.function_call_arguments.delta":
                # output_index is the index of the tool call
                idx = getattr(event, "output_index", 0)
                if idx not in tool_calls:  # if not in the tool calls dict, add it
                    tool_calls[idx] = {
                        "name": None,
                        "arguments_fragments": [],
                        "arguments": None,
                        "done": False,
                    }
                # delta (arguments) may be a string fragment so we add it
                args_frag = (
                    event.delta
                    if isinstance(event.delta, str)
                    else json.dumps(event.delta)
                )
                # add up the argument strings for the tool call
                tool_calls[idx]["arguments_fragments"].append(args_frag)
                logger.info(f"[DEBUG] Arg fragment for idx={idx}: {args_frag}")

            # else if the tool call is done
            elif event.type == "response.function_call_arguments.done":
                # output_index is the index of the tool call
                idx = getattr(event, "output_index", 0)
                # if the index is not in the tool calls dict, add it
                if idx not in tool_calls:
                    tool_calls[idx] = {
                        "name": None,
                        "arguments_fragments": [],
                        "arguments": None,
                        "done": False,
                    }
                # mark the tool call as done
                tool_calls[idx]["done"] = True
                # join the argument fragments into a single string
                tool_calls[idx]["arguments"] = "".join(
                    tool_calls[idx]["arguments_fragments"]
                ).strip()
                # log statment for tool done
                logger.info(f"[DEBUG] Marked tool idx={idx} done")

        logger.info(f"TOOL CALLS: {tool_calls}")

        # Execute the tool calls
        for tool_idx, tool in tool_calls.items():
            tool_name = tool["name"]
            args_str = tool["arguments"]

            if not tool_name:  # if tool name is None
                print(f"[DEBUG] No tool name for idx={tool_idx}, skipping")
                continue  # continue

            # try to parse the arguments
            try:
                parsed_args = json.loads(args_str)
            except json.JSONDecodeError:
                parsed_args = {}
                logger.info(
                    f"[DEBUG] Failed to parse args for idx={tool_idx}, using empty dict"
                )
            # yield the tool call
            yield json.dumps(
                {"type": "tool_use", "tool_name": tool_name, "tool_input": parsed_args}
            )
            try:
                result = self.execute_tool(tool_name, parsed_args)
            except TypeError:
                result = self.execute_tool(tool_name, parsed_args.get("location"))

            logger.info(f"[DEBUG] Tool result for idx={tool_idx}: {result}")
            parsed_result = self.parse_result(tool_name, result)
            logger.info(f"[DEBUG] Tool result for idx={tool_idx}: {parsed_result}")

            # yield the tool result
            yield json.dumps(
                {
                    "type": "tool_result",
                    "tool_name": tool_name,
                    "tool_input": parsed_args,
                    "tool_result": parsed_result,
                }
            )
            logger.info(f"[DEBUG] Tool result for idx={tool_idx}: {parsed_result}")

            # Add the tool call result to the chat history
            self.chat_history.append(
                {
                    "role": "assistant",
                    "content": f"TOOL_NAME: {tool_name}, RESULT: {parsed_result}",
                }
            )

        # Get the final answer
        # IF we called tools to get updated information then we must form a final response
        if tool_calls:
            logger.info("[DEBUG] Calling model for final answer...")
            # Call the model again with the tool call results
            final_stream = self.llm.responses.create(
                model=self.model_name,
                input=self.chat_history,
                stream=True,
            )

            print("Assistant (final): ", end="", flush=True)
            # Stream partial text
            for ev in final_stream:
                logger.info(
                    f"\n[DEBUG EVENT FINAL] type={ev.type}, delta={getattr(ev, 'delta', None)}"
                )
                # if there is text, print it/yield it
                if ev.type == "response.output_text.delta":
                    yield json.dumps({"type": "final_response", "text": ev.delta})
                    logger.info(ev.delta)
                    print(ev.delta, end="", flush=True)
                # if there is no text, print a newline
                elif ev.type == "response.output_text.done":
                    print()
        pass
