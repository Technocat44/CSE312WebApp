byteDict = {}
def all_bytes_of_file(read_bytes: bytes):
    byteDict["bytes"] = read_bytes
    
def sendBytes():
    return byteDict


def fileUploadParser(byteArray):
    fakeContentType = b'multipart/form-data; boundary=----WebKitFormBoundaryeNi5mScyPz2Yd19u'
    findBoundary = fakeContentType.find(b"----")
    boundary = b'--' + fakeContentType[findBoundary:]
    print(boundary)








if __name__ == '__main__':
   # sample_GET_request = b'GET /hkgkg HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nPragma: no-cache\r\nCache-Control: no-cache\r\nsec-ch-ua: " Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"\r\nsec-ch-ua-mobile: ?0\r\nsec-ch-ua-platform: "Windows"\r\nDNT: 1\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nSec-Fetch-Site: none\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9\r\n\r\n'
   # request = Request(sample_GET_request)
    # sample_htmlform_request = b'POST /image-upload HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nContent-Length: 287\r\nPragma: no-cache\r\nCache-Control: no-cache\r\nsec-ch-ua: " Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"\r\nsec-ch-ua-mobile: ?0\r\nsec-ch-ua-platform: "Windows"\r\nOrigin: http://localhost:8080\r\nUpgrade-Insecure-Requests: 1\r\nDNT: 1\r\n'
    # sample_htmlform_request += b'Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryam94SD6c9rqAs6td\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9'
    # sample_htmlform_request += b'\r\n\r\n------WebKitFormBoundaryam94SD6c9rqAs6td\r\nContent-Disposition: form-data; name="comment"\r\n\r\nhey\r\n------WebKitFormBoundaryam'
    # request = Request(sample_htmlform_request)
    largeIncompleteFile = b'------WebKitFormBoundaryeNi5mScyPz2Yd19u\r\nContent-Disposition: form-data; name="comment"\r\n\r\nThis is a new upload image. Its a pic of UB.\r\n------WebKitFormBoundaryeNi5mScyPz2Yd19u\r\nContent-Disposition: form-data; name="upload"; filename="UB.jpg"\r\nContent-Type: image/jpeg\r\n\r\n\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00\x84\x00\t\x06\x07\x13\x12\x12\x15\x11\x12\x13\x16\x16\x12\x15\x19\x1d\x1b\x19\x18\x18\x18\x1e\x1f\x18\x1c\x18#\x19!\x1b\x1a\x1a \x18\x1a\x1d( \x1a\x1f%\x1b\x1e"!2!%)+... \x1f383.7(-.+\x01\n\n\n\x0e\r\x0e\x1b\x10\x10\x1a-& %--/-.22--++/2+----/-------------------------------\xff\xc0\x00\x11\x08\x00\xb8\x01\x13\x03\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1c\x00\x01\x00\x03\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x06\x07\x04\x03\x02\x01\x08\xff\xc4\x00N\x10\x00\x02\x01\x03\x02\x03\x05\x03\x05\x0c\x06\x08\x06\x03\x00\x00\x01\x02\x03\x00\x04\x11\x12!\x05\x061\x07\x13AQa"q\x81\x142\x91\x92\xa1\x16\x17#BRSTbr\x82\xb1\xd334\x93\xb2\xc1\xd2\x15s\x94\xa2\xc2\xd4\xe1\xf0$5\x83\xd1\xe3\xf1\x08%U\xff\xc4\x00\x1a\x01\x01\x00\x03\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x04\x05\x02\x01\x06\xff\xc4\x005\x11\x00\x02\x02\x02\x00\x04\x02\t\x04\x02\x02\x02\x03\x00\x00\''
    request = fileUploadParser(largeIncompleteFile)
    pass 