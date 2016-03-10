domain = "asdfasdfasdf.com"
int_code=""
for c in domain:
    int_code += "%"+"%d" % ord(c)
domain = int_code
print (domain
       )