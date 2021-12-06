#!/usr/bin/python  
#importing required libraries                                              
from tkinter import *
import threading
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from tkinter.messagebox import *
from tkinter.simpledialog import *
import tkinter as tk
import cv2
import cv2 as cv
import numpy as np
import sys, os,socket
import time
import csv
import glob , select , fnmatch
import config
import face
import smtplib
import mimetypes
import time

global already_mailed
already_mailed = False

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
 # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)

global class_code

#global declarations
LARGE_FONT=("Verdana",13,'bold')
med_font = ("Verdana",12,)
small_font =("Verdana",12)
MEAN_FILE = 'mean.png'
POSITIVE_EIGENFACE_FILE = 'positive_eigenface.png'
NEGATIVE_EIGENFACE_FILE = 'negative_eigenface.png'
s_font =("Verdana",10,'bold')
global counter
counter = 0
global filename
global fname
global lo_w, lo_h
global size
size = 4

#required initialization and variables

fn_haar = 'haarcascade_frontalface_alt.xml'
fn_dir = 'training'
haar_cascade = cv2.CascadeClassifier(fn_haar)

# function definitions

def quit_(root):
    global already_mailed
    
    if not already_mailed:
        attendance_mail(root)
        
    root.destroy()

#-- function to Pop up message event handing --#

def popup(name):
    showinfo('confirmation message','your  attendance is marked...'+name)

def popuptrained():
    showinfo('confirmation message','your faces are trained to system')
    return None

def popuperror():
    showerror("error", "Sorry.. unable to recognize")

def popupconnectionerror():
    showinfo('connection error','check your  internet connection')
    
def popupgmailerror():
    showinfo('gmail error',"couldn't find name in database")
    
def errornamenotfound():
    showerror("error", "sorry...name not found")
def showattendannce(attendance): 
    message = "Your attendance is " + str (attendance)
    showinfo("Check attendance ",message)
    
def errorfilenotexist():
    showerror("error", "Sorry.. file does not exists")
def popupfilecreation():
    showinfo('confirmation message','create file')
def popupfilecreated():
    showinfo('confirmation message','file created ')

def popupmanualattendance():
    showinfo('confirmation message','attendance is manually marked and notification send to HOD')

def walk_files(directory, match='*'):
        """Generator function to iterate through all files in a directory recursively
        which match the given filename match parameter.
        """
        for root, dirs, files in os.walk(directory):
                for filename in fnmatch.filter(files, match):
                        yield os.path.join(root, filename)

def prepare_image(filename):
        """Read an image as grayscale and resize it to the appropriate size for
        training the face recognition model.
        """
        return face.resize(cv2.imread(filename, cv2.IMREAD_GRAYSCALE))

def normalize(X, low, high, dtype=None):
        """Normalizes a given array in X to a value between low and high.
        Adapted from python OpenCV face recognition example at:
          https://github.com/Itseez/opencv/blob/2.4/samples/python2/facerec_demo.py
        """
        X = np.asarray(X)
        minX, maxX = np.min(X), np.max(X)
        # normalize to [0...1].
        X = X - float(minX)
        X = X / float((maxX - minX))
        # scale to [low...high].
        X = X * (high-low)
        X = X + low
        if dtype is None:
                return np.asarray(X)
        return np.asarray(X, dtype=dtype)

def mail(emailfrom,emailto,fileToSend,username,password):
    global already_mailed
    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = emailto
    msg["Subject"] = " Attendance mail"
    msg.preamble = " Attendance mail "

    ctype, encoding = mimetypes.guess_type(fileToSend)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)

    if maintype == "text":
        fp = open(fileToSend)
        attachment = MIMEText(fp.read(), _subtype=subtype)
        fp.close()
    else:
        fp = open(fileToSend, "rb")
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
    msg.attach(attachment)
    try :
        server = smtplib.SMTP("smtp.gmail.com", 587)
        #server = smtplib.SMTP("smtp.gmail.com:587")
        server.ehlo()
        server.starttls()
        server.ehlo()
        print ('connected to gmail'+'\n')
        try :
            server.login("iotprojectgroup2@gmail.com","vinaychamola")
            print ('sucessfully logged in to gmail')
            print ('WEL-COME to gmail')
            try:
                server.send_message(msg)
                already_mailed = True
                print ('email has been send to your mail id')
                server.quit()
            except  smtplib.SMTPException:
                 print ('Email could not be sent'+'\n')
                 pass;
        except  smtplib.SMTPException:
             print ('authentication failed'+'\n')
             
             pass;
    except (socket.gaierror,socket.error,socket.herror,smtplib.SMTPException) as e:
     print ('connection to gmail failed ...')
     print ('check the internet connection ')
     popupconnectionerror()
     pass;

def attendance_mail(root) :
    global class_code
    
    emailfrom = "iotprojectgroup2@gmail.com"
    c = 0
    while c == 0 :
        #code = askstring("Course Code", "Course Code")
        gmail = "iotprojectgroup2@gmail.com"
        #with open("./course/" +  code + ".csv",'rU') as f :
         #                  f_reader = csv.reader(f)
                           #for row in f_reader:
                           #    if row[0] == name :
                           #        gmail = row[3]
        #f.close()

        if gmail == "empty@gmail.com":
            c = 0
            popupgmailerror()
            print ("enter a valid name ")
            print ('')
        else :
            c = 1
            emailto = gmail
            print ("From- " + emailfrom)
           # print("To - " + email)
            fileToSend = "./courses/" +  class_code + ".csv"
            username = "iotprojectgroup2"
            password = "vinaychamola"
            mail(emailfrom,emailfrom,fileToSend,username,password)
            return
        
        
def newcourse(root):
    
    code_name = askstring("New member", "Enter Course Code")
    while code_name == '' :
        showinfo('Name error','enter the name correctly')
        nname = askstring("New member", "Enter Your Name")
        
        
    course_name = askstring("New member", "Enter Course Name")
    while course_name == '' :
        showinfo('Name error','enter the name correctly')
        nname = askstring("New member", "Enter Your Name")
        
    ic_name = askstring("New member", "Enter IC Name")
    while ic_name == '' :
        showinfo('Name error','enter the name correctly')
        nname = askstring("New member", "Enter Your Name")
        
    with open("./courses/" + code_name + ".csv",'w') as f :
        f_writer = csv.writer(f)
        f_writer.writerow(["course_code","course_name","ic_name"])
        
    f.close()

        
    showinfo('confirmation message','Your details are successfully entered')
    return None
    
        
    
    
    
    
    
    
    
#-- function to access and modify CSV file --#
def newmember(root):
    nname = askstring("New your ID", "Enter Your ID")
    while nname == '' :
        showinfo('Name error','enter the name correctly')
        nname = askstring("New member", "Enter Your Name")
    #print 'name :',nname

    ngender = askstring("New member", "Enter Gender")
    while ngender == '' :
        showinfo('error',"The parameter can't be empty")
        nname = askstring("New member", "Enter Gender")
    #print 'Gender :',ngender
    
    nid = askstring("New member name", "Enter Your Name")
    while nid == '' :
        showinfo('ID error','enter the id correctly')
        nid = askstring("New ID", "Enter Your BITS-Id")
    #print 'e-mail :',nemail
       
    nmobileno = askinteger("New member ", "Enter Your mobile no")
    mobile = str(nmobileno)
    
    with open("Details_Database.csv",'a') as f :
        f_writer = csv.writer(f)
        f_writer.writerow([nname,nid,ngender,nmobileno])
    f.close()
        
    showinfo('confirmation message','Your details are successfully entered')
    return None
def askname():
    asname = askstring("Name", "Enter Your Name")
    return asname
####-- function to update attendance --#
def mark(code,id_, attendtime) :
    if (os.path.isfile('./courses/' + code +'.csv')) :
        with open('./courses/' + code + ".csv",'a') as f :
                f_writer = csv.writer(f)
                f_writer.writerow([id_, attendtime])
        f.close()
    else :
        errorfilenotexist()
        filename = name+'.csv'
        file=open(filename,'w+')
        file.close()
        with open(name+".csv",'a') as f :
                f_writer = csv.writer(f)
                f_writer.writerow([attendtime])
        f.close()
        popupfilecreated()
    return  None

def check(root) :
    name = askname()
    if (os.path.isfile(name+'.csv')) :
        with open(name+".csv",'rU') as f :
                   f_reader = csv.reader(f)
                   count = 0
                   for row in f_reader:
                       count +=1
        f.close()
        showattendannce(count)
        
    else :
        errornamenotfound()


def manual_attendance(root):
    
        name = askname()
        id_ = askstring("ID:", "ID:")
        #code = askstring("Course Code - ", "Course Code - ")
        attendtime=time.asctime(time.localtime(time.time()))
        mark(class_code, id_, attendtime)
        popupmanualattendance()          

#---Training Recognizer function-------
def training(root):
        fn_name = askstring("Enter ID", "Enter ID")
        camera = config.get_camera()
        if not os.path.exists(config.POSITIVE_DIR):
                os.makedirs(config.POSITIVE_DIR)
        path = os.path.join(config.POSITIVE_DIR,fn_name)
        if not os.path.isdir(path):
            os.mkdir(path)
        files = sorted(glob.glob(os.path.join(path,'[0-9][0-9][0-9].pgm')))
        count = 0
        if len(files) > 0:
                count = int(files[-1][-7:-4])+1
        c =0
        while c < 10 :
                        ret,image = camera.read()
                        # Convert image to grayscale.
                        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                        # Get coordinates of single face in captured image.
                        result = face.detect_single(image)
                        if result is None:
                                print ('Could not detect single face!  Check the image in capture.pgm' \
                                          ' to see what was captured and try again with only one face visible.')
                                continue
                        x, y, w, h = result
                        # Crop image as close as possible to desired face aspect ratio.
                        # Might be smaller if face is near edge of image.
                        crop = face.crop(image, x, y, w, h)
                        # Save image to file.
                        filename = os.path.join(path,'%03d.pgm' % count)
                        cv2.imwrite(filename, crop)
                        print ('Found face and wrote training image', filename)
                        c += 1
                        count += 1
        popuptrained()
        
#---Recognise and Mark attendance function-------
def mark_attendance(root):
                    
            flag = 1
            #print "Reading training images...!"
            #code = askstring("Course Code", "Enter Your Couse Code")
            
            while flag == True :
                    faces = []
                    labels = []
                    names = {}
                    pos_count = 0
                    neg_count = 0
                    id = 1
                    # Read all positive images
                    for (subdirs, dirs, files) in os.walk(config.POSITIVE_DIR):
                          for subdir in dirs:
                            names[id] = subdir
                            subjectpath = os.path.join(config.POSITIVE_DIR, subdir)
                            for filename in os.listdir(subjectpath):
                                    path = subjectpath + '/' + filename
                                    faces.append(prepare_image(path))
                                    label = id
                                    labels.append(int(label)) 
                                    pos_count += 1
                            id += 1
                    # Read all negative images
                    for filename in walk_files(config.NEGATIVE_DIR, '*.pgm'):
                            faces.append(prepare_image(filename))
                            labels.append(config.NEGATIVE_LABEL)
                            neg_count += 1

                    # Train model
                    flag = 0
                    model = cv2.face.createEigenFaceRecognizer()
                    model.train(np.asarray(faces), np.asarray(labels))

                    # Save model results
                    model.save(config.TRAINING_FILE)

                    # Save mean and eignface images which summarize the face recognition model.
                    mean = model.getMean().reshape(faces[0].shape)
                    cv2.imwrite(MEAN_FILE, normalize(mean, 0, 255, dtype=np.uint8))
                    eigenvectors = model.getEigenVectors()
                    pos_eigenvector = eigenvectors[:,0].reshape(faces[0].shape)
                    cv2.imwrite(POSITIVE_EIGENFACE_FILE, normalize(pos_eigenvector, 0, 255, dtype=np.uint8))
                    neg_eigenvector = eigenvectors[:,1].reshape(faces[0].shape)
                    cv2.imwrite(NEGATIVE_EIGENFACE_FILE, normalize(neg_eigenvector, 0, 255, dtype=np.uint8))
            # Load training data into model
            print ('Loading training data...')
            model = cv2.face.createEigenFaceRecognizer()
            model.load(config.TRAINING_FILE)
            print ('Training data loaded!')
            # Initialize camera
            camera = config.get_camera()
            c = 0
            while c < 1:
                    ret, image = camera.read()
                    # Convert image to grayscale.
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                    # Get coordinates of single face in captured image.
                    result = face.detect_single(image)
                    if result is None:
                            print ('Could not detect single face!  Check the image in capture.pgm' \
                                      ' to see what was captured and try again with only one face visible.')
                            continue
                    x, y, w, h = result
                    # Crop and resize image to face.
                    crop = face.resize(face.crop(image, x, y, w, h))
                    # Test face against model.
                    label, confidence = model.predict(crop)
                    if not label == config.NEGATIVE_LABEL and confidence < config.POSITIVE_THRESHOLD:
                            
                            tattend=time.asctime(time.localtime(time.time()))
                            c+=1
                            id_ = names[label]
                            mark(class_code, id_, tattend)
                            popup(id_)
                    else:
                            popuperror()
                            c+=1
       
       
    

    


#while True:
if __name__ == '__main__':
    

    #while True:
    
        root = tk.Tk()
        time1 = ''
        clock = tk.Label(master=root, font=s_font,fg='green', bg='white')
        clock.grid(column=1, columnspan=2,row=1)
        def tick():
            global time1
            time2 = time.strftime('%H:%M:%S')
            if time2 != time1:
                time1 = time2
                clock.config(text="Time:"+time2)
            clock.after(200, tick)
        tick()
        
        global class_code
        class_code = askstring("Enter Class Code","Class Code")
        
        with open("./courses/" + class_code + ".csv",'w') as f :
            f.truncate()
            f_writer = csv.writer(f)
            f_writer.writerow(["course_code","course_name","ic_name"])
        
        f.close()
        
        
        label1=tk.Label(master=root,text="BITS Attendance System",font=LARGE_FONT,fg='black',bg='white')
        label1.grid(column=1,row= 0,columnspan=2, padx=2, pady=2)
        
        
        
        button3 = tk.Button(master=root, text='New Member',font=small_font,fg='blue',bg='white', command=lambda: newmember(root))
        button3.grid(column=1, columnspan=2, row=1, padx=5, pady=5)
        
        button2 = tk.Button(master=root, text='Train Recognizer',font=small_font,fg='blue',bg='white', command=lambda: training(root))
        button2.grid(column=1, columnspan=2, row=2, padx=5, pady=5)
        button1 = tk.Button(master=root, text='Mark attendance',font=small_font,fg='blue',bg='white', command=lambda: mark_attendance(root))
        button1.grid(column=1, columnspan=2, row=3, padx=5, pady=5)
        button4 = tk.Button(master=root, text='Manual marking',font=small_font,fg='blue',bg='white', command=lambda:  manual_attendance(root))
        button4.grid(column=1, columnspan=2, row=4, padx=5, pady=5)
        mailbutton = tk.Button(master=root, text='mail my attendance',font=med_font,fg='blue',bg='white', command=lambda:attendance_mail(root))
        mailbutton.grid(column=1, row=5, padx=5, pady=5)
        

        
        quit_button = tk.Button(master=root, text='END',font=med_font,bg="red3", fg="white", command=lambda: quit_(root))
        quit_button.grid(column=1, row=6, padx=5, pady=5)
        root.title("BITS Attendance System")
        root.geometry("350x400")
        #root.mainloop()
        
        def run():
            count = 0            
            while True: # Run forever 
                if GPIO.input(10) == GPIO.HIGH:                
                    count += 1
                    time.sleep(0.5)
                    mark_attendance(root)

    
        thread = threading.Thread(target = run)
        thread.start()

        root.mainloop()
        
        


                
                
                
        
