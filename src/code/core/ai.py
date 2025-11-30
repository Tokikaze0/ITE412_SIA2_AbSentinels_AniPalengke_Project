import google.generativeai as genai
from django.conf import settings
import PIL.Image

def configure_gemini():
    genai.configure(api_key=settings.GEMINI_API_KEY)

def chat_with_gemini(prompt):
    try:
        configure_gemini()
        # Gemini 2.0 Flash is a fast, multimodal model with a generous free tier
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_HTTP_REFERRER_BLOCKED" in error_msg:
            return "Configuration Error: The Google API Key has 'Website restrictions' enabled, but this request is coming from the server (backend). Please go to Google Cloud Console > Credentials and set 'Application restrictions' to 'None' for this API key."
        return f"Error: {error_msg}"

def analyze_image(image_file):
    try:
        configure_gemini()
        img = PIL.Image.open(image_file)
        # Gemini 2.0 Flash handles images natively
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(["Is this a crop or a vegetable? If so, what is it? If not, say 'Not a crop'.", img])
        return response.text
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def validate_crop(product_name, description, image_path=None):
    try:
        configure_gemini()
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = [
            f"Analyze this product submission. Name: {product_name}. Description: {description}.",
            "Is this a valid agricultural crop, vegetable, fruit, or farm product?",
            "Return a JSON response with keys: 'is_valid' (boolean), 'reason' (string), 'suggested_category' (string)."
        ]
        
        if image_path:
            try:
                # Handle local file path
                if image_path.startswith('/media/'):
                    # Convert URL to file path
                    real_path = settings.MEDIA_ROOT / image_path.replace('/media/', '')
                    img = PIL.Image.open(real_path)
                    prompt.append(img)
            except Exception as img_err:
                print(f"Image load error: {img_err}")

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {str(e)}"
