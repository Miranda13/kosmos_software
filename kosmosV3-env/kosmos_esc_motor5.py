#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Controle du moteur ESC

"""

import logging
from gpiozero import LED, Button, DigitalOutputDevice, PWMOutputDevice
import time
from threading import Thread
from threading import Event

from kosmos_config import *

class kosmosEscMotor(Thread):

    def __init__(self, aConf: KosmosConfig):
        Thread.__init__(self)
        
        # Initialisation port GPIO ESC & RElai               
        self.Relai_GPIO = DigitalOutputDevice(aConf.get_val_int("11_MOTOR_power_gpio"))
        self.PWM_GPIO = PWMOutputDevice(pin=aConf.get_val_int("10_MOTOR_esc_gpio"),frequency=50)
        
        # Initialisation du bouton asservissement moteur
        self.Button_motor = Button(aConf.get_val_int("12_MOTOR_button_gpio"),bounce_time=1.0)
        
        # Evénement pour commander l'arrêt du Thread
        self._pause_event = Event()
        self._continue_event = Event()
        self._t_stop = False 
                  
        # Paramètres Moteur
        self.tps_POSE=aConf.get_val_int("15_MOTOR_pause_time")
        self.vitesse_moteur=aConf.get_val_int("14_MOTOR_vitesse_favorite")
        self.vitesse_min = aConf.get_val_int("13_MOTOR_vitesse_min")
        
    def power_on(self):
        """Commande le relai d'alimentation de l'ESC"""
        self.Relai_GPIO.on() # Fermeture du relai

    def power_off(self):
        """Commande le relai d'alimentation de l'ESC"""
        self.Relai_GPIO.off() # Ouverture du relai
        
    def set_speed(self, aSpeed):
        """Lancement à la vitesse passée en paramètre
        1000 < vitesse < 2100 """
        self.PWM_GPIO.value=aSpeed*0.00005
        logging.debug(f"Moteur vitesse {aSpeed}.")    
        
    def autoArm(self): 
        self.power_on()
        time.sleep(1)
        self.set_speed(self.vitesse_min) #cette commande ne fait pas tourner le KOSMOS
        time.sleep(2)
        
        self.set_speed(self.vitesse_moteur) #celle-ci oui
        self.Button_motor.wait_for_press()#timeout=8)
        logging.info('Bouton asservissement Moteur détecté')
        time.sleep(2)
        
        self.set_speed(0)
        time.sleep(1)
        logging.info('Moteur et ESC prêts !')
        
    def arret_complet(self):
        self.set_speed(0)
        self.PWM_GPIO.off()
    
    def run(self):
        logging.info('Debut du thread moteur ESC.')
        while not self._t_stop:
            if not self._pause_event.isSet():
                self.set_speed(self.vitesse_moteur)
                print(self.Button_motor.value)
                self.Button_motor.wait_for_press()#timeout=8)
                logging.info('Bouton asservissement Moteur détecté')
                time.sleep(1)
                print(self.Button_motor.value)
                self.set_speed(0)
                
                time_debut=time.time()
                delta_time=0
                while not self._pause_event.isSet() and delta_time < self.tps_POSE:
                    delta_time = time.time()-time_debut
                    time.sleep(1.0)
                    print(self.Button_motor.value)
                
            else:
                self.set_speed(0)
                self._continue_event.wait()  
        # End While        
        self.arret_complet()
        logging.info("Thread moteur terminé")
   
    def stop_thread(self):
        """positionne l'évènement qui va provoquer l'arrêt du thread"""
        self._t_stop = True
        self._continue_event.set()
        self._pause_event.set()
  
    def pause(self):
        """suspend le thread pour pouvoir le redémarrer."""
        self._continue_event.clear()
        self._pause_event.set()

    def restart(self):
        """Relance le thread"""
        if self.is_alive():
            self._pause_event.clear()
            self._continue_event.set()
        else:
            self.start()
           
