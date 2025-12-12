import sys
from typing import List

from maestro.context import context_add, context_list, context_remove
from maestro.session import list_sessions, start_session, status_session
from maestro.tools import run_command, set_tool


def print_usage() -> None:
    print("Uso:", file=sys.stderr)
    print("  maestro session start <nome>", file=sys.stderr)
    print("  maestro session list", file=sys.stderr)
    print("  maestro session status", file=sys.stderr)
    print("  maestro context add <arquivo>", file=sys.stderr)
    print("  maestro context list", file=sys.stderr)
    print("  maestro context remove <id>", file=sys.stderr)
    print("  maestro use <nome-da-ferramenta>", file=sys.stderr)
    print('  maestro run "<prompt>"', file=sys.stderr)


def main(argv: List[str]) -> int:
    if len(argv) >= 2 and argv[0] == "session":
        if argv[1] == "start":
            if len(argv) < 3:
                print("Erro: nome da sessão é obrigatório.", file=sys.stderr)
                print_usage()
                return 1
            session_name = " ".join(argv[2:]).strip()
            if not session_name:
                print("Erro: nome da sessão é obrigatório e não pode ser vazio.", file=sys.stderr)
                print_usage()
                return 1
            try:
                session_id, session_dir = start_session(session_name)
            except (FileExistsError, ValueError) as e:
                print(str(e), file=sys.stderr)
                return 1
            print(f"Sessão criada: {session_id}")
            print(f"Diretório: {session_dir}")
            return 0
        if argv[1] == "list" and len(argv) == 2:
            return list_sessions()
        if argv[1] == "status" and len(argv) == 2:
            return status_session()
    if len(argv) >= 2 and argv[0] == "context":
        if argv[1] == "add":
            if len(argv) < 3:
                print("Erro: caminho do arquivo é obrigatório.", file=sys.stderr)
                print_usage()
                return 1
            file_arg = argv[2]
            return context_add(file_arg)
        if argv[1] == "list" and len(argv) == 2:
            return context_list()
        if argv[1] == "remove":
            if len(argv) < 3:
                print("Erro: ID do item é obrigatório.", file=sys.stderr)
                print_usage()
                return 1
            return context_remove(argv[2])
    if len(argv) >= 1 and argv[0] == "use":
        if len(argv) < 2:
            print("Erro: nome da ferramenta é obrigatório.", file=sys.stderr)
            print_usage()
            return 1
        tool_name = " ".join(argv[1:]).strip()
        if not tool_name:
            print("Erro: nome da ferramenta é obrigatório.", file=sys.stderr)
            print_usage()
            return 1
        return set_tool(tool_name)
    if len(argv) >= 1 and argv[0] == "run":
        if len(argv) < 2:
            print("Erro: prompt é obrigatório.", file=sys.stderr)
            print_usage()
            return 1
        prompt_text = " ".join(argv[1:]).strip()
        return run_command(prompt_text)

    print("Comando não suportado.", file=sys.stderr)
    print_usage()
    return 1
