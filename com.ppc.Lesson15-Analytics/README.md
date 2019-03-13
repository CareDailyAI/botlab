# Lesson 15 : Analytics

Please reach out to the developers if you would like a tutorial on Analytics.

The analytics.py module in com.ppc.Bot can be easily replaced with an implementation that allows developers to capture analytics to their favorite online analytics services. The current implementation supports MixPanel.

Use the com.ppc.Bot/location/location.py location object to track analytics very easily:

    location_object.track("something happened", properties={"name": statistic})
    
If using the default mixpanel analytics.py implementation, you can set your mixpanel token and turn mixpanel analytics on and off inside domain.py. See the attached domain.py.
