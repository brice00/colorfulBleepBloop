# Control the color and notes using the mouse.
from math import floor, ceil
from sys import exit
from time import sleep

import pygame
import pygame.midi  # not included in base pygame module


def setup_and_loop():
    pygame.init()  # have to init to get the rest of the game functions to work
    pygame.midi.init()  # have to initialize the midi interface before use
    for i in range(pygame.midi.get_count()):  # choose an output device
        r = pygame.midi.get_device_info(i)
        (interf, name, is_input, is_output, is_opened) = r
        if is_output:
            last_port = i
    midi_out = pygame.midi.Output(last_port, 0)
    midi_out.set_instrument(1)  # start with grand piano

    size = (1000, 700)  # w, l // feel free to change the size 
    # note: 0, 0 = top left corner
    screen = pygame.display.set_mode(size)  # draw a screen of size size
    # top left corner = black
    blue, blue_direction = 0, 1  # start blue as 0, ascending
    while 1:  # go get mouse events forever
        blue, blue_direction = get_event_loop(size, screen, blue, blue_direction, midi_out)


def get_event_loop(size, screen, blue, blue_direction, midi_out):
    blue = blue
    blue_direction = blue_direction
    # have to set these here since the first event is never a mouse event to avoid null return later
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.MOUSEMOTION:  # set the color and note with the mouse
            blue, blue_direction = color_things(event, size, screen, blue, blue_direction)
            duration = 0.1  # how long notes should last, 0.1 feels about right
            y = 20 + floor(event.pos[1] / size[1] * 60)  # lowest note = 20, go up to 80
            x = floor(event.pos[0] / size[0] * 128)  # instrument selection max = 128
            play_note(y, duration, x, midi_out)
            # Instrument examples: 1 piano, 13 marimba, 28 guitar, 43 cello, 59 tuba, 53 choir aah
            # https://www.midi.org/specifications-old/item/gm-level-1-sound-set
            # 21 is the bottom piano note, c7 is 96 consider approximately that range
            # https://www.inspiredacoustics.com/en/MIDI_note_numbers_and_center_frequencies
        pygame.event.clear()  # clean the events to prevent filling up
    return blue, blue_direction


def color_things(event, size, screen, blue, blue_direction):
    red = ceil(event.pos[0] * 255 / size[0])  # x = red
    green = ceil(event.pos[1] * 255 / size[1])  # y = green
    # blue increases, then decreases, could apply to any color
    blue, blue_direction = color_adjuster(blue, blue_direction)
    fillcolor = red, green, blue  # set the screen color
    screen.fill(fillcolor)
    pygame.display.flip()  # actually draw all changes to the screen
    return blue, blue_direction


def color_adjuster(rgb, blue_direction):
    if rgb >= 255:
        rgb, blue_direction = 255, -1  # if the value would go out of range, decrement
    if rgb <= 0:
        rgb, blue_direction = 0, 1
    rgb = rgb + blue_direction  # blue_direction*3 to adjust the blue faster
    return rgb, blue_direction


def play_note(note, duration, instrument, midi_out):
    midi_out.set_instrument(instrument)  # every mouse movement can be a different instrument
    midi_out.note_on(note=note, velocity=120)
    sleep(duration)
    midi_out.note_off(note=note, velocity=0)


if __name__ == '__main__':
    setup_and_loop()
