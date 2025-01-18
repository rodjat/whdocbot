import sqlite3

from ..config import config

from ..models import UserModelSchema


async def init_table():
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            cursor = conn.cursor()

            try:
                with conn:
                    cursor.execute(
                        """
                        create table if not exists Users (
                        id integer primary key,
                        username text not null,
                        role text not null,
                        unique(username)
                        )
                        """
                    )
            except Exception as e:
                print(f"[ERROR]: CREATE TABLE FAILED \n{e}")

    except Exception as e:
        print(f"[ERROR]: INIT TABLE FAILED \n{e}")


async def add_user(creds: UserModelSchema):
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            cursor = conn.cursor()

            try:
                with conn:
                    cursor.execute(
                        f"""
                        insert or ignore into Users (username, role) values(?, ?)
                        """,
                        (f"{creds.username}", "user")
                    )
            except Exception as e:
                print(f"[ERROR]: ADD USER FAILED \n{e}")

    except Exception as e:
        print(f"[ERROR]: OPERATION FAILED \n{e}")


async def get_user(creds: UserModelSchema):
    result = []
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            cursor = conn.cursor()

            try:
                with conn:
                    cursor.execute(
                        f"""
                        select username, role from Users where username=?)
                        """,
                        (f"{creds.username}", )
                    )
                    result = cursor.fetchall()
            except Exception as e:
                print(f"[ERROR]: GET USER FAILED \n{e}")

    except Exception as e:
        print(f"[ERROR]: OPERATION FAILED \n{e}")