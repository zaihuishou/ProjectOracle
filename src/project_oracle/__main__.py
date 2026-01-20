"""Entry point for running ProjectOracle as an MCP server.

This allows running the server with:
    python -m project_oracle
"""

import asyncio
from .server import main

if __name__ == "__main__":
    asyncio.run(main())
