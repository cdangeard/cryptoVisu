#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 18:23:08 2019

@author: drimer
"""


class goldenRise:
    def __init__(self):
        self.varema = 0
        self.varrsi = 0
        self.strategy = ''
        self.position = 0
        self.stock = 0

    def makeDecision(self, EMA1,EMA2,rsi):
        decision = 0
        if (EMA1[-1])>(EMA2[-1]):
            if (self.varema)==0:
              self.varema=1
              self.varrsi=0
              self.strategy = "Long strategy"
            if (self.varema)==2:
                if (self.varrsi)==0:
                    self.varema=0
                    self.strategy = "Trend Reversal - Short strategy off"
            if (self.varema)==2:
                if (self.varrsi)==1:
                    self.varema=0
                    self.varrsi=0
            if (self.varema)==2:
                if (self.varrsi)==2:
                    self.varema=0
                    self.varrsi=0
                    self.strategy = "Trend Reversal - SELL 6000$"
                    decision += -6000
        if (EMA1[-1])<(EMA2[-1]):
            if (self.varema)==0:
                self.varema=2
                self.varrsi=0
                self.strategy = "Short strategy"
            if (self.varema)==1:
                if (self.varrsi)==0:
                    self.varema=0
                    self.strategy = "Trend Reversal - Long strategy off"
            if (self.varema)==1:
                if (self.varrsi)==1:
                   self.varema=0
                   self.varrsi=0
                   self.strategy = "Trend Reversal - SELL 5000$"
                   decision += -5000
        if (self.varema)==1:
            if (self.varrsi)==0:
                if (rsi[-1])<31:
                    if (rsi[-2])>(rsi[-1]):
                        self.strategy = "Scanning best buying zone"
                    if (rsi[-2])<(rsi[-1]):
                        self.varrsi=1
                        self.strategy = "BUY 5000$"
                        decision += 5000
            if (self.varrsi)==1:
                if (rsi[-1])>68:
                    if (rsi[-2])<(rsi[-1]):
                        self.strategy = "Scanning best buying zone"
                    if (rsi[-2])>(rsi[-1]):
                        self.varrsi=0
                        self.strategy = "BUY 5000$"
                        decision += -5000
        if (self.varema)==2:
            if (self.varrsi)==0:
                if (rsi[-1])<15:
                    if (rsi[-2])>(rsi[-1]):
                        self.strategy = "Scanning best buying zone"
                    if (rsi[-2])>(rsi[-1]):
                        self.varrsi=1
                        self.strategy = "BUY 2000$"
                        decision += 2000
            if (self.varrsi)==1:
                if (rsi[-1])>53:
                    if (rsi[-2])<(rsi[-1]):
                        self.strategy = "Scanning best buying zone"
                    if (rsi[-2])>(rsi[-1]):
                        self.varrsi=0
                        self.strategy = "SELL 2000$"
                        decision += -2000
                if (rsi[-1])<10:
                    if (rsi[-2])>(rsi[-1]):
                        self.strategy = "Scanning best buying zone"
                    if (rsi[-2])<(rsi[-1]):
                        self.varrsi=2
                        self.strategy = "BUY 4000$"
                        decision += 4000
            if (self.varrsi)==2:
                if (rsi[-1])>53:
                    if (rsi[-2])<(rsi[-1]):
                        self.strategy = "Scanning best buying zone"
                    if (rsi[-2])>(rsi[-1]):
                        self.varrsi=0
                        self.strategy = "SELL 6000$"
                        decision += -6000
        self.position += decision
        return decision
