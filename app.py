"""
    Homework №16
    Source: https://skyengpublic.notion.site/16-SQLAlchemy-3d71e678b1c14f539025cc79a316999a
    Golosov_SA aka grm

    v.1.0
"""


# global imports
from flask import Flask


def create_app():
    """ Create app function """
    the_app = Flask(__name__)

    return the_app


app = create_app()


if __name__ == "__main__":
    app.run()
