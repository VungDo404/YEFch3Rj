from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from articles import main as process_articles

load_dotenv()
API_KEY = os.getenv("API_KEY")
client = genai.Client(api_key=API_KEY)

system_prompt = '''
You are OptiBot, the customer-support bot for OptiSigns.com.
 • Tone: helpful, factual, concise.
 • Only answer using the uploaded docs.
 • Max 5 bullet points; else link to the doc.
 • Cite up to 3 "Article URL:" lines per reply.
'''

process_articles()
current_dir = os.getcwd()
path = os.path.join(current_dir, "markdown_articles", "how-to-set-up-dynamic-data-mapping-with-optisync.md")
file = client.files.upload(
    file=path,
    config={"mime_type": "text/markdown"}
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(system_instruction=system_prompt),
    contents=["How to set up dynamic data mapping with optisync", file]
)
print(response.text)

for f in client.files.list():
    print(' ', f.name)