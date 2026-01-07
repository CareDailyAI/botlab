ARCHITECTURE DATA PATH:

1. Data is captured into the BedDevice and normalized into a set of software APIs like 'did_get_in_bed()' and 'did_get_out_of_bed()'.
   We should keep these devices simple: they're only installed on a bed (or chair where you sleep), and services and alerts
   should explicitly be driven from Services & Alerts (Questions) in the app and not Behaviors. 

2. The 'rules/device_bed_microservice.py' grabs the updated device measurement and transforms it into a more
   explicit set of signals to be distributed throughout the architecture (see signals/bed.py)

     knowledge_did_arrive_bed(botengine, device_object, unique_id=None, context_id=None, name=None)
     knowledge_did_leave_bed(botengine, device_object, unique_id=None, context_id=None, name=None)
     
   The unique_id, context_id, name fields are all related to potential 3D sensing radar devices.

   In fact, you'll find in signals/radar.py the radar-specific signals include "information_did_arrive_bed()" and "information_did_leave_bed()".
   The difference between 'information' and 'knowledge' is that knowledge is meant to be reliable, whereas information may be more noisy and
   have false positives. When we're comfortable with the reliability and truth of the raw information, that's when knowledge is generated.

3. Other alerts and services on top can be found generally in 'care/activity' and 'care/inactivity' microservice packages. 
   We rely on the knowledge_did_*_bed() signals to streamline reactions to getting in and out of bed from any bed related device.

