from flask import Blueprint, jsonify, request, Response  # type: ignore
from app.chat.services import ChatService  # type: ignore
from app.auth.decorators import login_required
import json

chat = Blueprint("chat", __name__)
chat_service = ChatService()


@chat.route("/message", methods=["POST"])
@login_required
def send_message():
    """Send a message to the AI agent and get a streaming response."""
    try:
        data = request.get_json()
        message = data.get("message")

        if not message:
            return jsonify({"error": "Message is required"}), 400

        # Get response from agent
        response_data = chat_service.process_message(message)

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": f"Failed to process message: {str(e)}"}), 500


@chat.route("/message/stream", methods=["POST"])
@login_required
def send_message_stream():
    """Send a message to the AI agent and get a streaming SSE response."""
    try:
        data = request.get_json()
        message = data.get("message")

        if not message:
            return jsonify({"error": "Message is required"}), 400

        def generate():
            try:
                # Stream blocks from the agent
                for event_data in chat_service.process_message_stream(message):
                    yield f"data: {json.dumps(event_data)}\n\n"
            except Exception as e:
                error_event = {"type": "error", "error": str(e)}
                yield f"data: {json.dumps(error_event)}\n\n"

        return Response(
            generate(),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control",
            },
        )

    except Exception as e:
        return jsonify({"error": f"Failed to process message: {str(e)}"}), 500


@chat.route("/health", methods=["GET"])
@login_required
def health_check():
    """Simple health check for the chat service."""
    return jsonify({"status": "healthy", "service": "chat"}), 200
