import asyncio
import json
from ollama import AsyncClient
from mcp_interface import MCPClientManager
# Sur mon PC je suis limité à des petits modèles
# MODEL_NAME = "llama3.1:latest"
MODEL_NAME = "qwen2.5:3b"
# MODEL_NAME = "gemma3:latest"
# MODEL_NAME = "ollama:latest"
# MODEL_NAME = "llama3.2:latest"
async def run_chat():
    # Client Ollama (par défaut sur http://localhost:11434)
    client_ollama = AsyncClient()

    # Les petits modèles ollama ont besoin qu'on les cadre pour essayer de limiter les hallucinations.
    system_instruction = """
        Tu es un assistant intelligent. Tu as accès à des outils spécifiques via MCP.

        RÈGLES STRICTES :
        1. N'utilise un outil QUE si la demande de l'utilisateur correspond exactement à la fonction de l'outil.
        2. NE JAMAIS INVENTER d'outils. Utilise uniquement ceux fournis dans la liste.
        3. Si l'utilisateur te dit "bonjour", "salut" ou pose une question générale (ex: recette de cuisine), RÉPONDS SIMPLEMENT par du texte. N'appelle PAS d'outil.
        4. Si aucun outil ne correspond, dis simplement que tu ne peux pas faire cette action, mais essaie d'aider par texte.

        Comportement attendu :
        - User: "Lance un dé" -> CALL TOOL roll_dice
        - User: "Salut" -> TEXTE "Bonjour ! Comment puis-je vous aider ?"
        - User: "Cuis des pâtes" -> TEXTE "Je n'ai pas d'outil pour ça, mais voici la recette..."
        """
    # Historique de la conversation
    messages = [{"role": "system", "content": system_instruction}]

    print(f"Connexion au serveur MCP (Modèle local : {MODEL_NAME})...")
    
    async with MCPClientManager() as mcp_client:
        # On récupère les outils
        tools_def = await mcp_client.get_tools_for_ollama()
        print(f"{len(tools_def)} outils chargés.\n")
        print("💬 Vous pouvez discuter avec votre LLM Local (tapez 'quit').")

        while True:
            user_input = input("\nVous: ")
            if user_input.lower() in ["quit", "exit"]:
                break

            messages.append({"role": "user", "content": user_input})

            # Premier appel à Ollama
            response = await client_ollama.chat(
                model=MODEL_NAME,
                messages=messages,
                tools=tools_def,
            )

            # Ollama renvoie un dictionnaire, pas un objet. On accède via ['cle']
            message = response['message']
            messages.append(message) # On ajoute la réponse de l'assistant à l'historique

            # Vérification des outils
            # Dans la lib Ollama, 'tool_calls' est une clé du dictionnaire message
            if message.get('tool_calls'):
                valid_tool_names = [t['function']['name'] for t in tools_def]
                for tool in message['tool_calls']:
                    f_name = tool['function']['name']
                    # VÉRIFICATION DE SÉCURITÉ
                    if f_name not in valid_tool_names:
                        print(f"Tentative d'hallucination bloquée : {f_name}")
                        messages.append({
                            "role": "tool",
                            "content": f"Erreur : L'outil '{f_name}' n'existe pas. N'invente pas d'outils.",
                            "name": f_name
                        })
                        continue # On passe à l'outil suivant ou on arrête là
                    f_args = tool['function']['arguments']
                    
                    print(f"🤖 Llama décide d'appeler : {f_name} avec {f_args}")
                    
                    try:
                        # Exécution via MCP
                        tool_result = await mcp_client.call_tool(f_name, f_args)
                        print(f"Retour de l'outil : {tool_result}")
                        
                        # Injection du résultat
                        messages.append({
                            "role": "tool",
                            "content": str(tool_result),
                            # Ollama n'a pas toujours besoin d'ID, mais c'est plus propre
                            # S'il n'y a pas d'ID, on peut parfois l'omettre selon le modèle
                            "name": f_name 
                        })
                    except Exception as e:
                        print(f"Erreur outil : {e}")
                        messages.append({
                            "role": "tool",
                            "content": f"Error: {str(e)}",
                            "name": f_name
                        })

                # Second appel pour la synthèse finale
                final_response = await client_ollama.chat(
                    model=MODEL_NAME,
                    messages=messages,
                    # On ne repasse pas les tools au 2eme tour pour éviter une boucle infinie
                    # (bien que certains modèles le supportent)
                    # tools=tools_def 
                )
                
                final_answer = final_response['message']['content']
                print(f"Llama: {final_answer}")
                messages.append(final_response['message'])

            else:
                # Réponse simple sans outil
                print(f"Llama: {message['content']}")

if __name__ == "__main__":
    asyncio.run(run_chat())