from uuid import uuid1

def generate_pass():
    return (str(uuid1())[0:8])