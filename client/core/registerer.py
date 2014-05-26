class Registerer:
    def __init__(self, client):
        client.attach(self)
        
        client.out_buffer = '''{"type":"action","value":"get","target":"resource_register_data"}'''

    def update(self, msg):
        