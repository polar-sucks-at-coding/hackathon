class Note:
    def __init__(self, _t: str, _c: str, _id = None, likes: int = 0):
        self.id = _id
        self.title = _t
        self.content = _c
        self.likes = likes

    def __repr__(self):
        return f"Note(id={self.id}, title='{self.title}', content='{self.content}', likes={self.likes})"
