import os
from dotenv import *
from flask import Flask, request, jsonify
from jsonschema import validate, ValidationError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app) 

load_dotenv()

api_key = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key=api_key)

generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
    safety_settings=safety_settings
)

prompt_parts = [
  "You create themes for Meower. Do not change any of the variable names, only their values! The only values should be \"orange\" (main color), \"orangeLight\" (main color but lighter), \"orangeDark\" (main color but darker). \"background\" (the background color), \"foreground\" (mainly used for text and a few other things), \"foregroundOrange\" (used for outlines of buttons) and \"tinting\" (used for tinting)",
  "input: The default orange theme",
  "output: {\"v\":1,\"orange\":\"#f9a636\",\"orangeLight\":\"#ffcb5b\",\"orangeDark\":\"#d48111\",\"background\":\"#ffffff\",\"foreground\":\"#000000\",\"foregroundOrange\":\"#ffffff\",\"tinting\":\"#252525\"}",
  "input: The default orange theme but turqouise",
  "output: {\"v\":1,\"orange\":\"#2ec4b6\",\"background\":\"#ffffff\",\"foreground\":\"#000000\",\"foregroundOrange\":\"#ffffff\",\"tinting\":\"#252525\",\"orangeLight\":\"#53e9db\",\"orangeDark\":\"#099f91\"}",
  "input: A red theme with dark mode",
  "output: {\"v\":1,\"orange\":\"#e62739\",\"orangeLight\":\"#ff6974\",\"orangeDark\":\"#bf001d\",\"background\":\"#181818\",\"foreground\":\"#ffffff\",\"foregroundOrange\":\"#ffffff\",\"tinting\":\"#252525\"}",
  "input: A dark mode green theme",
  "output: {\"v\":1,\"orange\":\"#28b485\",\"orangeLight\":\"#52d8a8\",\"orangeDark\":\"#008e60\",\"background\":\"#181818\",\"foreground\":\"#ffffff\",\"foregroundOrange\":\"#ffffff\",\"tinting\":\"#252525\"}",
  "input: Android holo ui colours with dark background and blue accents",
  "output: {\"v\":1,\"orange\":\"#0099cc\",\"background\":\"#090909\",\"foreground\":\"#ffffff\",\"foregroundOrange\":\"#C5EAF8\",\"tinting\":\"#001820\",\"orangeLight\":\"#00b1ec\",\"orangeDark\":\"#0081ac\"}",
  "input: A dark mint-green theme with dark-green tinting",
  "output: {\"v\":1,\"orange\":\"#2e8b57\",\"orangeLight\":\"#64d88d\",\"orangeDark\":\"#00693e\",\"background\":\"#181818\",\"foreground\":\"#ffffff\",\"foregroundOrange\":\"#ffffff\",\"tinting\":\"#00301b\"}",
  "input: Light caramel colored background and and main color with white tinting",
  "output: {\"v\":1,\"orange\":\"#c39f81\",\"orangeLight\":\"#f6d7b8\",\"orangeDark\":\"#97755d\",\"background\":\"#f6d7b8\",\"foreground\":\"#000000\",\"foregroundOrange\":\"#000000\",\"tinting\":\"#ffffff\"}",
  "input: A pitch black AMOLED theme with cool cyan accents",
  "output: {\"v\":1,\"orange\":\"#00bfff\",\"orangeLight\":\"#33e0ff\",\"orangeDark\":\"#008cba\",\"background\":\"#000000\",\"foreground\":\"#ffffff\",\"foregroundOrange\":\"#ffffff\",\"tinting\":\"#00171f\"}",
  "input: ",
  "output: ",
]

request_schema = {
    "type": "object",
    "properties": {
        "style": {"type": "string"}
    },
    "required": ["style"]
}

limiter = Limiter(app, default_limits=["3 per minute"])

@app.route('/generate-theme', methods=['POST'])
@limiter.limit("1 per second")  # Additional rate limit of 1 request per second
def generate_theme():
    try:
        # Validate the JSON payload against the schema
        validate(request.json, request_schema)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    user_style = request.json['style']
    prompt_parts.append(f"input: {user_style}")
    
    response = model.generate_content(prompt_parts)
    return response.text


if __name__ == '__main__':
    app.run()
