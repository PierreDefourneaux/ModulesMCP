from mcp.server.fastmcp import FastMCP

mcp = FastMCP("AdditionServer")
# Définition de l'outil 'add_numbers'
# FastMCP utilise les "type hints" (ici, int) et la docstring pour générer 
# automatiquement l'inputSchema pour le client. Ces éléments sont donc primordiaux.
@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """
    Additionne deux nombres entiers et retourne le résultat.
    
    Args:
        a: Le premier nombre.
        b: Le deuxième nombre.
    """
    # Le SDK mcp se encapsulera ce résultat dans une structure adaptée (Structured Output).
    return a + b

if __name__ == "__main__":
    # La méthode run() utilise par défaut le transport stdio
    mcp.run()