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



def insertIntoDB(user): #firstname, lastname, username, password, passwordSalt, sessionID):
    print("\n########## insertIntoDB ##############\n")
    db.insert(
        {'firstname': user.firstName,
         'lastname': user.lastName,
         'username': user.userName,
         'password': user.password,
         'passwordSalt': user.passwordSalt,
         'sessionID' : user.sessionID,
         'credentials': "CREDENTIALS",
         'cur_aaguid' : "00000000-0000-0000-0000-000000000000",
         'cur_credential_id': 'b\xc2\x9ar\xc3\xb0\xc3\xb0\xc2\x98\x1f5b\xc2\x81\x0e\xc3\x89\xc3\xbc\xc2\xafe\xc2\x88",/K\xc3\x98X\xc3\xb4\xc3\xae\x11"Y\xc2\x92\x0fhn\xc2\xb5\x11\x0e\xc2\x85\xc2\xaf\xc2\x96\xc2\xb8\xc2\x98\xc2\xaek\x1c\xc3\x9c:\xc2\x96X\xc2\x9c\x07\xc3\xa6\xc3\x81\xc2\x92\xc2\xbc\xc3\xa0Vk\x1b+UzT3\xc2\xa17\xc3\xa0',
         'cur_public_key' : "{1: 2, 3: -7, -1: 1, -2: b'\xce\x8f\xda\xf2\x96\x7fH\xdan\xbb\xc2\xcdH\xe5>\xb1#\xc5\x84YY\x02I:m\xd0V\x84\xafs\x8c\xb9', -3: b'\x01\xc1\xad\xdc\x1f\x99h\xbdE\x9d.\xad\x01$\xd2\xf2\xec#\xd7O\xfc\xa3&q\xa8\x9c3j\x84w\xe9\x11'}",
         'fido': 0
        }
    )
