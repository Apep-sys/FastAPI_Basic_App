from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import  CryptContext
from pydantic import BaseModel

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

users_db = {
    'johndoe': {
    'username': 'johndoe',
    'full_name': 'John Doe',
    'email': 'johndoe@example.com',
    'hashed_password': 'hash-pass-john',
    'disabled': False,
},
    'alice': {
    'username': 'alice',
    'full_name': 'Alice Wonderlaya',
    'email': 'alice@example.com',
    'hashed_password': 'hash-pass-alice',
    'disabled': True,
    }
}

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


class Token(BaseModel):
    accest_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]       # user_dict will contain the data of the username from the database ex. data: fullname, mail etc.
        return UserInDB(**user_dict)   # returns an unwrapped object representing the user with all data as key-value pairs

def verify_pass(plain_pass, hashed_pass):
    return pwd_context.verify(plain_pass, hashed_pass)


def get_hash_pass(password):
    return pwd_context.hash(password)


def fake_decode_token(token):
    user = get_user(users_db, token)
    return user


def authenticate_user(users_db, username: str, password: str):
    user = get_user(users_db, username)
    if not user:
        return False
    if not verify_pass(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# This is the authentication - AKA introducing username and password in the form fields
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):  # Annotated = token: str = Depends(oauth2_scheme)
    # oauth2_scheme is a callable object, FastAPI knows it defines a security scheme - it's a dependency

    # Define the HTTP Error that will be raised
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,   # If the user is not correctly authenticated, raise errpr
            detail='Invalid authentication credentials',
            headers={'WWW-Authenticate': 'Bearer'}) # The 401 status code must return this header, using Bearer bcs Bearer tokens

    # If
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(users_db, username=token_data.username)
    # If the unwrapped user data is not there, the user does not exist
    if user is None:
        raise credentials_exception
    return user


# Only if the user is active will he proceed
async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user


@app.post('/token')         # OAUTH2PasswordRequestForm declares a form body with username, password, scope, client id/secret
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):

    # We get the user data from the database using the 'username' from the form field, or raise exception if there isnt any user
    user_dict = authenticate_user(users_db, form_data.username, form_data.password)    # user_dict will be a dictionary made of the data of the user - fullname, mail etc.
    if not user_dict:                               # if the introduced username isnt in the database, it raises error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_tokendata = {'sub': user_dict.username}
    expires_delta = access_token_expires
    # JSON keys must always be access_token and token_type
    return {'access_token': access_token, 'token_type': 'bearer'}  # response of token ENDPOINT must be JSON object
'''
# Unwrap the dictionary user_dict as key-value pairs in UserInDB - Check user_in.dict documentation
# meaning the data of a single user, in dict form, will be put individually as the values of the keys with the same name - username, mail, fullname
user = UserInDB(**user_dict)
hashed_password = fake_hash_password(form_data.password)    # Hash the introduced password
if not hashed_password == user.hashed_password:     # If the hashed password is not in the user's data, raise error
return HTTPException(status_code=400, detail='Incorrect username or password')'''


@app.get('/users/me')
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


@app.get('/items/')
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {'token:', token}
