import re



# pattern = "(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|(?:2131|1800|35\d{3})\d{11})"
pattern = "([0-9]{16})"
card = re.findall(pattern, "<html>\n<body>\n<h1>4272301000618202</h1><h1>4276123456789100</h1><h1>5469345678901234</h1><h1>4276800052412887</h1></body>\n</html>")

print (card)

import datetime

c_d = datetime.date.today()

print (c_d)


def prime(lst):
    for i in lst:
        if i % 2 == 0:
            yield i


f = prime([1, 2, 3, 4, 5, 6, 7, 8, 9])

for i in f:
    print(i)
