from time import sleep
class Blocking():
    def block_10ms(self):
        print("Blocking for 10 ms..")
        sleep(0.01)
    def block(self, num):
        print("Blocking for {} seconds".format(num))
        sleep(num)


