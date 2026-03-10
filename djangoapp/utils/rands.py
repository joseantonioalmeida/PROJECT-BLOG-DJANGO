import string
from random import SystemRandom
from django.utils.text import slugify

#gera 5 letras aleatórias
def random_letters(k=5):
    return ''.join(SystemRandom().choices(
        string.ascii_lowercase + string.digits,
        k=k  
    ))


def slugify_new(text, k):
    return slugify(text) + '-' + random_letters(k)


# print(slugify_new('BLA BLA BLA BL UI'))