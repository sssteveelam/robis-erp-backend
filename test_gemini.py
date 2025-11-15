import google.generativeai as genai

# Replace 'YOUR_API_KEY' with your actual Gemini API key
genai.configure(api_key="AIzaSyAAVdBeckk-ynYxbNkASbZWil8EhAIZo_o")

# Now you can interact with the models
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content("Write a short story about a cat.")
print(response.text)
