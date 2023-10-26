from home import models as home_models


def create_holes_for_course(course):
    hole_count = 9
    if course.hole_count == "18":
        hole_count = 18

    for hole_num in range(1, hole_count + 1):
        hole_obj = home_models.Hole(
            name=f"Hole: {hole_num}", course=course, order=hole_num
        )
        hole_obj.save()
    return True


def is_admin(user):
    return user.is_superuser or user.groups.filter(name="Admin").exists()
