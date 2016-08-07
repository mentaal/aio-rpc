from time import sleep
class Blocking():
    def block_10ms(self):
        'basic test function to sleep for 10 ms'
        #print("Blocking for 10 ms..")
        a = 5
        sleep(0.01)
    def block(self, num):
        #print("Blocking for {} seconds".format(num))
        sleep(num)
    def add(self, num1, num2):
        #print("Blocking for {} seconds".format(num))
        return num1+num2


