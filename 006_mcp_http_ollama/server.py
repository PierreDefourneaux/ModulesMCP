import logging
import random
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)

file_handler = logging.FileHandler("mcp_server.log", mode="w")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(message)s")
file_handler.setFormatter(formatter)
mcp_logger = logging.getLogger("mcp")
mcp_logger.setLevel(logging.DEBUG)
mcp_logger.addHandler(file_handler)
mcp_logger.propagate = False
logger = logging.getLogger(__name__)

MCP_NAME = "Server_Ollama"

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
        logger.info(
            f"{MCP_NAME} prêt sur http://localhost:8000/mcp")
        mcp.run(transport="streamable-http")
    except Exception as e:
        logger.error(f"Erreur: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()