import logging
import random
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MCP_NAME = "Serveur MCP HTTP lanceur de dé"
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
    @mcp.tool()
    def roll_dice() -> int:
        """Lance un dé à 6 faces et retourne le résultat."""
        result = random.randint(1, 6)
        logger.info(f"Lancé de dé : {result}")
        return result
    
    return mcp

def main():
    """Point d'entrée principal."""
    try:
        mcp = create_server()
        logger.info(f"{MCP_NAME} prêt sur http://localhost:8000/mcp")
        mcp.run(transport="streamable-http")
    except Exception as e:
        logger.error(f"Erreur: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()