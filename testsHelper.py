import bluetooth
import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches

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

        self.state = 0
        self.reps = 0
        self.numStates = 3
        self.numReps = 10
        self.count = 0

        #####################################
        #       Checkpoint definitions      #
        #####################################
        # Format
        '''
        [
            (#lower1, #upper1), (#lower2, #upper2), ...
        ]
        '''
        rollTargets = [
            (0, 0), (0, 0), (0, 0)
        ]
        rollOffsets = [15, 15, 15]

        yawTargets = [
            (0, 0), (-150, -40), (-150, -80)
        ]
        yawOffsets = [20, 20, 20]
        self.durations = [1, 1, 8]

        helper = lambda target, offset: [
            [
                target[0] - offset,
                target[0] + offset,
                target[1] - offset,
                target[1] + offset
            ] for target, offset in zip(target, offset)
        ]
        self.rollLimits = helper(rollTargets, rollOffsets)
        self.yawLimits = helper(yawTargets, yawOffsets)

    def createSubPlotLine(self, fig, ax, yLabel, idx, color, limits=None):
        ax.set_ylabel(yLabel)
        ax.relim()
        ax.autoscale_view()
        ax.set_ylim(-180, 180)
        lowerLine, = ax.plot([], [], f"{color}-", label="lower arm")
        upperLine, = ax.plot([], [], f"{color}--", label="upper arm")

        if limits:
            limit = limits[self.state]
            lowerRect = patches.Rectangle(xy=(0, limit[0]), width=0, height=limit[1]-limit[0], 
                                          color=color)
            lowerRect.set_alpha(0.5)
            upperRect = patches.Rectangle(xy=(0, limit[2]), width=0, height=limit[3]-limit[2], 
                                          color=color, fill=False, hatch="/")
            ax.add_patch(lowerRect)
            ax.add_patch(upperRect)
        else:
            lowerRect = patches.Rectangle(xy=(0,0), width=0, height=0)
            upperRect = patches.Rectangle(xy=(0,0), width=0, height=0)

        ax.legend()
        lines = (lowerLine, upperLine)
        rects = (lowerRect, upperRect)
        ani = animation.FuncAnimation(fig, self.animateSide, fargs=(ax, lines, rects, limits, idx), 
                                      interval=self.timeInterval)
        return ani

    def createSubPlotBar(self, fig, ax):
        bars = ax.bar(["Progress", "Checkpoint", "Reps Done"], [0,0,0], color=["C0", "C1", "C2"])
        ax.set_ylim(0, self.numStates*self.numReps)
        ani = animation.FuncAnimation(fig, self.animateMain, fargs=(ax, bars), interval=self.timeInterval)
        return ani

    def run(self):
        # check number of charts to decide subplot orientation
        sp1 = 313
        sp2 = 312
        sp3 = 311

        fig = plt.figure(figsize=(15,7))
        gs = gridspec.GridSpec(3, 4)

        # initialize subplots
        ax1 = fig.add_subplot(gs[0,:3])
        ax2 = fig.add_subplot(gs[1,:3])
        ax3 = fig.add_subplot(gs[2,:3])
        ax4 = fig.add_subplot(gs[:,3])

        ani4 = self.createSubPlotBar(fig, ax4)
        ani1 = self.createSubPlotLine(fig, ax1, "Roll", 1, "r", limits=self.rollLimits)
        ani2 = self.createSubPlotLine(fig, ax2, "Pitch", 2, "b")
        ani3 = self.createSubPlotLine(fig, ax3, "Yaw", 3, "k", limits=self.yawLimits)

        print("Commence data acquisition.")
        plt.tight_layout()
        plt.show()

    # animation to update graph for each data point collected
    def animateMain(self, i, ax, bars):
        def inner(data, sock):
            time, roll, pitch, yaw = getSocketData(sock)
            data = np.concatenate((data, np.vstack((time, roll, pitch, yaw))), axis=1)
            return data

        # Poll data
        self.dataLower = inner(self.dataLower, self.sockLower)
        self.dataUpper = inner(self.dataUpper, self.sockUpper)

        # Check limits
        yawLimit = self.yawLimits[self.state]
        yawCheck = yawLimit[0] < np.rad2deg(self.dataLower[3][-1]) < yawLimit[1] \
            and yawLimit[2] < np.rad2deg(self.dataUpper[3][-1]) < yawLimit[3]
        rollLimit = self.rollLimits[self.state]
        rollCheck = rollLimit[0] < np.rad2deg(self.dataLower[1][-1]) < rollLimit[1] \
            and rollLimit[2] < np.rad2deg(self.dataUpper[1][-1]) < rollLimit[3]
        if yawCheck and rollCheck:
            self.count += 1

        if self.count >= self.durations[self.state]:
            self.count = 0
            state = self.state + 1
            repComplete = state == self.numStates
            self.state = state % self.numStates
            
            if repComplete:
                self.reps += 1

        # Update bars
        bars[0].set_height(self.count/self.durations[self.state]*self.numReps*self.numStates)
        bars[1].set_height((self.state)*self.numReps)
        bars[2].set_height((self.reps)*self.numStates)

        print(self.state)

        return

    # sub-animation for each subsequent data point collected
    def animateSide(self, i, ax, lines, rects, limits, idx):
        lines[0].set_data([self.dataLower[0]-self.dataLower[0][0], np.rad2deg(self.dataLower[idx])])
        lines[1].set_data([self.dataUpper[0]-self.dataUpper[0][0], np.rad2deg(self.dataUpper[idx])])
        
        if limits:
            width = max(self.dataLower[0][-1]-self.dataLower[0][0], self.dataUpper[0][-1]-self.dataUpper[0][0])
            rects[0].set_width(width)
            rects[1].set_width(width)

            limit = limits[self.state]
            rects[0].set_xy((0,limit[0]))
            rects[0].set_height(limit[1]-limit[0])
            rects[1].set_xy((0,limit[2]))
            rects[1].set_height(limit[3]-limit[2])

        ax.relim()
        ax.autoscale_view()

        return lines,

