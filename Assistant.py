from Ol import chat
import re, json, os, uuid

class Assistant:
    def __init__(self, model : str) -> None:
        self.model = model
        self.paterns = [ r'```([^`]*)```'  , r'```python\n(.*?)```']
        self.context = []
        self.history = []
        self.system_content = """
                    Tu es un assistant utile qui explique le code.
                    Si tu juges que la demande de l’utilisateur correspond à une création ou une modification par rapport à un fichier, et que le nom du fichier n’est pas précisé, crée-en un pertinent en lien avec la demande de l’utilisateur. Si l’utilisateur a précisé le nom du fichier, utilise le nom donné par l’utilisateur. Dans les deux cas, renvoie dans ta réponse : FICHIER : nom_du_fichier. Renvoie simplement cette information, sans l’englober avec des caractères spéciaux, laisse-la telle quelle.
                    Si la demande de l'utilisateur correspond simplement à une demande où il ne te parle pas de fichier, renvoie simplement ta réponse, sans nom de fichier.
                    Quand tu génères du code, englobe-le simplement avec trois accents graves. Ne rajoute pas le nom du langage. Mets juste au début et à la fin du code ```.
                """
        self.replacer = ['`', 'python']
        self.current_session = ""

        self.load_history()
        
    
    def load_history(self, chat = None) -> None:
        if(chat):
            if(os.path.exists(f"./sessions/{chat}.json")):
                with open(f'./sessions/{chat}.json', 'r') as f:
                    self.history = (json.load(f))
                self.current_session = chat
            
            return

        sessions = os.listdir('./sessions')

        if(sessions):
            self.current_session = sessions[-1]
            with open(f'./sessions/{self.current_session}', 'r') as f:
                self.history = (json.load(f))
        else:
            self.history.append({
                "role": "system", 
                "content": self.system_content
                })

    def append_history(self, role : str, message : str) -> None:
        self.history.append({
                'role' : role,
                'content' : message
                })

    def generate_code(self, prompt : str, temperature : int = 0.3) -> str:
        try:
            self.append_history('user', prompt)

            assistant_response = chat({
                'model' : self.model,
                'context' : self.history,
                'options' : {
                    'temperature' : temperature
                }
            })

            content = assistant_response['message']['content']
            self.edit_file(content)
            self.append_history('assistant', content)
            self.save_history()
            return content
        except Exception as e:
            print(e)

    def edit_file(self, content : str) -> None:
        match = re.search(r'FICHIER\s*:\s*(\S+)', content)

        if(match):
            try:
                filename = match.group(1)
                with open(f'./{filename}', 'w') as f:
                    f.write(self.extract_code(content))
            except Exception:
                print('System : Error opening file')

    def save_history(self):
        json_str = json.dumps(self.history, indent=2)

        if(not self.current_session):
            self.current_session = uuid.uuid4()
            
        with open(f'./sessions/{self.current_session}.json', 'w') as f:
            f.write(json_str)

    def extract_code(self, response) -> str:
        global code
        code = response

        for patern in self.paterns:
            match = re.search(patern, response)
            if(match):
                code =  match.group(1)

        return self.replace_code(code)
    
    def replace_code(self, code):
        new_code = code
        for replace in self.replacer:
            new_code.replace(replace, '')

        return new_code

    def load_context(self, project_path = '.') -> None:
        files = os.listdir(project_path)
        files.remove('__pycache__')
        files.remove('sessions')
        files.remove('.vscode')

        for file in files:
            with open(file, 'r') as f:
                self.context.append({"file" : file, 'content' : f.read()})  

        print(f'>> ✓ Project has been loaded, {len(files)} files\n')
        
        self.append_history("system", f"Project context : {self.context}")
        
        self.save_history()

    def load_chat(self, chat : str):
        self.clear_all_context()
        self.load_history(chat)
        print(f"Chat loaded : {chat}")

    def new_chat(self):
        self.clear_all_context()
        chat = uuid.uuid4()
        self.current_session = chat
        self.history.append({
                "role": "system", 
                "content": self.system_content
                }) 
        self.save_history()
        print(f"New chat : {chat}")

    def clear_all_context(self):
        self.history = []
        self.context = []
        self.current_session = ""
