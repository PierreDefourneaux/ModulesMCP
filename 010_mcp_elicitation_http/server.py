import random
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP, Context
import logging

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

mcp = FastMCP("Serveur HTTP Elicitation", host="0.0.0.0", port=8000)
class ConfirmationRequest(BaseModel):
    """Schéma pour demander une confirmation à l'utilisateur."""
    confirme_dice: bool = Field(description="Mettre à True pour lancer le dé, False pour annuler")

@mcp.tool()
async def roll_dice(ctx: Context) -> str:
    """Lance un dé à 6 faces après confirmation de l'utilisateur."""
    
    result = await ctx.elicit(
        message="Tu veux vraiment que je lance un dé ?",
        schema=ConfirmationRequest
    )

    if result.action == "accept" and result.data:
        if result.data.confirme_dice:
            valeur = random.randint(1, 6)
            return f"Le dé a été lancé ! Résultat : {valeur}"
        else:
            return "Lancement annulé par l'utilisateur."
    
    return "Action annulée ou refusée."

if __name__ == "__main__":
    mcp.run(transport="streamable-http")