from dataclasses import dataclass


@dataclass
class Credentials:
    hash: str
    access_token: str
    refresh_token: str
    expires_at: int
