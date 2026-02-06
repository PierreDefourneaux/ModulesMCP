import asyncio
import logging
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_interactive_cli():
    """
    Client CLI interactif pour tester le serveur de dé.
    """
    # L'URL par défaut exposée par l'API FastMCP sur le port 8000
    server_url = "http://localhost:8000/mcp"
    
    logger.info(f"\n--- Connexion au serveur MCP: {server_url} ---")

    try:
        # Établissement du transport HTTP Streamable
        async with streamable_http_client(server_url) as (read_stream, write_stream, _):
            
            # Création de la session client
            async with ClientSession(read_stream, write_stream) as session:
                
                # Initialisation ("Handshake" protocolaire obligatoire)
                await session.initialize()
                logger.info("Session initialisée. Serveur prêt.")

                while True:
                    logger.info("\nOptions: [lancer] Lancer le dé | [q] Quitter")
                    choice = input("Votre choix > ").strip().lower()

                    if choice == 'q':
                        logger.info("Fermeture du client...")
                        break
                    
                    if choice == 'lancer':
                        logger.info("Appel de l'outil 'roll_dice'...")
                        # Appel de l'outil via le nom défini sur le serveur
                        # On ne passe pas d'arguments ici car roll_dice n'en attend pas
                        result = await session.call_tool("roll_dice")
                        # Analyse et affichage du résultat
                        # FastMCP encapsule les retours simples dans 'structuredContent'
                        if hasattr(result, "structuredContent") and result.structuredContent:
                            # Par défaut, un int est retourné comme {"result": valeur}
                            valeur = result.structuredContent.get("result")
                            logger.info(f">>> Résultat du serveur : {valeur}")
                        else:
                            logger.info(f">>> Résultat (text) : {result.content.text}")
                    else:
                        logger.info("Choix invalide, réessayez.")

    except Exception as e:
        logger.error(f"Erreur de connexion ou d'exécution : {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run_interactive_cli())
    except KeyboardInterrupt:
        pass