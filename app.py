"""
    Homework №16
    Source: https://skyengpublic.notion.site/16-SQLAlchemy-3d71e678b1c14f539025cc79a316999a
    Golosov_SA aka grm

    v.1.0
"""

# global imports
from flask import Flask
import dotenv
import os


# local imports
from main.models import db
from main.views import bp_main


def create_app() -> Flask:
    """ Create app function """

    the_app = Flask(__name__)

    dotenv.load_dotenv(override=True)

    the_app.config.update({
        "SQLALCHEMY_DATABASE_URI": f"postgresql+psycopg2://"
                                   f"{os.getenv('DB_USER')}:"
                                   f"{os.getenv('DB_PASSWORD')}@"
                                   f"{os.getenv('DB_HOST')}:"
                                   f"{os.getenv('DB_PORT')}/"
                                   f"{os.getenv('DB_NAME')}",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JSON_AS_ASCII": False,
    })

    the_app.register_blueprint(bp_main, url_prefix="/")

    return the_app


app = create_app()
with app.app_context():
    db.init_app(app)

if __name__ == "__main__":
    app.run()
