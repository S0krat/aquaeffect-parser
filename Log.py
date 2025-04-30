import datetime


def info(text: str) -> None:
    print(f"\033[92m{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} INFO : {text}")


def warn(text: str) -> None:
    print(f"\033[93m{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WARN : {text}")


def error(text: str) -> None:
    print(f"\033[91m{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ERROR : {text}")
