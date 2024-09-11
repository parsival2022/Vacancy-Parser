import os
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, field_validator
from .constants import NOT_DEFINED

class BasicVacancyModel(BaseModel):
    url:str = Field(min_length=10, pattern=r'https?:\/\/[^\s/$.?#].[^\s]*')
    extr_date:str = Field(default_factory=lambda: datetime.now().strftime(os.environ.get("TIMEFORMAT")))
    location:str = Field(min_length=5)
    keyword:str = Field(min_length=1)
    source:str = Field(min_length=2)
    completed:bool = Field(default=False)
    title:str = Field(min_length=2)
    company:str = Field(default=NOT_DEFINED, min_length=2)
    description:str = Field(min_length=10)
    eng_level:str|list = Field(default=NOT_DEFINED, min_length=5)
    level:str|list = Field(default=NOT_DEFINED)
    skills:list = Field(default_factory=lambda: [])
    workplace_type:str = Field(default=NOT_DEFINED)
    employment_type:str = Field(default=NOT_DEFINED)
    salary:str = Field(default=NOT_DEFINED)

    @model_validator(mode='after')
    def check_level(self):
        title = self.title.casefold()
        if self.level == NOT_DEFINED:
            if "senior" in title:
                self.level = "Senior"
            elif "middle" in title:
                self.level = "Middle"
            elif "junior" in title:
                self.level = "Junior"
            elif "lead" in title:
                self.level = "Lead"
        return self
    
    @classmethod
    def normalize_str(self, str):
        if len(str) % 2 == 0:
            h = len(str) // 2
            if str[:h] == str[h:]: str = str[:h]        
        return str
        
    @field_validator('title')
    def validate_title(cls, title):
        return cls.normalize_str(title)