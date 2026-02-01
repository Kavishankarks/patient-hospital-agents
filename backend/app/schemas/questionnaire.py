from pydantic import BaseModel, Field

class QuestionnaireNext(BaseModel):
    questions: list[str] = Field(default_factory=list)

class QuestionnaireAnswer(BaseModel):
    answers: dict
