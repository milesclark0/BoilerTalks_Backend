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

def get_all_courses_aggregate():
    return [
    {
        '$match': {
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

def get_course_users_aggregate(courseName):
    return [
        {
            '$match': {
                'courses': courseName
            }
        },{
            '$lookup': {
                'from': 'Profiles',
                'localField': 'username',
                'foreignField': 'username',
                'as': 'profile'
            }
        }, {
            '$unwind': {
                'path': '$profile'
            }
        }, {
            '$project': {
                '_id': 0, 
                'username': 1,
                'profilePic': "$profilePicture",
                'displayName': "$profile.displayName"
            }
        }
    ]
   
