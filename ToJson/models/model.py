from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def to_dict(self):
    model_dict = dict(self.__dict__)
    del model_dict['_sa_instance_state']
    return model_dict


Base.to_dict = to_dict  # 注意:这个跟使用flask_sqlalchemy的有区别


class ToJsonRecord(Base):
    __tablename__ = 'to_json_record'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(String(32), index=True)
    record = Column(Text)


class ToJsonSuggest(Base):
    __tablename__ = 'to_json_suggest'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(String(32), index=True)
    name = Column(String(512))
    description = Column(Text)
