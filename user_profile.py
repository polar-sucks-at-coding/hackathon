class Profile:
    def __init__(self, username, note_ids=None):
        self.username = username
        self.note_ids = note_ids if note_ids is not None else []

    def add_note(self, note_id):
        if note_id not in self.note_ids:
            self.note_ids.append(note_id)

    def to_string(self):
        return f"{self.username}|{','.join(map(str, self.note_ids))}"

    @staticmethod
    def from_string(line):
        parts = line.strip().split('|')
        if len(parts) == 2:
            username = parts[0]
            note_ids = [int(id) for id in parts[1].split(',')] if parts[1] else []
            return Profile(username, note_ids)
        return None
