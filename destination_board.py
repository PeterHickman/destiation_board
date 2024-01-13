#!/usr/bin/env python3

import sys
import re
import requests
import time

import pygame
import yaml

try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

import settings

class Stops:
    def __init__(self, stops):
        self.image = pygame.Surface((settings.screen_width, settings.screen_height))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()

        images = []
        self.rects = []
        self.actions = []
        self.rows = 0
        max_width = 0

        for stop in stops:
            self.rows += 1
            i = font1.render(stops[stop], True, YELLOW, BLACK)
            r = i.get_rect()
            images.append(i)
            self.rects.append(r)
            self.actions.append(stop)

            w = r.width
            if w > max_width:
                max_width = w

        offset_x = (settings.screen_width - max_width) // 2

        y = (self.rects[0].height * len(stops)) - ((self.rows - 1) * 5)

        offset_y = (settings.screen_height - y) // 2

        for r in self.rects:
            r.x += offset_x
            r.y += offset_y
            offset_y += r.height + 5

        for i in range(self.rows):
            self.image.blit(images[i], self.rects[i])

    def draw(self):
        screen.fill(background)
        screen.blit(self.image, self.rect)
        pygame.display.flip()

    def clicked(self, pos):
        for i in range(self.rows):
            if self.rects[i].collidepoint(pos):
                return self.actions[i]

        return None

class Board:
    def __init__(self, stops):
        self.stops = stops
        self.stop_id = None
        self.loaded_at = None

        self.image = pygame.Surface((settings.screen_width, settings.screen_height))
        self.rect = self.image.get_rect()

    def draw(self, stop_id):
        if self.stop_id != stop_id:
            self._load_stop(stop_id)
        else:
            diff = time.time() - self.loaded_at
            if diff > 60:
                self._load_stop(stop_id)

        screen.fill(background)
        screen.blit(self.image, self.rect)
        pygame.display.flip()

    def _load_stop(self, stop_id):
        self.stop_id = stop_id
        self.loaded_at = time.time()
        try:
            html = self._get_page(stop_id)
            destinations = self._parse_page(html)
        except:
            destinations = []
            print('There was an issue getting the page')

        m0 = 0
        m1 = 0
        m2 = 0
        for d in destinations:
            if d[0].get_rect().width > m0:
                m0 = d[0].get_rect().width
            if d[1].get_rect().width > m1:
                m1 = d[1].get_rect().width
            if d[2].get_rect().width > m2:
                m2 = d[2].get_rect().width

        offset_x = (settings.screen_width - m0 - m1 - m2 - 10) // 2

        self.image.fill(background)

        h = font1.render(self.stops[stop_id], True, YELLOW, BLACK)
        r = h.get_rect()
        r.x = (settings.screen_width - r.width) // 2
        r.y = 3
        self.image.blit(h, r)

        if len(destinations) == 0:
            h = font2.render("No services available", True, YELLOW, BLACK)
            r = h.get_rect()
            r.center = (settings.screen_width // 2, settings.screen_height // 2)
            self.image.blit(h, r)
        else:
            y = (destinations[0][0].get_rect().height * len(destinations)) + ((len(destinations) - 1) * settings.destination_y_gap)

            offset_y = ((settings.screen_height - y) // 2) + r.height + 6

            for d in destinations:
                r = d[0].get_rect()
                r.x = offset_x + (m0 - r.width)
                r.y = offset_y
                self.image.blit(d[0], r)

                r = d[1].get_rect()
                r.x = offset_x + settings.destination_y_gap + m0
                r.y = offset_y
                self.image.blit(d[1], r)

                r = d[2].get_rect()
                r.x = offset_x + (m2 - r.width) + settings.destination_y_gap + m0 + settings.destination_y_gap + m1
                r.y = offset_y
                self.image.blit(d[2], r)

                offset_y += r.height + 5

    def _get_page(self, stop_id):
        url = f"https://www.buses.co.uk/stops/{stop_id}"
        r = requests.get(url)
        return r.text

    def _parse_page(self, html):
        destinations = []

        parsed_html = BeautifulSoup(html, features="html.parser")
        c = 0
        for line in parsed_html.body.find_all('p', attrs={'class':'sr-only'}):
            text = re.sub("\s+"," ",line.text.strip())
            # Service - 22. Destination - Churchill Sq. Departure time - 1 min. Departure 1 of 5. Live. Follow the link for a list of stops this journey stops at.
            m = re.search(r' ([0-9A-Z]+)\. Destination - (.*)\. .* time - ([0-9:Due]+)', text)
            if m:
                if c < settings.destinations:
                    c += 1
                    destinations.append([font2.render(x, True, YELLOW, BLACK) for x in m.groups()])
            else:
                print(text)

        return destinations

class Favourites:
    def __init__(self, favourites):
        self.favourites = favourites
        self.loaded_at = 0

        self.image = pygame.Surface((settings.screen_width, settings.screen_height))
        self.rect = self.image.get_rect()

    def draw(self):
        diff = time.time() - self.loaded_at
        if diff > 60:
            self._load_favourites()

        screen.fill(background)
        screen.blit(self.image, self.rect)
        pygame.display.flip()

    def _load_favourites(self):
        self.loaded_at = time.time()

        rows = []
        for fleet_number in self.favourites:
            try:
                html = self._get_page(fleet_number)
                rows.append(font2.render(self._parse_page(html, fleet_number), True, YELLOW, BLACK))
            except Exception as inst:
                # print(inst)
                rows = []
                print('There was an issue getting the page')

        self.image.fill(background)
        i = font1.render('Favourites', True, YELLOW, BLACK)
        r = i.get_rect()
        r.x = (settings.screen_width - r.width) // 2
        self.image.blit(i, r)

        if len(rows) == 0:
            h = font2.render("No services available", True, YELLOW, BLACK)
            r = h.get_rect()
            r.center = (settings.screen_width // 2, settings.screen_height // 2)
            self.image.blit(h, r)
        else:
            y = (rows[0].get_rect().height * len(rows)) + ((len(rows) - 1) * settings.destination_y_gap)

            offset_y = ((settings.screen_height - y) // 2) + r.height + 6

            m = 0
            for d in rows:
                r = d.get_rect()
                if r.width > m:
                    m = r.width

            offset_x = (settings.screen_width - m) // 2;

            for d in rows:
                r = d.get_rect()
                r.x = offset_x
                r.y = offset_y
                self.image.blit(d, r)

                offset_y += r.height + 5


    def _get_page(self, fleet_number):
        url = f"https://www.buses.co.uk/_ajax/vehicles/{fleet_number}"
        r = requests.get(url)
        return r.text

    def _parse_page(self, html, fleet_number):
        if "This vehicle's route is" in html:
            i1 = html.index('<h3>') + 4
            i2 = html.index('</h3>')
            t = html[i1:i2]
            return f"{fleet_number} is on route {t}"
        else:
            return f"{fleet_number} is at the garage"

def load_stops():
    with open("config.yaml", 'r') as stream:
        stops = yaml.safe_load(stream)['stops']
        stops['0'] = '**Favourites**'

    return stops

def load_favourites():
    with open("config.yaml", 'r') as stream:
        favourites = yaml.safe_load(stream)['favourites']

    return favourites

def where_the_user_clicked():
    pos = None

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()

    return pos

pygame.init()

pygame.mouse.set_visible(True)
if settings.fake_touch:
    pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))

BLACK = 0, 0, 0
YELLOW = 255, 255, 0

background = BLACK

font1 = pygame.font.Font(settings.font, 48)
font2 = pygame.font.Font(settings.font, 24)

stops = load_stops()
main = Stops(stops)
board = Board(stops)

favourites = load_favourites()
faves = Favourites(favourites)

screen = pygame.display.set_mode((settings.screen_width, settings.screen_height), settings.mode_flags)

stop_id = None

while True:
    if stop_id == None:
        main.draw()
    elif stop_id == '0':
        faves.draw()
    else:
        board.draw(stop_id)

    pos = where_the_user_clicked()

    if pos:
        if stop_id == None:
            stop_id = main.clicked(pos)
        else:
            stop_id = None

