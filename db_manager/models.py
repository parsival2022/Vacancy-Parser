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
    complited:bool = Field(default=False)
    


    @field_validator('location')
    def validate_location(cls, value):
        choices = {EU, UA, USA}
        if value not in choices:
            raise ValueError(f"Invalid value for location. Allowed values are {choices}.")
        return value
    
class Vacancy(BaseModel):
    complited:bool = Field(default=True)
    exact_location:str = Field(min_length=2)
    title:str = Field(min_length=2)
    company:str = Field(default=NOT_DEFINED)
    description:str = Field(min_length=50)
    level:str|list = Field(default=NOT_DEFINED)
    skills:list = Field(default_factory=lambda: [])
    workplace_type:str = Field(default=NOT_DEFINED)
    employment_type:str = Field(default=NOT_DEFINED)
    salary:str = Field(default=NOT_DEFINED)
