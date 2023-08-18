import bluetooth
import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from multiprocessing import Process

def initBluetoothSocket(address):
    d = bluetooth.find_service(address=address)[0]
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((d["host"], d["port"]))
    return sock

def euler_from_quaternion(x, y, z, w):
    """
    Convert a quaternion into euler angles (roll, pitch, yaw)
    roll is rotation around x in radians (counterclockwise)
    pitch is rotation around y in radians (counterclockwise)
    yaw is rotation around z in radians (counterclockwise)
    """
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = np.arctan2(t0, t1)
    
    t2 = +2.0 * (w * y - z * x)
    t2 = np.clip(t2, -1.0, +1.0)
    pitch_y = np.arcsin(t2)
    
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = np.arctan2(t3, t4)
    
    return roll_x, pitch_y, yaw_z # in radians

def getSocketData(sock):
    dataStr = str(sock.recv(numbytes=2048).decode("utf-8"))
    print(dataStr)
    data = dataStr.splitlines()
    data = filter(lambda row: row[0] == "@" and row[-1] == "@" and len(row) > 1, data)
    data = map(lambda x: list(x.strip("@").split(",")), data)
    data = np.array(list(data), dtype=np.float64)
    time, quatI, quatJ, quatK, quatReal, _ = data.T
    time /= 1e3
    roll, pitch, yaw = euler_from_quaternion(x=quatI, y=quatJ, z=quatK, w=quatReal)

    return time, roll, pitch, yaw

class AnimationWorker():
    def __init__(self, address):
        self.sock = initBluetoothSocket(address=address)
        self.data = np.array([[],[],[],[]])

    def run(self):
        time_interval = 500
        
        # check number of charts to decide subplot orientation
        sp1 = 313
        sp2 = 312
        sp3 = 311

        fig = plt.figure(figsize=(12,7))

        # initialize subplot 1
        ax1 = fig.add_subplot(sp1)
        plt.ylabel("Roll")
        ax1.relim()
        ax1.autoscale_view()
        y1line, = plt.plot([], [], "r-")
        ani1 = animation.FuncAnimation(fig, self.animateMain, fargs=(ax1, y1line, 1), interval=time_interval)

        # initialize subplot 2
        ax2 = fig.add_subplot(sp2)
        plt.ylabel("Pitch")
        ax2.relim()
        ax2.autoscale_view()
        y2line, = plt.plot([], [], "b-")
        ani2 = animation.FuncAnimation(fig, self.animateSide, fargs=(ax2, y2line, 2), interval=time_interval)

        # initialize subplot 3
        ax3 = fig.add_subplot(sp3)
        plt.ylabel("Yaw")
        ax3.relim()
        ax3.autoscale_view()
        y3line, = plt.plot([], [], "k-")
        ani3 = animation.FuncAnimation(fig, self.animateSide, fargs=(ax3, y3line, 3), interval=time_interval)

        print("Commence data acquisition.")
        plt.tight_layout()
        plt.show()

    # animation to update graph for each data point collected
    def animateMain(self, i, ax, line, idx):
        time, roll, pitch, yaw = getSocketData(self.sock)
        self.data = np.concatenate((self.data, np.vstack((time, roll, pitch, yaw))), axis=1)

        line, = self.animateSide(i, ax, line, idx)

        return line,

    # sub-animation for each subsequent data point collected
    def animateSide(self, i, ax, line, idx):
        line.set_data([self.data[0], self.data[idx]])
        ax.relim()
        ax.autoscale_view()

        return line,

