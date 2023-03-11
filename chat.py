from transformers import pipeline

CHAT_TEMPLATE = '''This is a conversion between a really sad chatbot named SadGPT and a user
###
[User]: Hi.
[EdgeGPT]: Hello!
###
[User]: What is your name?
[EdgeGPT]: My name is SadGPT.'''

class ChatBot:
    def __init__(self, model_name:str):
        '''
            Initialize the chatbot

            args:
            ---------
            model_name: str
                Name of the model to use
        '''
        self.chatbot = pipeline('text-generation', model=model_name, tokenizer='GPT2')
        self.chat_history = CHAT_TEMPLATE

    def generate_reply(self, text:str) -> str:
        '''
            Generate a reply from the chatbot

            args:
            ---------
            text: str
                Text to generate a reply from

            Returns
            -------
            str
                Generated reply
        '''
        prompt = self.chat_history + '###\n[User]: ' + text + '\n[EdgeGPT]: '
        prompt_len = len(prompt.split())
        response = self.chatbot(prompt, max_length= 4 * prompt_len, num_return_sequences=1)[0]['generated_text']
        response = response.split('[EdgeGPT]: ')[-1].split('\n')[0]
        response = response.replace(u'\xa0', u'')
        response = response.replace('  ', '')
        self.chat_history = prompt + response
        return response
