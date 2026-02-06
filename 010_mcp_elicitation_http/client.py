import asyncio
import logging
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
import mcp.types as types

logging.basicConfig(level=logging.INFO)
file_handler = logging.FileHandler("mcp_client.log", mode="w")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
mcp_logger = logging.getLogger("mcp")
mcp_logger.setLevel(logging.DEBUG)
mcp_logger.addHandler(file_handler)
mcp_logger.propagate = False
logger = logging.getLogger("logs_applicatifs")

# Définition du callback d'élicitation
async def handle_elicitation(context, params: types.ElicitRequestParams) -> types.ElicitResult:
    """
    Ce callback est déclenché quand le serveur appelle ctx.elicit().
    params.message contient le message du serveur.
    params.requestedSchema contient le schéma JSON (ConfirmationRequest).
    """
    print(f"\n[SERVEUR DEMANDE] : {params.message}")
    # Dans un vrai client, on afficherait un formulaire à l'utilisateur ici.
    # Pour ce test, nous allons simuler la saisie en fonction du schéma reçu.
    # On vérifie si le schéma attend bien 'confirme_dice'
    schema = params.requestedSchema
    if schema and "confirme_dice" in schema.get("properties", {}):
        # On simule une réponse positive
        user_input = {"confirme_dice": True}
        print(f"[CLIENT RÉPOND] : Envoi de la donnée {user_input}")
        # On retourne un ElicitResult avec l'action 'accept'
        return types.ElicitResult(
            action="accept",
            content=user_input)
    # En cas de refus ou de problème
    return types.ElicitResult(action="cancel")

async def run_dice_client():
    """
    Client MCP pour interagir avec le serveur de lancé de dé.
    """
    server_url = "http://localhost:8000/mcp"
    
    logger.info(f"Connexion au serveur MCP sur {server_url}...")

    async with streamable_http_client(server_url) as (read_stream, write_stream, _):
        
        async with ClientSession(read_stream, write_stream, elicitation_callback=handle_elicitation) as session:
        
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