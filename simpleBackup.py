# NOTES
# https://stackoverflow.com/questions/3964681/find-all-files-in-a-directory-with-extension-txt-in-python
# https://stackoverflow.com/questions/151199/how-to-calculate-number-of-days-between-two-given-dates
# https://docs.python.org/3/library/datetime.html#timedelta-objects
# https://sevenzip.osdn.jp/chm/cmdline/switches/update.htm
# https://superuser.com/questions/544336/incremental-backup-with-7zip
# Cretae a full folder archiv: "C:\Program Files\7-Zip\7z.exe" a c:\1\exist2.7z ".\Neuer Ordner\*"
# Create an update diff archiv: "C:\Program Files\7-Zip\7z.exe" u c:\1\exist.7z -u- -up0q3x2z0!c:\1\update2.7z ".\Neuer Ordner\*"
# https://docs.python.org/3/library/subprocess.html#module-subprocess
# https://docs.python.org/3/library/sched.html

from datetime import datetime
from datetime import timedelta
import os
import subprocess
import sched, time
import random # for testing purpose
import string # for testing purpose

##############################################################################################

# Config:
exePath = "C:\\Program Files\\7-Zip\\7z.exe"
storageFolder = "c:\\backups\\"
folderToDoBackupsOf = "c:\\veryimportantfiles\\"
writeLogfile = True
fullBackupStep = timedelta(days=7)
incrementalStep = timedelta(days=1)
removeOldBackups = True
keepFullBackupsFor = timedelta(days=7*5)
keepIncrementalBackupsFor = timedelta(days=7*2)

##############################################################################################

dateLastFullBack = datetime(2000, 2, 20)
dateLastFullBackFileName = ""
dateLastIncrementalBack = datetime(2000, 2, 20)
dateLastIncrementalBackFileName = ""

testing = False # used for dev debug
s = sched.scheduler(time.time, time.sleep)

if testing == True:
  fullBackupStep = timedelta(seconds=10)
  incrementalStep = timedelta(seconds=2)
  keepFullBackupsFor = timedelta(seconds=7*10)
  keepIncrementalBackupsFor = timedelta(seconds=7*2)

##############################################################################################

def writeLog(message):
  if writeLogfile == True:
    f = open(storageFolder+"_backup_log.txt", "a")
    f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + message + "\n")
    f.close()

def findLastFullBackup():
  global dateLastFullBack, dateLastFullBackFileName
  for file in os.listdir(storageFolder):
    if file.endswith("_full.7z"):
      #print(os.path.join(storageFolder, file))
      curFileDatetime = datetime.strptime(file[0:15], "%Y%m%d_%H%M%S")
      if curFileDatetime > dateLastFullBack:
        dateLastFullBack = curFileDatetime
        dateLastFullBackFileName = file
  #print("::findLastFullBackup() Last full backup found:" , dateLastFullBack, "-> " + dateLastFullBackFileName)

def findLastIncrementalBackup():
  global dateLastIncrementalBack, dateLastIncrementalBackFileName
  for file in os.listdir(storageFolder):
    if file.endswith("_increment.7z"):
      #print(os.path.join(storageFolder, file))
      curFileDatetime = datetime.strptime(file[0:15], "%Y%m%d_%H%M%S")
      if curFileDatetime > dateLastIncrementalBack:
        dateLastIncrementalBack = curFileDatetime
        dateLastIncrementalBackFileName = file
  #print("::findLastIncrementalBackup() Last incremental backup found:" , dateLastIncrementalBack, "-> " + dateLastIncrementalBackFileName)

def doCleanUp():
  if removeOldBackups == True:
    #writeLog("::doCleanUp() start")
    global dateLastFullBack, dateLastFullBackFileName
    for file in os.listdir(storageFolder):
      filename = os.path.join(storageFolder, file)
      if file.endswith("_full.7z"):
        curFileDatetime = datetime.strptime(file[0:15], "%Y%m%d_%H%M%S")
        if datetime.now() - keepFullBackupsFor > curFileDatetime:
          try:
            writeLog("::doCleanUp() remove full backup: filename='"+filename+"'")
            print("::doCleanUp() remove full backup: filename='"+filename+"'")
            os.remove(filename)
          except OSError as error:
            writeLog("::doCleanUp() error remove file: strerror='"+error.strerror+"'")
      elif file.endswith("_increment.7z"):
        curFileDatetime = datetime.strptime(file[0:15], "%Y%m%d_%H%M%S")
        if datetime.now() - keepIncrementalBackupsFor > curFileDatetime:
          try:
            writeLog("::doCleanUp() remove incremental backup: filename='"+filename+"'")
            print("::doCleanUp() remove incremental backup: filename='"+filename+"'")
            os.remove(filename)
          except OSError as error:
            writeLog("::doCleanUp() error remove file: strerror='"+error.strerror+"'")
    #writeLog("::doCleanUp() end")

def createFullBackup(targetFolder):
  writeLog("::createFullBackup() start: targetFolder="+targetFolder)
  newFileFullBackup = datetime.now().strftime("%Y%m%d_%H%M%S") + "_backup_full.7z"
  output = subprocess.run([exePath, "a", storageFolder+newFileFullBackup, targetFolder], capture_output=True)
  writeLog("::createFullBackup() result: returncode='"+str(output.returncode)+"' stdout='"+str(output.stdout)+"'")
  if output.returncode == 0:
    #print("::createFullBackup() output=",output)
    print("::createFullBackup() created ", newFileFullBackup)
  else:
    print("::createFullBackup() ERROR output=", output)
  writeLog("::createFullBackup() end: targetFolder="+targetFolder)

def createIncrementalBackup(targetFolder, referenceArchiv):
  writeLog("::createIncrementalBackup() start: targetFolder="+targetFolder+" referenceArchiv="+referenceArchiv)
  newFileFullBackup = datetime.now().strftime("%Y%m%d_%H%M%S") + "_backup_"+referenceArchiv[0:15]+"_increment.7z"
  output = subprocess.run([exePath, "u", storageFolder+referenceArchiv, "-u-", "-up0q3x2z0!"+storageFolder+newFileFullBackup, targetFolder], capture_output=True)
  writeLog("::createIncrementalBackup() result: returncode='"+str(output.returncode)+"' stdout='"+str(output.stdout)+"'")
  if output.returncode == 0:
    #print("::createIncrementalBackup() output=",output)
    print("::createIncrementalBackup() created ", newFileFullBackup)
  else:
    print("::createIncrementalBackup() ERROR output=", output)
  writeLog("::createIncrementalBackup() end: targetFolder="+targetFolder+" referenceArchiv="+referenceArchiv)

def get_random_string(length):
  return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def randomChange(targetFolder):
  f = open(targetFolder+"TEST_CHANGE.txt", "a")
  f.write(get_random_string(256))
  f.close()

# testing simple creation process
if testing == True:
  findLastFullBackup()
  findLastIncrementalBackup()
  createFullBackup(folderToDoBackupsOf+"*")
  findLastFullBackup()
  findLastIncrementalBackup()
  createIncrementalBackup(folderToDoBackupsOf+"*", dateLastFullBackFileName)
  findLastFullBackup()
  findLastIncrementalBackup()

def executeBackup():
  #print(time.time(), "::executeBackup()")
  doCleanUp()
  findLastFullBackup()
  findLastIncrementalBackup()

  if datetime.now() - dateLastFullBack > fullBackupStep:
    # last full backup is old then intended
    createFullBackup(folderToDoBackupsOf+"*")
  else:
    if datetime.now() - dateLastIncrementalBack > incrementalStep and datetime.now() - dateLastFullBack > incrementalStep:
      createIncrementalBackup(folderToDoBackupsOf+"*", dateLastFullBackFileName)
  
  findLastFullBackup()
  findLastIncrementalBackup()

  if testing == True:
    # create some random changed file on the folder
    randomChange(folderToDoBackupsOf)

  nextTriggerInAbsSeconds = incrementalStep.total_seconds()

  # just check if the fullback up would be required due earlier as the increment
  if incrementalStep > datetime.now() - dateLastFullBack:
    nextTriggerInAbsSeconds = (datetime.now() - dateLastFullBack).total_seconds()
  s.enter(nextTriggerInAbsSeconds, 1, executeBackup)

executeBackup()
s.run()