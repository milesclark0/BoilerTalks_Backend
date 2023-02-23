def get_course_aggregate(user):
    return [
    {
        '$match': {
            'name': {
                '$in': user['courses']
                
            }
        }
    }, {
        '$unwind': {
            'path': '$rooms'
        }
    }, {
        '$lookup': {
            'from': 'Rooms', 
            'localField': 'rooms', 
            'foreignField': '_id', 
            'as': 'rooms'
        }
    }, {
        '$lookup': {
            'from': 'Rooms', 
            'localField': 'modRoom', 
            'foreignField': '_id', 
            'as': 'modRoom'
        }
    }, {
        '$lookup': {
            'from': 'Threads', 
            'localField': 'userThread', 
            'foreignField': '_id', 
            'as': 'userThread'
        }
    }, {
        '$unwind': {
            'path': '$userThread'
        }
    }, {
        '$unwind': {
            'path': '$modRoom'
        }
    }
]