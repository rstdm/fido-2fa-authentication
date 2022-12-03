from tinydb import TinyDB, Query

db = TinyDB('db.json')

def main():
    run = 1
    while run:
        print("\n********** main **********\n")

        print("    Create User: 1\n")
        print("    Print User: 2\n")
        print("    Remove User: 3\n")
        print("    Update User FIDO: 4\n")

        print("    Terminate program: 5\n")

        choice = int(input("    Choose: "))

        if choice == 1:
            createUser()
        elif choice == 2:
            queryUser()
        elif choice == 3:
            removeUser()
        elif choice == 4:
            fidoUpdate()
        elif choice > 5:
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

def insertIntoDB(firstname, lastname, username, password):
    print("\n########## insertIntoDB ##############\n")
    db.insert(
        {'nr': len(db) + 1,
         'firstname': firstname,
         'lastname': lastname,
         'username': username,
         'password': password,
         'fido': 0
        }
    )

def queryUserDB(username, password):
    print("\n########## queryUserDB ##############\n")

    user_query = Query()
    
    user = db.search(user_query.username == username)
#    print(user)

    print("    Requested User")
    print(f"        User Firstname: {user[0]['firstname']}")
    print(f"        User Lastname: {user[0]['lastname']}")
    print(f"        User Username: {user[0]['username']}")
    print(f"        User Passwort: {user[0]['password']}")
    print(f"        User FidoActive: {user[0]['fido']}")

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

if __name__ == "__main__":
    main()