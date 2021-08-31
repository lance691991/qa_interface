import time

a = "2019-5-10 23:40:00"

time_array = time.strptime(a, "%Y-%m-%d %H:%M:%S")

time_stamp = time.mktime(time_array)
print(time_stamp)