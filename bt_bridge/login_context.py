class LoginContext:
    _login_session = ""

    @classmethod
    def set_session(cls, token: str):
        cls._login_session = token or ""

    @classmethod
    def get_session(cls) -> str:
        return cls._login_session

    @classmethod
    def clear(cls):
        cls._login_session = ""
