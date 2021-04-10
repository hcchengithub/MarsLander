
# Mars Lander 

class Ship:
    def __init__(self, p0, s0, a0, pwr0, fuel0):
        self.inTheAir = True
        self.fuel = fuel0
        self.p0 = p0  # position, episode-1 only one dimension, the height.
        self.s0 = s0  # speed, episode-1 only one dimension, the virtical speed.  
        self.a0 = a0  # angle, episode-1 only one angle, always 0.
        self.pwr0 = pwr0  # power, thrust power.
        self.trace = []   # all positions
        self.chromosome = []  # all (rotate, thrust) pairs
        self.score = 0
        
    def evaluate(self):
        distances = [lineseg_dists([self.p0], land[i], land[i+1])[0] for i in range(len(land)-1)]  # 與所有 surface 的距離
        shortest = np.argmin(distances)  # 最小的 index 
        self.inTheAir = (0 < np.cross(land[shortest+1]-land[shortest],self.p0-land[shortest+1]))
        self.score = distances[flate]  # distance to target 
        if not self.inTheAir:
            if shortest != flate : self.score = -1  # 撞毀了
            else:
                # bonus1 已經降落目的地，通通有獎
                self.score += B0  
                # bonus2 angle the smaller the better 
                self.score += 2*B0 - (B0/90)*abs(self.a0)
                # bonus3 horizantal speed < 20, virtical speed < 40
                self.score += 2*B0 - (B0/500)*abs(0 if self.s0[0] < 20 else self.s0[0])
                self.score += 2*B0 - (B0/500)*abs(0 if self.s0[1] < 40 else self.s0[1])
                # bonus4 remaining fuel the more the better
                self.score += B0 + (B0/Fuel)*(self.fuel)
        
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
        self.chromosome.append((a1,pwr1))  # 這一步的 command 就是這一步的 gene 
        self.trace.append(p1)  # 這一步走完到達的新位置
        assert pwr1 <=4 and pwr1 >=0 , "Assertion error! 引擎推力超過範圍了！(0~4 之間)"
        assert a1 <=90 and a1 >=-90 , "Assertion error! 小艇角度超過範圍了！(-90~90度之間)"

    # debug version
    def debug_one_step(self):
        # return the score after this step
        chromosome = [(-12, 0), (-12, 1), (-1, 2), (7, 2), (13, 1), (24, 2), (9, 3), (3, 4), (9, 4), (-6, 4), (8, 3), (14, 2), (5, 3), (6, 2), (7, 2), (1, 2), (10, 2), (16, 3), (5, 4), (0, 3), (-2, 3), (-8, 2), (-23, 3), (-32, 2), (-23, 2), (-31, 1), (-40, 1), (-54, 0), (-61, 1), (-61, 1), (-59, 1), (-64, 1), (-56, 2), (-50, 1), (-60, 1), (-69, 0), (-63, 0), (-74, 0), (-74, 0), (-63, 1), (-63, 2), (-66, 3), (-75, 3), (-63, 4), (-49, 4), (-35, 3), (-25, 3), (-10, 3), (-21, 3), (-35, 4), (-33, 4), (-48, 4), (-50, 4), (-65, 4), (-60, 3)] 
        a1 = chromosome[len(self.chromosome)][0] # 這一步的角度 0~15 之間亂轉
        pwr1 = chromosome[len(self.chromosome)][1]  # 這一步的 引擎推力 -1 0 1 亂選
        self.move(a1, pwr1)
    
    def one_step(self):
        # return the score after this step
        a1 = angle15(self.a0, self.a0 + random.randint(-15, 15))  # 這一步的角度 0~15 之間亂轉
        pwr1 = thrust_1(self.pwr0, self.pwr0 + random.randint(-1,1))  # 這一步的 引擎推力 -1 0 1 亂選
        self.move(a1, pwr1)
        # 結果 self.score = -1 表示已經飛出範圍。
        if (self.p0[1] < 0) or (self.p0[0] < 0) or (self.p0[0] > 7000) :  # higher than 3000 is allowed
            self.score = -1
        else:
            self.evaluate()
    
    def explore(self):
        while(True):
            self.one_step()
            if self.score < 0 or not self.inTheAir: 
                break
                
print('~~~ Finished loading ship.py ~~~') 


