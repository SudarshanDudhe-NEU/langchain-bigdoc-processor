from typing import Optional
from typing_extensions import Annotated, List
from pydantic.functional_validators import AfterValidator
from bson import ObjectId as _ObjectId

from pydantic import BaseModel, Field
from bson import ObjectId


class Question(BaseModel):
    question: str
    options: List[str]


class QuestionAnswer(BaseModel):
    question: str
    options: List[str]
    answer: str
    justification: str


class ReqData(BaseModel):
    topic: str
    question: Question


class Answer(BaseModel):
    Answer: str = ""
    Justification: str = ""


class FileSummary(BaseModel):
    file_name: str = ""
    summary: str = ""


def check_object_id(value: str) -> str:
    if not _ObjectId.is_valid(value):
        raise ValueError('Invalid ObjectId')
    return value

# ObjectId("662c7428fb45c882e17567b8")


ObjectId = Annotated[str, AfterValidator(check_object_id)]


class UserFileDetails(BaseModel):
    user_id: str = "662c7428fb45c882e17567b8"
    file_details: FileSummary


class QueryData(BaseModel):
    question: str
    filename: Optional[str] = None


class QueryAnswer(BaseModel):
    # code: int
    answer: Optional[str] = None
