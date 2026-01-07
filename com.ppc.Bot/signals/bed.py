"""
Created on June 18, 2025

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

Author: David Moss

Information vs Knowledge
------------------------
These bed signals come in two flavors that look similar but are intended for
different phases of decision-making:

- information: High-frequency, lower-reliability, immediate observations from devices.
  For example, a radar might report that someone just arrived in bed, even when that
  could be noise or a transient artifact. Information is useful for responsive UX and
  for starting short-lived timers or hypotheses, but it may be wrong.

- knowledge: Slower, higher-reliability conclusions derived from multiple observations
  over time. Knowledge typically requires conditions to hold for a period (e.g., seconds
  to minutes) or corroboration from additional signals before being promoted from
  information. It gives extra confidence about the state of the world (e.g., someone is
  truly in bed), though it can still be wrong in edge cases.

Guidance
--------
- Use information_* signals when you need to react quickly to device-level events or
  to propose a tentative state.
- Use knowledge_* signals when your logic requires confidence and stability (e.g.,
  analytics, notifications that should avoid flapping, or downstream automation).
- Microservices may listen to both and implement their own promotion logic from
  information to knowledge based on domain-specific thresholds and corroboration.
"""

# Your microservices can implement the following events:
# def knowledge_did_arrive_bed(self, botengine, device_object, unique_id, context_id, name)
# def knowledge_did_leave_bed(self, botengine, device_object, unique_id, context_id, name)
# def information_did_arrive_bed(self, botengine, device_object, unique_id, context_id, name)
# def information_did_leave_bed(self, botengine, device_object, unique_id, context_id, name)



def knowledge_did_arrive_bed(botengine, location_object, device_object, unique_id=None, context_id=None, name=None):
    """
    Knowledge: Higher-confidence signal that an occupant has arrived in bed.

    This should be emitted when upstream logic has sufficient evidence that the arrival
    condition is durable (e.g., persistence thresholds met, corroborating sensors agree).

    Parameters
    - botengine: BotEngine
    - location_object: Location object
    - device_object: Device object
    - unique_id: Optional subregion unique ID
    - context_id: Optional context ID
    - name: Optional subregion name; defaults to the device description
    """
    if name is None:
        name = device_object.description

    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'knowledge_did_arrive_bed'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].knowledge_did_arrive_bed(botengine, device_object, unique_id, context_id, name)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'knowledge_did_arrive_bed' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'knowledge_did_arrive_bed'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].knowledge_did_arrive_bed(botengine, device_object, unique_id, context_id, name)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'knowledge_did_arrive_bed' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def knowledge_did_leave_bed(botengine, location_object, device_object, unique_id=None, context_id=None, name=None):
    """
    Knowledge: Higher-confidence signal that an occupant has left the bed.

    Emit this when the leave condition has persisted long enough or has been corroborated,
    reducing the likelihood of false departures from transient noise.

    Parameters
    - botengine: BotEngine
    - location_object: Location object
    - device_object: Device object
    - unique_id: Optional subregion unique ID
    - context_id: Optional context ID
    - name: Optional subregion name; defaults to the device description
    """
    if name is None:
        name = device_object.description

    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'knowledge_did_leave_bed'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].knowledge_did_leave_bed(botengine, device_object, unique_id, context_id, name)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'knowledge_did_leave_bed' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'knowledge_did_leave_bed'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].knowledge_did_leave_bed(botengine, device_object, unique_id, context_id, name)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'knowledge_did_leave_bed' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def information_did_arrive_bed(botengine, location_object, device_object, unique_id=None, context_id=None, name=None):
    """
    Information: Immediate, device-level indication that an occupant may have arrived in bed.

    This is high-frequency and lower-reliability. It is appropriate for responsive UI updates,
    short-lived timers, and hypothesis generation. Promote to knowledge when durability or
    corroboration criteria are satisfied.

    Parameters
    - botengine: BotEngine
    - location_object: Location object
    - device_object: Device object
    - unique_id: Optional subregion unique ID
    - context_id: Optional context ID
    - name: Optional subregion name; defaults to the device description
    """
    if name is None:
        name = device_object.description

    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'information_did_arrive_bed'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].information_did_arrive_bed(
                    botengine, device_object, unique_id, context_id, name
                )
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'information_did_arrive_bed' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'information_did_arrive_bed'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].information_did_arrive_bed(
                            botengine, device_object, unique_id, context_id, name
                        )
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'information_did_arrive_bed' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def information_did_leave_bed(botengine, location_object, device_object, unique_id=None, context_id=None, name=None):
    """
    Information: Immediate, device-level indication that an occupant may have left the bed.

    This is high-frequency and lower-reliability. Use for fast reactions while deferring
    durable decisions until promotion to knowledge.

    Parameters
    - botengine: BotEngine
    - location_object: Location object
    - device_object: Device object
    - unique_id: Optional subregion unique ID
    - context_id: Optional context ID
    - name: Optional subregion name; defaults to the device description
    """
    if name is None:
        name = device_object.description

    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'information_did_leave_bed'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].information_did_leave_bed(
                    botengine, device_object, unique_id, context_id, name
                )
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'information_did_leave_bed' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'information_did_leave_bed'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].information_did_leave_bed(
                            botengine, device_object, unique_id, context_id, name
                        )
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'information_did_leave_bed' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())
