from mymemopy.translator import MyMemoryTranslate

class Translate:

    def translate(self, text):
        translate = MyMemoryTranslate()
        res = translate.translate(text, source_lang='en', target_lang='ru')
        return res