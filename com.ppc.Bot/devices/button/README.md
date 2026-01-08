# Button Device Class Information

These are the classes in this directory:

* button.py
* button_multi.py
* button_panic.py
    
A **Multi Button** is one that can identify when the button is being pressed, and when it is released.

A **Panic Button** is one that identifies only a binary on/off panic status.

While they both come in a button form factor, these are actually 2 completely different devices from a software perspective.   For consistency, both are subclassed from the **Button** device class.