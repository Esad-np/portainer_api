import os

username = os.environ.get("PORTAINER_USERNAME")

if username is None:
   raise RuntimeError("PORTAINER_USERNAME not set")
else:
   print(f"PORTAINER_USERNAME is {username}")