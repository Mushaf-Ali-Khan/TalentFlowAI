from app.repositories.base import BaseRepository
from app.models.shortlist import Shortlist

class ShortlistRepository(BaseRepository[Shortlist]):
    def __init__(self):
        super().__init__(Shortlist)

shortlist_repo = ShortlistRepository()
