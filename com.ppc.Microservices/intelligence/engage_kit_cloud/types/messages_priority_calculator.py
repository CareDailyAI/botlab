'''
Created on October 16, 2023

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from intelligence.engage_kit_cloud.types.cloud_model import CloudTopicPriority

class PriorityCalculator:
    @staticmethod
    def custom_priority_calculation(content: str, phrases: list = []) -> CloudTopicPriority:
        # priority calculation based on model that use messages content
        priority_value = CloudTopicPriority.UNSET.value
        
        for phrase in phrases:
            text = phrase.get('text', '')
            scores = phrase.get('scores', [])
            if content == text and len(scores) > 0:
                priority_value = max(range(len(scores)), key=scores.__getitem__)
                break
        return CloudTopicPriority(priority_value)