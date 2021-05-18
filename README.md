# Alexa Timer

This app will call a service at the end of alexa timer. You may 
define from which devices the app will be called. You may also
define which "named" timers the app will act, so for example 
you may say: "alexa, timer kitchen 10 minutes" and have the app
acting only on this timer.

The app also support automatically silencing the alexa device
after a defined delay, so you may let it ring for 30s and then 
be silenced.

Please, note that if ask alexa to cancel a timer, the app will 
also cancel its inner timer.

Note that "devices" and "timer_name" have to be configured as
yaml lists (see the example).