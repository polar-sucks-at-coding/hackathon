from user_profile import Profile

class User:
    def __init__(self, username, password, profile=None):
        self.username = username
        self.password = password
        self.profile = profile if profile is not None else Profile(username)

    def to_string(self):
        return f"{self.username}|{self.password}"

    @staticmethod
    def from_string(line):
        parts = line.strip().split('|')
        if len(parts) == 2:
            return User(parts[0], parts[1])
        return None
