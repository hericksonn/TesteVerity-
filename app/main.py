"""Ponto de entrada da CLI: orquestra o agente com um servidor MCP local (stdio)."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

from app.agents.dry_run import run_dry_run
from app.agents.story_refinement_agent import format_analysis_markdown, refine_user_story
from app.utils.config import project_root


async def _run_with_mcp(user_story: str) -> None:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    root = project_root()
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp.server"],
        cwd=str(root),
        env=os.environ.copy(),
    )
    print("Iniciando servidor MCP em subprocess (stdio)...", flush=True)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Conectado ao MCP. Executando fluxo do agente...\n", flush=True)
            analysis = await refine_user_story(session, user_story)
            print("\n" + format_analysis_markdown(analysis) + "\n", flush=True)


def _read_story_file(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agile Story Assistant — MVP de agente para refinamento de histórias."
    )
    parser.add_argument(
        "--story-file",
        type=str,
        default=None,
        help="Caminho para um .txt com a história (alternativa à entrada interativa).",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Usa examples/sample_story.txt como entrada.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Valida o fluxo sem OpenAI e sem subprocess MCP: contexto estático a partir de data/, "
            "resposta simulada e gravação direta em memory/history.json."
        ),
    )
    args = parser.parse_args()

    try:
        if args.demo:
            story = _read_story_file(project_root() / "examples" / "sample_story.txt")
        elif args.story_file:
            story = _read_story_file(Path(args.story_file))
        else:
            stop = "---"
            print(
                "Cole a história de usuário. Para finalizar, envie uma linha contendo apenas:\n"
                f"  {stop}\n",
                flush=True,
            )
            lines = []
            while True:
                try:
                    line = input()
                except EOFError:
                    break
                if line.strip() == stop:
                    break
                lines.append(line)
            story = "\n".join(lines).strip()

        if not story.strip():
            print("Nenhuma história informada. Encerrando.", file=sys.stderr)
            sys.exit(1)

        if args.dry_run:
            print(
                "Modo --dry-run: nenhuma chamada à API OpenAI; servidor MCP não é iniciado.\n",
                flush=True,
            )
            analysis = run_dry_run(story)
            print("\n" + format_analysis_markdown(analysis) + "\n", flush=True)
        else:
            asyncio.run(_run_with_mcp(story))
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
