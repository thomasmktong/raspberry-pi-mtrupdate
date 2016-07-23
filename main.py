from twitter import Twitter
from status import Status
from screen import Screen
from control import Control

print('Initializing...')

screen = Screen()
screen.display_clear()
screen.display_loading_async()

control = Control()
twitter = Twitter()
status = Status()

def message_to_display(messages = None):
    
    global twitter
    global status
    global screen
    
    if(not messages):
        screen.display_loading_async()
        twitter.refresh()
        messages = twitter.messages

    s = status.overall(messages)
    print('Displaying...')
    print(s)
    screen.display_status(s)


screen.display_clear()
print('Running...')

twitter.stream_async(message_to_display)
control.monitor_shake_async(message_to_display)
control.monitor_rotate_async(screen.display_rotate)
