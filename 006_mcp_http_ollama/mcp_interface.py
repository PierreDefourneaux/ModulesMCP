import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
import logging


logging.basicConfig(level=logging.ERROR)
file_handler = logging.FileHandler("mcp_client.log", mode="w")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
mcp_logger = logging.getLogger("mcp")
mcp_logger.setLevel(logging.DEBUG)
mcp_logger.addHandler(file_handler)
mcp_logger.propagate = False
logger = logging.getLogger("logs_applicatifs") 

class MCPClientManager:
    def __init__(self, server_url="http://localhost:8000/mcp"):
        self.server_url = server_url
        self.session = None
        self.exit_stack = None

    async def __aenter__(self):
        """Gestionnaire de contexte pour ouvrir la connexion"""
        self.client_context = streamable_http_client(self.server_url)
        read_stream, write_stream, _ = await self.client_context.__aenter__()
        self.session = ClientSession(read_stream, write_stream)
        await self.session.__aenter__()
        await self.session.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermeture propre de la session"""
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
        if self.client_context:
            await self.client_context.__aexit__(exc_type, exc_val, exc_tb)

    async def get_tools_for_ollama(self):
        """Récupère les outils et les formate pour l'API ollama"""
        result = await self.session.list_tools()
        ollama_tools = []

        for tool in result.tools:
            # Conversion du format MCP vers le format ollama (Function Calling)
            ollama_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })
        return ollama_tools

    async def call_tool(self, name, arguments):
        """Exécute l'outil via MCP"""
        result = await self.session.call_tool(name, arguments=arguments)
        
        # Gestion simplifiée du retour (texte ou structuré)
        content = ""
        if hasattr(result, 'content'):
            for item in result.content:
                if item.type == 'text':
                    content += item.text
                elif item.type == 'resource':
                    content += str(item.resource)
        
        return content