import random, string

def return_random(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))