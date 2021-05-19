
# Mars Lander Episode-2

import numpy as np
import math, random


# Utilities

def v(x,y):
    # vectorize to numpy array which is also a vector 
    return np.array([x,y])

def uv(v):
    # Normalize the given vector to an unit vector
    # https://stackoverflow.com/questions/21030391/how-to-normalize-an-array-in-numpy
    norm = np.linalg.norm(v)
    return v if norm==0 else v/norm;

def norm(v):
    # length of a vector, where v (vector) is a np.array
    return np.linalg.norm(v)

def angle2uv(an):
    # Convert the given absolute angle in degrees to a unit vector that represents the angle
    an1 = np.deg2rad(an + 90)  # ? 90 ? Mars Lander ???????????????
                               # ?? g ? Mars Lander ???????? -180 
    return uv(v(math.cos(an1), math.sin(an1))) 

def angle15(a0,rotate):
    # rotate command ??? absolute target angle ????? +-15??
    if rotate > a0:
        result = a0 + min(rotate-a0,15)
    else :
        result = a0 - min(a0-rotate,15)
    return int(np.round(max(min(90,result),-90),0))

def thrust_1(power,thrust):
    # thrust_1 command ?? power ????? +1 or -1 
    result = power
    if thrust > power:
        result += 1
    if thrust < power:
        result -= 1
    return int(np.round(max(min(4,result),0),0))

# Calculate the euclidian distance between an array of points to a line segment in Python without for loop
# https://stackoverflow.com/questions/54442057/calculate-the-euclidian-distance-between-an-array-of-points-to-a-line-segment-in

def lineseg_dists(p, a, b):
    # where p is an array of points, a,b is the line segment
    if np.all(a == b):
        return np.linalg.norm(p - a, axis=1)

    # normalized tangent vector
    d = np.divide(b - a, np.linalg.norm(b - a))

    # signed parallel distance components
    s = np.dot(a - p, d)
    t = np.dot(p - b, d)

    # clamped parallel distance
    h = np.maximum.reduce([s, t, np.zeros(len(p))])

    # perpendicular distance component, as before
    # note that for the 3D case these will be vectors
    c = np.cross(p - a, d)

    # use hypot for Pythagoras to improve accuracy
    return np.hypot(h, c)


# Constants 

land = [v(0,100), v(1000,500), v(1500,1500), v(3000,1000), 
        v(4000+500,150), v(5500-500,150),  # flate ground 要內縮一點，避免 ship 來到與相鄰 surface 的平分線上撞毀被誤判成降落到位。
        v(6999,800)]

flate = [i for i in range(len(land)-1) if land[i][1] == land[i+1][1]][0]  # flate ground left point index of land array 
fuel0 = 5501  # full tank 
p0 = v(2500, 2700)  # Initial position
a0 = 0        # absolute angle of the ship 
pwr0 = 0      # 引擎出力
s0 = v(0,0)   # Initial speed vector
B0 = np.linalg.norm(v(7000,3000))  # bonus base 
gravity = 3.711  # constant on Mars
g = angle2uv(-180) * gravity  # 重力向量

    
# Genetic Algorithm

def crossover(spouse):
    # spouse 有兩條 chromosome, 遍歷其中短的一條，輪流撿 gene 來組成子代，不夠的用長的續接。
    # 傳回值是子代的 chromosome
    if len(spouse[0][1]) >= len(spouse[1][1]): longer, shorter = spouse[0][1], spouse[1][1]
    else: longer, shorter = spouse[1][1], spouse[0][1]
    shorter_len = len(shorter)
    cross = []
    for i in range(shorter_len): 
        cross.append(spouse[i%2][1][i])
    return cross + longer[i+1:]

# 光用 crossover 才兩代就到了「高原」不會再進步了，這麼快！所以要加上 mutation 才行。參考 Study "Genetic Algorithm Implementation in Python" with helps of peforth 學到了這個方法
# np.random.uniform(-15, 15, 1)  
# np.random.uniform(-1, 1, 1)  
# 本來的加上這個亂數就是 mutation 了！我想只給子代的加上 mutation 以防破壞到好的父代。

# 基因突變 
def mutation(gene):
    # mutation happens on a gene
    delta_rotate = np.random.uniform(-15, 15, 1)  
    delta_power  = np.random.uniform(-1, 1, 1)  
    return (gene[0] + delta_rotate, gene[1] + delta_power)


# The Mars shuttle lander
# 做出一個 class 叫作 Ship, 有油料、位置、速度、角度、引擎出力、軌跡、
# 從開始到落地的一長串 chromosome 也就是一長串的基因 genes (rotate,power)、
# 還有 score。

class Ship:
    def __init__(self, p0, s0, a0, pwr0, fuel0):
        self.inTheAir = True
        self.fuel0 = self.fuel = fuel0
        self.p0 = p0
        self.s0 = s0
        self.a0 = a0
        self.pwr0 = pwr0
        self.trace = []
        self.chromosome = []
        self.score = 0
        
    def make_score(self):
        distances = [lineseg_dists([self.p0], land[i], land[i+1])[0] for i in range(len(land)-1)]  # 與所有 surface 的距離
        shortest = np.argmin(distances)  # 最小的 index 
        self.inTheAir = (0 <= np.cross(land[shortest+1]-land[shortest],np.round(self.p0,0)-land[shortest+1]))
                        # 這裡要 大於/等於 0 而不是只 大於 0 ，這純粹是看 CodinGame 怎麼寫法。
        self.score = B0 - distances[flate]  # distance to target 
        # assert self.p0[1] > 200, "close to the problem point"
        if not self.inTheAir:
            if shortest != flate : self.score = -1  # 撞毀了
            else:
                # bonus1 已經降落目的地，通通有獎
                self.score += B0 + 40000  # 速度各減 20000 假設最高速 200 的平方  
                # bonus2 angle the smaller the better 
                self.score -= (B0/90)*abs(self.a0)
                # bonus3 horizantal speed < 20, virtical speed < 40
                self.score += B0 if abs(self.s0[0]) < 20 else -abs(self.s0[0])**2
                self.score += B0 if abs(self.s0[1]) < 40 else -abs(self.s0[1])**2
                assert self.score > 0 , "Assertion error! too much speed penalty !"
                # bonus4 remaining fuel the more the better
                self.score += self.fuel # 不到時候去太強調省油
        
    def move(self, rotate, thrust):
        a1 = angle15(self.a0,rotate)  # 這一步的角度 
        pwr1 = thrust_1(self.pwr0,thrust)  # 這一步的 引擎推力
        force = g + angle2uv(a1) * pwr1   # force on the ship during this step 
        s1 = self.s0 + force  # 這一步將達到的速度
        p1 = self.p0 + self.s0 + (1/2)*(force)  # where "s0 + (1/2)*(force)" is position delta 這一步將到達的位置
        self.fuel -= pwr1
        self.a0 = a1
        self.pwr0 = pwr1
        self.s0 = s1
        self.p0 = p1
        self.chromosome.append([a1,pwr1])  # 這一步的 command 就是這一步的 gene 
        self.trace.append(p1)  # 這一步走完到達的新位置
        assert pwr1 <=4 and pwr1 >=0 , "Assertion error! 引擎推力超過範圍了！(0~4 之間)"
        assert a1 <=90 and a1 >=-90 , "Assertion error! 小艇角度超過範圍了！(-90~90度之間)"
    
    def obsoleted_random_step(self):
        # return the score after this step
        a1 = angle15(self.a0, self.a0 + random.randint(-15, 15))  # 這一步的角度 0~15 之間亂轉
        pwr1 = thrust_1(self.pwr0, self.pwr0 + random.randint(-1,1))  # 這一步的 引擎推力 -1 0 1 亂選
        self.move(a1, pwr1)
        # 結果 self.score = -1 表示已經飛出範圍。
        if (self.p0[1] < 0) or (self.p0[0] < 0) or (self.p0[0] > 7000) :  # higher than 3000 is allowed
            self.score = -1
        else:
            self.make_score()
    
    def explore(self):
        # 用亂數摸索出到達 flate ground 的一條 chromosome
        while(True):
            a1 = angle15(self.a0, self.a0 + random.randint(-15, 15))  # 這一步的角度 0~15 之間亂轉
            pwr1 = thrust_1(self.pwr0, self.pwr0 + random.randint(-1,1))  # 這一步的 引擎推力 -1 0 1 亂選
            self.move(a1, pwr1)
            if (self.p0[1] < 0) or (self.p0[0] < 0) or (self.p0[0] > 7000) :  # higher than 3000 is allowed
                # 結果 self.score = -1 表示已經飛出範圍。
                self.score = -1
            else:
                self.make_score()
            if self.score < 0 or not self.inTheAir: 
                # 用亂數摸索出到達 flate ground 的一條 chromosome 為止。
                break

    def evaluate(self, chromosome):
        # 給這條 chromosome 打分數
        # 若怕用完了還在空中，可重複最後一個命令很多次，或用亂數先加很長很長再送進來試驗。
        # 傳回值是這條 chromosome 的有效長度
        
        for i in range(len(chromosome)):
            self.move(chromosome[i][0], chromosome[i][1])
            if (self.p0[1] < 0) or (self.p0[0] < 0) or (self.p0[0] > 7000) :  # higher than 3000 is allowed
                # 結果 self.score = -1 表示已經飛出範圍。
                self.score = -1
            else:
                self.make_score()
            if self.score < 0 or not self.inTheAir: 
                break
        return i  # lengh of this chromosome
        



