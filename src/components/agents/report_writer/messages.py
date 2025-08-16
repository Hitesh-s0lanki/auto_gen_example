from pydantic import BaseModel, Field
from typing import List
from dataclasses import dataclass

@dataclass
class CreatorMessage:
    name:str
    description:str
    output: str

# Input Message Type from User
@dataclass
class UserMessage:
    topic: str
    sections: List[CreatorMessage]

## Structured Outputs!
class Section(BaseModel):
    name:str = Field(description="Name for this section of the Report")
    description:str = Field(description="Brief Overview of the main topics and concepts of the section")

class Sections(BaseModel):
    sections:List[Section] = Field(description="Sections of the report")

@dataclass 
class CreatorOutput:
    sections: List[CreatorMessage]
