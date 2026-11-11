import csv,sys,os
files={'wk1':'/home/claude/bt/133104.csv','wk2':'/mnt/user-data/uploads/134251-280648284.csv',
'wk3':'/mnt/user-data/uploads/134503-280745135.csv','wk4':'/mnt/user-data/uploads/134747-280845253.csv',
'wk5':'/mnt/user-data/uploads/135023-280945043.csv'}
for wk,f in files.items():
    build=[];sealed=[]
    with open(f,encoding='utf-8-sig',newline='') as fh:
        r=csv.reader(fh); next(r)
        for row in r:
            if len(row)<11 or not row[6].strip(): 
                continue
            build.append((row[6],row[7],row[10]))
            sealed.append((row[6],row[7],row[8],row[9]))
    with open(f'/home/claude/bt/build/{wk}.csv','w',newline='') as o:
        w=csv.writer(o);w.writerow(['name','pos','salary']);w.writerows(build)
    with open(f'/home/claude/bt/sealed/{wk}.csv','w',newline='') as o:
        w=csv.writer(o);w.writerow(['name','pos','own','fpts']);w.writerows(sealed)
    print(wk,len(build),'players; positions:',sorted(set(b[1] for b in build)))
