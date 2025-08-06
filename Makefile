# Simple Makefile for backend application using uv


# Install dependencies using uv
.PHONY: install
install:
	@echo "Installing dependencies with uv..."
	.venv/bin/uv sync

# Run the application
.PHONY: run
run:
	@echo "Starting application..."
	.venv/bin/python main.py


.PHONY: mcp
mcp:
	@echo "Starting application..."
	.venv/bin/python -m app.chat.agent.mcp_client_server.server
# IF running locally uncomment for database setup
# 	flask db upgrade
# 	.venv/bin/python seed.py