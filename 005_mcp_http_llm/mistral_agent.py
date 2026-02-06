import asyncio
import os
import json
from mistralai import Mistral
from mcp_interface import MCPClientManager
from dotenv import load_dotenv
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
model = "mistral-small-latest"

async def run_chat():
    client_mistral = Mistral(api_key=MISTRAL_API_KEY)
    
    # Historique de la conversation
    messages = [{"role": "system", "content": "Tu es un lanceur de dé à 6 faces."}]

    print("Connexion au serveur MCP...")
    
    async with MCPClientManager() as mcp_client:
        # 1. On récupère les définitions des outils
        tools_def = await mcp_client.get_tools_for_mistral()
        print(f"{len(tools_def)} outils chargés et prêts pour Mistral.\n")
        print("💬 Vous pouvez commencer à discuter (tapez 'quit' pour quitter).")

        while True:
            user_input = input("\nVous: ")
            if user_input.lower() in ["quit", "exit"]:
                break

            # Ajout du message utilisateur à l'historique
            messages.append({"role": "user", "content": user_input})

            # 2. Premier appel à Mistral avec les outils disponibles

            # chat.complete_async() est la fonction qui envoie l'historique de conversation
            #  à Mistral et attend sa réponse, sans bloquer tout le programme pendant l'attente
            # une "completion" signifie "compléter la conversation"
            # async permet de gérer d'autres tâches MCP en meme temps 
            # tool_choice="auto" : C'est le paramètre qui rend l'agent intelligent.
            # Cela dit à Mistral : "Regarde la question de l'utilisateur. Si tu peux
            #  répondre par du texte, fais-le. Si tu as besoin d'un outil
            #  pour répondre (ex: 'lance un dé'), choisis l'outil."

            response = await client_mistral.chat.complete_async(
                model=model,
                messages=messages,
                tools=tools_def,
                tool_choice="auto" 
            )

            # On récupère le choix de l'assistant
            choice = response.choices[0].message
            messages.append(choice) # On garde la trace de la réponse de l'assistant

            # 3. Vérification : Mistral veut-il utiliser un outil ?
            if choice.tool_calls:
                for tool_call in choice.tool_calls:
                    f_name = tool_call.function.name
                    f_args = json.loads(tool_call.function.arguments)
                    
                    print(f"🤖 Mistral décide d'appeler : {f_name} avec {f_args}")
                    
                    # 4. Exécution réelle via notre client MCP
                    try:
                        tool_result = await mcp_client.call_tool(f_name, f_args)
                        print(f"Retour de l'outil : {tool_result}")
                        
                        # 5. On renvoie le résultat de l'outil à Mistral
                        messages.append({
                            "role": "tool",
                            "name": f_name,
                            "content": str(tool_result),
                            "tool_call_id": tool_call.id
                        })
                    except Exception as e:
                        print(f"Erreur outil : {e}")
                        messages.append({
                            "role": "tool",
                            "name": f_name,
                            "content": f"Error: {str(e)}",
                            "tool_call_id": tool_call.id
                        })

                # 6. Second appel à Mistral pour qu'il formule sa réponse finale
                # maintenant qu'il a le résultat de l'outil
                final_response = await client_mistral.chat.complete_async(
                    model=model,
                    messages=messages
                )
                final_answer = final_response.choices[0].message.content
                print(f"Mistral: {final_answer}")
                messages.append(final_response.choices[0].message)

            else:
                # Pas d'outil appelé, réponse simple
                print(f"Mistral: {choice.content}")

if __name__ == "__main__":
    asyncio.run(run_chat())