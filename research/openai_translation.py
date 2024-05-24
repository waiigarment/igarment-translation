import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key = os.getenv('OPENAI_API_KEY')
)

languages = {
    'en': 'English',
    'jp': 'Japanese',
    'vm': 'Vietnamese',
    'zh': 'Chinese'
}

def translate_with_openai(text, frLang = 'jp', toLang = 'vm'):
    # currently commented out the actual ChatGPT calling part
    return 'TRANSLATION_NOT_FOUND[chatgpt\'s result]'
    prompt = 'Translate the following %s to %s.\n\n' % (languages[frLang], languages[toLang]) + text
    completion = client.chat.completions.create(
        model = 'gpt-4',
        # Change the prompt parameter to the messages parameter
        messages = [
            {'role': 'user',
            #'content': s['_in'] % (s[toLang], text),
            'content': prompt,
            }
        ],
        temperature = 0  
    )
    return completion.choices[0].message.content