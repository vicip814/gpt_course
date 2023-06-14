import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")


prompt="what is semantic search"
completion = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "user", "content": prompt}
  ]
)

print(completion.choices[0].message)

 