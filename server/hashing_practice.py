import hashlib
import base64


# example key                       Sec-WebSocket-Key: 25dJisszYN+6UXLJCSqTEw==
# example of proper response key:   sec-websocket-accept: vdlhb7ci/qt6pmGqd9J31pZtxss=
                                       # result         # vdlhb7ci/qt6pmGqd9J31pZtxss=

                                    # request key    # OTmcC838C0ySmM4JMMgp5g==
                                    # accept key     # Vjdsbll+jbpMnZRDClZZWc25TbE=
                                     # result        # Vjdsbll+jbpMnZRDClZZWc25TbE=
def generate_hash():
    fake_key = "OTmcC838C0ySmM4JMMgp5g==" 
    guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11" 
    fake_websocket_key = fake_key + guid 
    hash_object = hashlib.sha1(fake_websocket_key.encode()).hexdigest()
    hashy = base64.b64encode(bytes.fromhex(hash_object)).decode()
    return hashy




if __name__ == '__main__':
    h = generate_hash()
    print(h)
    pass