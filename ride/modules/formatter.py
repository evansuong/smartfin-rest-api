

class DataFormatter:

    def __init__(self):
        print('formatter initialized')

    def categorize_date(self, dates):
        # for each ride in array
            # parse the unix date into datetime, then map the datetime value into a dictionary 
            # return that dictionary
        print('hey')
        
    def parseAttributes(self, fields):

        if 'rideId' not in fields:
            fields = 'rideId,' + fields

        # parse attributes
        attributes = []
        if ',' in fields:
            attributes = fields.split(',')
        else:
            attributes.append(fields)

        return attributes
