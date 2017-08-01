# import re
# import base64
    
# a = "{}".format(base64.encodestring("O:9:AKFactory:1:{s:18:' + \x00 + 'AKFactory' + \x00 + 'varlist;a:2:{s:27:kickstart.security.password;s:0:;s:26:kickstart.setup.sourcefile;s:' + srv_uri.length.to_s + ':' + srv_uri + ';".encode()).decode())

# print(a)

# b  = base64.decodestring(a.encode())

# print (b)


# # pattern = "(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|(?:2131|1800|35\d{3})\d{11})"
# pattern = "([0-9]{16})"
# card = re.findall(pattern, "<html>\n<body>\n<h1>4272301000618202</h1><h1>4276123456789100</h1><h1>5469345678901234</h1><h1>4276800052412887</h1></body>\n</html>")

# print (card)

# import datetime

# c_d = datetime.date.today()

# print (c_d)


# def prime(lst):
#     for i in lst:
#         if i % 2 == 0:
#             yield i


# f = prime([1, 2, 3, 4, 5, 6, 7, 8, 9])

# for i in f:
#     print(i)



n = 4

def mini(n):
    # Проверяем если n = 1 то возвращаем 1
    mmin = 1
    if n == 1 :
        mmin = 1
    # если число четное то у него наименьший делить всегда 2
    elif n % 2 == 0:
        mmin = 2
    # если число не четное, то на 2 оно точно не делится, проверяем только не четные делители
    else:
        for i in range (3, n, 2):
            # если найден наименьший не четный делитель, то  сохраняем его и прекращаем поиск
            if n % i == 0 :
                mmin = i
                break
        # если найден не был, то возвращаем само n
        else:
            mmin = n

    return mmin

def MinDivisor(n):
    i = 2
    while i <= n:
        if n % i == 0:
            return i
        else:
            i += 1

print (mini(n))
print (MinDivisor(n))
