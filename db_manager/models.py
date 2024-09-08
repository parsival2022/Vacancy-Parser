import os
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from pydantic.types import datetime
from typing import Literal
from parsers.constants import USA, EU, UA

load_dotenv()
NOT_DEFINED = "This requirement wasn't defined in vacancy."

class BasicVacancy(BaseModel):

    url:str = Field(min_length=10, pattern=r'https?:\/\/[^\s/$.?#].[^\s]*')
    extr_date:str = Field(default_factory=lambda: datetime.now().strftime(os.environ.get("TIMEFORMAT")))
    location:str = Field(min_length=5)
    keyword:str = Field(min_length=1)
    source:str = Field(min_length=2)
    completed:bool = Field(default=False)
    


    @field_validator('location')
    def validate_location(cls, value):
        choices = {EU, UA, USA}
        if value not in choices:
            raise ValueError(f"Invalid value for location. Allowed values are {choices}.")
        return value
    
class Vacancy(BasicVacancy):
    completed:bool = Field(default=True)
    exact_location:str = Field(min_length=2)
    title:str = Field(min_length=2)
    company:str = Field(default=NOT_DEFINED)
    description:str = Field(min_length=10)
    level:str|list = Field(default=NOT_DEFINED)
    skills:list = Field(default_factory=lambda: [])
    workplace_type:str = Field(default=NOT_DEFINED)
    employment_type:str = Field(default=NOT_DEFINED)
    salary:str = Field(default=NOT_DEFINED)
    
    @classmethod
    def normalize_str(self, str, **kwargs):
        if len(str) % 2 == 0:
            h = len(str) // 2
            f_h = str[:h]
            s_h = str[h:]
            if f_h == s_h:
                str = f_h
        return str
        
    @field_validator('title')
    def validate_title(cls, title):
        return cls.normalize_str(title)

    @field_validator('completed')
    def validate_completed(cls, completed):
        if not completed:
            return True
