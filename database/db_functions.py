from datetime import datetime
from typing import Optional
import re
from pydantic import BaseModel, validator, field_validator


class AppointmentSchema(BaseModel):
    user_id: float
    master_id: float
    date: str
    time: str
    price: int
    service_id: int

    @field_validator('date')
    @classmethod
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%d.%m.%Y')
        except ValueError:
            raise ValueError('Дата должна быть в формате DD.MM.YYYY')
        return v

    @field_validator('time')
    @classmethod
    def validate_time(cls, v: str) -> str:
        if not re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', v):
            raise ValueError('Время должно быть в формате ЧЧ:ММ')

        hour, minute = map(int, v.split(':'))
        if hour < 8  or hour > 21:
            raise ValueError('Время должно быть с 08:00 до 21:00')

        return v