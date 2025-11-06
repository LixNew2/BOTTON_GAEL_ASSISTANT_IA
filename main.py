from Assistant import Assistant
from Ol import get_models
import os

if __name__ == '__main__':
    models = get_models()
    assistant = Assistant(models[0])
    while True:
        user_input = input('>> ')
        user_input_split = user_input.split(' ')
        if(user_input_split[0] == '/load'):
            path =user_input_split[1]
            if(os.path.exists(path)):
                assistant.load_context(path)
        elif(user_input_split[0] == '/loadchat'):
            assistant.load_chat(user_input_split[1])
        elif(user_input_split[0] == '/newchat'):
            assistant.new_chat()
        else:
            response = assistant.generate_code(user_input)
            print('\n' + str(response) + '\n')