# Comprendre le Model Context Protocol

## Table des matières
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [MCP local : stdio (001)](#001_mcp_local_tool)
4. [MCP distant : http (002)](#002_mcp_http)
5. [MCP distant avec tool (003)](#003_mcp_http_tool)
6. [MCP distant suivi à la trace avec des logs (004)](#004_mcp_http_logs)
7. [MCP distant chatbot (005)](#005_mcp_http_llm)
8. [MCP serveur distant, chatbot local pour le client (ollama) (006)](#006_mcp_http_ollama)
9. [MCP local élicitation pour inspecteur (007)](#007_mcp_elicitation_local_inspector)
10. [MCP local élicitation pour client python (008)](#008_mcp_elicitation_local_client)
11. [MCP local élicitation pour client python en CLI (009)](#009_mcp_elicitation_local_client_CLI)
11. [MCP distant élicitation pour client python (010)](#010_mcp_elicitation_http)
---

## Introduction
Bienvenue sur ***Modules MCP***.  
Le *Model Context Protocol*, publié en open source par Anthropic en novembre 2024, est souvent qualifié de « câble USB-C » pour les agents IA. Il standardise la façon dont les modèles se connectent aux données.  
L'objectif de ce dépôt est de faire comprendre ce qu'est exactement le MCP par la pratique. Je vous partage ma démarche d'apprentissage, au bout de laquelle j'ai été capable de construire intégralement un service d'IA agentique utilsant le MCP. J'entends par là, la création d'un serveur et d'un client MCP en python, avec le client exploité par un LLM, local (avec Ollama par exemple) ou distant (pour ma part c'est Mistral API).  
Pour cheminer dans cet apprentissage, j'ai décortiqué la [documentation du SDK python](https://github.com/modelcontextprotocol/python-sdk) et isolé chaque fonctionnalité dans un module de test indépendant.  
Je vous invite à aborder ces modules l'un après l'autre, dans la progression proposée ci-après.

## Installation
Installez UV sur votre ordinateur si ce n'est pas déjà fait.  
Puis git clone le repo.  
Quand vous travaillez avec le SDK mcp, utilisez `uv` pour installer les dépendances.  
La [documentation du SDK](https://github.com/modelcontextprotocol/python-sdk) le conseille.  
Et UV facilite le lancement de l'inspecteur.  
  
A propos de l'inspecteur : s'il ne libère pas le port après une fermeture brutale du navigateur, vos nouvelles tentatives de connexion échoueront.
Il faut libérer le port avec fuser -k <N°du port>/tcp

[🔝 Retour au sommaire](#table-des-matières)

## 001_MCP_local_tool
Dans ce dossier, lancez la commande
```bash
uv run mcp dev server.py
```
### Un module pour apprendre que ...
- ... dans le SDK MCP, il y a deux façons de coder : avec l'API de bas niveau **mcp.server.Server** ou avec **mcp.server.fastmcp**
- ... la classe **Fastmcp** est une surcouche simplifiée, qui permet de créer des serveurs facilement
- ... il existe trois **couches de transport**, ici on teste la couche locale **stdio**. Les deux autres sont **sse**, qui est obsolète et **streamable http**, qui la remplace.
- ... pour un protocole MCP, il faut un **serveur**, qui expose les outils, et un **client**, qui les utilise
- ... on peut tester son serveur dans l'**inspecteur** sans coder de client ni recourir à des services comme Claude Desktop :    
    - Lancer son serveur et ouvrir simultanément l'inspecteur dans son navigateur :  
        ```bash
        uv run mcp dev server.py
        ```
    -  Sinon, dans les cas plus tard où vous voudrez accéder à l'inspecteur pour un serveur déjà lancé :  
        ```bash
        npx -y @modelcontextprotocol/inspector
        ```
    Une fois dans l'inspecteur on connecte et on observe le début des logs dans *history*
- ... **les échanges se font en JSON** comme le montre la méthode **initialize**, le *"handshake"* protocolaire
- ... l'onglet Tools de l'inspecteur montre la méthode cruciale **tools/list** : le serveur renseigne le client sur ce qu'il peut faire, et on peut le voir dans les logs JSON
- ... l'onglet Tools permet d'appeler la méthode **tool/call** et de suivre ses logs en JSON

[🔝 Retour au sommaire](#table-des-matières)
## 002_MCP_http
Lancez le serveur et l'inspecteur en deux temps :
```bash
uv run server.py
```
et dans un autre terminal :
```bash
npx -y @modelcontextprotocol/inspector
```
Souvent, quand le mcp utilise la couche de transport http, l'inspecteur ne s'ouvre plus automatiquement avec uv run mcp dev. Notez donc bien cette dernière commande.  
Votre serveur tourne sur **http://0.0.0.0:8000/mcp**.  
Dans l'inspecteur, renseignez la nouvelle couche de transport si besoin (streamable http) pour que votre serveur soit trouvé.  
Il se peut aussi que vous deviez coller le token pris dans le terminal dans le champ "authentication".
### Un module pour apprendre que ... :
- ... pour faire un serveur utilisant la couche de transport distant http, on le construit avec
    ```python
    mcp = FastMCP(MCP_NAME, stateless_http=True, json_response=True, host="0.0.0.0", port=8000)
    ```
    où
    *"stateless_http=True"* et *"json_response=True"* sont recommandés par la documentation pour la scalabilité en production et la facilité de débogage,  
    et
    ```python
    mcp.run(transport="streamable-http")
    ```
- ...l'inspecteur, votre client, peut atteindre votre serveur **depuis une autre machine** en renseignant la vraie IP au lieu de "0.0.0.0"
- ... le transport **sse** est obsolète. Si toutefois vous voulez tester un *mcp.run(transport="sse")*, vous devrez changer l'URL 0.0.0.0:8000/mcp en 0.0.0.0:8000/sse dans l'interface de l'inspecteur

[🔝 Retour au sommaire](#table-des-matières)
## 003_MCP_http_tool
Testez un tool servi par la couche de transport http, depuis l'inspecteur :
```bash
uv run mcp dev server.py
```
Puis testez un véritable client personnalisé en python :
- lancez le serveur :
    ```bash
    uv run server.py
    ```
- dans un autre terminal lancez le client qui va déclencher le tool :
    ```bash
    uv run client.py
    ```
Enfin, testez un autre client personnalisé en python, cette fois en CLI :
Lancez votre serveur, puis :
```bash
uv run CLI_client.py
```
Avec *choice = input()*, ça commence à devenir un tout petit plus interactif...

### Un module pour comprendre que ...
- ... avec le SDK mcp, on construit un client avec
    ```python
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client
    ```
- ... les fonctions du client MCP sont asynchrones (elles utilisent asyncio) pour lui permettre de gérer des tâches de fond MCP, comme l'envoi de notifications de progression ou la réception de logs. Il faut pouvoir attendre des résultats complexes sans jamais "geler" l'application.  
- ... grâce à la librairie *logging* on a un peu plus de renseignements qu'avec l'inspecteur, on découvre notament la **version du protocole** négociée dans la methode **initialize**  
- ... plus besoin de Claude Desktop ou autre service d'IA payant pour tester son serveur MCP !

[🔝 Retour au sommaire](#table-des-matières)
## 004_MCP_http_logs
```bash
uv run server.py
```
```bash
uv run client.py
```
Observez les logs qui viennent de se créer dans les fichiers.
### Un module pour apprendre que...
- ... pour les serveurs MCP utilisant le **transport STDIO**, il est impératif de ne **jamais écrire quoi que ce soit sur la sortie standard (stdout)** en dehors des messages JSON-RPC du protocole. 
- ... en plus de la fonction **print()** en Python, on doit éviter toute bibliothèque ou tout framework qui envoie des messages, des bannières de démarrage ou des journaux sur **stdout** par défaut.
- ... il faut s'assurer que la bibliothèque de journalisation (comme logging en Python) est explicitement configurée pour écrire sur la **sortie d'erreur standard (stderr)** ou dans un **fichier**
- ... toute donnée supplémentaire envoyée sur stdout **corrompt le cadrage des messages JSON-RPC 2.0 et rompt le protocole**.
- ... quand on utilise le transport **Streamable HTTP, la restriction sur stdout ne s'applique plus**, car les journaux de la console n'interfèrent pas avec les réponses HTTP structurées. C'est l'un des arguments en faveur de cette couche de transport.  
- ... en faisant seulement écouter au logger qui écrit dans le fichier l'activité du SDK-MCP du programme, et en le paramétrant sur DEBUG, on récupère tous les logs JSON RPC du trafic MCP. On a le détail des méthodes pour toutes les requêtes/réponses...
    ```bash
    2026-01-12 10:01:14,167 - mcp.client.streamable_http - DEBUG - Sending client message: root=JSONRPCRequest(method='initialize', params={'protocolVersion': '2025-11-25', 'capabilities': {}, 'clientInfo': {'name': 'mcp', 'version': '0.1.0'}}, jsonrpc='2.0', id=0)
    ```
- ... une connexion mcp a un **cycle de vie** qui commence à la méthode **initialize** et qui se caractérise par un **MCP-Session-Id**. Pour le découvrir, observez les logs dans le terminal où vous avez lancé le client. Il ne faut pas le confondre avec l'ID de requete qu'on voit à la fin des lignes dans le fichier de logs JSON client (comme ci dessus *id=0* pour la requête initialize).
    ```bash
    Received POST message for sessionId d61de207-4e68-4dc7-aa06-d8e93aa76af3
    ```

[🔝 Retour au sommaire](#table-des-matières)
## 005_MCP_http_llm
Lancez votre serveur, comme d'habitude :  
```bash
uv run server.py
```
Puis lancez votre agent IA :
```bash
uv run mistral_agent.py
```
Cette fois, pas besoin de lancer un client. Ce fichier qu'on avait l'habitude de lancer en parallèle, est devenu "mcp_interface.py" et il est importé dans le script de l'agent. 
### Un module pour tester...
- ... une application MCP interactive avec un chatbot : c'est un LLM qui commande le client MCP.  
L'utilisateur renseigne le LLM sur ce qu'il voudrait faire. Le LLM connait les capacités du serveur car il utilise le client MCP comme interface. Donc quand il y a une opportunité dans un input de l'utilisateur (le langage naturel), le LLM déclenche un tool pour satisfaire cet input.  
 
- ... la gestion de contexte offerte par le standart MCP : l'agent est inteligent car il ne déclenche le tool que si c'est nécéssaire (tool_choice="auto" : c'est le paramètre qui rend l'agent Mistral intelligent). Il ne lance pas de dé quand on lui dit bonjour ou qu'on lui parle d'autre chose.
    ```console
    Connexion au serveur MCP...
    1 outils chargés et prêts pour Mistral.

    💬 Vous pouvez commencer à discuter (tapez 'quit' pour quitter).

    Vous: Salut !
    Mistral: Salut ! Comment puis-je vous aider aujourd'hui ?

    Vous: Ben je sais pas tu sais faire quoi?
    Mistral: Je peux lancer un dé à 6 faces pour toi. Veux-tu essayer ?

    Vous: Ah non !
    Mistral: D'accord, si tu changes d'avis, fais-le moi savoir !

    Vous: Bon ok allez vas-y
    🤖 Mistral décide d'appeler : roll_dice avec {}
    ✅ Retour de l'outil : 3
    Mistral: Le dé montre le chiffre 3. Tu veux relancer ?

    Vous: Non dis moi plutot comment jouer au UNO
    Mistral: Bien sûr ! Voici les règles de base du jeu UNO :

    Objectif du jeu
    Être le premier joueur à se débarrasser de toutes ses cartes.
    ...
    ... # plusieurs lignes où mistral explique les règles UNO sans lancé de dé ...
    ...
    Amusez-vous bien en jouant à UNO !
    ```

[🔝 Retour au sommaire](#table-des-matières)
## 006_MCP_http_ollama
```bash
uv run server.py
```
```bash
uv run ollama_agent.py
```
### Un module pour tester...
- ... des petits modèles qui tournent en local. Qwen2.5:3b s'en sort pas trop mal :  
    ```console
    uv run ollama_agent.py
    Connexion au serveur MCP (Modèle local : qwen2.5:3b)...
    1 outils chargés.

    💬 Vous pouvez discuter avec votre LLM Local (tapez 'quit').

    Vous: salut
    Llama: Bonjour ! Comment puis-je vous aider aujourd'hui ?

    Vous: je sais pas...
    Llama: Pas de soucis, je suis là pour vous aider. Avez-vous besoin de jouer à un petit jeu ou avez-vous une question spécifique que vous aimeriez poser ?

    Vous: Ah on peut jouer ?
    Llama: Ça dépend du type de jeu ! Je peux t'aider à jouer au dés, par exemple. Que voulons-nous lancer ? Un dé de 6 faces, d'un à six points, comme vous le savez.

    Vous: Ben lance un dé
    🤖 Llama décide d'appeler : roll_dice avec {}
    ✅ Retour de l'outil : 3
    Llama: Le résultat de votre dé est de 3 ! Enjoy your roll!
    ```
    ```console
    ollama show qwen2.5:3b
    Model
        architecture        qwen2     
        parameters          3.1B      
        context length      32768     
        embedding length    2048      
        quantization        Q4_K_M    

    Capabilities
        completion    
        tools
    ```
- ... llama3.1 ne s'en sort pas aussi bien :
    ```console
    uv run ollama_agent.py
    Connexion au serveur MCP (Modèle local : llama3.1)...
    1 outils chargés.

    💬 Vous pouvez discuter avec votre LLM Local (tapez 'quit').

    Vous: Salut
    🤖 Llama décide d'appeler : roll_dice avec {}
    ✅ Retour de l'outil : 4
    Llama: Vous venez de lancer un dé, et le résultat est 4 ! Qu'est-ce que vous voulez faire ensuite ?

    Vous: Mais je ne t'ai jamais demandé de lancer un dé !
    🤖 Llama décide d'appeler : roll_dice avec {'nFaces': 6}
    ✅ Retour de l'outil : 1
    Llama: Il semble qu'il y ait eu une erreur lors du lancement du dé.

    Voulez-vous demander quelque chose spécifique, comme des informations générales ou la définition d'un mot ? Je suis là pour vous aider !
    ```
    ```console
    ollama show llama3.1:latest
    Model
        architecture        llama     
        parameters          8.0B      
        context length      131072    
        embedding length    4096      
        quantization        Q4_K_M    

    Capabilities
        completion    
        tools
    ```
- ... ça ne fonctionne pas bien non plus avec *llama3.2* (3.2B), ni *mistral* (7.2B). Ils lancent un dé dès qu'on leur dit "salut".  
- ... avec *gemma3:latest* ça plante : c'est normal, on constate dans ses *Capabilities* que ce modèle ne supporte pas les tools .
    ```console
    ollama show gemma3:latest
    Model
        architecture        gemma3    
        parameters          4.3B      
        context length      131072    
        embedding length    2560      
        quantization        Q4_K_M    

    Capabilities
        completion    
        vision
    ```

[🔝 Retour au sommaire](#table-des-matières)
## 007_mcp_elicitation_local_inspector
```bash
uv run mcp dev server.py
```
### Un module pour apprendre...
- ... que l'élicitation en MCP sert, au déclenchement d'un tool, à demander des confirmations, collecter des données manquantes. Elle est soit de type *form* (données structurées simples) soit *URL* (collecte de données sensibles via *OAuth*). Ici on ne s'intéressera qu'au type *form*.
- ... l'utilisation d'une classe héritant de BaseModel est la méthode recommandée par le SDK pour définir la structure des données attendues dans une élicitation. On déclare donc pour cet exemple :
    ```python
    from pydantic import BaseModel
    class ConfirmationRequest(BaseModel):
    """Schéma pour demander une confirmation à l'utilisateur."""
    confirme_dice: bool = Field(description="Mettre à True pour lancer le dé, False pour annuler")
    ```
- ... pour accéder à la fonctionnalité d'élicitation, il faut injecter l'objet Context dans les paramètres de la fonction outil. C'est via ctx.elicit (dans une fonction asynchrone) que le serveur met l'exécution en pause pour interroger le client.  
    ```python
    from mcp.server.fastmcp import Context
    @mcp.tool()
    async def roll_dice(ctx: Context) -> str:
        """Lance un dé à 6 faces après confirmation de l'utilisateur."""
        result = await ctx.elicit(message="Tu veux vraiment que je lance un dé ?", schema=ConfirmationRequest)
    ```
- ... on peut déjà tester le début de cette élicitation dans l'inspecteur en déclenchant la requête *tools/call*.
    Cela fait nous fait basculer dans la fenêtre *Elicitations* de l'inspecteur :  
    - A gauche : Information Request
        ```console
        Tu veux vraiment que je lance un dé ?
        Request Schema:
            {
                "type": "object",
                "properties": {
                    "confirme_dice": {
                        "type": "boolean",
                        "title": "Confirme Dice",
                        "description": "Mettre à True pour lancer le dé, False pour annuler"
                    }
                },
                "required": [
                    0:"confirme_dice"
                ]
            }
        ```
    - A droite : Response Form  
        L'inspecteur fait apparaitre une tickbox dans l'affichage *"form"* car il a sans doute détecté qu'on attend un booléen
        Regardons plutôt avec l'affichage *"JSON"* :
        ```console
        {
        "confirme_dice": false
        }
        ```  
        On peut écrire true à la place, puis valider l'une des trois classes MCP de l'élicitation,
        **Submit**, **Decline**, **Cancel** qui gèrent les scénarii de l'Information Request.
- ... le serveur est en pause jusqu'à ce qu'il recoive **ElicitationResult** contenant un champ **action**. Ce champ peut prendre l'une des   trois valeurs suivantes :
    - ***accept*** : si *result.action == "accept"*, alors le champ result.data contiendra les informations structurées et validées selon le schéma fourni à ctx.elicit()
    - ***decline*** : le champ data sera vide car aucune donnée n'a été soumise
    - ***cancel*** : c'est l'action d'interruption totale. Le code s'arrête là ou renvoit un message indiquant que l'opération a été avortée par l'utilisateur.

[🔝 Retour au sommaire](#table-des-matières)
## 008_mcp_elicitation_local_client
Ici le script du client lance lui-même le serveur.
```bash
uv run client.py
```
### Un module pour apprendre...
- ... que le client communique avec le serveur via des flux spécifiques (les objets **read** et **write** créés par **stdio_client**). C'est la raison pour laquelle l'utilsation de *print()* est tolérée côté client. Le script écrit dans la console du terminal, et pas dans le flux stdin qu'il envoie au serveur. Le serveur n'écoute que ce que le client lui envoie explicitement via le pipe configuré lors du **StdioServerParameters**. La règle d'or reste de ne jamais utiliser *print()* sur le serveur pour ne pas écrire sur la sortie standart (*stdout*). 
- ... que le client qui gère l'élicitation d'un tool doit définir un callback d'élicitation, un "gestionnaire" pour cette demande du serveur, qu'on passera dans :
    ```python
    async with ClientSession(read, write, elicitation_callback=handle_elicitation) as session:
    ```
[🔝 Retour au sommaire](#table-des-matières)
## 009_mcp_elicitation_local_client_CLI
Ici aussi le script du client lance lui-même le serveur.
```bash
uv run client.py
```
C'est à vous de saisir le formulaire pour renvoyer l'élicitation au serveur.
### Un module pour comprendre, à propos de l'élicitation en mode "form"...
- ... que le client qui supporte la fonctionnalité élicitation doit, dans son gestionnaire **elicitation_callback** :
    - recevoir **params** depuis le serveur. Cet objet **params** est de type **ElicitRequestParams**.
    - en mode *form* il contient **message** et **requestedSchema**
    - **requestedSchema** est volontairement limité à des objets plats (structure JSON non imbriquée) avec des propriétés primitives (string, number, boolean, enum)
    - cette limitation constitue un standart dans la philosophie MCP pour que les clients gèrent dynamiquement les capacité de serveurs qu'ils ne connaissent pas
- ... le client ouvre le **requestedSchema**, détecte le type de données primitives attendues dans la clé **properties**, et en fonction de cela, propose l'input adapté à l'utilisateur afin de recevoir sa réponse
- ... une fois que l'utilisateur a rempli les informations via l'input proposé, le client effectue deux actions critiques avant de renvoyer la réponse au serveur :
   - Validation : Le client valide les données par rapport au schéma pour s'assurer qu'elles sont correctes. Par exemple, vérifier qu'un nombre est bien compris entre le minimum et le maximum spécifiés,  ou faire une validation par conversion:
        ```python
        val = input(f"{description} (o/n) : ").lower().strip()
        user_data[prop_name] = val in ['o', 'oui', 'y', 'yes', 'true']
        ```
   - Structuration : Le client encapsule les données dans un objet content à l'intérieur d'un résultat d'élicitation avec l'action accept
        ```python
        return types.ElicitResult(action="accept", content=user_data)
        ```

[🔝 Retour au sommaire](#table-des-matières)
## 010_mcp_elicitation_http
Cette fois ci on teste l'elicitation entre un serveur et un client distants. Observons comment ce traffic, généré par une demande d'informations adresseé au client par le serveur, est géré par MCP.  
Lancez le serveur :
```bash
uv run serveur.py
```
Puis le client dans un autre terminal:
```bash
uv run client.py
```
Observez les logs générés dans les nouveaux fichiers.
### Un module pour découvrir, à propos de l'élicitation en mode "form"...
- ... que dans la méthode **initialize**, le client, dans ses '**capabilities**' annonce au serveur qu'il supporte la fonctionnalité d'élicitation (en mode *form*, on s'en doutait, mais également en mode *URL*. Ce comportement est induit par défaut par *elicitation_callback*. Je n'ai pas trouvé à ce jour de méthode simple pour enlever cette déclaration):
    ```console
    Sending client message: root=JSONRPCRequest(
        method='initialize',
        params={
            'protocolVersion': '2025-11-25',
            'capabilities': {'elicitation': {'form': {}, 'url': {}}},
            'clientInfo': {'name': 'mcp', 'version': '0.1.0'}},
        jsonrpc='2.0',
        id=0)
    ```

[🔝 Retour au sommaire](#table-des-matières)