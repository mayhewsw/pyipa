# -*- encoding: utf-8 -*-
###
# IPA-based parser
#  Understands multi-codepoint graphemes

import copy
import unicodedata

## Config
WHITESPACE_INCLUDES_NEWLINES = True

## Debug and Test Config
SHOW_PASSES = False

MANNER = {"nasal": u'm̥mɱn̪n̥nn̠ɳɲ̥ɲŋ̊ŋɴ',
           "plosive": u'pbp̪b̪t̪d̪tdʈɖcɟkɡqɢʡʔ',
           "fricative": u'ɸβfvθðszʃʒʂʐçʝxɣχʁħʕʜʢhɦ',
           "approximant": u'ʋɹɻjɰʁʕʢhɦ',
           "trill": u'ʙrʀя', # does not include retroflex because of unsupported glyph stuff,
           "flap_or_tap": u'ⱱ̟ⱱɾɽɢ̆ʡ̯',
           "lateral_fric": u'ɬɮɭ˔̊ʎ̥˔ʟ̝̊ʟ̝',
           "lateral_approx": u'lɭʎʟ',
           "lateral_flap": u'ɺɺ̠ʎ̯'
}

PLACE = {
    "labial": {
        "bilabial": u'm̥pɸmbβⱱ̟',
        "labiodental": u'p̪fɱb̪vʋⱱ'
    },
    "coronal": {
        "dental": u'n̪t̪d̪θð',
        "alveolar": u'n̥ntdszɹrɾɬɮlɺ',
        "postlav": u'n̠ʃʒ',
        "retroflex": u'ɳʈɖʂʐɻɽɭ˔̊ɭɺ̠'
    },
    "dorsal": {
        "palatal": u'ɲ̥ɲcɟçʝjʎ̥˔ʎʎ̯',
        "velar": u'ŋ̊ŋkɡxɣɰʟ̝̊ʟ̝ʟ',
        "uvular": u'ɴqɢχʁʀɢ̆'
    },
    "radical": {
        "pharyngeal": u'ħʕ',
        "epiglottal": u'ʡʜʢяʡ̯'
    },
    "glottal": {
        "glottal": u'ʔhɦ'
    }
}

PLACE_MINOR = {}
PLACE_MAJOR = {}
for major in PLACE.keys():
    PLACE_MAJOR[major] = u''
    for minor in PLACE[major].keys():
        s = PLACE[major][minor]
        PLACE_MINOR[minor] = s
        PLACE_MAJOR[major] += s

VOICING = {
    "unvoiced": u'm̥pɸp̪ft̪θn̥tsɬʃʈʂɭ˔̊ɲ̥cçʎ̥˔ŋ̊kxʟ̝̊qχħʡʜʔh',
    "voiced": u'mbβʙⱱ̟ɱb̪vʋⱱn̪d̪ðndzɹrɾɮlɺn̠ʒɳɖʐɻɽɭɺ̠ɲɟʝjʎʎ̯ŋɡɣɰʟ̝ʟɴɢʁʀɢ̆ʕʢяʡ̯ɦ'
}



BACKNESS = {
    'front': u'iyeøe̞ø̞ɛœæaɶ',
    'near-front': u'ɪʏ',
    'central': u'ɨʉɪ̈ʊ̈ɘɵəɜɞɐä',
    'near-back': u'ʊ',
    'back': u'ɯuɤoɤ̞o̞ʌɔɑɒ'
}

HEIGHT = {
    'high/close': u'iyɨʉɯu',
    'near-close': u'ɪʏɪ̈ʊ̈ʊ',
    'close-mid': u'eøɘɵɤo',
    'mid': u'e̞ø̞əɤ̞o̞',
    'open-mid': u'ɛœɜɞʌɔ',
    'near-open': u'æɐ',		
    'low/open': u'aɶäɑɒ'
}

ROUNDEDNESS = {
    'unrounded': u'iɨɯɪɪ̈eɘɤe̞əɤ̞ɛɜʌæɐaäɑ',
    'rounded': u'yʉuʏʊ̈ʊøɵoø̞o̞œɞɔɐɶɒ'
}


def CombiningCategory(c):
    cat = unicodedata.category(c)
    return cat[0] == 'M' or cat == 'Lm' or cat == 'Sk'

def PopGrapheme(s):
    if len(s) == 0: return None, s
    elif len(s) == 1: return s, ''
    elif CombiningCategory(s[0]):
        raise Exception("Should not have a combining as first codepoint in grapheme")
    else:
        for ii in range(len(s[1:])):
            if not(CombiningCategory(s[1+ii])):
                return s[:ii+1], s[ii+1:]
        return s, ''

def GraphemeSplit(s):
    graphemeL = []
    while len(s) > 0:
        g, s = PopGrapheme(s)
        if g == None: break
        graphemeL.append(g)
    return graphemeL

ALL_CONSONANTS = GraphemeSplit(VOICING['unvoiced'] + VOICING['voiced'])
ALL_VOWELS = GraphemeSplit(ROUNDEDNESS['unrounded'] + ROUNDEDNESS['rounded'])
ALL_ALPHA = ALL_CONSONANTS + ALL_VOWELS

ConsonantData = {}
for c in ALL_CONSONANTS:
    ConsonantData[c] = {}
VowelData = {}
for c in ALL_VOWELS:
    VowelData[c] = {}

def FillData(byGrapheme, byType, typeType):
    for t in byType.keys():
        graphemeL = GraphemeSplit(byType[t])
        for grapheme in graphemeL:
            byGrapheme[grapheme][typeType] = t

FillData(ConsonantData, MANNER, 'manner')
FillData(ConsonantData, PLACE_MAJOR, 'place_major')
FillData(ConsonantData, PLACE_MINOR, 'place_minor')
FillData(ConsonantData, VOICING, 'voicing')

FillData(VowelData, BACKNESS, 'backness')
FillData(VowelData, HEIGHT, 'height')
FillData(VowelData, ROUNDEDNESS, 'roundedness')

class ParserNode:
    def __init__(self, name=None):
        self.Name = name
    def Recognize(self, s0):
        s1, res = self.Parse(s0)
        return s1, res != None
    def Parsed(self, s0, s1):
        n = copy.copy(self)
        n.Text = s0[:len(s0)-len(s1)]
        return s1, n
    def Parsing(self):
        self.Text = None
    def FindAll(self, name):
        if self.Name == name and self.Text != None: return [self]
        else: return []

def WeaveAndClean(l1, l2):
    result = []
    for ii in range(len(l1)):
        result.append(l1[ii])
        if len(l2) > ii: result.append(l2[ii])
    return [r for r in result if r != None]

class SeparatedSequenceNode (ParserNode):
    def __init__(self, separatorNode, sequenceNodes, initialSep=False, finalSep=False, storeSep=True, name=None):
        ParserNode.__init__(self, name)
        self.Nodes = [node for node in sequenceNodes]
        self.SepNode = separatorNode
        self.InitialSep = initialSep
        self.FinalSep = finalSep
        self.StoreSep = storeSep
    def __repr__(self):
        initial = ""
        final = ""
        store = ""
        if self.InitialSep: initial = ", initialSep=True"
        if self.FinalSep: final = ", finalSep=True"
        if not(self.StoreSep): store = ", storeSep=False"
        return "SeparatedSequenceNode(" + str(self.SepNode) + ", " + str(self.Nodes) + initial + final + store + ")"
    def Parse(self, s0):
        self.Parsing()
        self.ParsedNodes = []
        self.Separators = []
        s1 = s0
        if self.InitialSep:
            s1, res = self.SepNode.Parse(s1)
            if res == None: return s0, None
            self.Separators.append(res)
        for ii in range(len(self.Nodes)):
            node = self.Nodes[ii]
            s1,res = node.Parse(s1)
            if res == None:
                return s0, None
            self.ParsedNodes.append(res)
            if self.FinalSep or (ii != len(self.Nodes) - 1):
                s1,res = self.SepNode.Parse(s1)
                if res == None:
                    return s0, None
                if self.StoreSep: self.Separators.append(res)
        return self.Parsed(s0, s1)
    def __WeaveAndClean(self, nodes, sep):
        if not(self.StoreSep):
            return [node for node in nodes if node != None]
        elif self.InitialSep:
            return WeaveAndClean(sep, nodes)
        else:
            return WeaveAndClean(nodes, sep)
    def GetParsedResult(self):
        if len(self.ParsedNodes) == 0:
            return None
        else:
            nodes = [n.GetParsedResult() for n in self.ParsedNodes]
            if not(self.StoreSep): return nodes
            sep = [n.GetParsedResult() for n in self.Separators]
            return self.__WeaveAndClean(nodes, sep)
    def FindAll(self, name):
        results = ParserNode.FindAll(self, name)
        for node in self.__WeaveAndClean(self.ParsedNodes, self.Separators):
            results.extend(node.FindAll(name))
        return results
            
class SequenceNode (ParserNode):
    def __init__(self, nodes, name=None):
        ParserNode.__init__(self, name)
        self.Nodes = [node for node in nodes]
    def __repr__(self):
        return "SequenceNode(" + str(self.Nodes) + ")"
    def Parse(self, s0):
        self.Parsing()
        self.ParsedNodes = []
        s1 = s0
        for node in self.Nodes:
            s1,res = node.Parse(s1)
            if res == None: return s0, None
            self.ParsedNodes.append(res)
        return self.Parsed(s0, s1)
    def GetParsedResult(self):
        if len(self.ParsedNodes) == 0:
            return None
        else:
            return [x for x in [n.GetParsedResult() for n in self.ParsedNodes] if x != None]
    def FindAll(self, name):
        results = ParserNode.FindAll(self, name)
        for node in self.ParsedNodes:
            results.extend(node.FindAll(name))
        return results
    
class OrNode (ParserNode):
    def __init__(self, nodes, name=None):
        ParserNode.__init__(self, name)
        self.Nodes = [node for node in nodes]
    def __repr__(self):
        return "OrNode(" + str(self.Nodes) + ")"
    def Parse(self, s0):
        self.Parsing()
        self.ParsedNode = None
        for node in self.Nodes:
            s1,res = node.Parse(s0)
            if res != None:
                self.ParsedNode = res
                return self.Parsed(s0, s1)
        return s0, None
    def GetParsedResult(self):
        return self.ParsedNode.GetParsedResult()
    def FindAll(self, name):
        results = ParserNode.FindAll(self, name)
        results.extend(self.ParsedNode.FindAll(name))
        return results

class GraphemeNode (ParserNode):
    def __init__(self, graphemes, name=None):
        ParserNode.__init__(self, name)
        s = u''.join(graphemes)
        self.Graphemes = []
        while len(s) > 0:
            g, s = PopGrapheme(s)
            self.Graphemes.append(g)
    def __repr__(self):
        return "GraphemeNode(" + str(self.Graphemes) + ")"
    def Parse(self, s0):
        self.Parsing()
        self.ParsedGrapheme = None
        if len(s0) == 0: return s0, None
        g, s1 = PopGrapheme(s0)
        if g in self.Graphemes:
            self.ParsedGrapheme = g
            return self.Parsed(s0, s1)
        return s0, None
    def GetParsedResult(self):
        return self.ParsedGrapheme

class WhitespaceNode (ParserNode):
    def __init__(self, name=None):
        ParserNode.__init__(self, name)
    def __repr__(self):
        return "WhitespaceNode()"
    def Parse(self, s0):
        self.Parsing()
        if (len(s0) == 0): return s0, None
        for ii in range(len(s0)):
            if (not(s0[ii].isspace())
                or (not(WHITESPACE_INCLUDES_NEWLINES)
                    and (s0[ii] == '\n' or s0[ii] == '\r')
                )):
                if ii > 0:
                    return self.Parsed(s0, s0[ii:])
                else: return s0, None
        return self.Parsed(s0, u'')
    def GetParsedResult(self):
        return self.Text

class OptionalNode (ParserNode):
    def __init__(self, node, name=None):
        ParserNode.__init__(self, name)
        self.Node = node
    def __repr__(self):
        return "OptionalNode(" + str(self.Node) + ")"
    def Parse(self, s0):
        self.Parsing()
        s1, res = self.Node.Parse(s0)
        self.Chosen = res
        return self.Parsed(s0, s1)
    def GetParsedResult(self):
        if self.Chosen == None: return None
        else: return self.Chosen.GetParsedResult()
    def FindAll(self, name):
        results = ParserNode.FindAll(self, name)
        if self.Chosen != None:
            results.extend(self.Chosen.FindAll(name))
        return results

class ManyNode (ParserNode):
    def __init__(self, node, name=None):
        ParserNode.__init__(self, name)
        self.Node = node
    def __repr__(self):
        return "ManyNode(" + str(self.Node) + ")"
    def Parse(self, s0):
        self.Parsing()
        self.ParsedNodes = []
        s1 = s0
        if len(s0) == 0:
            s1, res = self.Node.Parse(u'')
            if (res == None):
                return s0, None
            else:
                self.ParsedNodes.append(res)
        while len(s1) > 0:
            pending,res = self.Node.Parse(s1)
            if res == None or (pending == s1 and len(self.ParsedNodes) > 0):
                break
            self.ParsedNodes.append(res)
            s1 = pending
        if len(self.ParsedNodes) > 0:
            return self.Parsed(s0, s1)
        else:
            return s0, None
    def GetParsedResult(self):
        if len(self.ParsedNodes) == 0:
            return None
        else:
            return [n.GetParsedResult() for n in self.ParsedNodes]
    def FindAll(self, name):
        results = ParserNode.FindAll(self, name)
        for node in self.ParsedNodes:
            results.extend(node.FindAll(name))
        return results

# =================================================
# ============ Composite Helper Nodes =============
# =================================================
class OptionalWhitespaceNode (OptionalNode):
    def __init__(self, name=None):
        OptionalNode.__init__(self, WhitespaceNode(), name)
    def __repr__(self):
        return "OptionalWhitespaceNode()"

class AlphaNode(GraphemeNode):
    def __init__(self, name=None):
        GraphemeNode.__init__(self, ALL_ALPHA, name)
    def __repr__(self):
        return "AlphaNode()"

## Python automatically converts CrLf EOL when reading files as
##   text so this isn't needed. Add it back in if data might come
##   in from other means, like binary data converted or something
##class EOLNode(OrNode):
##    def __init__(self, name=None):
##        OrNode.__init__(self, [
##            GraphemeNode(u'\n')
##            , GraphemeNode(u'\r')
##            , SequenceNode(GraphemeNode(u'\n'), GraphemeNode(u'\r'))]
##            , name)
class EOLNode(GraphemeNode):
    def __init__(self, name=None):
        GraphemeNode.__init__(self, u'\n', name)
    def __repr__(self):
        return "EOLNode()"

class EndNode (ParserNode):
    def __init__(self, name=None):
        ParserNode.__init__(self, name)
        self.WhitespaceAndEOL = OptionalNode(ManyNode(OrNode([WhitespaceNode(), EOLNode()])))
    def __repr__(self):
        return "EndNode()"
    def Parse(self, s0):
        self.Parsing()
        s1, res = self.WhitespaceAndEOL.Parse(s0)
        if res != None and s1 == '':
            return self.Parsed(s0, s1)
        else:
            return s0, None
    def GetParsedResult(self):
        return self.Text

# =================================================
# ================== Testing ======================
# =================================================
    
def MakeTest(env):
    def Test(esPair):
        expect,statement = esPair
        result = eval(statement,env)
        if expect == result:
            if SHOW_PASSES: print "PASS:", statement, " == ", expect
            return True
        else:
            print "FAIL: " + statement
            print "===> expected:", expect
            print "===> actual:", result
            return False
    return Test

def RunTests(env, esPairs):
    return all(map(MakeTest(env), esPairs))

def DoTests():
    p = GraphemeNode(['a','b'])
    RunTests({'p': p}, 
        [ (("", True), 'p.Recognize(u"a")')
         ,(("", True), 'p.Recognize(u"b")')
         ,(("e", False), 'p.Recognize(u"e")')
        ])

    p = GraphemeNode(u"m̥ɱn̪n̥ŋ̊ɴ")
    RunTests({'p': p}, 
        [ (("", True), u'p.Recognize(u"m̥")')
         ,(("", True), u'p.Recognize(u"ɱ")')
         ,(("", True), u'p.Recognize(u"n̪")')
         ,(("", True), u'p.Recognize(u"n̥")')
         ,(("", True), u'p.Recognize(u"ŋ̊")')
         ,(("", True), u'p.Recognize(u"ɴ")')
         ,((u"̪", False), u'p.Recognize(u"̪")')
         ,((u"̥", False), u'p.Recognize(u"̥")')
         ,((u"̊", False), u'p.Recognize(u"̊")')
         ,(("e", False), u'p.Recognize(u"e")')
        ])

    p = OrNode([GraphemeNode("a"), GraphemeNode("b")])
    #print p
    RunTests({'p': p}, 
        [ (("", True), 'p.Recognize(u"a")')
         ,(("", True), 'p.Recognize(u"b")')
         ,((u"e", False), 'p.Recognize(u"e")')
        ])

    p = WhitespaceNode()
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u" ")')
         ,(("", True), 'p.Recognize(u"  ")')
         ,(("", True), 'p.Recognize(u" \\t  ")')
         ,((u"b", True), 'p.Recognize(u" b")')
         ,((u"b", False), 'p.Recognize(u"b")') # whitespace is not optional
         ,((u"", False), 'p.Recognize(u"")') # whitespace is not optional
        ])
    RunTests({'p': p, 'WHITESPACE_INCLUDES_NEWLINES': True},[(("", True), 'p.Recognize(u" \\n  ")')])
    global WHITESPACE_INCLUDES_NEWLINES
    temp = WHITESPACE_INCLUDES_NEWLINES
    WHITESPACE_INCLUDES_NEWLINES = False
    RunTests({'p': p, 'WHITESPACE_INCLUDES_NEWLINES': False},[(("\n  ", True), 'p.Recognize(u" \\n  ")')])
    WHITESPACE_INCLUDES_NEWLINES = temp

    p = EOLNode()
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"\\n")')
         ,((" ", True), 'p.Recognize(u"\\n ")')
         ,((" \n", False), 'p.Recognize(u" \\n")')
        ])

    p = EndNode()
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"")')
         ,(("", True), 'p.Recognize(u"\\n")')
         ,(("", True), 'p.Recognize(u"\\n ")')
         ,(("", True), 'p.Recognize(u" \\n")')
         ,((" \na", False), 'p.Recognize(u" \\na")')
        ])

    p = OptionalWhitespaceNode()
    # print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"")')
         ,(("", True), 'p.Recognize(u" ")')
         ,(("b ", True), 'p.Recognize(u"b ")')
         ,(("b ", True), 'p.Recognize(u" b ")')
        ])

    p = OptionalNode(GraphemeNode("a"))
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"a")')
         ,((u"b", True), 'p.Recognize(u"b")')
         ,(u"a", 'str(p.Parse(u"a")[1].GetParsedResult())')
        ])
    
    p = SequenceNode([
        OrNode([
            GraphemeNode("ab"),
            WhitespaceNode()
        ]),
        OptionalNode(WhitespaceNode()),
        GraphemeNode("cd")
    ])
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"a c")')
         ,(("", True), 'p.Recognize(u" d")')
         ,(("e", True), 'p.Recognize(u" de")')
         ,(("de", False), 'p.Recognize(u"de")')
         ,(("e", False), 'p.Recognize(u"e")')
         ,("[u'a', u'c']", 'str(p.Parse(u"ac")[1].GetParsedResult())')
        ])

    p = SequenceNode([
            ManyNode(GraphemeNode("a"))
            , GraphemeNode(["b"])
        ])
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"ab")')
         ,(("", True), 'p.Recognize(u"aab")')
         ,(("", True), 'p.Recognize(u"aaab")')
         ,(("b", False), 'p.Recognize(u"b")')
         ,(("a", False), 'p.Recognize(u"a")')
        ])

    p = SeparatedSequenceNode(
            OptionalNode(WhitespaceNode()),
            [
                GraphemeNode("a")
                , GraphemeNode("b")
            ])
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"ab")')
         ,(("", True), 'p.Recognize(u"a b")')
         ,(("", True), 'p.Recognize(u"a  b")')
         ,((" ", True), 'p.Recognize(u"ab ")') # no sep picked up at end
         ,((" ab", False), 'p.Recognize(u" ab")') # no sep picked up at beginning
        ])

    p = SeparatedSequenceNode(
            WhitespaceNode(),   # NOTE: NOT OPTIONAL NOW (as opposed to test above)
            [
                GraphemeNode("a")
                , GraphemeNode("b")
            ]
            , initialSep = True)
    #print p
    RunTests({'p': p},
        [ (("a b", False), 'p.Recognize(u"a b")')
         ,(("a b", False), 'p.Recognize(u"a b")')
         ,(("a  b", False), 'p.Recognize(u"a  b")')
         ,(("a b ", False), 'p.Recognize(u"a b ")')
         ,(("", True), 'p.Recognize(u" a b")')
         ,(("", True), 'p.Recognize(u" a b")')
         ,((" ", True), 'p.Recognize(u" a b ")')
        ])

    p = SeparatedSequenceNode(
            WhitespaceNode(),   # NOTE: NOT OPTIONAL NOW (as opposed to test earlier)
            [
                GraphemeNode("a")
                , GraphemeNode("b")
            ]
            , finalSep = True)
    #print p
    RunTests({'p': p},
        [ (("a b", False), 'p.Recognize(u"a b")')
         ,(("a b", False), 'p.Recognize(u"a b")')
         ,(("a  b", False), 'p.Recognize(u"a  b")')
         ,(("", True), 'p.Recognize(u"a b ")')
         ,((" a b", False), 'p.Recognize(u" a b")')
         ,((" a b ", False), 'p.Recognize(u" a b ")')
         ,(("a", True), 'p.Recognize(u"a b a")')
        ])

    p = SeparatedSequenceNode(
            WhitespaceNode(),   # NOTE: NOT OPTIONAL NOW (as opposed to test earlier)
            [
                GraphemeNode("a")
                , GraphemeNode("b")
            ]
            , finalSep = True
            , storeSep = False
        )
    #print p
    RunTests({'p': p},
        [ (("a b", False), 'p.Recognize(u"a b")')
         ,(("a b", False), 'p.Recognize(u"a b")')
         ,(("a  b", False), 'p.Recognize(u"a  b")')
         ,(("", True), 'p.Recognize(u"a b ")')
         ,((" a b", False), 'p.Recognize(u" a b")')
         ,((" a b ", False), 'p.Recognize(u" a b ")')
         ,(("a", True), 'p.Recognize(u"a b a")')
        ])

    p = SequenceNode([
            OptionalNode(ManyNode(GraphemeNode("e")))
            , GraphemeNode(["f"])
        ])
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"ef")')
         ,(("", True), 'p.Recognize(u"eef")')
         ,(("", True), 'p.Recognize(u"eeef")')
         ,(("", True), 'p.Recognize(u"f")')
         ,(("e", False), 'p.Recognize(u"e")')
         ,("[[u'e', u'e'], u'f']", 'str(p.Parse(u"eef")[1].GetParsedResult())')
        ])

    p = SequenceNode([
            ManyNode(OptionalNode(GraphemeNode("a")))
            , GraphemeNode(["b"])
        ])
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"ab")')
         ,(("", True), 'p.Recognize(u"aab")')
         ,(("", True), 'p.Recognize(u"aaab")')
         ,(("", True), 'p.Recognize(u"b")')
         ,(("a", False), 'p.Recognize(u"a")')
         ,("[[u'a', u'a'], u'b']", 'str(p.Parse(u"aab")[1].GetParsedResult())')
        ])

    p = GraphemeNode(MANNER["nasal"])
    expStr = "GraphemeNode([u'm\u0325', u'm', u'\u0271', u'n\u032a', u'n\u0325', u'n', u'n\u0320', u'\u0273', u'\u0272\u0325', u'\u0272', u'\u014b\u030a', u'\u014b', u'\u0274'])"
    RunTests({'p': p},
        [ (expStr, 'str(p)') ])

    p = AlphaNode()
    #print p
    RunTests({'p': p},
        [ (("", True), 'p.Recognize(u"a")')
         ,(("", True), 'p.Recognize(u"b")')
         ,((" ", False), 'p.Recognize(u" ")')
         ,(("[", False), 'p.Recognize(u"[")')
        ])

    p = SequenceNode([
            ManyNode(OptionalNode(GraphemeNode("a", name="grapheme"), name="optional"), name="many")
            , GraphemeNode(["b"], name="grapheme")
            ]
        , name = "seq")
    #print p
    RunTests({'p': p},
        [ (u'b', 'p.Parse(u"ab")[1].FindAll("seq")[0].FindAll("grapheme")[1].Text')
        ])

    p = SeparatedSequenceNode(OptionalWhitespaceNode(), [
            ManyNode(OptionalNode(GraphemeNode("a", name="grapheme"), name="optional"), name="many")
            , GraphemeNode(["b"], name="grapheme")
            ]
        , name = "seq", storeSep = False, initialSep = True, finalSep = True)
    #print p
    RunTests({'p': p},
        [ (u'b', 'p.Parse(u" a b ")[1].FindAll("seq")[0].FindAll("grapheme")[1].Text')
        ])

if __name__ == '__main__':
    DoTests()
