#!/usr/bin/env python3
"""
Gmail MCP Server with OAuth Authentication using FastMCP
Provides email fetching capabilities through MCP protocol
"""
import sys
import logging

from app import mcp
import app.handlers
from app.utils.logging import setup_logging


def main():
    """Start Gmail MCP server."""
    try:
        logger = setup_logging()
        logger.info("Starting Gmail MCP server")
        logger.info("Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET env vars")
        logger.info("Run authenticate_gmail first")
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        logging.getLogger('gmail-mcp').info("Server shutdown")
    except Exception as e:
        logging.getLogger('gmail-mcp').error(f"Startup failed: {str(e)}")
        sys.exit(1)
    finally:
        logging.getLogger('gmail-mcp').info("Server shutdown complete")

if __name__ == "__main__":
    main()  