import matplotlib.pyplot as plt
import csv

x=[]
y=[]
z=[]
time=[]

with open('data.csv', 'r') as csvfile:
    plots= csv.reader(csvfile, delimiter=',')
    for row in plots:
        x.append(row[0])
        y.append(row[1])
        z.append(row[2])
        time.append(str(row[3])[11:21])

plt.plot(time,x,time,y,time,z, marker='o')
plt.title('Data from the RC-Car')
plt.xlabel('Time')
plt.ylabel('Data')
plt.show()

