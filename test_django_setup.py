import os

print("step 1")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "herbapi.settings")

print("step 2")
import django

print("step 3")
django.setup()

print("step 4")