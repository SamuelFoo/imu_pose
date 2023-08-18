import bluetooth
import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt

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
    if not data.any():
        return np.array([]), np.array([]), np.array([]), np.array([])
    time, quatI, quatJ, quatK, quatReal, _ = data.T
    time /= 1e3
    roll, pitch, yaw = euler_from_quaternion(x=quatI, y=quatJ, z=quatK, w=quatReal)

    return time, roll, pitch, yaw

class AnimationWorker():
    def __init__(self, addressLower, addressUpper, timeInterval=500):
        self.sockLower = initBluetoothSocket(address=addressLower)
        self.sockUpper = initBluetoothSocket(address=addressUpper)
        self.dataLower = np.array([[],[],[],[]])
        self.dataUpper = np.array([[],[],[],[]])
        self.timeInterval = timeInterval

    def createSubPlot(self, fig, ax, yLabel, idx, color):
        plt.ylabel(yLabel)
        ax.relim()
        ax.autoscale_view()
        lowerLine, = plt.plot([], [], f"{color}-")
        upperLine, = plt.plot([], [], f"{color}--")
        lines = (lowerLine, upperLine)
        ani = animation.FuncAnimation(fig, self.animateMain, fargs=(ax, lines, idx), interval=self.timeInterval)
        return ani

    def run(self):        
        # check number of charts to decide subplot orientation
        sp1 = 313
        sp2 = 312
        sp3 = 311

        fig = plt.figure(figsize=(12,7))

        # initialize subplots
        ax1 = fig.add_subplot(sp1)
        ani1 = self.createSubPlot(fig, ax1, "Roll", 1, "r")

        ax2 = fig.add_subplot(sp2)
        ani2 = self.createSubPlot(fig, ax2, "Pitch", 2, "b")

        ax3 = fig.add_subplot(sp3)
        ani3 = self.createSubPlot(fig, ax3, "Yaw", 3, "k")

        print("Commence data acquisition.")
        plt.tight_layout()
        plt.show()

    # animation to update graph for each data point collected
    def animateMain(self, i, ax, lines, idx):
        def inner(data, sock):
            time, roll, pitch, yaw = getSocketData(sock)
            data = np.concatenate((data, np.vstack((time, roll, pitch, yaw))), axis=1)
            return data

        self.dataLower = inner(self.dataLower, self.sockLower)
        self.dataUpper = inner(self.dataUpper, self.sockUpper)

        line, = self.animateSide(i, ax, lines, idx)

        return line,

    # sub-animation for each subsequent data point collected
    def animateSide(self, i, ax, lines, idx):
        lines[0].set_data([self.dataLower[0]-self.dataLower[0][0], self.dataLower[idx]])
        lines[1].set_data([self.dataUpper[0]-self.dataUpper[0][0], self.dataUpper[idx]])
        ax.relim()
        ax.autoscale_view()

        return lines,

