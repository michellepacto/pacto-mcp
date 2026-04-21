"""
MCP Server para atualizar arquivos no GitHub
Repositório: michellepacto/Pacto_CRM
"""
from mcp.server.fastmcp import FastMCP
import httpx
import base64
import os

mcp = FastMCP("github-updater")

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = os.environ.get("GITHUB_REPO", "michellepacto/Pacto_CRM")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json",
}
BASE_URL = f"https://api.github.com/repos/{REPO}/contents"


def get_file_sha(path: str) -> str | None:
    """Busca o SHA atual de um arquivo no repositório."""
    url = f"{BASE_URL}/{path}"
    r = httpx.get(url, headers=HEADERS)
    if r.status_code == 200:
        return r.json().get("sha")
    return None


@mcp.tool()
def update_file(path: str, content: str, message: str = "Atualização via Claude") -> str:
    """
    Atualiza um arquivo existente no repositório GitHub.

    Args:
        path: Caminho do arquivo no repo (ex: 'app.py' ou 'utils/database.py')
        content: Conteúdo completo do arquivo em texto
        message: Mensagem do commit

    Returns:
        Confirmação de sucesso ou mensagem de erro
    """
    sha = get_file_sha(path)
    if not sha:
        return f"❌ Arquivo '{path}' não encontrado no repositório."

    content_b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")

    payload = {
        "message": message,
        "content": content_b64,
        "sha": sha,
    }

    url = f"{BASE_URL}/{path}"
    r = httpx.put(url, headers=HEADERS, json=payload)

    if r.status_code in (200, 201):
        commit_sha = r.json()["commit"]["sha"][:7]
        return f"✅ '{path}' atualizado com sucesso! Commit: {commit_sha}"
    else:
        return f"❌ Erro {r.status_code}: {r.json().get('message', 'Erro desconhecido')}"


@mcp.tool()
def create_file(path: str, content: str, message: str = "Novo arquivo via Claude") -> str:
    """
    Cria um novo arquivo no repositório GitHub.

    Args:
        path: Caminho do arquivo no repo (ex: 'sql/crm_schema.sql')
        content: Conteúdo completo do arquivo em texto
        message: Mensagem do commit

    Returns:
        Confirmação de sucesso ou mensagem de erro
    """
    content_b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")

    payload = {
        "message": message,
        "content": content_b64,
    }

    url = f"{BASE_URL}/{path}"
    r = httpx.put(url, headers=HEADERS, json=payload)

    if r.status_code in (200, 201):
        commit_sha = r.json()["commit"]["sha"][:7]
        return f"✅ '{path}' criado com sucesso! Commit: {commit_sha}"
    elif r.status_code == 422:
        return f"⚠️ Arquivo já existe. Use update_file para atualizar."
    else:
        return f"❌ Erro {r.status_code}: {r.json().get('message', 'Erro desconhecido')}"


@mcp.tool()
def list_files(folder: str = "") -> str:
    """
    Lista os arquivos de uma pasta do repositório.

    Args:
        folder: Pasta a listar (vazio = raiz do repo)

    Returns:
        Lista de arquivos e pastas
    """
    url = f"{BASE_URL}/{folder}" if folder else BASE_URL
    r = httpx.get(url, headers=HEADERS)

    if r.status_code != 200:
        return f"❌ Erro ao listar: {r.json().get('message')}"

    items = r.json()
    result = []
    for item in items:
        icon = "📁" if item["type"] == "dir" else "📄"
        result.append(f"{icon} {item['path']} ({item.get('size', 0)} bytes)")

    return "\n".join(result) if result else "Pasta vazia."


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
