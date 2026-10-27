class Profile:
    def __init__(self, username, faculty="", department="", about="", note_ids=None):
        self.username = username
        self.faculty = faculty if faculty else ""
        self.department = department if department else ""
        self.about = about if about else ""
        self.note_ids = note_ids if note_ids is not None else []

    def add_note(self, note_id):
        if note_id not in self.note_ids:
            self.note_ids.append(note_id)

    def to_string(self):
        f = str(self.faculty).replace('|', ' ')
        d = str(self.department).replace('|', ' ')
        a = str(self.about).replace('|', ' ').replace('\n', ' ')
        notes_str = ','.join(map(str, self.note_ids))
        return f"{self.username}|{f}|{d}|{a}|{notes_str}"

    @staticmethod
    def from_string(line):
        parts = line.strip().split('|')
        if len(parts) >= 5:
            username = parts[0]
            faculty = parts[1]
            department = parts[2]
            about = parts[3]
            note_ids = [int(id) for id in parts[4].split(',')] if parts[4] else []
            return Profile(username, faculty, department, about, note_ids)
        elif len(parts) == 2:
            # Eski format uyumluluğu
            username = parts[0]
            note_ids = [int(id) for id in parts[1].split(',')] if parts[1] else []
            return Profile(username, "", "", "", note_ids)
        return None
