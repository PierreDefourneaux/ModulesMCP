import asyncio
import logging
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_dice_client():
    """
    Client MCP pour interagir avec le serveur de lancé de dé.
    """
    server_url = "http://localhost:8000/mcp"
    
    logger.info(f"Connexion au serveur MCP sur {server_url}...")
    async with streamable_http_client(server_url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            logger.info("Session initialisée avec succès.")
            tools_response = await session.list_tools()
            available_tools = [t.name for t in tools_response.tools]
            logger.info(f"Outils disponibles sur le serveur : {available_tools}")
            if "roll_dice" in available_tools:
                logger.info("Déclenchement du lancer de dé...")
                result = await session.call_tool("roll_dice")
                if hasattr(result, "structuredContent") and result.structuredContent:
                    valeur = result.structuredContent.get("result")
                    print(f"\nRésultat du dé (via structuredContent) : {valeur}")
                else:
                    text_result = result.content.text
                    print(f"\nRésultat du dé (via content) : {text_result}")
            else:
                logger.error("L'outil 'roll_dice' n'a pas été trouvé.")

if __name__ == "__main__":
    try:
        asyncio.run(run_dice_client())
    except Exception as e:
        logger.error(f"Erreur du client : {e}")