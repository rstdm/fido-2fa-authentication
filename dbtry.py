from tinydb import TinyDB, Query
from userManagament import User
from json import loads, dumps

#db = TinyDB('usertest.json')


testUser = User("test user", "test password", "test passwordSalt", "test fidoInfo", "test sessionID", "test firstName", "test lastName")

# user to json
userJson = testUser.__dict__
print(userJson)

# json to user
user = User(**userJson)
print(user)

