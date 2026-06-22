import pandera as pa
import pandas as pd
from pandera import DataFrameSchema, Column, Check
from pandera.dtypes import Float, Int, String 

def strict_datetime_column(series: pd.Series) -> bool:
    """ Проверяем целую колонку на соответсвие формата timestamp.
    """
    def is_strict_format(val):
        try:
            datetime.strptime(val, "%Y-%m-%d %H:%M:%S UTC")
            return True
        except:
            return False
    mask = series.apply(is_strict_format)
    return mask

taxi_schema = pa.DataFrameSchema(
    columns={
        "pickup_datetime": Column(
            str,
            required=True,
            checks=Check(strict_datetime_column, 
                         error="pickup_datetime: не все значения соответствуют формату 'YYYY-MM-DD HH:MM:SS UTC'")
        ),
        "fare_amount": Column(
            float,
            required=True,
            checks=[
                Check.ge(0),
                Check.le(100)
            ]
        ),
        "pickup_longitude": Column(
            float,
            required=True,
            checks=Check.in_range(-180, 180)
        ),
        "pickup_latitude": Column(
            float,
            required=True,
            checks=Check.in_range(-180, 180)
        ),
        "dropoff_longitude": Column(
            float,
            required=True,
            checks=[
                Check.ge(-180),
                Check.le(180)
            ]
        ),
        "dropoff_latitude": Column(
            float,
            required=True,
            checks=[
                Check.ge(-180),
                Check.le(180) # Максимум 180 не включительно
            ]
        ),
        "passenger_count": Column(
            int,
            required=True,
            checks=[
                Check.ge(1),   # Минимум 1 включительно
                Check.lt(10)   # Максимум 10 не включительно
            ]
        ),
    },
    # Запрещаем любые другие колонки (строгое соответствие схеме)
    strict=True,
    # Порядок колонок нам не важен.
    ordered=False
)  