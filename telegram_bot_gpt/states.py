from enum import Enum


class RandomState(Enum):
    RUNNING = 1


class GptState(Enum):
    RUNNING = 1


class TalkState(Enum):
    CHOOSING_PERSON = 1
    TALKING = 2


class QuizState(Enum):
    CHOOSING_QUIZ = 1
    QUIZ_RUNNING = 2


class TranslateState(Enum):
    CHOOSING_LANG = 1
    TRANSLATING = 2


class ResumeState(Enum):
    ASK_RESUME = 1
