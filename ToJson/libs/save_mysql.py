from libs.print_error_info import *
from models.model import ToJsonRecord, ToJsonSuggest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

engine = create_engine(f'mysql+pymysql://root:{quote_plus("Allone888..")}@localhost:3306/tojson?charset=utf8mb4')
Session = sessionmaker(bind=engine)
session = Session()
ToJsonRecord.__table__.create(engine, checkfirst=True)
ToJsonSuggest.__table__.create(engine, checkfirst=True)
session.close()


def save_to_json_record(data_str):
    session = Session()
    tsr = ToJsonRecord()
    tsr.time = str_f_time()
    tsr.record = data_str
    session.add(tsr)
    session.commit()
    session.close()


def save_suggest(name,description):
    session = Session()
    tsr = ToJsonSuggest()
    tsr.time = str_f_time()
    tsr.name = name
    tsr.description = description
    session.add(tsr)
    session.commit()
    session.close()
