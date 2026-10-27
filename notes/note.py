import datetime

class Note:
    def __init__(self, id, title, content, author, likes=0, date=None, file_name=""):
        self.id = id
        self.title = title
        self.content = content
        self.author = author
        self.likes = likes
        self.date = date if date else datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        self.file_name = file_name if file_name else ""

    def to_string(self):
        return f"{self.id}|{self.title}|{self.content}|{self.author}|{self.likes}|{self.date}|{self.file_name}"

    @staticmethod
    def from_string(line):
        parts = line.strip().split('|')
        if len(parts) >= 5:
            note_id = int(parts[0])
            title = parts[1]
            content = parts[2]
            author = parts[3]
            likes = int(parts[4])
            date = parts[5] if len(parts) > 5 else "Bilinmiyor"
            file_name = parts[6] if len(parts) > 6 else ""
            return Note(note_id, title, content, author, likes, date, file_name)
        return None
