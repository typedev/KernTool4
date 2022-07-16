from vanilla import Window
from mojo.UI import CodeEditor
# # from pygments.lexers import YamlLexer #

from pygments.lexer import RegexLexer, inherit, bygroups
from pygments.token import *
from pygments.styles import get_style_by_name
# >>> get_style_by_name('colorful') # solarized-light

txtx = """

--- 3.0	2015-04-03 10:46:36.623702436 +0300
+++ 3.1	2015-04-03 10:46:57.399761884 +0300
@ for in
-identifier  ::=  id_start id_continue*
+identifier   ::=  xid_start xid_continue*
-id_continue ::=  <all characters in id_start, plus characters in the categories Mn, Mc, Nd, Pc and others with the Other_ID_Continue property>

before: id_start     ::=  <all characters in general categories Lu, Ll, Lt, Lm, Lo, Nl, the underscore, and characters with the Other_ID_Start property>
+id_continue  ::=  <all characters in id_start, plus characters in the categories Mn, Mc, Nd, Pc and others with the Other_ID_Continue property>
after: xid_start    ::=  <all characters in id_start whose NFKC normalization is in "id_start xid_continue*">
-id_start    ::=  <all characters in general categories Lu, Ll, Lt, Lm, Lo, Nl, the underscore, and characters with the Other_ID_Start property>

+xid_continue ::=  <all characters in id_continue whose NFKC normalization is in "id_continue*">
@@ -125 +127,3 @@
* sdd
Index 3443
===================================
 <all characters in id_start whose 
 NFKC normalization is 
 in "id_start xid_continue*">
===================================
+xid_continue ::=  <all characters in id_continue whose NFKC normalization is in "id_continue*">



"""
class BaseLexer(RegexLexer):
     tokens = {
        'root': [
            (r' .*\n', Name),
            (r'before:.*\n', Keyword),
            (r'after:.*\n', Error),
            (r'@.*\n', Generic.Subheading),
            (r'\*.*\n', Generic.Heading),
            (r'=.*\n', Generic.Heading),
            # (r'Index.*\n', Keyword),
            (r'.*\n', Text),
        ]
    }  
class CodeEditorDemo(object):

    def __init__(self):
        self.w = Window((400, 600))
        self.w.codeEditor = CodeEditor((10, 10, -10, -10),
                            callback=self.codeEditorCallback,
                            showLineNumbers=True,
                            # text = '',
                            lexer = BaseLexer()
                            )
        self.w.open()
        # self.w.codeEditor.setLexer(YamlLexer()) #YamlLexer()
        self.w.codeEditor.setHighlightStyle(get_style_by_name('material')) # solarized-light)
        
        self.w.codeEditor.set(txtx)

    def codeEditorCallback(self, sender):
        print("text entry!", sender.get())

CodeEditorDemo()