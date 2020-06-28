from sqlalchemy import func

import sqlmodels as models
import models as schemas

from sqldatabase import engine, SessionLocal
from sqlmodels import SqaCheckin, SqaEventType, SqaEtInterface, Base

db = SessionLocal()

Base.metadata.create_all(bind=engine)

conn = engine.connect()

# populate_etinterfaces.sql
sql = """
insert into etinterfaces (event_type_id, value_type, input_type, minval, maxval)
	select et.id as event_type_id, 
		   'range' as value_type,
	       'radios' as input_type,
		   1 as minval,
		   5 as maxval
	from eventtypes et
	where et.is_checkinable = 1;
    """

conn.execute(sql)

conn.execute('select * from etinterfaces').fetchall()

# conn.commit() # no necessary, SQLite autocommits