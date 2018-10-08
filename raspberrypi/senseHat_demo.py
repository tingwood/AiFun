from sense_emu import SenseHat

sense = SenseHat()
sense.show_message("hello world!")


#green = (0, 255, 0)
#white = (255, 255, 255)

#while True:
#    humidity = sense.humidity
#    humidity_value = 64 * humidity / 100
#    pixels = [green if i < humidity_value else white for i in range(64)]
#    sense.set_pixels(pixels)