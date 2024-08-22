from pydantic import BaseModel


class Config(BaseModel):
    FCATS: dict = {
        "NULL":0,
        "Doujinshi":1021,
        "Manga":1019,
        "Artist-CG":1015,
        "Game-CG":1007,
        "Western":511,
        "Non-H":767,
        "Image-Set":991,
        "Cosplay":959,
        "Asian-Porn":895,
        "Misc":1022,
    }
    NEW_FCATS: dict = {v:k for k,v in FCATS.items()}
    FCATS_LIST: list = [0,1021,1019,1015,1007,511,767,991,959,895,1022]
    search_regex: str = r"^(ehbz)\s?(\d+)?\s?(.*)?"