import sqlalchemy as sa
import sqlite3
import pandas as pd

db_hm = sa.create_engine('sqlite:////home/rengineer/Documentos/DS/ds_ao_dev/Modulo_8/venv/database_hm.sqlite', echo=False)
conn = db_hm.connect()

query = """ SELECT product_id FROM vitrine_hm """

df = pd.read_sql_query( query, conn)
print(df.shape)
