class Note:
    def __init__(self, id, title, content, author, likes=0):
        self.id = id
        self.title = title
        self.content = content
        self.author = author
        self.likes = likes

    def to_string(self):
        return f"{self.id}|{self.title}|{self.content}|{self.author}|{self.likes}"

    @staticmethod
    def from_string(line):
        parts = line.strip().split('|')
        if len(parts) == 5:
            return Note(int(parts[0]), parts[1], parts[2], parts[3], int(parts[4]))
        return None
