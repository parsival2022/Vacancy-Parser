import os, re
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, field_validator 
from clusters import *

class BasicVacancyModel(BaseModel):
    url:str = Field(min_length=10, pattern=r'https?:\/\/[^\s/$.?#].[^\s]*')
    clusters:list = Field(default_factory=lambda: [])
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
    technologies:list = Field(default_factory=lambda: [])
    workplace_type:str = Field(default=NOT_DEFINED)
    employment_type:str = Field(default=NOT_DEFINED)
    salary:str = Field(default=NOT_DEFINED)

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
    
    def extract_technologies(self):
        _ = lambda s: s.lower().replace(" ", "")
        normalized_descr = self.description.lower()
        techs = [tech for sublist in (v["technologies"] for v in CLUSTERS.values()) for tech in sublist] + OTHER_TECHS
        self.technologies = [tech for tech in techs if re.search(rf"\b{re.escape(tech.lower())}\b", normalized_descr)]
        for tech in self.technologies:
            for v in CLUSTERS.values():
                if tech in v["technologies"] and not v["name"] in self.clusters:
                    self.clusters.append(v["name"])
        skills_to_remove = []
        for skill in self.skills:
            for v in CLUSTERS.values():
                if _(skill) == _(v['name']) or re.search(rf"\b{_(v['name'])}\b", _(skill)):
                    if not v["name"] in self.clusters: 
                        self.clusters.append(v["name"])
                    skills_to_remove.append(skill)
                    continue
                techs_fr_skills = [tech for tech in v["technologies"] if re.search(rf"\b{re.escape(_(tech))}\b", _(skill))]
                if techs_fr_skills: 
                    self.technologies = list(set(self.technologies + techs_fr_skills)) 
                    self.clusters.append(v["name"]) if not v["name"] in self.clusters else None
                    skills_to_remove.append(skill)
        self.skills = [skill for skill in self.skills if skill not in skills_to_remove]
        return self
    
    def define_cluster(self):
        _ = lambda s: s.lower().replace(" ", "")
        for v in CLUSTERS.values():
            if not v["name"] in self.clusters:
                if re.search(rf"\b{v['name'].lower()}\b", self.title):
                    self.clusters.append(v["name"])
                elif re.search(rf"\b{_(v['name'])}\b", self.description.lower()):
                    self.clusters.append(v["name"])
                elif any(tech in v["technologies"] for tech in self.technologies):
                    self.clusters.append(v["name"])
        return self
    
    @model_validator(mode="after")
    def normalization_suite(self):
        self.check_level()
        self.extract_technologies()
        self.define_cluster()
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