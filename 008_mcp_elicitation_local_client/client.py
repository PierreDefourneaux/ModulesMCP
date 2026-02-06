import asyncio
from typing import Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import mcp.types as types

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

async def run_client():
    server_params = StdioServerParameters(command="uv", args=["run","server.py"], env=None)
    async with stdio_client(server_params) as (read, write):
        # Initialisation de la session avec le callback d'élicitation
        # Le SDK MCP Python gère automatiquement la déclaration des capacités 
        # si le callback est fourni à l'instanciation.
        async with ClientSession(read, write, elicitation_callback=handle_elicitation) as session:
            await session.initialize()
            print("Client connecté et prêt.")
            print("\nAppel de l'outil 'roll_dice'...")
            try:
                result = await session.call_tool("roll_dice")
                # Affichage du résultat final envoyé par le serveur après l'élicitation
                for content in result.content:
                    if content.type == "text":
                        print(f"\n[RÉSULTAT FINAL] : {content.text}")
            except Exception as e:
                print(f"Erreur lors de l'appel : {e}")
if __name__ == "__main__":
    asyncio.run(run_client())