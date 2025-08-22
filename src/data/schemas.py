import pandera as pa
from pandera import Column, Check
import pandas as pd

class PriceDataSchema(pa.DataFrameModel):
    date: pd.DatetimeIndex
    Open: float = Column(Check.ge(0))
    High: float = Column(Check.ge(0))
    Low: float = Column(Check.ge(0))
    Close: float = Column(Check.ge(0))
    Volume: int = Column(Check.ge(0))

    class Config:
        coerce = True
        strict = True
