from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
import databases as dbase
import sqlalchemy as sql
from datetime import datetime

DATABASE_URL = 'sqlite:///./store.db'

metadata = sql.MetaData()

database = dbase.Database(DATABASE_URL)     # Create the database based on the url

register = sql.Table(
    "register",
    metadata,
    sql.Column('id', sql.Integer, primary_key=True),     # Primary key defines data on the row
    sql.Column('name', sql.String(500)),
    sql.Column('date_created', sql.DateTime())
)

# We make an engine
engine = sql.create_engine(
    DATABASE_URL, connect_args={'check_same_thread': False}     # Process to check everything in the same thread, set to False
)

metadata.create_all(engine)     # We create metadata about the engine

app = FastAPI()

class RegisterIn(BaseModel):
    name: str = Field(...)      # ... is default, like the pass keyword; something will be put in there

class Register(BaseModel):
    id: int
    name: str
    date_created: datetime

@app.on_event('startup')
async def connect():
    await database.connect()

@app.on_event('shutdown')
async def disconnect():
    await database.disconnect()

@app.post('/register', response_model=Register)
async def create(reg: RegisterIn = Depends()):     # Depends adds injecting of dependencies where we want to VERY OPTIONAL
    query = register.insert().values(            # Inserting the parameter values into the query
        name=reg.name,
        date_created=datetime.utcnow()
    )
    record_id = await database.execute(query)
    query = register.select().where(register.c.id == record_id) # Select id column where register_id = record_id, where equivalent to SQL sql
    row = await database.fetch_one(query)   # Returns the row where data is
    return {**row}      # Returns row as dictionary

@app.get('/register/{id}', response_model=Register)
async def get_one(id:int):
    query = register.select().where(register.c.id == id)
    user = await database.fetch_one(query)
    return {**user}

#OUTDATED CODE


