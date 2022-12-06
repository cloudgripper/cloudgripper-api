import time

class Robot():
    def __init__(self, teensy, camera):
        self.camera = camera
        self.teensy = teensy
        self.teensy.flush()
        self.teensy.write("\r\n\r\n".encode('utf-8')) # Hit enter a few times to wake the Printrbot
        time.sleep(2)   # Wait for Printrbot to initialize
        self.teensy.flushInput()  # Flush startup text in self.teensyial input
        
        self.teensy.readline()
        self.teensy.readline()
        self.teensy.readline()
        self.teensy.readline()
        self.teensy.readline()
        self.teensy.readline()
        #Initiailizing
        print("Initiailizing...")
        print("Caliberation might take few secs")
        print("---Caliberating")

        self.grip_open_close(40)
        time.sleep(2)
        self.grip_up_down(10)
        time.sleep(2)

        self.calibrate()
        time.sleep(10)
        #self.moveto(10,10)
        print("---Grip Up")
        # self.up()
        print("---Grip Close")
        #self.grip_close()
        #print("---Moving to center")
        #self.moveto(120,120)
        # time.sleep(2)
        print("---Rotate to 0")
        self.rotate(0)
        print("Initialization Completed")
        
    def calibrate(self):
        self.teensy.write( ('T1' + '\n').encode('utf-8'))
        
    def move_up(self):
        self.teensy.write(('T3' + '\n').encode('utf-8'))
        time.sleep(1)
        
    def move_down(self):
        self.teensy.write(('T4' + '\n').encode('utf-8'))
        time.sleep(1)
        
    def grip_open(self):
        self.teensy.write(('Z1' + '\n').encode('utf-8'))
        time.sleep(1)

    def grip_close(self):
        self.teensy.write(('Z2' + '\n').encode('utf-8'))
        time.sleep(1)

    def grip_open_close(self, val):
        self.teensy.write(('O'+str(val)+ '\n').encode('utf-8'))
    
    def grip_up_down(self, val):
        self.teensy.write(('P'+str(val)+ '\n').encode('utf-8'))
        
    def rotate(self,angle):
        self.teensy.write(('R'+str(angle) + '\n').encode('utf-8'))
        
    def move_to(self,x,y):
        self.teensy.write( ('G00 X'+str(x)+' Y'+str(y) + '\n').encode('utf-8'))
    
    def step_right(self):
        self.teensy.write(('DD' + '\n').encode('utf-8'))
    def step_left(self):
        self.teensy.write(('LL' + '\n').encode('utf-8'))
    def step_forward(self):
        self.teensy.write(('FF' + '\n').encode('utf-8'))
    def step_backward(self):
        self.teensy.write(('BB' + '\n').encode('utf-8'))
    def get_image(self):
        ret, frame  = self.camera.read()
        return frame