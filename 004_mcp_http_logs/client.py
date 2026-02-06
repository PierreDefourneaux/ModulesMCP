import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
import logging

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

async def test_tool_execution():
    server_url = "http://localhost:8000/mcp"
    
    async with streamable_http_client(server_url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Découverte des outils
            # Cette méthode interroge le serveur et renvoie un objet ListToolsResult
            available_tools = await session.list_tools()
            # L'objet tools_response contient une liste d'objets 'tools'
            # (je peux printer car je suis en http )
            print(f"--- {len(available_tools.tools)} outil(s) trouvé(s) ---")
            
            for tool in available_tools.tools:
                print(f"Nom de l'outil : {tool.name}")
                print(f"Description    : {tool.description}")
                print(f"Schéma d'entrée : {tool.inputSchema}")

            print("[*] Tentative d'appel de 'roll_dice'...")
            try:
                # On passe les arguments sous forme de dictionnaire
                result = await session.call_tool("roll_dice", arguments={})
                
                # FastMCP renvoie souvent des résultats structurés par défaut
                if hasattr(result, "structuredContent") and result.structuredContent:
                    valeur = result.structuredContent.get("result")
                    print(f"Résultat structuré reçu : {valeur}")
                else:
                    # Fallback sur le contenu textuel classique
                    print(f"Résultat texte reçu : {result.content.text}")
                    
            except Exception as e:
                print(f"Erreur lors de l'exécution : {e}")

if __name__ == "__main__":
    asyncio.run(test_tool_execution())