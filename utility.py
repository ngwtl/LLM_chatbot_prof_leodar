import re
import json
from trycourier import Courier
import secrets
from argon2 import PasswordHasher
import requests

ph = PasswordHasher()

def check_user_password(username: str, password: str) -> bool:
  #authenticate username and password

  with open("_secret_auth_.json", "r") as auth_json:
    authorized_users_data = json.load(auth_json)
  
  '''
  for registered_user in authorized_users_data:
      if registered_user['username']==username:
        try:
          passwd_verification_bool = ph.verify(registered_user['password'], password)
          if passwd_verification_bool == True:
              return True
        except:
          pass
  '''
  
  usernames = [i['username'] for i in authorized_users_data]
  passwords = [i['password'] for i in authorized_users_data]

  try:
    index = usernames.index(username)
    passwd_verfiication_bool = ph.verify(passwords[index], password)
    if passwd_verification_bool == True:
        return True
  except:
    pass
  
  return False

def load_lottieurl(url: str) -> str:
  #fetch lottie animation URL
  try:
      r = requests.get(url)
      if r.status_code != 200:
          return None
      return r.json()
  except:
      pass

def check_valid_name(name_sign_up: str) -> bool:
  #check username format
  name_regex = (r'^[A-Za-z_][A-Za-z0-9_]*')

  if re.search(name_regex, name_sign_up):
      return True
  return False

def check_valid_email(email_sign_up: str) -> bool:
  #check email format
  regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

  if re.fullmatch(regex, email_sign_up):
      return True
  return False

def check_unique_email(email_sign_up: str) -> bool:
  #check for unique email
  authorized_user_data_master = list()
  with open("_secret_auth_.json", "r") as auth_json:
      authorized_users_data = json.load(auth_json)
     
  authorized_user_data_master = [i['email'] for i in authorized_users_data]
  if email_sign_up in authorized_user_data_master:
      return False
  return True

def non_empty_str_check(username_sign_up: str) -> bool:
  #check empty strings
  empty_count = 0
  for i in username_sign_up:
      if i == ' ':
          empty_count = empty_count + 1
          if empty_count == len(username_sign_up):
              return False

  if not username_sign_up:
      return False
  return True

def check_unique_usr(username_sign_up: str):
  #check for unique username
  authorized_user_data_master = list()
  with open("_secret_auth_.json", "r") as auth_json:
      authorized_users_data = json.load(auth_json)

  authorized_user_data_master = [i['username'] for i in authorized_users_data]
  if username_sign_up in authorized_user_data_master:
      return False
  
  non_empty_check = non_empty_str_check(username_sign_up)

  if non_empty_check == False:
      return None
  return True

def register_new_usr(name_sign_up: str, email_sign_up: str, username_sign_up: str, password_sign_up: str) -> None:
  #save user info
  new_usr_data = {'username': username_sign_up, 'name': name_sign_up, 'email': email_sign_up, 'password': ph.hash(password_sign_up)}

  with open("_secret_auth_.json", "r") as auth_json:
      authorized_users_data = json.load(auth_json)

  with open("_secret_auth_.json", "w") as auth_json_write:
      authorized_users_data.append(new_usr_data)
      json.dump(authorized_users_data, auth_json_write)

def check_username_exists(user_name: str) -> bool:
  #check if username exists
  authorized_user_data_master = list()
  with open("_secret_auth_.json", "r") as auth_json:
      authorized_users_data = json.load(auth_json)

  authorized_user_data_master = [i['username'] for i in authorized_users_data]
  if user_name in authorized_user_data_master:
      return True
  return False

def check_email_exists(email_forgot_passwd: str):
  #check for existing email
  with open("_secret_auth_.json", "r") as auth_json:
      authorized_users_data = json.load(auth_json)

      for user in authorized_users_data:
          if user['email'] == email_forgot_passwd:
                  return True, user['username']
  return False, None

def generate_random_passwd() -> str:
  #generate random password
  password_length = 10
  return secrets.token_urlsafe(password_length)

def send_passwd_in_email(auth_token: str, username_forgot_passwd: str, email_forgot_passwd: str, app_name: str, random_password: str) -> None:
  #send email using random password
  client = Courier(auth_token = auth_token)

  resp = client.send_message(
  message={
      "to": {
      "email": email_forgot_passwd
      },
      "content": {
      "title": app_name + ": Login Password!",
      "body": "Hi! " + username_forgot_passwd + "," + "\n" + "\n" + "Your temporary login password is: " + random_password  + "\n" + "\n" + "{{info}}"
      },
      "data":{
      "info": "Please reset your password at the earliest for security reasons."
      }
  }
  )

def change_passwd(email_: str, random_password: str) -> None:
  #replace passwords
  with open("_secret_auth_.json", "r") as auth_json:
      authorized_users_data = json.load(auth_json)

  with open("_secret_auth_.json", "w") as auth_json_:
      for user in authorized_users_data:
          if user['email'] == email_:
              user['password'] = ph.hash(random_password)
      json.dump(authorized_users_data, auth_json_)

def check_current_passwd(email_reset_passwd: str, current_passwd: str) -> bool:
  #check password for reset 
    with open("_secret_auth_.json", "r") as auth_json:
        authorized_users_data = json.load(auth_json)

        for user in authorized_users_data:
            if user['email'] == email_reset_passwd:
                try:
                    if ph.verify(user['password'], current_passwd) == True:
                        return True
                except:
                    pass
    return False 

# Author: Thway
# GitHub: https://github.com/mgthway/llm_chatbot/
