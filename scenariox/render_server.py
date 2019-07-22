#!/usr/bin/env python3
import bottle
import os

class RenderServer():
    app = None
    
    def __init__(self, port):
        self.app = self.server("RenderServer")
        bottle.TEMPLATE_PATH.insert(0,'views')
        bottle.run(self.app, reloader=False, host='0.0.0.0', port=port)

    class server(bottle.Bottle):
        def __init__(self, name):
            super().__init__()
            self.name = name
            self.route('/', callback=self.index)
            self.route('/diagram', callback=self.diagram)
            self.route('/files/<filename:path>', callback=self.static_files)
            
        def index(self):
            return "index"

        @bottle.view('diagram')
        def diagram(self):
            return {'file' : "/files/diagram.bpmn"}

        @bottle.route('/files/<filename:path>')
        def static_files(self, filename):
            return bottle.static_file(filename, root='./')
