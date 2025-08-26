from flask import Blueprint, jsonify, request, stream_with_context, Response
from app.chat.services import ChatService  # type: ignore
from app.chat.decorators import chat_calendar_service_required
from app.auth.decorators import login_required
import sys
import json
import logging

logger = logging.getLogger(__name__)

chat = Blueprint("chat", __name__)


@chat_calendar_service_required
def generate_response(chat_service: ChatService, message: str):
    try:
        for chunk in chat_service.process_message(message):
            if isinstance(chunk, str):
                yield f"data: {chunk}\n\n"
                sys.stdout.flush()
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'text': str(e)})}\n\n"


@chat.route("/message/stream", methods=["POST"])
@login_required
def send_message_stream():
    """Send a message to the AI agent and get a streaming SSE response."""
    print("send_message_stream called")
    try:
        data = request.get_json()
        message = data.get("message")

        if not message:
            return jsonify({"error": "Message is required"}), 400

        return Response(
            stream_with_context(generate_response(message)),
            content_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )
    except Exception as e:
        return jsonify({"error": f"Failed to process message: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Failed to process message: {str(e)}"}), 500


@chat.route("/health", methods=["GET"])
@login_required
def health_check():
    """Simple health check for the chat service."""
    return jsonify({"status": "healthy", "service": "chat"}), 200
