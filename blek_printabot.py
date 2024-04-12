import requests
import re
import json
from fpdf import FPDF
from PIL import Image

RES_PRE = "Ressources/"
AUTH_URL = "https://auth.blek.ch/"
USER_FILE = RES_PRE+"user.txt"
TEST_FILE = RES_PRE+"prout.pdf"

auth_headers = {'Host': 'auth.blek.ch',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
           'Accept-Language': 'en-US,en;q=0.5',
           'Accept-Encoding': 'gzip, deflate, br',
           'Content-Type': 'application/x-www-form-urlencoded',
           'Origin': 'https://auth.blek.ch',
           'Connection': 'keep-alive',
           'Referer': 'https://auth.blek.ch/?cancel=1',
           'Cookie': 'lemonldap=0; llngconnection=0',
           'Upgrade-Insecure-Requests': '1',
           'Sec-Fetch-Dest': 'document',
           'Sec-Fetch-Mode': 'navigate',
           'Sec-Fetch-Site': 'same-origin',
           'Sec-Fetch-User': '?1'}

def print_ordered_headers(headers):
    mkeys = list(headers.keys())
    mkeys.sort()
    sorted = {i: headers[i] for i in mkeys}
    print(sorted)

def find_token(lines):
    for line in lines:
        if "token" in line:
            print(line)
            break
    line = line[re.search("value", line).end():]
    apo = []
    [apo.append(m) for m in re.finditer('"', line)]
    token = line[apo[0].end():apo[1].start()]
    print(token)
    return token

def open_session(user_auth_data):
    session = requests.Session()
    response = session.get(AUTH_URL)

    token = find_token(response.text.splitlines())
    auth_data = "url&timezone=2&lmAuth=1_Balelec&skin=blek&token={}&user={}&password={}".format(token, user_auth_data['user'], user_auth_data['pw'])

    response = session.post(AUTH_URL, headers=auth_headers, data=auth_data)
    error = False
    error_str = None
    error_count = 0
    for line in response.text.splitlines():
        if (error):
            error_str = error_str+"\n"+line
            error_count = error_count+1
        if "errormsg" in line:
            error_str = line
            error = True
            error_count = error_count+1
        if(error_count == 7):
            break
    return session, error_str

def print_file(session, user_auth_data, filename):
    print_headers = {
        'Accept': 'application/json'
    }

    files = {
        'file': open(filename, 'rb')
    }

    response = session.post(
        url='https://print.blek.ch/restful/v1/documents/print',
        headers=print_headers,
        files = files,
        # verify = False,
        auth=(user_auth_data['user'], user_auth_data['UUID'])
    )
    print(response)

def generate_pdf(file):
    img = Image.open(file)
    
    if(img.width>img.height):
        pdf_orient = "L"
    else:
        pdf_orient = "P"
    pdf = FPDF(orientation=pdf_orient, unit="mm", format="A4")
    pdf.add_page()
    # FPDF.eph
    size = min(pdf.eph, pdf.epw)
    # img.thumbnail((size, size), Image.Resampling.LANCZOS)
    print(pdf.eph, pdf.epw, img.height, img.width)
    if(pdf_orient == "L"):
        pdf.image(img, h=size)
    else:
        pdf.image(img, w=size)
    pdf.output("Ressources/test.pdf")

def main():
    with open(USER_FILE) as f:
        user_auth_data = json.load(f)
    session, error = open_session(user_auth_data)
    filename = TEST_FILE

    generate_pdf(FILE_PRE+"alpine.jpg")
    if(not error):
        response = session.get("https://print.blek.ch/restful/v1/tests/http/request")
        print(response.text)
        # # print_file(session, user_auth_data, filename)
    else:
        print("Found error in request blablabla :\n", error)

if __name__ == '__main__':
    main()
