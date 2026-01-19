def test():
    return 1,2,3,4,5,6
a,b,*args=test()
print(a,b)
print(*args)