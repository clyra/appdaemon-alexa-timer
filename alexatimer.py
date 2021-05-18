import hassapi as hass
import json


class AlexaTimer(hass.Hass):

    def initialize(self):
        self.mytimers = {}
        self.mytimer_name = []
        self.myservice = None
        self.myservice_entity = None
        self.mydelay = None
        self.mystopword = 'stop'
        self.debug = False

        if "devices" in self.args:
            for device in self.args["devices"]:
                sensor = "sensor." + device + "_next_timer"
                #self.log("iniciando: {}".format(sensor))
                self.listen_state(self.update_timerlist, sensor, attribute="sorted_active")
                self.mytimers[sensor] = {}
                self.init_timerlist(sensor)

        if "timer_name" in self.args:
            for tn in self.args["timer_name"]:
                self.mytimer_name.append(tn)
        #self.log("names: {}".format(self.mytimer_name))
        
        if "service" in self.args:
            self.myservice = self.args['service']

        if "entity_id" in self.args:
            self.myservice_entity = self.args['entity_id']

        if "silence_alexa_delay" in self.args:
            self.mydelay = self.args['silence_alexa_delay']

        if "alexa_stop_word" in self.args:
            self.mystopword = self.args['alexa_stop_word']

        if "debug" in self.args:
            self.debug = self.args['debug']        

    def add_timer(self, sensor, timer):
        
        self.mylog('add_timer')
        if 'timerLabel' in timer[1].keys() and timer[1]['timerLabel']:
            label = timer[1]['timerLabel'].lower()
        else:
            label = None

        if not self.mytimer_name or label in self.mytimer_name:
        
           self.mytimers[sensor][timer[0]] =  {}
           self.mytimers[sensor][timer[0]]['remainingTime'] = timer[1]['remainingTime'] 
           if label:
              self.mytimers[sensor][timer[0]]['timerLabel'] = label
           
           self.mytimers[sensor][timer[0]]['handler'] = self.run_in(self.timer_up, int(timer[1]['remainingTime']/1000+1), dsensor = sensor)
           
    def remove_timer(self, sensor, remove_id, cancel_handler=True):

        if (remove_id in self.mytimers[sensor].keys() and
           (not self.mytimer_name or self.mytimers[sensor][remove_id]['timerLabel'] in self.mytimer_name)):
            
            try:
                if cancel_handler:
                  self.cancel_timer(self.mytimers[sensor][str(remove_id)]['handler'])
                  #self.log('timer canceled')
            except:
                self.mylog('this should never happen')
                pass
            
            
            self.mytimers[sensor].pop(str(remove_id), None)

    def timer_up(self, kwargs):
        
        self.mylog("timer_up: {}".format(kwargs['dsensor']))
        self.call_service(self.myservice, entity_id = self.myservice_entity)
        if self.mydelay:
            alexa_dev = "media_player." + kwargs['dsensor'][7:-11]
            self.run_in(self.silence_alexa, self.mydelay, alexa = alexa_dev)

    def silence_alexa(self, kwargs):

        self.mylog("shutdown {}: sending: {} ".format(kwargs['alexa'], self.mystopword))
        self.call_service('media_player/play_media', entity_id = kwargs['alexa'], media_content_id = self.mystopword, media_content_type = 'custom')

    def update_timerlist(self, sensor, attribute, old, new, kwargs):

        current_timers = []
        deleted_timers = []
        
        self.mylog("estado: {} {}".format(self.friendly_name(sensor), new))

        try:
            timers = json.loads(new)
        except:
            timers = []

        for i in timers:
          self.mylog("timers: {} {}".format(i[0], i[1]['remainingTime']))
          current_timers.append(i[0])

          if i[0] not in self.mytimers[sensor].keys():
              self.add_timer(sensor, i)

        for j in self.mytimers[sensor].keys():            
           if str(j) not in current_timers:
            self.mylog("it seems that {} is not on the list".format(j))
            deleted_timers.append(j)

        for h in deleted_timers:
            self.remove_timer(sensor, h)    

        self.mylog("mytimers: {}".format(self.mytimers))


    def init_timerlist(self, sensor):

        self.mylog("to add: {}".format(sensor))
        active = json.loads(self.get_state(entity_id=sensor, attribute="sorted_active"))
               
        for i in active:
           #self.log("active timers: {} {}".format(i[0], i[1]['remainingTime']))
           if i[0] not in self.mytimers[sensor].keys():
             self.add_timer(sensor, i)

        self.mylog("mytimers: {}".format(self.mytimers))
        
    def mylog(self, s):
        if self.debug:
            self.log(s)


