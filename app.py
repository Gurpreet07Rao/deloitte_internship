import json
import unittest
import datetime

with open("./data-1.json","r") as f:
    jsonData1 = json.load(f)
with open("./data-2.json","r") as f:
    jsonData2 = json.load(f)
with open("./data-result.json","r") as f:
    jsonExpectedResult = json.load(f)


def convertFromFormat1 (jsonObject):
    # Add error handling for missing or invalid 'location'
    if 'location' not in jsonObject or not isinstance(jsonObject['location'], str):
        raise ValueError("Invalid or missing 'location' field in format 1 JSON")

    # split the location field using the / as the delimiter
    locationParts = jsonObject['location'].split('/')
    if len(locationParts) < 5:
        raise ValueError("Invalid 'location' format, expected 5 parts separated by '/'")

    # create a new dictionary for the unified format
    result = {
        "deviceID": jsonObject.get('deviceID'), #Extract deviceID
        "deviceType": jsonObject.get('deviceType'), #Extract deviceType
        "timestamp": jsonObject.get('timestamp'), #Extract timestamp
        "location": {
            'country': locationParts[0], #Extract the country from the location 
            'city': locationParts[1],  #Extract the city from the location 
            'area': locationParts[2],  #Extract the area from the location 
            'factory': locationParts[3],  #Extract the factory from the location 
            'section': locationParts[4],  #Extract the section from the location 
        },
        'data':{
            'status': jsonObject.get('operationStatus'), # copy the operationStatus as status
            'temperature': jsonObject.get('temp'), # copy the temp as temperature
        }
    }

    return result

# convert json format 2 to the unified format
def convertFromFormat2 (jsonObject):
    # Add error handling for required keys
    required_keys = ['timestamp', 'deviceID', 'deviceType', 'country', 'city', 'area', 'factory', 'section', 'data']
    for key in required_keys:
        if key not in jsonObject:
            raise ValueError(f"Missing key '{key}' in format 2 JSON")

    #convert the ISO timestamp to milliseconds since epoch
    date = datetime.datetime.strptime(jsonObject['timestamp'], #Extract the ISO timestamp
                                      '%Y-%m-%dT%H:%M:%S.%fZ') #ISO timestamp format
    timestamp = round((date-datetime.datetime(1970,1,1)).total_seconds()*1000) # convert to milliseconds
    # create a new dictionary for the unified format
    result = {
        "deviceID": jsonObject['deviceID']['id'], #Extract device ID
        "deviceType": jsonObject['deviceType']['type'], #Extract device Type
        "timestamp": timestamp, #copy the timestamp
        "location": {
            'country': jsonObject['country'], #Extract country 
            'city': jsonObject['city'],  #Extract city 
            'area': jsonObject['area'],  #Extract area 
            'factory': jsonObject['factory'],  #Extract factory 
            'section': jsonObject['section'],  #Extract section 
            },
            'data': jsonObject['data'] # copy the data
    }

    return result


def main (jsonObject):

    result = {}

    # Detect format based on keys present
    # Check for format 2 first: deviceID is dict
    if ('deviceID' in jsonObject and isinstance(jsonObject['deviceID'], dict)):
        result = convertFromFormat2(jsonObject)
    # Then check for format 1 keys
    elif ('deviceID' in jsonObject and 'deviceType' in jsonObject and 'timestamp' in jsonObject):
        result = convertFromFormat1(jsonObject)
    else:
        raise ValueError("Unknown JSON format")

    return result


class TestSolution(unittest.TestCase):

    def test_sanity(self):
        result = json.loads(json.dumps(jsonExpectedResult))
        self.assertEqual(
            result,
            jsonExpectedResult
        )

    def test_dataType1(self):
        result = main(jsonData1)
        self.assertEqual(
            result,
            jsonExpectedResult,
            'Converting from Type 1 failed'
        )

    def test_dataType2(self):
        result = main(jsonData2)
        self.assertEqual(
            result,
            jsonExpectedResult,
            'Converting from Type 2 failed'
        )

    def test_missing_location_format1(self):
        invalid_json = {
            "deviceID": "12345",
            "deviceType": "sensor",
            "timestamp": 1625097600000,
            # 'location' key missing
            "operationStatus": "active",
            "temp": 22.5
        }
        with self.assertRaises(ValueError) as context:
            main(invalid_json)
        self.assertIn("Invalid or missing 'location' field", str(context.exception))

    def test_invalid_location_format1(self):
        invalid_json = {
            "deviceID": "12345",
            "deviceType": "sensor",
            "timestamp": 1625097600000,
            "location": "USA/NewYork",  # incomplete location parts
            "operationStatus": "active",
            "temp": 22.5
        }
        with self.assertRaises(ValueError) as context:
            main(invalid_json)
        self.assertIn("Invalid 'location' format", str(context.exception))

    def test_missing_keys_format2(self):
        invalid_json = {
            "deviceID": {"id": "12345"},
            "deviceType": {"type": "sensor"},
            "timestamp": "2021-07-01T00:00:00.000Z",
            # missing 'country' key
            "city": "NewYork",
            "area": "Manhattan",
            "factory": "Factory1",
            "section": "SectionA",
            "data": {
                "status": "active",
                "temperature": 22.5
            }
        }
        with self.assertRaises(ValueError) as context:
            main(invalid_json)
        self.assertIn("Missing key 'country'", str(context.exception))

    def test_unknown_format(self):
        invalid_json = {
            "someKey": "someValue"
        }
        with self.assertRaises(ValueError) as context:
            main(invalid_json)
        self.assertIn("Unknown JSON format", str(context.exception))

if __name__ == '__main__':
    unittest.main()
