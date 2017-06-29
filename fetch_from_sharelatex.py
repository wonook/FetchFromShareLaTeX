try:
    from bs4 import BeautifulSoup
    import requests
except ImportError:
    exit('Please run $ pip3 install requests bs4')

from zipfile import ZipFile, BadZipFile
import os
import re
import sys
import getpass

# Download sharelatex project and extract and delete the zip file.
def main(argv):
    if len(sys.argv) is not 4 and len(sys.argv) is not 3:
        print("please fix fetch_from_sharelatex.default")
        return

    file_name = 'sharelatex.zip'

    url = sys.argv[1]
    base_url = extract_base_url(url)
    login_url = "{}/login".format(base_url)
    download_url = "{}/download/zip".format(url)

    print("Downloading files: {}...".format(download_url))

    email = sys.argv[2]
    if len(sys.argv) is 4:
        password = sys.argv[3]
    else:
        password = None

    try:
        session = requests.Session()
        
        if email is not None:
            if password is None:
                password = getpass.getpass("Enter password: ")
            print("Logging in {} for {}...".format(login_url, email))
            r = session.get(login_url)
            csrf = BeautifulSoup(r.text, 'html.parser').find('input', { 'name' : '_csrf' })['value']
            session.post(login_url, { '_csrf' : csrf , 'email' : email , 'password' : password })

        r = session.get(download_url, stream=True)
        with open(file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk:
                    f.write(chunk)
    except:
        print('Check your ID or your network connection.')
        return # Never reached. Here to calm down static analysis

    print("Unzipping files...")

    try:
        with ZipFile(file_name, 'r') as f:
            f.extractall()
    except BadZipFile:
        os.remove(file_name)
        print("Please check fetch_from_sharelatex for project url, email, and password")

    os.remove(file_name)

    try:
        r = session.get(url)
        return BeautifulSoup(r.text, 'html.parser').find('title').text.rsplit('-',1)[0].strip()
    except:
        return None

#------------------------------------------------------------------------------
# Extract the base URL from the project's full URL
#------------------------------------------------------------------------------
def extract_base_url(url):
    try:
        p = re.compile("(http.*)/project/[a-zA-Z0-9]*", re.IGNORECASE)
        return p.search(url).group(1)
    except:
        print('Unexpected url format ({}), unable to extract base url'.format(url))

if __name__ == "__main__":
    main(sys.argv[1:])
