from flask import Blueprint, jsonify, request, Response  # type: ignore

from app.chat.services import ChatService  # type: ignore
from app.chat.decorators import chat_calendar_service_required
from app.auth.decorators import login_required
import json
import logging

logger = logging.getLogger(__name__)

chat = Blueprint("chat", __name__)


def generate(message: str, chat_service):
    print(f"process_message called with message: {message}")
    try:
        for chunk in chat_service.process_message_stream(message):
            if isinstance(chunk, str):
                yield f"data: {chunk}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'text': str(e)})}\n\n"


@chat.route("/message/stream", methods=["POST"])
@login_required
@chat_calendar_service_required
def send_message_stream(chat_service: ChatService):
    """Send a message to the AI agent and get a streaming SSE response."""
    print("send_message_stream called")
    try:
        data = request.get_json()
        message = data.get("message")
        print(data)
        print(message)
        logger.info(f"Calendar service type: {type(chat_service.calendar_service)}")

        if not message:
            return jsonify({"error": "Message is required"}), 400

        return Response(
            generate(message=message, chat_service=chat_service),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "http://localhost:5173",
                "Access-Control-Allow-Headers": "Cache-Control",
                "Access-Control-Allow-Credentials": "true",
            },
        )

    except Exception as e:
        return jsonify({"error": f"Failed to process message: {str(e)}"}), 500


@chat.route("/health", methods=["GET"])
@login_required
def health_check():
    """Simple health check for the chat service."""
    return jsonify({"status": "healthy", "service": "chat"}), 200
