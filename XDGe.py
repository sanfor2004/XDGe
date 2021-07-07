import urllib.request
import urllib.error
import time
import sys
import os
import re


def SaveData(DATA):
	DATAFILE = open("DATA_XAR.txt","a")
	DATAFILE.write(DATA)
	DATAFILE.close()

def SaveGOData(DATA):
	DATAFILE = open("GODATA_XAR.txt","a")
	DATAFILE.write(DATA)
	DATAFILE.close()
	
def UScanner(x75726c):
	try:
		XDG = urllib.request.Request(x75726c)
		XDG.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
		REQ = urllib.request.urlopen(XDG, timeout=10)
		print("["+str(x.getcode())+"] found_ " +x75726c)
		SaveData(x75726c)
	except Exception as e:
		if "404" in str(e):
			print("[404] Not found_ "+x75726c)

def cls():
    os.system('cls' if os.name=='nt' else 'clear')




def GOscan(URLTARGET,DORKUSERFILE):
	DOKERLIST = []
	GODOKERFILE = open(DORKUSERFILE,"r")
	for CONGODOKER in GODOKERFILE:
		DOKERLIST.append(CONGODOKER)
	for CONDOKERLIST in range(len(DOKERLIST)):
			DORKTARGET = DOKERLIST[CONDOKERLIST].replace(" ","+").replace("\n","")
			SETGODORK  = "site:{URLTARGET}+{DORKTARGET}".format(URLTARGET=URLTARGET, DORKTARGET=DORKTARGET)
			SETGOWEBS  = 'https://www.google.com/search?q='+SETGODORK+'&client=firefox-b-d&start=0'
			REQGODORK  = urllib.request.Request(SETGOWEBS)
			REQGODORK.add_header('User-Agent', 'Mozilla/7000.0 XAR')
			#---------------------------------------------
			REQGOOGLE  = urllib.request.urlopen(REQGODORK, timeout=10)
			RESGODORK  = REQGOOGLE.read()
			REQGOOGLE.close()
			CLEARREQD  = re.findall('<a.href="/url\?q=(.*?)\&amp', str(RESGODORK))
			for DO in CLEARREQD:
				if "https://support.google.com" in DO or "https://accounts.google.com/" in DO:
					pass
				else:
					print(DO)
					SaveGOData(DO)
			time.sleep(1)




def vulnScan(iNPTARGET):
	VUL = ["apache.txt", "cgis.txt", "coldfusion.txt","domino.txt","fatwire.txt","fatwire_pagenames.txt","frontpage.txt","iis.txt","iplanet.txt","jrun.txt","netware.txt","oas.txt","sharepoint.txt","sunas.txt","tests.txt","tomcat.txt","vignette.txt","weblogic.txt","websphere.txt"]
	for i in range(len(VUL)):
		print("\n\tRead > "+VUL[i]+"\n")
		VULFILE = open("xarWORD\\vulns\\"+VUL[i],"r+")
		for VULNDIR in VULFILE:
			VULWORD = VULFILE.readline().replace("\n","")
			MTARGETVULN = iNPTARGET+"/"+VULWORD
			UScanner(MTARGETVULN)


def NormalScan(iNPTARGET):
	NOR = ["big.txt", "catala.txt", "catala.txt","euskera.txt","extensions_common.txt","indexes.txt","frontpage.txt","mutations_common.txt","small.txt","spanish.txt","stress\\alphanum_case.txt","stress\\alphanum_case_extra.txt","stress\\char.txt","stress\\doble_uri_hex.txt","stress\\test_ext.txt","stress\\unicode.txt","stress\\uri_hex.txt","others\\names.txt","others\\common_pass"]
	for z in range(len(NOR)):
		print("\n\tRead > "+NOR[z]+"\n")
		NORFILEOP = open("xarWORD\\"+z,"r+")
		for NORDIR in NORFILEOP:
			NORWORD = NORFILEOP.readline().strip()
			MTARGETNOR = iNPTARGET+"/"+NORWORD
			UScanner(MTARGETNOR)

def UserScan(iNPTARGET,USERWord):
	print("\n\tRead > "+USERWord+"\n")
	cou = 0
	with open(USERWord, 'r') as USEFILE:
		for li in USEFILE:
			cou += 1
	USEFILEOP = open(USERWord,"r+")
	for eg in range(cou):
		USERWORD = USEFILE.readline().strip()
		MTARGETNOR = iNPTARGET+"/"+USEWORD
		UScanner(MTARGETNOR)


def Main():
	timelocal = time.localtime()
	retimeloc = time.strftime("%I:%M:%S %p", timelocal)
	bannar = """
	██╗  ██╗██████╗  ██████╗ 
	╚██╗██╔╝██╔══██╗██╔════╝ 
	 ╚███╔╝ ██║  ██║██║  ███╗
	 ██╔██╗ ██║  ██║██║   ██║
	██╔╝ ██╗██████╔╝╚██████╔╝
	╚═╝  ╚═╝╚═════╝  ╚═════╝ 
	               
                                
	██╗  ██╗ █████╗ ██████╗		
	╚██╗██╔╝██╔══██╗██╔══██╗ (AhmedAbdelaziz.Reda )
	 ╚███╔╝ ███████║██████╔╝ ( """+retimeloc+"""  )
	 ██╔██╗ ██╔══██║██╔══██╗ (All CopyRight Save  )
	██╔╝ ██╗██║  ██║██║  ██║ 	
	╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ (Discord :  https://discord.gg/kz4Y5fa9x9 )"""
	print(bannar)
	uINPTARGET = input("\n(https://www.exampla.com) Please Pute The Website :")
	uINP = input("\n Use OUR WordList [y/n] :")
	time.sleep(3)
	cls()

	if uINP == "y":
		uINPDORK = input("\n\tEgyptian Eagles\nWanna Use Google Dork Scan ON\n("+uINPTARGET+") [y/n] :")
		if uINPDORK == "Y":
			DORKUSERFILE = input("Please Put Dork List Not More Than 10 :")
			vulnScan(uINPTARGET)
			GOscan(uINPTARGET,DORKUSERFILE)
			NormalScan(uINPTARGET)
		
		elif uINPDORK == "y":
			DORKUSERFILE = input("Please Put Dork List Not More Than 10 :")
			vulnScan(uINPTARGET)
			GOscan(uINPTARGET,DORKUSERFILE)
			NormalScan(uINPTARGET)
		
		elif uINPDORK == "n":
			vulnScan(uINPTARGET)
			NormalScan(uINPTARGET)

		elif uINPDORK == "N":
			vulnScan(uINPTARGET)
			NormalScan(uINPTARGET)
	
	elif uINP == "Y":
		uINPDORK = input("\n\tEgyptian Eagles\nWanna Use Google Dork Scan ON\n("+uINPTARGET+") [y/n] :")
		if uINPDORK == "Y":
			DORKUSERFILE = input("Please Put Dork List Not More Than 10 :")
			vulnScan(uINPTARGET)
			GOscan(uINPTARGET,DORKUSERFILE)
			NormalScan(uINPTARGET)
		
		elif uINPDORK == "y":
			DORKUSERFILE = input("Please Put Dork List Not More Than 10 :")
			vulnScan(uINPTARGET)
			GOscan(uINPTARGET,DORKUSERFILE)
			NormalScan(uINPTARGET)
		
		elif uINPDORK == "n":
			vulnScan(uINPTARGET)
			NormalScan(uINPTARGET)
		
		elif uINPDORK == "N":
			vulnScan(uINPTARGET)
			NormalScan(uINPTARGET)

	elif uINP == "n":
		uINPWORDLIST = input("Please Pute Your WordList :")
		UserScan(uINPTARGET,uINPWORDLIST)
		uINPDORK = input("\n\tEgyptian Eagles\nWanna Use Google Dork Scan ON\n("+uINPTARGET+") [y/n] :")
		if uINPDORK == "Y":
			DORKUSERFILE = input("Please Put Dork List Not More Than 10 :")

			GOscan(uINPTARGET,DORKUSERFILE)

		elif uINPDORK == "y":
			DORKUSERFILE = input("Please Put Dork List Not More Than 10 :")

			GOscan(uINPTARGET,DORKUSERFILE)


		elif uINPDORK == "n":
			pass
		elif uINPDORK == "N":
			pass


	elif uINP == "N":
		uINPWORDLIST = input("Please Pute Your WordList :")
		UserScan(uINPTARGET,uINPWORDLIST)
		uINPDORK = input("\n\tEgyptian Eagles\nWanna Use Google Dork Scan ON\n("+uINPTARGET+") [y/n] :")
		if uINPDORK == "Y":
			DORKUSERFILE = input("Please Put Dork List Not More Than 10 :")

			GOscan(uINPTARGET,DORKUSERFILE)

		elif uINPDORK == "y":
			DORKUSERFILE = input("Please Put Dork List Not More Than 10 :")

			GOscan(uINPTARGET,DORKUSERFILE)

		elif uINPDORK == "n":
			pass
		elif uINPDORK == "N":
			pass

	else:
		exit()




if __name__ == '__main__':
	Main()
