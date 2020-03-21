from datetime import datetime

from sqlalchemy import (
    MetaData, Table, Column, Integer, DateTime, Enum, Unicode, Boolean
)

metadata = MetaData()

SEX = ('male', 'female')

user = Table(
    'user',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('sex', Enum(*SEX, name='sex')),
    Column('nick', Unicode(length=50), unique=True, nullable=False),
    Column('name', Unicode(length=50)),
    Column('surname', Unicode(length=50),),
    Column('password', Unicode(length=70), nullable=False),
    Column('email', Unicode(length=80), unique=True, nullable=False),
    Column('is_active', Boolean, default=True),
    Column('reg_date', DateTime(timezone=True), default=datetime.now()),
)
