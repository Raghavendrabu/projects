users = {
"alice": {"password": "alice123", "role": "admin"},
"bob": {"password": "bob123", "role": "student"},
"charlie": {"password": "charlie123", "role": "faculty"}
}
permissions = {
"admin": ["read", "write", "delete"],
"faculty": ["read", "write"],
"student": ["read"]
}
username = input("Username: ")
password = input("Password: ")
if username not in users:
   print("User does not exist")
elif users[username]["password"] != password:
   print("Authentication Failed")
else:role = users[username]["role"]
print("Authentication Successful")
print("Role:", role)
action = input("Action (read/write/delete): ")
if action in permissions[role]:
   print("Access Granted")
else:
   print("Access Denied")