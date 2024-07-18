import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason, Image
import vertexai.preview.generative_models as generative_models
import google.generativeai as genai
import google.ai.generativelanguage as glm
from dotenv import load_dotenv
import os

# Load the environment variables
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

PROJECT_ID = 'eighth-server-424121-b6'
REGION = "us-central1"
vertexai.init(project=PROJECT_ID, location=REGION)
vertexai.init(project="eighth-server-424121-b6", location="us-central1")

MODEL_NAME = "gemini-1.5-pro-preview-0514"

def generate_response(system_prompt, user_prompt, model_name="gemini-1.5-pro-preview-0514", n=1, max_output_tokens=8192, temperature=1, top_p=0.95):
  model = GenerativeModel(model_name, system_instruction=system_prompt)

  generation_config = {
    "max_output_tokens": max_output_tokens,
    "temperature": temperature,
    "top_p": top_p
  }

  res = []
  
  for i in range(n):
    response = model.generate_content(
        [user_prompt],
        generation_config=generation_config
    )

    res.append(response.candidates[0].text)


  return res
