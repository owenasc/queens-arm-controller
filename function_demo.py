#Variables
var = 10
var = "a"
var= ["apple", "banana", "cherry"]

#Class Definition
class Dog:
    def __init__(self, name, age, hunger, mood):
        self.name = name
        self.age = age
        self.hunger = hunger
        self.mood = mood

    def bark(self, mood):
        if mood == 'happy':
            print(f"{self.name} says woof!")
        else:
            print(f"{self.name} woofs sadly!")

    def eat_food(self):
        self.hunger -= 1

#Creating an object
dog = Dog(name="Max", age=3, mood="happy", hunger = 5)

# Conditional Statements
if dog.mood == "happy":
    print(dog.bark('happy')) # This would print "Buddy says Woof!"

else:
    print(dog.bark('sad'))   # This would print "Buddy says Sad Woof!"

while dog.hunger > 0:   
    dog.eat_food()
    print(f"{dog.name}'s hunger level is now {dog.hunger}")








