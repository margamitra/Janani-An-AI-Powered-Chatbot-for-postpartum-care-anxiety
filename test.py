import openai
import re
import pyttsx3
import base64
import speech_recognition as sr
from pywebio.output import put_html, put_markdown, put_buttons, output


openai.api_key = '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'
engine = pyttsx3.init()


def get_api_response(prompt: str) -> str | None:
    text: str | None = None

    try:
        response: dict = openai.Completion.create(
            model='text-davinci-003',
            prompt=prompt,
            temperature=0.9,
            max_tokens=150,
            top_p=0.4,
            frequency_penalty=2,
            presence_penalty=0.6,
            stop=[' Human:', ' AI:']
        )

        choices: dict = response.get('choices')[0]
        text = choices.get('text')

    except Exception as e:
        print('ERROR:', e)

    return text


def update_list(message: str, pl: list[str]):
    pl.append(message)


def create_prompt(message: str, pl: list[str]) -> str:
    p_message: str = f'\nHuman: {message}'
    update_list(p_message, pl)
    prompt: str = ''.join(pl)
    return prompt


def get_bot_response(message: str, pl: list[str]) -> str:
    prompt: str = create_prompt(message, pl)
    bot_response: str = get_api_response(prompt)

    if bot_response:
        update_list(bot_response, pl)
        pos: int = bot_response.find('\nAI: ')
        bot_response = bot_response[pos + 5:]
    else:
        bot_response = 'Something went wrong...'

    return bot_response


def text_to_speech(text: str):
    engine.setProperty('rate', 205)
    engine.say(text)
    engine.runAndWait()


def get_user_audio() -> str:
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        user_audio_text = r.recognize_google(audio)
        print(f"User: {user_audio_text}")
        return user_audio_text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand what you said."
    except sr.RequestError as e:
        return "Sorry, there was an error with the speech recognition service."


def remove_bullet_points(text: str) -> str:
    # Remove bullet points using regular expressions
    return re.sub(r'\n\s*\*\s*', ' ', text)

def chatbot():
    with open('icon.png', 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    header_html = f"""
    <div style="display: flex; align-items: center; justify-content: center;">
        <img src="data:image/png;base64,{encoded_image}" alt="Icon" style="width: 128px; height: 128px; margin-right: 8px;">
        <h1 style="text-align: center; margin: 0;">Janani: The Jeevan Dayini</h1>
    </div>
    """
    put_html(header_html)

    prompt_list: list[str] = ['You need to help patients with postpartum care, anxiety and depression. Answer questions with empathy and you will show them that you care for their well being. Try to sound as human as possible. End every answer on an emphatic & inspiring note. If user asks anything related to delivery, congratulate them on their baby.',
                              '\nHuman: I am feeling depressed. Nothing just feels right. I don not like myself.',
                              '\nAI: I\nm so sorry to hear that. I totally understand how you feel. I am here to help. Remember you are not alone',
                              '\nAI: I am very glad to help you. I am always by your side & ready to assist you in every way possible !',
                              '\nHuman: Who are you ?',
                              '\nAI: Hello There ! I am Janani. Designed to help young mothers with everything related to postpartum care & people suffering from anxiety and depression. Feel free to ask me anything. I am always here in your service. Wishing you all the best with your recovery !']

    while True:
        user_input = get_user_audio()
        put_markdown(f'**You**: {user_input}')
        response = get_bot_response(user_input, prompt_list)
        put_markdown(f'**Janani**: {response}')

        response_without_bullet_points = remove_bullet_points(response)

        text_to_speech(response_without_bullet_points)


if __name__ == '__main__':
    chatbot()
