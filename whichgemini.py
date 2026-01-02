from google import genai
client = genai.Client(api_key="AIzaSyC-DOBQagfDS6fNBKdOZJQIszLeDRB1NH4")
for m in client.models.list():
    print(m.name)
