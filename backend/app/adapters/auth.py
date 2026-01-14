from jose import JWTError, jwt


def verify_token(token: str) -> dict:
    try:
        # TODO: вынести в конфиг
        payload = jwt.decode(
            token,
            "asfdslknfsdfsdfjksdlkjfkjdsfjskjfsjdfndsfnkjfnskjfskjfskjfk",
            algorithms=["HS256"]
        )
        return payload
    except JWTError:
        return None
