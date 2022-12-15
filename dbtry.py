from tinydb import TinyDB, Query
import userManagament as userm

db = TinyDB('db.json')

def main():
    run = 1
    while run:
        print("\n********** main **********\n")

        print("    Create User: 1\n")
        print("    Print User: 2\n")
        print("    Remove User: 3\n")
        print("    Update User FIDO: 4\n")
        print("    List all User: 5\n")
        print("    Check User Exists: 6\n")

        print("    Terminate program: 10\n")

        choice = int(input("    Choose: "))

        if choice == 1:
            createUser()
        elif choice == 2:
            queryUser()
        elif choice == 3:
            removeUser()
        elif choice == 4:
            fidoUpdate()
        elif choice == 5:
            listAllUser()
        elif choice == 6:
            checkIfUserExists()
        elif choice > 10:
            run = 0


def createUser():
    print("\n########## createUser ##############\n")

    firstname = input("    Firstname: ")
    lastname = input("    Lastname: ")
    username = input("    Username: ")
    password = input("    Password: ")

    insertIntoDB(firstname, lastname, username, password)

def queryUser():
    print("\n########## queryUser ##############\n")

    username = input("    Username: ")
    password = input("    Password: ")

    queryUserDB(username, password)

def fidoUpdate():
    print("\n########## fidoUpdate ##############\n")

    firstname = input("    Firstname: ")
    lastname = input("    Lastname: ")

    updateFidoUserDB(firstname, lastname)

def removeUser():
    print("\n########## removeUser ##############\n")

    firstname = input("    Firstname: ")
    lastname = input("    Lastname: ")

    removeFromDB(firstname, lastname)

def listAllUser():
    print("\n########## listAllUser ##############\n")

    listAllUserDB()

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

def checkIfUserExists():#(username, password) -> bool:
    print("\n########## checkIfUserExists ##############\n")
    username = input("    Username: ")
    if userExists(username):
        print("Exists")
    else:
        print("Dont Exists")

def userExists(username) -> bool:
    print("\n########## userExists ##############\n")
    user_query = Query()
    user = db.search(user_query.username == username)
    #print(user)
    if len(user) == 1:
        return True
    else:
        return False

def queryUserDB(username, password) -> bool:
    print("\n########## queryUserDB ##############\n")

    user_query = Query()
    
    user = db.search(user_query.username == username)
    print(user)

    if userm.checkPassword2(password, user[0]['passwordSalt'], user[0]['password']):
        print("    Password was correct following User Data")
        print("    Requested User")
        print(f"        User Firstname: {user[0]['firstname']}")
        print(f"        User Lastname: {user[0]['lastname']}")
        print(f"        User Username: {user[0]['username']}")
        print(f"        User Passwort: {user[0]['password']}")
        print(f"        User Passwort Salt: {user[0]['passwordSalt']}")
        print(f"        User sessionID: {user[0]['sessionID']}")
        print(f"        User credentials: {user[0]['credentials']}")
        print(f"        User FidoActive: {user[0]['fido']}")
        return True
    else:
        print("    Wrong Password")
        return False

    

#    print(f" Number of Items: {len(db)}")


def updateFidoUserDB(firstname, lastname):
    print("\n########## updateFidoUserDB ##############\n")

    user_query = Query()

    db.update({'fido': 1}, user_query.firstname == firstname and
                     user_query.lastname == lastname)


def removeFromDB(firstname, lastname):
    print("\n########## removeFromDB ##############\n")

    print(f" Number of Items before removal: {len(db)}")

    test = input("    Continue press Enter")

    user_query = Query()

    db.remove(user_query.firstname == firstname and
                     user_query.lastname == lastname)

    print(f" Number of Items after removal: {len(db)}")

def listAllUserDB():
    print("\n########## listAllUserDB ##############\n")

    db.all()
    
    for item in db:
        print(item)


if __name__ == "__main__":
    main()