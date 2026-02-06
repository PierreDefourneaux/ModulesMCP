import asyncio
import sys
from typing import Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import mcp.types as types

# Le Callback interactif
async def handle_interactive_elicitation(context, params: types.ElicitRequestParams) -> types.ElicitResult:
    """
    Ce callback est déclenché par ctx.elicit() côté serveur.
    Il va lire le schéma et demander une saisie réelle à l'utilisateur.
    """
    print(f"\n--- INTERACTION REQUISE ---")
    print(f"Message du serveur : {params.message}")
    
    user_data = {}
    schema = params.requestedSchema
    
    # On parcourt les propriétés demandées dans le schéma JSON
    if schema and "properties" in schema:
        properties = schema["properties"]
        
        for prop_name, prop_info in properties.items():
            description = prop_info.get("description", prop_name)
            prop_type = prop_info.get("type")
            
            # Gestion interactive selon le type de donnée attendu par le serveur
            if prop_type == "boolean":
                # Pour roll_dice, on attend un booléen
                val = input(f"{description} (o/n) : ").lower().strip()
                user_data[prop_name] = val in ['o', 'oui', 'y', 'yes', 'true']
            
            elif prop_type == "string":
                user_data[prop_name] = input(f"{description} : ")
                
            elif prop_type in ["number", "integer"]:
                val = input(f"{description} : ")
                user_data[prop_name] = int(val) if prop_type == "integer" else float(val)

    # On retourne le résultat avec l'action 'accept' et les données saisies
    return types.ElicitResult(action="accept", content=user_data)

async def run_interactive_client():
    server_params = StdioServerParameters(command="uv", args=["run", "server.py"], env=None)
    print("Démarrage du client MCP...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write, elicitation_callback=handle_interactive_elicitation) as session:
            await session.initialize()
            print("Connecté au serveur de dé.")
            print("\nExécution de 'roll_dice'...")
            try:
                result = await session.call_tool("roll_dice")
                for content in result.content:
                    if content.type == "text":
                        print(f"\n[SERVEUR] : {content.text}")
            except Exception as e:
                print(f"\nErreur : {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run_interactive_client())
    except KeyboardInterrupt:
        pass