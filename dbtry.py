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