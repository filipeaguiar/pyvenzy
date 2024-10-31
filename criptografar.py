import settings


def encrypt(number):
    return number ^ int(settings.salt or 1)


def decrypt(number):
    return number ^ int(settings.salt or 1)
