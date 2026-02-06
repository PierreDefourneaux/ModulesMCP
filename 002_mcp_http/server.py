import logging
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MCP_NAME = "Serveur MCP HTTP minimal sans tool"
def create_server() -> FastMCP:
    """
    Crée et configure le serveur MCP.
    """
    mcp = FastMCP(
        MCP_NAME,
        stateless_http=True,
        json_response=True,
        host="0.0.0.0",
        port=8000
    )
    return mcp

def main():
    """Point d'entrée principal."""
    try:
        mcp = create_server()
        logger.info(f"{MCP_NAME} créé !")
        mcp.run(transport="streamable-http")
    except Exception as e:
        logger.error(f"Erreur : {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()