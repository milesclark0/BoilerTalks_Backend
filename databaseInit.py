
import re
from app.models.Course import Course
from app.models.Room import Room
from app.models.Thread import Thread



def sentence_case(string):
    if string != '':
        # camel case to sentence case
        result = re.sub('([a-z])([A-Z])', r'\1 \2', string=string)
        #clean up special cases
        # turn Ph D into PhD if space is after
        result = re.sub('(Ph)([ ])(D)([ ])', r'\1\3\4', result)
        # turn Ph D into PhD if no space is after
        result = re.sub('(Ph)([ ])(D)([A-Z])', r'\1\3 \4', result)  
        # put space after comma if there is no space
        result = re.sub('(,)([A-Z])', r'\1 \2', result)
        # put space after : if there is no space
        result = re.sub('(:)([A-Z])', r'\1 \2', result)
        # put space after acronym if there is no space
        result = re.sub('([A-Z]{2,})([A-Z][a-z])', r'\1 \2', result)
        #replace weird pattern occurring in some class names
        result = re.sub('(â€™s)', "'s", result)
        return result
    return

#sample = True will only save a course for every different department
def populate_db_from_file(sample = False):
    with open("./app/assets/all_purdue_courses.txt", "r") as f:
        prev_abbr = ""
        for line in f:
            section = line.split("-")
            class_abbr = ""
            class_num = ""
            for i, letter in enumerate(section[0]):
                if letter.isdigit():
                    class_abbr = section[0][:i]
                    class_num = section[0][i:]
                    break
            class_name = sentence_case(section[1].strip())
            class_abbr, class_name, class_num = class_abbr.strip(), class_name, class_num.strip()
            course = Course(class_abbr+ " " + class_num, class_name, "user1", class_abbr, "Spring 2023")
            #print(section[0], section[1])        
            #print(f"\t1: {class_abbr} 2: {class_num} 3: {class_name}")
            #only save a course for every different department
            if sample:
                if prev_abbr != class_abbr:
                    print(course.getDepartment(), course.getDescription())
                    ret = course.save()
                    if not ret.success:
                        print(f"\tError: {ret.message}")
                        print(f"\tField Errors: {ret.data}")
                prev_abbr = class_abbr
            else:
                ret = course.save()
                if not ret.success:
                    print(f"\tError: {ret.message}")
                    #print(f"\tField Errors: {ret.data}")


def clear_courses_threads_rooms():
    Course.collection.delete_many({})
    Room.collection.delete_many({})
    Thread.collection.delete_many({})

if __name__ == "__main__":
    populate_db_from_file()
    #clear_courses_threads_rooms()
        