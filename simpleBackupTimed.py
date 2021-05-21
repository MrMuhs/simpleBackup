from datetime import datetime
from datetime import timedelta
import os
import subprocess
import sched, time

##############################################################################################

# Config:
exePath = "C:\\Program Files\\7-Zip\\7z.exe"
storageFolder = "c:\\backups\\"
folderToDoBackupsOf = "c:\\veryimportantfiles\\"
writeLogfile = True

timeOfDayToStartBackup = "02:00:00" # like hour:minute:second
dayToDoFullBackup = 6 # like weekday as a decimal number [0->Sunday, 1->Monday, 2->Thuesday, 3->Wednesday, 4->Tu, 5->Fr, 6->Sa].

removeOldBackups = True
keepFullBackupsFor = timedelta(days=7*5)
keepIncrementalBackupsFor = timedelta(days=7*2)

##############################################################################################

dateLastFullBack = datetime(2000, 2, 20)
dateLastFullBackFileName = ""
dateLastIncrementalBack = datetime(2000, 2, 20)
dateLastIncrementalBackFileName = ""

s = sched.scheduler(time.time, time.sleep)

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

def executeBackup():
  #print(time.time(), "::executeBackup()")
  doCleanUp()
  findLastFullBackup()
  findLastIncrementalBackup()

  if datetime.now() - timedelta(days=7) > dateLastFullBack or datetime.now().strftime("%w") == dayToDoFullBackup:
    # last full backup is old then intended
    createFullBackup(folderToDoBackupsOf+"*")
  else:
    if datetime.now() - timedelta(days=1) > dateLastIncrementalBack and datetime.now() - timedelta(days=1) > dateLastFullBack:
      createIncrementalBackup(folderToDoBackupsOf+"*", dateLastFullBackFileName)
  
  findLastFullBackup()
  findLastIncrementalBackup()
  
  nextBackupTime = datetime.strptime(datetime.now().strftime("%Y%m%d") + "_" + timeOfDayToStartBackup, "%Y%m%d_%H:%M:%S")
  if nextBackupTime < datetime.now():
    nextBackupTime = nextBackupTime + timedelta(days=1)
  
  print("::executeBackup() next backup execution: ", nextBackupTime, "which is",(nextBackupTime - datetime.now()).total_seconds(), "s from now")
  writeLog("::executeBackup() next backup execution: " + str(nextBackupTime) +" which is " + str((nextBackupTime - datetime.now()).total_seconds()) + "s from now")

  s.enter((nextBackupTime - datetime.now()).total_seconds(), 1, executeBackup)

writeLog("::main() script started")
executeBackup()
s.run()