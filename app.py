"""
    Homework №16
    Source: https://skyengpublic.notion.site/16-SQLAlchemy-3d71e678b1c14f539025cc79a316999a
    Golosov_SA aka grm

    v.1.0
"""


# global imports
from flask import Flask, jsonify
import os
import dotenv
from sqlalchemy import create_engine


def create_app():
    """ Create app function """

    the_app = Flask(__name__)

    dotenv.load_dotenv(override=True)

    the_app.config.update({
        "SQLALCHEMY_DATABASE_URI": f"postgresql+psycopg2://"
                                   f"{os.getenv('DB_USER')}:"
                                   f"{os.getenv('DB_PASSWORD')}@"
                                   f"{os.getenv('DB_HOST')}/"
                                   f"{os.getenv('DB_NAME')}",
    })

    test_connection = create_engine(the_app.config["SQLALCHEMY_DATABASE_URI"])

    test_connection.connect().execute("SELECT 1 + 1")

    test_result = str(test_connection)

    test_connection.dispose()

    the_app.config["test_connection_result"] = test_result

    return the_app


app = create_app()


@app.route("/")
def index():
    return jsonify(
        test_connection_result=app.config["test_connection_result"]), 200


if __name__ == "__main__":
    app.run()
