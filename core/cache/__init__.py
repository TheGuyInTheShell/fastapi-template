import redis as r


class Redis:
    __instance: r.Redis = None

    def __init__(self):
        if Redis.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Redis.__instance = self

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = r.Redis(host='localhost', port=6379)
        return cls.__instance
    

if __name__ == '__main__':
    print(Redis().set('key', 'value'))
    print(Redis().get('key'))