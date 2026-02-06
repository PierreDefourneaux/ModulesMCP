import random
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("elicitation_local_server")

# Définition du schéma de confirmation pour l'élicitation
class ConfirmationRequest(BaseModel):
    """Schéma pour demander une confirmation à l'utilisateur."""
    confirme_dice: bool = Field(description="Mettre à True pour lancer le dé, False pour annuler")

@mcp.tool()
async def roll_dice(ctx: Context) -> str:
    """Lance un dé à 6 faces après confirmation de l'utilisateur."""
    
    # Déclenchement de l'élicitation
    # Cette méthode met l'outil en pause et envoie la question au client
    result = await ctx.elicit(
        message="Tu veux vraiment que je lance un dé ?",
        schema=ConfirmationRequest
    )

    # Traitement de la réponse de l'utilisateur
    if result.action == "accept" and result.data:
        if result.data.confirme_dice:
            valeur = random.randint(1, 6)
            return f"Le dé a été lancé ! Résultat : {valeur}"
        else:
            return "Lancement annulé par l'utilisateur."
    
    return "Action annulée ou refusée."

if __name__ == "__main__":
    mcp.run()