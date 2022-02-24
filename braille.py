import serial
import time


class Braille():
    def __init__(self,COM):  #initialises the braille printer, use COM as serial port
        self.xstep = 1.5
        self.zstep = 40
        self.xmin = 5
        self.xsize = 84
        self.speed = 600
        self.x = 0
        self.y = 0
        self.z = 30
        self.ser = serial.Serial(COM, '250000', timeout=4)

    def init_printer(self):
        self.readall()
        self.write('G28')                   # home all
        self.x = 0
        self.y = 0
        self.z = 0
        self.write('M211 Z1 S0')            # disable the z endStop
        self.move()

    def open_serial(self):
        if (not self.ser.is_open) :
            self.ser.open()
    
    def close_serial(self):
        if (self.ser.is_open) :
            self.ser.close()
    
    def servo(self,number):                        # move servo to position 0-7
        self.write('M400')
        self.write('M280 P0 S' + str(self.servo_number(number)))
        time.sleep(0.5)

    def servo_number(self,number):                 # Calibration of the servo position from 0-7 to degres
        return {
            0: 0,
            1: 100,
            2: 50,
            3: 150,
            4: 25,
            5: 130,
            6: 70,
            7: 175,
        }[number]

    def letters(self,letter):					#Transforms the letters into numbers for the encoder
        return{
            '1' : [1,0],
            '2' : [3,0],
            '3' : [1,1],
            '4' : [1,3],
            '5' : [1,2],
            '6' : [3,1],
            '7' : [3,3],
            '8' : [3,2],
            '9' : [2,1],
            '0' : [2,3],
            'а' : [1,0],
            'б' : [3,0],
            'в' : [2,7],
            'г' : [3,3],
            'д' : [1,3],
            'е' : [1,2],
            'ё' : [1,4],
            'ж' : [1,3],
            'з' : [5,6],
            'и' : [2,1],
            'й' : [7,5],
            'к' : [5,0],
            'л' : [7,0],
            'м' : [5,1],
            'н' : [5,3],
            'о' : [5,2],
            'п' : [7,1],
            'р' : [7,2],
            'с' : [6,1],
            'т' : [6,3],
            'у' : [5,4],
            'ф' : [3,1],
            'х' : [3,2],
            'ц' : [1,1],
            'ч' : [7,3],
            'ш' : [1,6],
            'щ' : [5,5],
            'ъ' : [7,6],
            'ы' : [6,5],
            'ь' : [6,7],
            'э' : [2,5],
            'ю' : [3,6],
            'я' : [3,5],
            '.' : [2,6],
            '!' : [6,2],
            '-' : [4,4],
            '"' : [6,4],
            '(' : [4,3],
            ')' : [3,4],
            ',' : [2,0],
            '?' : [2,4],
            'a' : [1,0],
            'b' : [3,0],
            'c' : [1,1],
            'd' : [1,3],
            'e' : [1,2],
            'f' : [3,1],
            'g' : [3,3],
            'h' : [3,2],
            'i' : [2,1],
            'j' : [2,3],
            'k' : [5,0],
            'l' : [7,0],
            'm' : [5,1],
            'n' : [5,3],
            'o' : [5,2],
            'p' : [7,1],
            'q' : [7,3],
            'r' : [7,2],
            's' : [6,1],
            't' : [6,3],
            'u' : [5,4],
            'v' : [7,4],
            'W' : [2,7],
            'x' : [5,5],
            'y' : [5,7],
            'z' : [5,6],
            ' ' : [0,0],
        }.get(letter, [7, 7])
    x = 0

    def write(self,line):                           ## Serial write to the arduino
        print(line)
        self.ser.write((line+' \n').encode())
        response = ' : ' + self.ser.readline().decode()
        print(response)
        while response.find('unknown') != -1:
            self.ser.write((line + ' \n').encode())
            response = ' : ' + self.ser.readline().decode()
            print("reprinting line : " + line)
        while response.find('busy') != -1:
            time.sleep(1)
            response = ' : ' + self.ser.readline().decode()
            print(response)




    def move(self):						
        self.write('G1' + ' X' + str(self.x) + ' Y' + str(self.y) + ' Z' + str(self.z) + ' F' + str(self.speed))
        #print('G0' + ' X' + str(self.x) + ' Y' + str(self.y) + ' Z' + str(self.z))
        time.sleep(0.5)

    def eject_paper(self):
        
        self.servo(0)
        if self.x > 30:
            self.x = self.x - 30
        else:
            self.x = 0 
        
        
        self.move()
        self.z = self.z + 100
        self.move()
        

    def emboss(self,digits):							#routine for embossing letters
        if self.x < self.xmin:
            self.y = self.xmin
            self.move()
            self.x = self.xmin - 2*self.xstep
            self.move()
        if self.x > self.xsize:

            self.x = self.x - 3*self.xstep
            self.move()
            self.z = self.z + self.zstep
            self.move()
            self.x = self.xmin - 3*self.xstep
            self.y = self.xmin
            self.move()
           
            
        for digit in digits:
            if digit==0:
                self.x = self.x + self.xstep
                self.y = self.y + self.xstep
                self.move()
            else:
                self.servo(digit)
                self.y = self.y + self.xstep
                self.move()
                self.x = self.y + 2*self.xstep
                self.move()
                self.x = self.y - 3*self.xstep
                self.move()
                self.servo(0)
        self.x = self.x + self.xstep
        self.y = self.y + self.xstep
        self.move()

    def readall(self):										#Clears the buffer
        self.ser.readline()
        while self.ser.in_waiting != 0:
            print(self.ser.readline().decode("utf-8"))


# abcdefghijklmnopqrstuvxyz



