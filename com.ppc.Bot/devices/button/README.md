These are the classes in this directory:

* button_multi.py
    * button_multi_develco.py
    * button_multi_linkhigh.py
    
* button_panic.py
    * button_panic_develco.py
    
A **Multi Button** is one that can identify when the button is being pressed, and when it is released.

A **Panic Button** is one that identifies only a binary on/off panic status.

While they both come in a button form factor, these are actually 2 completely different devices from a software perspective.

We can delete the following after around January 1, 2021 (and update the controller.py to remove these references too)
* button.py
* button_develco.py
* button_linkhigh.py
