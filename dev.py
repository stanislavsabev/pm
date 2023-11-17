import typer

app = typer.Typer(add_completion=False, short_help="h")


@app.callback(invoke_without_command=True)
def foo(lat: float = None, long: float = None, method: str = None):
    typer.echo(f"{lat}, {long}, {method}")


@app.command()
def bar():
    typer.echo("I'm just here to mess things up...")


if __name__ == "__main__":
    app()
