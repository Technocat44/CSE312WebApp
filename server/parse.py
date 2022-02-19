# This is going to be my parsing file
# There is some important module os functions in here

###h
"""    
This function takes in a HTTP request decoded string and returns a dictionary with key-value pairs. 
The keys are the HTTP headers 
The values are the values of the headers.
    Example:
        key - Content-Length
        value - 5
"""
def buildHeaderDict(decodedSplitHeaders):
    # example input == "HTTP/1.1 200 OK\r\nContent-Length: 5\r\nContent-Type: text/plain; charset;utf-8\r\nx-Content-Something-Type: nosniffing\r\n\r\nWhat's up world!!"
    print('\n\n')

    # the input is a list that was split on \r\n. Essentially each element in the list 
    # will be a line. The first element will be the request line, and the last element will be the body 

    # I create a new list that contains all elements in the list except the request line var[0], the second last 
    # element (the CLRF ''), var[-2], and the last element (the body) var[-1]. The only things left in this list are the headers 
    #e = decodedSplitHeaders[1:-2]
    e = decodedSplitHeaders[1:]
    # print("e ",e)

    newHeaderDict = {}
    # for line in e:
    #     t = line.split(":")
    #     newHeaderDict[t[0]] = t[1].strip(' ')
    # return newHeaderDict

    # I loop over the headers such as:
    #           'Content-Length: 5'
    # and I split each line on the colon. I create the first part of that line to be the key, and I 
    # assign the second part of the line as the value and I strip the line of any leading whitespace
    for s in e:
        if s == '':
            break
        else:
            t = s.split(':')
            newHeaderDict[t[0]] = t[1].strip(' ')
    return newHeaderDict



