from openai import OpenAI

client = OpenAI(
    api_key="sk-proj-XXXXXXXXXXXXXXXXXXXXXXXX"
)

resp = client.responses.create(
    model="gpt-4.1-mini",
    input="ping"
)

print(resp.output_text)
