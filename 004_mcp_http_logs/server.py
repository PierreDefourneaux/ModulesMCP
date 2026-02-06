# ATTENTION QUAND ON LOG LE SERVEUR MCP :
# stdio et print() cassent le protocole, ça interfère avec les flux de données,
# ça les corromp, ce qui constitue un argument en faveur de l'utilsation de 
# la couche de transport streamable-http plutôt que STDIO

import logging
import random
from mcp.server.fastmcp import FastMCP, Context

# 1. On configure le Root Logger de manière minimaliste vers la console
logging.basicConfig(level=logging.INFO)

# 2. On crée un handler spécifique pour le fichier JSON-RPC
file_handler = logging.FileHandler("mcp_server.log", mode="w")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(message)s")
file_handler.setFormatter(formatter)

# 3. On cible UNIQUEMENT le logger du SDK MCP
mcp_logger = logging.getLogger("mcp")
mcp_logger.setLevel(logging.DEBUG)
mcp_logger.addHandler(file_handler)
mcp_logger.propagate = False  # Empêche de polluer la console avec le DEBUG du SDK

# 4. Le logger applicatif reste propre
logger = logging.getLogger(__name__) # Celui-ci ne loggera PAS dans le fichier

MCP_NAME = "Serveur MCP HTTP avec logs JSON RPC"

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
        logger.info(f"Message pour la console seulement : lancé de dé : {result}")
        return result
    
    @mcp.tool()
    async def trouver_le_MCP_Session_Id(ctx: Context):
        return f"ID de client : {ctx.client_id}"
    
    @mcp.tool()
    async def inspecter_le_contexte(ctx: Context) -> str:
        # On regarde ce qu'il y a vraiment dans l'objet
        details = {
        "request_context": str(ctx.request_context),
        "session": str(ctx.session) if hasattr(ctx, 'session') else "Pas de session",
        "meta": str(ctx.meta) if hasattr(ctx, 'meta') else "Pas de meta"
        }
        return f"Détails du contexte : {details}"
    
    @mcp.tool()
    async def fouiller_dans_les_headers(ctx: Context) -> str:
        """Affiche les headers HTTP et les paramètres de l'URL brute."""
        if not hasattr(ctx.request_context, 'request'):
            return "Pas d'objet 'request' trouvé (es-tu en mode Stdio ?)"
        request = ctx.request_context.request
        headers = dict(request.headers)
        query_params = dict(request.query_params)
        client_ip = request.client.host if request.client else "Inconnu"
        rapport = (
            f"--- INFOS CONNEXION ---\n"
            f"IP Client : {client_ip}\n"
            f"URL appel : {request.url}\n\n"
            f"--- QUERY PARAMS ---\n"
            f"{query_params}\n\n"
            f"--- HEADERS HTTP ---\n"
        )
        for key, value in headers.items():
            rapport += f"{key}: {value}\n"
        return rapport
    return mcp

def main():
    """Point d'entrée principal."""
    try:
        mcp = create_server()
        logger.info(
            f"Message pour la console seulement:{MCP_NAME} prêt sur http://localhost:8000/mcp")
        mcp.run(transport="streamable-http")
    except Exception as e:
        logger.error(f"Erreur: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()