import string
import sys
from PIL import Image
import pytesseract
from ics import Calendar,Event
def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

img_name = sys.argv[1]
img = Image.open(img_name)
py = pytesseract.image_to_string(img,lang = "eng")
res = ""
for c in py:
    if 0 <= ord(c) <=127:
        res += c


def processData(newRawData):
    resultList = []
    for line in (newRawData.strip()).splitlines():
        if(not line.startswith(' ')) and (line != ''):
            resultList.append(line)
    #for i in resultList:

    return resultList

def getTime(data):
    timeList = []
    for i in data:
        if(":" in i or "PM" in i or "AM" in i):
            timeList.append(i)
    timeLista = []
    for i in timeList:
        for j in i.split(' '):
            timeLista.append(j)
    timeList2 = []
    for i in timeLista:
        newi = ''
        for j in i:
            if(j.isdigit() or j == ':' or j ==  '.' or j == '/'):
                newi += j
        timeList2.append(newi)
        lp = [x for x in timeList2 if x != '']
    return lp

def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

places_string = readFile("location.txt")
places_list = []
for place in places_string.split("\n")[:-2]:
    places_list.append(place)

word_list = processData(res)

def find_hall(word_list):
    res = []
    indeces = []
    for i in range(len(word_list)):
        c = word_list[i]
        for place in places_list:
            if place in c.upper():
                res.append(place)
                indeces.append(i)
    r = []
    is_changed = False
    for i in range(len(res)):
        c = res[i]
        for j in range(len(res)):
            if i != j and c in res[j]:
                r.append(res[j])
                is_changed = True
    return (r if is_changed else res, [word_list[i] for i in indeces])

def find_room(word_list):
    def is_valid_room(s):
        for c in s[:-1]:
            if not c.isdigit() : 
                return False
        return s[-1].isalnum()
    for word in word_list:
        word_len_list = [4,3]
        for word_len in word_len_list:
            for c in range(len(word)-word_len):
                tar = word[c:c+word_len+1]
                if tar.startswith(" ") and is_valid_room(tar[1:]):
                    return tar
                elif tar.endswith(" ") and is_valid_room(tar[:-1]):
                    return tar
    return ""

(hall,hall_list) = find_hall(word_list)
location = " ".join(hall) + find_room(hall_list)


Corpus_list = readFile("words.txt").split("\n")[:-1]
count = 0
p = []
def strip_words(word):
    res = ""
    for c in word:
        if c.isalpha():
            res += c
    return res
for sent in word_list:
    words = sent.strip().split(" ")
    for word in words:
        strip_words(word)
        if word.lower() in Corpus_list:
            p.append(sent)
            count += 1
            break
    if count == 2:
        break 

event = "  ".join(p)

# below is for finding time:

def getMonth(data):
    month = ['jan','feb','mar','april','may','jun','jul','aug','sept','oct','nov','dec']
    for i in data:
        for mon in month:
            if(mon in i.lower()):
                return mon

def getDate(data):
    result = ''
    aa = []
    for i in data:
        num = ''
        if('th' in i.lower()):
            for j in i:
                if(j.isdigit()):
                    result += j
    if(result != ''):
        return result
    else:
        for i in data:
            for j in i:
                if(j.isdigit()):
                    return i[:2]

def getAMPM(data):
    for i in data:
        if ('AM' in i.upper()):
            return 'AM'
        elif('PM' in i.upper()):
            return 'PM'


def getStartTime(data):
    time = []
    for i in data:
        if('-' in i and ('am' in i or 'pm' in i)):
            return i[0]
        if(':' in i):
            if('30' in i):
                return i[0] + '.5'
            else:
                return i[0]

def getTime(data):
    month = ['jan','feb','mar','april','may','jun','jul','aug','sept','oct','nov','dec']
    timeList = []
    for i in data:
        if(":" in i or "PM" in i.upper() or "AM" in i.upper() or '-' in i):
            timeList.append(i)
        for mon in month:
            if(mon in i.lower() and (i not in timeList)):
                timeList.append(i)
    
    timeLista = []
    for i in timeList:
        for j in i.split(' '):
            timeLista.append(j)
    
    month = getMonth(timeLista)
    date = getDate(timeLista)
    ampm = getAMPM(timeLista)
    starttime = getStartTime(timeLista)
    duration = 1
    return [month,date,ampm,starttime,duration]

Time_Data_List = getTime(word_list)

# To ics
# [month,date,ampm,starttime,duration]
c = Calendar()
e = Event()
e.name = event

def convertMonth(data):
    month = ['jan','feb','mar','april','may','jun','jul','aug','sept','oct','nov','dec']
    mon = data[0]
    result = ''
    for index in range(len(month)):
        if(mon == month[index]):
            result += str(index+1)
    if(len(result) < 2):
        return '0'+result
    else:
        return result

def convertTime(Time_Data_List):
    starttime = Time_Data_List[-2] if "." in Time_Data_List[-2] else Time_Data_List[-2] + ".0"
    minutes = "30" if ".5" in starttime else "00"
    hours = int(starttime[:-2])
    if Time_Data_List[2].lower() == "pm":
        hours += 12
    return "0" * (2-len(str(hours))) + str(hours) + minutes


begin = '2016%s%sT%s00' % (convertMonth(Time_Data_List),Time_Data_List[1],convertTime(Time_Data_List))
hours = int(begin[9:11])
day   = int(begin[6:8])
hours += 4
if hours >= 24:
    hours -= 24
    day += 1
begin = begin[:6] + "0" * (2-len(str(day))) + str(day) + "T"  + "0" * (2-len(str(hours))) + str(hours) + begin[11:]
e.begin = begin
e.duration = {"hours": Time_Data_List[-1]}
e.location = location

c.events.append(e)
c.events
with open('event.ics', 'w') as my_file:
    my_file.writelines(c)
