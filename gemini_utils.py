import google.generativeai as genai

def generate_response(prompt):
    try:
        genai.configure(api_key="AIzaSyCJwGRlV4V-D8bWp79hy9u4T2r4HdazQgk")
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("Gemini Error:", e)
        return None
