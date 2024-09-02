from datetime import datetime
from pydantic import BaseModel, Field, ValidationError
from pydantic.types import datetime


class Vacancy(BaseModel):
    date_of_extraction:datetime
    source:str
    title:str
    country:str
    level:list
    skills:list
    job_type:str
    employment_type:str
    salary:str
