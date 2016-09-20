class PasswordSaltedHash():
    def __init__(self,salt_byte_length=32,algorithm='sha256'):
        import hashlib
        from random import randint
        from binascii import hexlify
        self.hashlib = hashlib
        self.randint = randint
        self.hexlify = hexlify
        self.salt_length = salt_byte_length
        self.algorithm = str(algorithm).lower()
    def create(self,password):
        salt = str(self.hexlify(''.join([chr(self.randint(32,126)) for x in range(0,self.salt_length//2)]).encode()),'ascii')
        if self.algorithm == 'md5'   : return self.hashlib.md5(salt.encode() + password.encode()).hexdigest() + salt
        if self.algorithm == 'sha1'  : return self.hashlib.sha1(salt.encode() + password.encode()).hexdigest() + salt
        if self.algorithm == 'sha224': return self.hashlib.sha224(salt.encode() + password.encode()).hexdigest() + salt
        if self.algorithm == 'sha256': return self.hashlib.sha256(salt.encode() + password.encode()).hexdigest() + salt
        if self.algorithm == 'sha384': return self.hashlib.sha384(salt.encode() + password.encode()).hexdigest() + salt
        if self.algorithm == 'sha512': return self.hashlib.sha512(salt.encode() + password.encode()).hexdigest() + salt
    def validate(self,hashed_password,user_password):
        password = hashed_password[0:len(hashed_password)-self.salt_length]
        salt = hashed_password[len(hashed_password)-self.salt_length:]
        if self.algorithm == 'md5'   : return password == self.hashlib.md5(salt.encode() + user_password.encode()).hexdigest()
        if self.algorithm == 'sha1'  : return password == self.hashlib.sha1(salt.encode() + user_password.encode()).hexdigest()
        if self.algorithm == 'sha224': return password == self.hashlib.sha224(salt.encode() + user_password.encode()).hexdigest()
        if self.algorithm == 'sha256': return password == self.hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()
        if self.algorithm == 'sha384': return password == self.hashlib.sha384(salt.encode() + user_password.encode()).hexdigest()
        if self.algorithm == 'sha512': return password == self.hashlib.sha512(salt.encode() + user_password.encode()).hexdigest()

#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    
    pw = PasswordSaltedHash()
    
    mypass = 'TestOfThisClass'
    print('mypass =',mypass)
    
    salted_pw_hash = pw.create(mypass)
    print('salted_pw_hash is',len(salted_pw_hash),'bytes =',salted_pw_hash)
    
    pw2test = 'test'
    result = pw.validate(salted_pw_hash,pw2test)
    print(pw2test,'->',result)

    pw2test = 'attempto'
    result = pw.validate(salted_pw_hash,pw2test)
    print(pw2test,'->',result)

    pw2test = mypass.lower()
    result = pw.validate(salted_pw_hash,pw2test)
    print(pw2test,'->',result)

    pw2test = mypass
    result = pw.validate(salted_pw_hash,pw2test)
    print(pw2test,'->',result)
