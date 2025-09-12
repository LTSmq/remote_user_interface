# runner.py

def run(path: str) -> None:
    from subprocess import run
    from sys import executable as python

    run([python, path])
