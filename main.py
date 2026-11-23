"""Ponto de entrada do RentSmart. Execute: python main.py"""

from rentsmart.interface import InterfaceConsole


def main() -> None:
    try:
        InterfaceConsole().executar()
    except (KeyboardInterrupt, EOFError):
        print("\nExecução encerrada pelo usuário.")


if __name__ == "__main__":
    main()
