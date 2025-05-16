import os
import random
import unicodedata


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

    import django
    django.setup()

    from db.dictionary.models import *

    count = HanjaUsage.objects.count()
    while input('> ') != 'q':
        usage = HanjaUsage.objects.all()[random.randint(0, count - 1)]
        print(usage.word.word)
        for sense in KoreanWordSense.objects.filter(word=usage.word):
            print('\t' + sense.definition)
        input(': ')
        print(usage.word.hanja)
