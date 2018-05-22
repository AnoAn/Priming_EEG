# coding=utf-8

############################################################################
#########################--AFFECTIVE PRIMING--##############################
############################################################################

from psychopy import visual, data, core, event, gui, parallel
import random
import datetime #library to get the current date
import pyglet
import csv
import itertools
import os
import demogrAno

#set port
parallel.setPortAddress(888) #address for parallel port on many machines = 888

#get demographics
demogrAno.demographics()
subj = int(demogrAno.subj)
age = demogrAno.age
gender = demogrAno.gender

print subj, age, gender

#--------------------------------------------------------------------------#
#------------------------------Parameters----------------------------------#
#--------------------------------------------------------------------------#
win = visual.Window([1200,800], fullscr = 1, units = 'pix', color='gray', screen = 0) #set the window's size
clock = core.Clock() #set the clock
tmpData = str(datetime.datetime.now())[0:10] #get the current date
tmpOra = str(datetime.datetime.now())[11:19]
tmpOra = tmpOra.replace(":","-")
fix = visual.TextStim(win,text="x",units = "pix", height = 88,pos=(0,5), font = "lucida sans typewriter", color = 'black', alignHoriz='center', alignVert='center')


#create save folder
if not os.path.exists("Results"):
    os.makedirs("Results")

#Assign labels and keys
if subj%2==1:
    labels=[['Positiva','f','P'],['Negativa','j','N']]
elif subj%2==0:
    labels=[['Negativa','f','N'],['Positiva','j','P']]

parallel.setData(0)

#------------IMPORT STIMULI
with open("Lists/practice_stim.csv") as g:
    reader = csv.reader(g, delimiter=';')
    practice_stim=[]
    counter=0
    for row in reader:
        if counter>0:
            practice_stim.append(row)
        counter+=1

random.shuffle(practice_stim)

with open("Lists/Trials_PP_%i.csv"%(subj)) as f:
    reader = csv.reader(f, delimiter=';')
    stimuli=[]
    counter=0
    for row in reader:
        if counter>0:
            stimuli.append(row)
        counter+=1

#define functions
def AffPriming(stim):
    global resp,RT, corr_practice, fix
    pause = visual.TextStim(win, font = "lucida sans typewriter", text="Puoi fare una breve pausa.\n\
    \n\
    RICORDA:\n\
    F = %s\t J= %s\n\
    \n\
    Per continuare premi F o J."%(labels[0][0],labels[1][0]),units = "pix", height = 30,pos=(0,0), color = 'black', alignHoriz='center', alignVert='center')
    prime = visual.TextStim(win,text="",units = "pix", height = 53,font = "lucida sans typewriter", pos=(0,-5), color = 'black', alignHoriz='center', alignVert='center')
    tgt = visual.TextStim(win,text="",units = "pix", height = 63, font = "lucida sans typewriter", pos=(0,0), color = 'black', alignHoriz='center', alignVert='center')
    label_L = visual.TextStim(win,text=labels[0][0],units = "pix", height = 40,pos=(-250,250), color = 'black', alignHoriz='center', alignVert='center')
    label_R = visual.TextStim(win,text=labels[1][0],units = "pix", height = 40,pos=(250,250), color = 'black', alignHoriz='center', alignVert='center')
    trialcounter=0
    corr_practice=0
    core.wait(1)
    for i in stim:
        prime.setText(i[0])
        tgt.setText(i[1])
        trialcounter+=1
        if trialcounter%28==0 and trialcounter!=324:
            pause.draw()
            win.flip()
            parallel.setData(2)
            event.waitKeys(keyList=[labels[0][1],labels[1][1]])
            parallel.setData(0)
            
            core.wait(float(random.randrange(1000,2000,100))/1000)
        
        fix.setAutoDraw(1)
        for x in range(30): #--FIXATION (500 ms)
            win.flip()
        fix.setAutoDraw(0)

        
        for x in range(11): #--BLANK (200 ms)
            win.flip()
        
        win.callOnFlip(parallel.setData,7)#   <---trigger Prime
        prime.setAutoDraw(1)
        for x in range(9): #--PRIME (150 ms)
            win.flip()
        win.callOnFlip(parallel.setData,0)
        prime.setAutoDraw(0)
        
        for x in range(6): #--BLANK (100 ms) -counting extra frame
            win.flip()
        
        event.clearEvents()
        frames = 0
        clock.reset()
        tgt.setAutoDraw(1)
        win.callOnFlip(parallel.setData,int(i[6]))#   <---trigger
        while 1:
            win.flip()
            frames+=1
            if frames>=18: # --TARGET (300 ms)
                tgt.setAutoDraw(0)
            if frames == 6:
                win.callOnFlip(parallel.setData,0)
            resp = event.getKeys(keyList=['f','j'])
            if resp != []:
                RT0 = clock.getTime()
                RT = ('%.4f' % RT0).replace('.',',')
                if resp[0]=='f' and i[4]==labels[0][2] or resp[0]=='j' and i[4]==labels[1][2]:
                    parallel.setData(100)
                    tgt.setAutoDraw(0)
                    acc = 1
                    if int(i[7])==0:
                        corr_practice += 1
                    print "correct", RT
                    win.flip()
                else:
                    parallel.setData(150)#  <---trigger ERROR
                    tgt.setAutoDraw(0)
                    acc = 0
                    print "error",RT
                    win.flip()
                break
            if clock.getTime() >=1.8:
                parallel.setData(200) #  <---trigger No RESP
                resp = ['X']
                RT = 0
                acc = 2
                print acc,RT
                win.flip()
                break
            if event.getKeys(keyList=['escape']):
                data_frame.close()
                parallel.setData(0)
                core.quit()
        data_frame.write("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n"%
        (tmpData,tmpOra,subj,age,gender,prime.text,tgt.text,i[2],i[3],i[4],i[5],trialcounter,RT,acc,labels[0][1:3],resp[0],i[6],i[7]))
        for frm in range(5): #counting the flip before
            if frm == 4:
                win.callOnFlip(parallel.setData,0)
            win.flip()
        core.wait(float(random.randrange(900,1900,100))/1000) #-random jitter 800-1200 ms by 100 ms



#create save file
data_frame = open("Results/%s_%s_Output_Subject_%s.csv"%(tmpData,tmpOra,subj),"a")
data_frame.write("date;time;Subject;Age;Gender;Prime;Target;tgt_Cat;prime_Val;tgt_Val;congr;TrialNum;RT;accuracy;ButtonMap;Choice;Trigger;Round\n")

#----------EVENTS---------#
event.Mouse(visible=0)
parallel.setData(0)
fix.draw()
win.flip()
event.waitKeys(keyList=['space'])
fix.setText("+")
win.callOnFlip(parallel.setData, 1)
event.clearEvents()
clock.reset()
#resting state
while 1:
    fix.draw()
    win.flip()
    if clock.getTime() >=300:
        parallel.setData(0)
        break
    if event.getKeys(keyList=['escape']):
        parallel.setData(0)
        win.close()
        core.quit()
    if event.getKeys(keyList=['return']):
        parallel.setData(0)
        break
core.wait(0.1)


#ISTRUZIONI PRATICA
parallel.setData(2)
demogrAno.istruzioni(win,
u"Vedrai comparire al centro dello schermo delle coppie di parole, una per volta. \
A volte una serie di segni # comparirà al posto della prima parola.\n\
\n\
Il tuo compito è indicare il tipo di sensazione (positiva o negativa) che evoca la SECONDA parola.\n\
\n\
La seconda parola comparirà solo per un breve intervallo. Cerca di rispondere il più velocemente possibile, anche dopo la sua scomparsa.\n\
\n\
Premi il tasto %s se la sensazione è %s.\nPremi il tasto %s se la sensazione è %s.\n\
\n\
Ora iniziera' la pratica."%
(labels[0][1].upper(), labels[0][0].upper(),labels[1][1].upper(), labels[1][0].upper()), continueButtons=['space'])
core.wait(float(random.randrange(1000,2000,100))/1000) #-random wait jitter 800-1200 ms by 100 ms
parallel.setData(0)

AffPriming(practice_stim)
print corr_practice

#CHECK ACCURACY PRATICA
while corr_practice<15:
    parallel.setData(2)
    demogrAno.istruzioni(win,
    "Prima di continuare, contatta lo sperimentatore.")
    demogrAno.istruzioni(win,u"indica il tipo di sensazione che evoca la SECONDA parola che compare sullo schermo.\n\nPremi il tasto %s se la sensazione è %s.\n\nPremi il tasto %s se la sensazione è %s"%
    (labels[0][1].upper(), labels[0][0].upper(),labels[1][1].upper(), labels[1][0].upper()))
    parallel.setData(0)
    random.shuffle(practice_stim)
    AffPriming(practice_stim)

parallel.setData(2)

#ISTRUZIONI TASK
demogrAno.istruzioni(win,
u"La pratica è finita ed ora inizierà il test.\n\n\
IMPORTANTE:\n\
-valuta sempre la SECONDA parola.\n\
-rispondi il più velocemente possibile, anche dopo la scomparsa della parola.\n\
-cerca di non sbattere le palpebre prima di aver risposto.\n\
-Premi il tasto %s se la sensazione è %s.\nPremi il tasto %s se la sensazione è %s.\n\n\
Ora inizierà il test."%
(labels[0][1].upper(), labels[0][0].upper(),labels[1][1].upper(), labels[1][0].upper()))
parallel.setData(0)

#RANDOM INITIAL JITTER
core.wait(float(random.randrange(800,1200,100))/1000) #-random wait jitter 800-1200 ms by 100 ms

#MAIN TASK
AffPriming(stimuli)
data_frame.close()

#BYE
demogrAno.istruzioni(win, U"L'esperimento è finito. Contatta lo sperimentatore")
win.close()
core.quit()