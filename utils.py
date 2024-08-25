import json

def read_message_from_file(file_path: str):
    with open(file_path, encoding='utf-8') as f:
        return f.read()

def get_json(file_path: str):
    with open(file_path, encoding='utf-8') as f:
        return json.load(f)

def update_json(file_path:str, prop_key: str, value):

    file_data = get_json(file_path)
    file_data[prop_key] = value
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(file_data, f)

def update_props(prop_key: str, value):
    update_json('props.json', 'allow_twitter_posting', value)
