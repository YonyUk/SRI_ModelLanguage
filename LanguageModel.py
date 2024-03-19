import fitz
from pathlib import Path
import re
from os import system
from random import randint

prepositions = [
    'a',
    'ante',
    'bajo',
    'con',
    'contra',
    'de',
    'desde',
    'en',
    'entre',
    'hasta',
    'hacia',
    'para',
    'por',
    'sin',
    'según',
    'sobre',
    'tras'
]

articles = [
    'el',
    'la',
    'les',
    'le',
    'lo',
    'del',
    'las',
    'los'
]

conjuntions = [
    'y',
    'e',
    'u',
    'o',
    'pero',
    'sino',
    'mas'
]

class FileReader:
    
    _path = None
    _title = None
    _extension = None
    _reader = None
    
    def __init__(self,doc_path):
        path = Path(doc_path)
        
        if not path.exists() or not path.is_file():
            raise Exception('Direccion invalida')
        
        self._path = path.parent
        name = path.name
        
        pos = name.rindex('.')
        self._title = name[:pos]
        self._extension = name[pos + 1:]
        pass
    
    @property
    def Title(self):
        return self._title
    
    @property
    def Extension(self):
        return self._extension
    
    @property
    def Path(self):
        return self._path.resolve()
    
    def Open(self):
        raise NotImplementedError()
    
    def Close(self):
        raise NotImplementedError()
    
    def Read(self):
        raise NotImplementedError()
    
    pass

class PDFReader(FileReader):
    
    def __init__(self,doc_path):
        super().__init__(doc_path)
        pass
    
    def Open(self):
        self._reader = fitz.Document(str(self._path.joinpath(f'{self._title}.{self._extension}')))
        pass
    
    def Close(self):
        self._reader.close()
    
    def Read(self):
        text = ''
        num_pages = self._reader.page_count
        for i in range(num_pages):
            text += self._reader.get_page_text(i)
            pass
        return text
    
    pass

class DataStructure:
    
    _words = None
    _sentences = None
    _bigram_probability_table = {}
    
    def __init__(self,text):
        self._text = text.lower()
        pass
    
    def _extract_data(self):
        
        self._words = []
        self._sentences = []
        sentences = self._text.split('.')
        
        
        for sentence in sentences:
            subsentences = sentence.split(',')
            for sub in subsentences:
                s = sub.split(';')
                for part in s:
                    self._sentences.append(re.findall('\\w+',part))
                    pass
                pass
            pass
        
        for sentence in self._sentences:
        
            if len(sentence) == 0:
                continue
            
            if list(self._bigram_probability_table.keys()).count(('$',sentence[0])) == 0:
                self._bigram_probability_table[('$',sentence[0])] = 1
                pass
            else:
                self._bigram_probability_table[('$',sentence[0])] += 1
                pass
            
            if list(self._bigram_probability_table.keys()).count((sentence[len(sentence) - 1],'$')) == 0:
                self._bigram_probability_table[(sentence[len(sentence) - 1],'$')] = 1
                pass
            else:
                self._bigram_probability_table[(sentence[len(sentence) - 1],'$')] += 1
                pass
            
            for i in range(len(sentence) - 1):
                
                if self._words.count(sentence[i]) == 0:
                    self._words.append(sentence[i])
                    pass
                
                if list(self._bigram_probability_table.keys()).count((sentence[i],sentence[i + 1])) == 0:
                    self._bigram_probability_table[(sentence[i],sentence[i + 1])] = 1
                    pass
                else:
                    self._bigram_probability_table[(sentence[i],sentence[i + 1])] += 1
                    pass
                
                pass
            
            if self._words.count(sentence[len(sentence) - 1]) == 0:
                self._words.append(sentence[len(sentence) - 1])
                pass
                    
            pass
            
        pair_count = len(self._bigram_probability_table.keys())
            
        for pair in self._bigram_probability_table.keys():
            self._bigram_probability_table[pair] = self._bigram_probability_table[pair]/pair_count
            pass
        
        pass
   
    def _pair_probability(self,word1,word2):
        if list(self._bigram_probability_table.keys()).count((word1,word2)) == 0:
            return 0
        return self._bigram_probability_table[(word1,word2)]
   
    def _probability(self,word1,word2,last_probability):
        return last_probability * self._pair_probability(word1,word2)
    
    def NextWord(self,word,last_probability):
        
        posibles = [prepositions,articles,conjuntions]
        
        probability = 0
        word_result = ''
        last = word
        
        for w in self._words:
            p = self._probability(word,w,last_probability)
            
            can = True
            
            for v in posibles:
                if v.count(w) > 0:
                    can = True
                    break
                pass
            
            if p > probability and not w == last and (text.count(w) < 2 or can):
                probability = p
                word_result = w
                pass
            last = w
            pass
        
        return word_result,last_probability*probability
    
    def GenerateSentence(self,topic):
        
        sentence = []
        word = topic
        text = word
        last_probability = 1
        
        while len(word) > 0:
            if len(sentence) > 15:
                break
            s = f'{topic}'
            word,last_probability = self.NextWord(word,last_probability)
            
            if len(word) == 0:
                
                posibles = [prepositions,articles,conjuntions]
                
                invalid = False
                for v in posibles:
                    if v.count(sentence[len(sentence) - 1]):
                        invalid = True
                        break
                    pass
                
                while invalid:
                    
                    sentence.pop(len(sentence) - 1)
                    
                    invalid = False
                    for v in posibles:
                        if v.count(sentence[len(sentence) - 1]):
                            invalid = True
                            break
                        pass
                    
                    pass
                
                sentence.append(',')
                while len(word) < 4:
                    initial_words = [word_pair[1] for word_pair in self._bigram_probability_table.keys() if word_pair[0] == '$']
                    word = initial_words[randint(0,len(initial_words) - 1)]
                    last_probability = 1
                    pass
                pass
            
            system('clear')
            sentence.append(word)
            for w in sentence:
                s += f' {w}'
                pass
            text = s
            print(text)
            pass
        return text
    
    pass

file = PDFReader('14219.pdf')
file.Open()
text = file.Read()
file.Close()

# text = '''
# good morning.
# good afternoon.
# good afternoon.
# it is very good.
# it is good.
# '''

data = DataStructure(text)
print('learning')
data._extract_data()
topics = ['universidad','lenguaje','proyecto','estudio']

data.GenerateSentence(topics[0])
# topics = ['good','afternoon']
# sentences = []
# for topic in topics:
#     sentences.append(data.GenerateSentence(topic))
#     pass