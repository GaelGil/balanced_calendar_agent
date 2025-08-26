from app.chat.utils.tool_definitions import tool_definitions
from app.chat.utils.prompts import AGENT_PROMPT
from app.extensions import db
from app.calendar.services import CalendarService
from app.chat.models import ChatSession, ChatMessage
from app.chat.utils.tools import analyze_events
from app.chat.utils.formaters import (
    parse_composio_event_search_results,
    format_free_slots_to_markdown,
    format_events_to_markdown,
)
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
from composio import Composio
import os
import logging
import json
import traceback

# logging stuff
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
# load env
load_dotenv(Path("../../.env"))


class ChatService:
    def __init__(self, user_id, calendar_service: CalendarService, session_id=None):
        self.calendar_service = calendar_service
        self.user_id = user_id
        self.composio_user_id = "0000-1111-2222"
        self.session_id = session_id
        self.chat_session = None
        self.model_name = "gpt-4.1-mini"
        self.tools = tool_definitions
        self.composio = Composio()
        self.llm: OpenAI = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # with self.app.app_context():
        # Load existing chat session if session_id is provided
        if self.session_id:
            self.chat_session = ChatSession.query.get(self.session_id)
        # If no session exists, create a new one
        if not self.chat_session:
            self.chat_session = ChatSession(user_id=self.user_id)
            db.session.add(self.chat_session)
            db.session.commit()
            self.session_id = self.chat_session.id

        # Initialize chat_history from DB
        self.chat_history = self.get_chat_history()

        # Add initial developer prompt if history is empty
        if not self.chat_history:
            self.add_chat_history(role="developer", message=AGENT_PROMPT)
            self.chat_history = self.get_chat_history()

    def add_chat_history(self, role: str, message: str):
        chat_message = ChatMessage(
            session_id=self.chat_session.id, role=role, content=message
        )
        db.session.add(chat_message)
        db.session.commit()
        self.chat_history = self.get_chat_history()

    def get_chat_history(self):
        return [
            {"role": msg.role, "content": msg.content}
            for msg in ChatMessage.query.filter_by(
                session_id=self.chat_session.id
            ).order_by(ChatMessage.id)
        ]

    def process_message_stream(self, message: str):
        """Processes a message

        Args:
            message (str): The message to process

        Returns:
            None

        """
        # add user message to chat history
        self.add_chat_history(role="user", message=message)
        # self.update_chat_history()
        logger.info(f"[DEBUG] CHAT HISTORY BEFORE LLM CALL: {self.get_chat_history()}")
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
        init_response = ""
        # initial call
        for event in stream:
            logger.info(
                f"\n[DEBUG EVENT] type={event.type}, idx={getattr(event, 'output_index', None)}, delta={getattr(event, 'delta', None)}"
            )

            # if there is text, print it
            if event.type == "response.output_text.delta":
                # yield the text
                yield json.dumps({"type": "init_response", "text": event.delta})
                logger.info(f"response.output_text.delta: {event.delta}")
                init_response += event.delta
                # print(event.delta, end="", flush=True)
            # if there is no text, print a newline
            elif event.type == "response.output_text.done":
                print()

            # else if there is a tool call
            # name of the tool is in response.output.item
            elif (
                event.type == "response.output_item.added"
                and event.item.type == "function_call"
            ):
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
        self.add_chat_history(role="assistant", message=init_response)

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

            parsed_result = self.parse_tool_result(tool_name, result)
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

            # Add the tool call result to the chat history
            self.add_chat_history(
                role="assistant",
                message=f"TOOL_NAME: {tool_name}, RESULT: {parsed_result}",
            )
            self.chat_history = self.get_chat_history()

        logger.info(f"[DEBUG] CHAT HISTORY AFTER TOOL RUN: {self.get_chat_history()}")
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
            logger.info(
                f"[DEBUG] CHAT HISTORY AFTER FINAL LLM CALL: {self.get_chat_history()}"
            )

            final_response = ""

            for ev in final_stream:
                logger.info(
                    f"\n[DEBUG EVENT FINAL] type={ev.type}, delta={getattr(ev, 'delta', None)}"
                )
                # if there is text, print it/yield it
                if ev.type == "response.output_text.delta":
                    yield json.dumps({"type": "final_response", "text": ev.delta})
                    logger.info(f"response.output_text.delta: {ev.delta}")
                    final_response += ev.delta

                    # print(ev.delta, end="", flush=True)
                # if there is no text, print a newline
                elif ev.type == "response.output_text.done":
                    print()
            self.add_chat_history(role="assistant", message=final_response)

        pass

    def parse_tool_result(self, tool_name: str, tool_result: dict):
        """Parse the tool result

        Args:
            tool_name (str): The name of the tool
            tool_result (str): The result of the tool

        Returns:
            Any: The parsed result

        """
        if tool_name == "analyze_events":
            parsed_result = tool_result.model_dump()
            logger.info("Parsing analyze events result")
        elif tool_name == "get_events_in_month":
            parsed_result = format_events_to_markdown(tool_result)
            logger.info("Parsing get events in month result")
        elif tool_name == "calender_availability":
            parsed_result = format_free_slots_to_markdown(tool_result)
            logger.info("Parsing calender availability result")
        elif "event" in tool_name.lower():
            parsed_result = parse_composio_event_search_results(tool_result)
            logger.info("Used event search parser")
        return parsed_result

    def execute_tool(self, tool_name: str, tool_args: dict):
        """Execute a tool

        Args:
            tool_name (str): The name of the tool to execute
            tool_args (dict): The arguments to pass to the tool

        Returns:
            Any: The result of the tool

        """
        logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
        logger.info(
            f"Tool Name Type {type(tool_name)}, Tool Args Type {type(tool_args)}"
        )
        try:
            if tool_name == "analyze_events":
                result = analyze_events(tool_args["events"])
            elif tool_name == "get_events_in_month":
                result = self.calendar_service.get_events_in_month()
            else:
                composio = Composio()
                result = composio.tools.execute(
                    slug=tool_name,
                    user_id=self.composio_user_id,
                    arguments=tool_args,
                )
            logger.info(f"CHAT HISTORY: {self.chat_history}")
            logger.info(f"Tool result: {result}")
            logger.info(f"Result type: {type(result)}")
            return result
        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            logger.info("!!! TOOL EXECUTION EXCEPTION !!!")
            logger.info(f"Error type: {type(e).__name__}")
            logger.info(f"Error message: {str(e)}")
            logger.info(f"Traceback: {traceback.format_exc()}")

            return {"error": error_msg}
