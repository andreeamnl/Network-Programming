from ftplib import FTP
ftp = FTP('138.68.98.108')
ftp.login(user='yourusername', passwd='yourusername')
ftp.cwd('faf-212/Andreea')
file_list = ftp.nlst()
print("List of files:", file_list)