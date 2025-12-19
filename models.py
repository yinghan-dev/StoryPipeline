from pydantic import BaseModel

class Event(BaseModel):
    event_id: str
    chapter_id: str
    order_in_chapter: int
    year: int
    month: int
    location: str
    characters: str        
    scene_type: str       
    plot_direction: str    

class Chapter(BaseModel):
    chapter_id: str
    chapter_title: str
    chapter_goal: str      
    chapter_tone: str      
    notes: str

class Character(BaseModel):
    character_id: str
    canonical_name: str
    titles: str            
    age: str
    profession: str
    personality: str
    country_id: str
    notes: str

class Country(BaseModel):
    country_id: str
    name: str
    regime: str
    media_ecology: str
    alignment: str
    faction_id: str
    notes: str

class Faction(BaseModel):
    faction_id: str
    name: str
    core_tech: str
    ideology: str
    notes: str
