import sqlite3
import bcrypt


def register_user(
    username,
    password
):

    conn = sqlite3.connect(
        "database/users.db"
    )

    cursor = conn.cursor()

    password_hash = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )

    try:

        cursor.execute(
            """
            INSERT INTO users(
                username,
                password_hash
            )
            VALUES (?,?)
            """,
            (
                username,
                password_hash.decode()
            )
        )

        conn.commit()

        return True

    except:

        return False

    finally:

        conn.close()




def login_user(
    username,
    password
):

    conn = sqlite3.connect(
        "database/users.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT password_hash
        FROM users
        WHERE username=?
        """,
        (username,)
    )

    result = cursor.fetchone()

    conn.close()

    if not result:
        return False

    stored_hash = result[0]

    return bcrypt.checkpw(
        password.encode(),
        stored_hash.encode()
    )