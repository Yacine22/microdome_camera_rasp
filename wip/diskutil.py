import os
import shutil

result=os.statvfs('/')
blocksize= result.f_frsize
freeblock= result.f_bfree
giga=1024*1024*1024
free_size = freeblock*blocksize/giga
print(free_size)


total,used,free=shutil.disk_usage('/')
print("Free: %d Gb" % (free // (2**30)))