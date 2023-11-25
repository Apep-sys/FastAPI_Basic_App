from fastapi import FastAPI, HTTPException
from models import User, Gender, Role, UpdateUser, TestUser
from uuid import UUID, uuid4



app = FastAPI(title='The Big Documentation',
              description='This is the biggest documentation out there.',
              version='3.5')    # docs_url = None -> shows no documentation; you can add another path to docs_url

db: list[User] = [
    User(id=uuid4(),
         first_name='Jamila',
         last_name='Ahmed',
         gender=Gender.female,
         roles=[Role.student]),

    User(id=uuid4(),
         first_name='Alec',
         middle_name='Alexander',
         last_name='Jones',
         gender=Gender.male,
         roles=[Role.admin, Role.user])
]

@app.get('/')
    # Everytime user loads a page, this is the answer he gets
async def root():
    # Returns JSON automatically, but we can pass dict and it gets converted to JSON
    return {'message': 'Hello World!'}


@app.get('/api/v1/users')
async def fetch_users():
    return db

# No path in the app.get makes this a query automatically - using ? to start the query
@app.get('/component/query')
async def get_query(name: str, age: int):
    return {'Your age is:': age, 'And your name is:': name}


'''
RESPONSE MODEL

Using the POST method, to post without using path. A way to protect private attributes of User.
It will only return the attributes of TestUser, which uses the values of User.
'''

@app.post('/api/v1/users/secret', response_model=TestUser)
async def post_user(package: User):
    return package


@app.post('/api/v1/users')
async def register_users(user: User):
    db.append(user)
    return {'user_id': user.id}


@app.put('/api/v1/users/{user_id}')
async def update_users(user_update: UpdateUser, user_id: UUID):
    for user in db:
        if user.id == user_id:
            if user.first_name is not None:
                user.first_name = user_update.first_name
            if user.middle_name is None:
                user.middle_name = user_update.middle_name
            if user.last_name is not None:
                user.last_name = user_update.last_name
            if user.roles is not None:
                user.roles = user_update.roles
            return
    raise HTTPException(
        status_code=404,
        detail=f'User with id:{user_id} not in database. '
    )


@app.delete('/api/v1/users/{user_id}')
async def delete_user(user_id: UUID):
    for user in db:
        if user.id == user_id:
            db.remove(user)
            return
    raise HTTPException(
        status_code=404,
        detail=f'User with id {user_id} does not exist'
    )




