'''
    Using python script to simulate & calculate HW5
'''
import random

pr_get5head = 1/32
# You can customize simulation rounds for more precise
rounds = 50

# Run Experience
AtLeast1Get5Head_Round = 0
for _ in range(rounds):
    times = 0
    for i in range(100):
        p = random.uniform(0, 1)
        if(p<pr_get5head):
            times += 1
        else:
            pass
    if times > 0 :
        print(f"{times} of 100 people filp coin 5 times in a row and getting 5 head")
        AtLeast1Get5Head_Round+=1
    else:
        print("There is no one")
print(f"Run Simulation {rounds} times, and we can get prob:{AtLeast1Get5Head_Round/rounds}")
print()
# Calculate answer by math
Prob = 1 - ( ( 1-(1/32) )**100 )
print(f"The prob. of [At least 1 person get 5 head] calculated by math  1-( (1-(1/32))**100) is {Prob}")
