#Twitter encriptor controller (Watches a hashtag for orders and decrypts or encrypts)
#This software is just for testing purposes, dont rely on it on the real world!!

from pathlib import Path
import tweepy
import pyAesCrypt
import time
import os

#place your files under the folder secretos_de_estado
#the file pwd.txt must contain the password for encrypt/decrypt IT WILL BE HASHED TOO!!
#tweets must be like:
    #hashtag pwd:password
#if decrypting password must be the decryption key (yeah, i know, pretty dumb if someone copied our data)
#if encrypting password must be the same as trigger field below

####input your credentials here (Get a twitter developer account)
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''
###input your hashtags
safe_hashtag="#imsafenow"
risk_hashtag="#imatrisknow"
###input the encrypt activation passphrase NOT THE SAME AS THE ENCRYPTION KEY!!!
###This is just to avoid people randomly triggering the encryption process
trigger="patata"

last_risk = ''
last_safe = ''


def encrypt():
    bufferSize = 64 * 1024
    with open("./secretos_de_estado/pwd.txt", 'r') as reader:
        password = reader.read()
    # encrypt
    pathlist = Path("./secretos_de_estado").glob('./*.*')
    for path in pathlist:
         # because path is object not string
         path_in_str = str(path)
         print(path_in_str)
         pyAesCrypt.encryptFile(path_in_str, path_in_str+".aes", password, bufferSize)
         os.remove(path_in_str)

def decrypt(password):
    bufferSize = 64 * 1024
    # decrypt
    pathlist = Path("./secretos_de_estado").glob('./*.*')
    for path in pathlist:
         # because path is object not string
         path_in_str = str(path)
         print(path_in_str)
         pyAesCrypt.decryptFile(path_in_str, path_in_str[:-4], password, bufferSize)
         os.remove(path_in_str)

def tweet(enc):
    global last_risk, last_safe
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth,wait_on_rate_limit=True)

    while True:
        time.sleep(5)
        if enc:
            for tweet in tweepy.Cursor(api.search,q=safe_hashtag,count=100, since_id=last_risk).items():
                print (tweet.created_at, tweet.text)
                if "pwd:" in tweet.text:
                    if tweet.text[tweet.text.index("pwd:") + len("pwd:"):] == trigger:
                        last_risk = tweet.id
                        encrypt()
                        return
        else:
            for tweet in tweepy.Cursor(api.search,q=risk_hashtag,count=100, since_id=last_safe).items():
                print (tweet.created_at, tweet.text)
                if "pwd:" in tweet.text:
                    print("PWD DETECTED: " +tweet.text[tweet.text.index("pwd:") + len("pwd:"):])
                    last_safe = tweet.id
                    decrypt(tweet.text[tweet.text.index("pwd:") + len("pwd:"):])
                    return

if __name__=="__main__":
    while True:
        tweet(os.path.isfile('./secretos_de_estado/pwd.txt'))
