"""Console script for biodb_expression_atlas."""
import sys
import click
from .web import app
from .web.models.atlas import database
from .web.models.startup import create_new_database
from getpass import getpass
import pymysql


@click.command()
def main(args=None):
    """Console script for biodb_expression_atlas."""
    click.echo("Expression Atlas Database")
    return 


@click.group(help="Lonic Command Line Utilities on {}".format(sys.executable))
@click.version_option()
def main():
    pass

@main.command()
@click.option('-p', '--port', default='5000', help='server port [5000]')
@click.option('-d', '--debug_mode', is_flag=True, default=False, help='debug mode')
@click.option('-o', '--open_browser', is_flag=True, default=False, help='open browser')
def serve(port, debug_mode, open_browser):
    """Starts the API RESTful server."""
    app.run(port, debug_mode, open_browser)

@main.command()
def import_database():
    """Import data in db."""
    create_new_database()
    database()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
