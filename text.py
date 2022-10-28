import math

queries_quota : int
queries_per_second = 60 # None or 60
queries_per_minute = None # None or 6000

try: 
    if (type(queries_per_second) == int and type(queries_per_minute) == int ):
        queries_quota =  math.floor(min(queries_per_second, queries_per_minute/60))
    elif (queries_per_second):
        queries_quota = math.floor(queries_per_second)
    elif (queries_per_minute):
        queries_quota = math.floor(queries_per_minute/60)
    else:
        print("MISSING VALID NUMBER for queries_per_second or queries_per_minute")     
    print(queries_quota)

except NameError:
    print("MISSING VALUE for queries_per_second or queries_per_minute")