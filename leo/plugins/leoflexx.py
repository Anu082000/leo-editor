# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20181103094900.1: * @file leoflexx.py
#@@first
#@@language python
#@@tabwidth -4
'''
A Stand-alone prototype for Leo using flexx.
'''
import os
import sys
from flexx import flx
# import pscript ; assert pscript
#@+others
#@+node:ekr.20181103151350.1: **  init
def init():
    # At present, leoflexx is not a true plugin.
    # I am executing leoflexx.py from an external script.
    return False
#@+node:ekr.20181106070010.1: ** Python side classes
#@+node:ekr.20181104174357.1: *3* class LeoGui (object)
class LeoGui (object): ### flx.PyComponent):
    '''
    A class representing Leo's Browser gui and
    utils for converting data between Python and JS.
    '''
   
    #@+others
    #@+node:ekr.20181106070704.1: *4* gui.runMainLoop
    def runMainLoop(self):
        '''The main loop for the flexx gui.'''
            
    #@+node:ekr.20181105091545.1: *4* gui.open_bridge
    def open_bridge(self):
        '''Can't be in JS.'''
        import leo.core.leoBridge as leoBridge
        bridge = leoBridge.controller(gui = None,
            loadPlugins = False,
            readSettings = False,
            silent = False,
            tracePlugins = False,
            verbose = False, # True: prints log messages.
        )
        if not bridge.isOpen():
            print('Error opening leoBridge')
            return
        g = bridge.globals()
        path = g.os_path_finalize_join(g.app.loadDir, '..', 'core', 'LeoPy.leo')
        if not os.path.exists(path):
            print('open_bridge: does not exist:', path)
            return
        c = bridge.openLeoFile(path)
        ### runUnitTests(c, g)
        return c, g
    #@+node:ekr.20181105160448.1: *4* gui.find_body
    def find_body(self, c):
        for p in c.p.self_and_siblings():
            if p.b.strip():
                return p.b
        return ''
    #@+node:ekr.20181105095150.1: *4* gui.make_outline_list
    def make_outline_list(self, c):
        '''
        Make a serializable representation of the outline for the LeoTree
        class.
        '''
        return [(p.archivedPosition(), p.gnx, p.h) for p in c.all_positions()]
    #@-others

       
#@+node:ekr.20181106073959.1: *3* class LeoStore (PyComponent)
class LeoStore(flx.PyComponent):
    pass
#@+node:ekr.20181104082144.1: ** class LeoBody
base_url = 'https://cdnjs.cloudflare.com/ajax/libs/ace/1.2.6/'
flx.assets.associate_asset(__name__, base_url + 'ace.js')
flx.assets.associate_asset(__name__, base_url + 'mode-python.js')
flx.assets.associate_asset(__name__, base_url + 'theme-solarized_dark.js')

class LeoBody(flx.Widget):
    
    """ A CodeEditor widget based on Ace.
    """

    CSS = """
    .flx-CodeEditor > .ace {
        width: 100%;
        height: 100%;
    }
    """

    def init(self):
        global body, window
        self.ace = window.ace.edit(self.node, "editor")
        self.ace.setValue(body)
        self.ace.navigateFileEnd()  # otherwise all lines highlighted
        self.ace.setTheme("ace/theme/solarized_dark")
        self.ace.getSession().setMode("ace/mode/python")

    @flx.reaction('size')
    def __on_size(self, *events):
        self.ace.resize()
#@+node:ekr.20181104082149.1: ** class LeoLog
class LeoLog(flx.Widget):

    CSS = """
    .flx-CodeEditor > .ace {
        width: 100%;
        height: 100%;
    }
    """

    def init(self):
        global window
        self.ace = window.ace.edit(self.node, "editor")
        self.ace.navigateFileEnd()  # otherwise all lines highlighted
        # pscript.RawJS('''
            # var el = $(the_element);
            # var editor = el.data('ace').editor;
            # editor.$blockScrolling = Infinity;
        # ''')
        self.ace.setTheme("ace/theme/solarized_dark")
        
    def put(self, s):
        self.ace.setValue(self.ace.getValue() + '\n' + s)

    @flx.reaction('size')
    def __on_size(self, *events):
        self.ace.resize()
#@+node:ekr.20181104082130.1: ** class LeoMainWindow
class LeoMainWindow(flx.Widget):
    
    def init(self):
        global main_window
        main_window = self
        with flx.VBox():
            with flx.HBox(flex=1):
                self.tree = LeoTree(flex=1)
                self.log = LeoLog(flex=1)
            self.body = LeoBody(flex=1)
            self.minibuffer = LeoMiniBuffer()
            self.status_line = LeoStatusLine()
#@+node:ekr.20181104082154.1: ** class LeoMiniBuffer
class LeoMiniBuffer(flx.Widget):
    
    def init(self): 
        with flx.HBox():
            flx.Label(text='Minibuffer')
            self.widget = flx.LineEdit(
                flex=1, placeholder_text='Enter command')
        self.widget.apply_style('background: yellow')
#@+node:ekr.20181104082201.1: ** class LeoStatusLine
class LeoStatusLine(flx.Widget):
    
    def init(self):
        with flx.HBox():
            flx.Label(text='Status Line')
            self.widget = flx.LineEdit(flex=1, placeholder_text='Status')
        self.widget.apply_style('background: green')
#@+node:ekr.20181104082138.1: ** class LeoTree
class LeoTree(flx.Widget):

    CSS = '''
    .flx-TreeWidget {
        background: #000;
        color: white;
        /* background: #ffffec; */
        /* Leo Yellow */
        /* color: #afa; */
    }
    '''
    def init(self):
        with flx.TreeWidget(flex=1, max_selected=1) as self.tree:
            self.make_tree()

    #@+others
    #@+node:ekr.20181105045657.1: *3* tree.make_tree
    def make_tree(self):
        
        global outline_list
        stack = []
        for archived_position, gnx, h in outline_list:
            n = len(archived_position)
            if n == 1:
                item = flx.TreeItem(text=h, checked=None, collapsed=True)
                stack = [item]
            elif n in (2, 3):
                # Fully expanding the stack takes too long.
                stack = stack[:n-1]
                with stack[-1]:
                    item = flx.TreeItem(text=h, checked=None, collapsed=True)
                    stack.append(item)
    #@+node:ekr.20181104080854.3: *3* tree.on_event
    @flx.reaction(
        'tree.children**.checked',
        'tree.children**.selected',
        'tree.children**.collapsed',
    )
    def on_event(self, *events):
        
        global main_window
        for ev in events:
            id_ = ev.source.title or ev.source.text
            kind = '' if ev.new_value else 'un-'
            main_window.log.put('%s: %s' % (kind + ev.type, id_))
    #@-others
#@-others
if __name__ == '__main__':
    # Create the gui class.
    # JS can *not* use gui if LeoGui derives from object!
    gui = LeoGui()
    # Create the *python* globals.
    c, g = gui.open_bridge()
    outline_list = gui.make_outline_list(c)
    body = gui.find_body(c)
    main_window = None
    # Start the JS code.
    # JS can not access Leo's c and p vars!
    flx.launch(LeoMainWindow, runtime='firefox-browser')
        # Create the session.
        # LeoGui must have a session if it is a subclass of PyComponent.
    if c and g:
        flx.run()
    else:
        sys.exit(1)
#@-leo
