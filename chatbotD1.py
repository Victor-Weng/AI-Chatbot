import random
import json
import requests #used (in this code) for reading discord messages 
import pickle
import numpy as np
import pyautogui as auto #enable keystrokes
import time
import sys #to stop code
import nltk
from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import load_model

lemmatizer = WordNetLemmatizer()

directory = 'C:/Users/victo/OneDrive/Desktop/pythonCode/PythonChatbotD1/' #Directory where the general files are found
v = 'D1' #Version of file

a = np.random.random() #randomizer
cd = 1 #Cooldown between typing out messages
bfr = 1 #added cooldown between typing out messages, used as a multiplier of a, our brandomized value (between 0 and 1) 
ck = False #boolean for enabling the bot to type out messages
nm = False #boolean for checking if there is a new message that is not from the bot
tempid = '0' #Temporarily holds the id of the last message that the bot responds to, to check if there is a new message in Discord
did = '1004869219457970256' #Discord channel id
#This is found by refreshing the chrome page (still with cntrl+shift+i open). Filtering under 'Name' by 'messages'. Under 'Headers' on the right side, take the Request URL.
#You can ignore the '?limit=50'
uid = '998751586270584882' #user id of DualityOfMan#0643 (the bot)
auth = 'OTk4NzUxNTg2MjcwNTg0ODgy.GMjOGI.4i2DfrfkkANq73fAPud0N6Amhq6mQSL-v_7AAE' #Authorization value
#This is found by opening Discord on chrome, typing cntrl+shift+i to open dev tools, go into Network tab, type something in server, click "message" under "Name"
#then scrolling down to 'authorization' and copying the code


intents = json.loads(open(directory + 'intents' + v + '.json').read())
words = pickle.load(open(directory + 'words' + v + '.pkl', 'rb'))
classes = pickle.load(open(directory + 'classes' + v + '.pkl', 'rb'))
model = load_model(directory + 'chatbotmodel' + v + '.h5')


#functions to clean sentences, get bag of word, to predict class based on sentence, to get a response

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1 #if the word matches, change its value in the array from 0 to 1

    return np.array(bag)


def predict_class(sentence):
    bow = bag_of_words(sentence) #create a bag of words from the sentence
    res = model.predict(np.array([bow]))[0] #predict result based on bag of words
    ERROR_THRESHOLD = 0.25 #error threshold of 25%
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD] #don't want too much uncertainty

    results.sort(key=lambda x: x[1], reverse=True) #sort by probability, reverse so that the highest probability is first
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
        else:
            result = 'That is a new one' #Input incase there is an error finding the tag. This seems to not work when the input is "Not sure what you mean"

    return result

print('PROGRAM IS LAUNCHED')
print(f"Please type something: \n")



##################################################### DISCORD INTEGRATION #################################################################
#TODO YOU MAY NEED TO UPDATED THE AUTHORIZATION KEY "auth" every time

#METHOD TO RETRIEVES MESSAGES FROM A DISCORD CHANNEL AND SERVER
def get_input(channelid): #needs input of chanel id

    headers = {
        'authorization': auth
    }
    r = requests.get(f'https://discord.com/api/v9/channels/{channelid}/messages', headers=headers)
    json_parse = json.loads(r.text) #retrieve all of the messages r is defined from the request
    
    for value in json_parse:

        return(value['content']) #value gives all the information. Since it is a json file, you can add ['content'] to only obtain the message content

 #did is a string containing the channelid. It can be found in the same place as where requests are gotten up there (where channelid is replaced)


#METHOD TO CHECK IF THERE IS A NEW MESSAGE THAT IS SENT IN THE CHANNEL

def msg_check(channelid):

    global nm 
    #Using Global Keyword so I can modify the global variable within the function (Note how tempid doesnt need to be re-initialized as it is not being modified locally)

    headers = {
        'authorization': auth
    }
    r = requests.get(f'https://discord.com/api/v9/channels/{channelid}/messages', headers=headers)

    json_parse = json.loads(r.text) 
    
    for value in json_parse:
        if(value['id'] != tempid and value['author']['id'] != uid): #to check if there is a new message in Discord by comparing the new message id to that of the last one
            print('new')
            nm = True
        else:
            print('old')
            nm = False
        break

#To reset msg check method
def msg_check_reset(channelid):

    global nm, tempid

    headers = {
        'authorization': auth
    }
    r = requests.get(f'https://discord.com/api/v9/channels/{channelid}/messages', headers=headers)

    json_parse = json.loads(r.text) 
    
    for value in json_parse:
        tempid = value['id']
        nm = False
        print("Reset Complete")
        break
    
#chatting/printing the messages

while True:

    message = get_input(did) #GET INPUT FROM DISCORD
    msg_check(did) #check if there is a new message and if it is not from the bot

    time.sleep(0.2) #buffer for testing 

    if(message == "Bye DualityOfMan"):
        sys.exit() #This fully stops the bot from running

    elif(message == "DualityOfMan"):
        ck = not ck #toggles the boolean to enable typing. "DualityOfMan" needs to be said by someone in the chat to enable the bot to begin typing

    ints = predict_class(message)
    resp = get_response(ints, intents)

    if ck == True and nm == True: #if typing mode is on and there is a new message
        print("Input: " + message)
        print("Response: " + resp)
        msg_check_reset(did) #reset msg check


        time.sleep(cd) #cooldown between messages
        time.sleep(bfr*a) #buffer that is randomized to further delay each message
        for char in resp: #print out message
            auto.press(char)
            time.sleep(0.005) #time between typing each keystroke
        auto.press('enter') #enter the message
        #uid = get_uid(did)
        print("From the while True :" + uid)

    elif nm == True: #if there is a new message
        print("Input: " + message)
        print("Response: " + resp)
        msg_check_reset(did) #reset msg check
        time.sleep(2) #time buffer

    else:
        print("awaiting new message...")
        time.sleep(2) #time buffer



#TODO
# 1. Perhaps go through discord Dms following response answer format? Maybe implement reactions under each message check, cross, and a refresh to indicate the following:
# check = good answer (keep) cross = bad answer (delete) refresh = (answer and question are flipped, flip them)
# 2. Using what you read from a pattern-response format (1 from a user, 1 response from a user), eliminate
# and get rid of useless words (as well as NSFW words) to find important key words. Also ignore links/files (find a way to identify)
# 3. If the pattern matches close enough (using our created functions) to an existing intents.json pattern, append the 
# response to the "responses": section.
# 4. Elif the response matches close enough (using our created functions) to an existing intents.json response, append the
# pattern to the "pattern": section.
# 5. If neither, create a new intent section with the "pattern": and "response": and continue. I HAVE ATTACHED A YT VIDEO ON THIS IN EASY
# 6. Make the json file rewrite itself as its scanning a Discord server chat
# 7. Afterwards, I can go through the intents briefly and remove/add necessary elements. Then, I can train the bot again.
# 8. Make sure it reads content that is considered "good"

# Extras: If someone says "Bye DualityOfMan", the bot closes its program
# Make a seperate method that is training mode. It will take all the 'content' from a user (multiple messages included, use if statements to see if its the same user)
# and then, it will record the 'content' in messages directly from the user that comes after as the response. It does not type anything during this period that is me
