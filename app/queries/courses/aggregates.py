def get_course_aggregate(user):    
    return [
        {
            '$match': {
                'name': {
                    '$in': user['courses']
                }
            }
        }, {
            '$lookup': {
                'from': 'Rooms', 
                'localField': 'generalRoom', 
                'foreignField': '_id', 
                'as': 'generalRoom'
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
                'path': '$generalRoom'
            }
        }, {
            '$unwind': {
                'path': '$modRoom'
            }
        }, {
            '$unwind': {
                'path': '$userThread'
            }
        }
    ]