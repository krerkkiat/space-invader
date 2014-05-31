class Registerer:
    def __init__(self, client):
        client.attach(self)
        
        self.con = False

        # client.setOutMessage('''{"type":"action","value":"get","target":"resource_register_data"}''')
    def update(self, msg):
        if msg['target'] == 'resource_register_data':
            data = msg['data']
            self.regisSurface(data['surface'])
            self.con = True

    def regisSurface(self, data):
        for id_ in data:
            color_key = 'color_key' in data[id_]
            convert_alpha = 'convert_alpha' in data[id_]

            if color_key and convert_alpha:
                SurfaceManager.register(id_, os.path.join(Config.assetsRoot, data[id_]['path']), color_key=tuple(data[id_]['color_key']), convert_alpha=data[id_]['convert_alpha'])
            elif convert_alpha:
                SurfaceManager.register(id_, os.path.join(Config.assetsRoot, data[id_]['path']), convert_alpha=data[id_]['convert_alpha'])
            elif color_key:
                SurfaceManager.register(id_, os.path.join(Config.assetsRoot, data[id_]['path']), color_key=tuple(data[id_]['color_key']))