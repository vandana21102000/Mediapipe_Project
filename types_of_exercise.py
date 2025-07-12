import numpy as np
from body_part_angle import BodyPartAngle
from utils import detection_body_part

# Threshold constants
PUSHUP_DOWN_ANGLE = 90
PUSHUP_UP_ANGLE = 150

SQUAT_DOWN_ANGLE = 70
SQUAT_UP_ANGLE = 160

SITUP_DOWN_ANGLE = 55
SITUP_UP_ANGLE = 105


class TypeOfExercise(BodyPartAngle):
    def __init__(self, landmarks):
        super().__init__(landmarks)

    def push_up(self, counter, status):
        left_arm_angle = self.angle_of_the_left_arm()
        right_arm_angle = self.angle_of_the_right_arm()
        avg_arm_angle = (left_arm_angle + right_arm_angle) // 2

        print(f"Push-up Avg Arm Angle: {avg_arm_angle}, Status: {status}, Counter: {counter}")

        if status:
            if avg_arm_angle < PUSHUP_DOWN_ANGLE:
                counter += 1
                status = False
        else:
            if avg_arm_angle > PUSHUP_UP_ANGLE:
                status = True

        return counter, status

    def pull_up(self, counter, status):
        nose = detection_body_part(self.landmarks, "NOSE")
        left_elbow = detection_body_part(self.landmarks, "LEFT_ELBOW")
        right_elbow = detection_body_part(self.landmarks, "RIGHT_ELBOW")
        avg_elbow_y = (left_elbow[1] + right_elbow[1]) / 2

        print(f"Pull-up Nose Y: {nose[1]:.2f}, Elbow Avg Y: {avg_elbow_y:.2f}, Status: {status}, Counter: {counter}")

        if status:
            if nose[1] > avg_elbow_y:
                counter += 1
                status = False
        else:
            if nose[1] < avg_elbow_y:
                status = True

        return counter, status

    def squat(self, counter, status):
        left_leg_angle = self.angle_of_the_left_leg()
        right_leg_angle = self.angle_of_the_right_leg()
        avg_leg_angle = (left_leg_angle + right_leg_angle) // 2

        print(f"Squat Avg Leg Angle: {avg_leg_angle}, Status: {status}, Counter: {counter}")

        if status:
            if avg_leg_angle < SQUAT_DOWN_ANGLE:
                counter += 1
                status = False
        else:
            if avg_leg_angle > SQUAT_UP_ANGLE:
                status = True

        return counter, status

    def walk(self, counter, status):
        right_knee = detection_body_part(self.landmarks, "RIGHT_KNEE")
        left_knee = detection_body_part(self.landmarks, "LEFT_KNEE")

        print(f"Walk Knee X: L={left_knee[0]:.2f}, R={right_knee[0]:.2f}, Status: {status}, Counter: {counter}")

        if status:
            if left_knee[0] > right_knee[0]:
                counter += 1
                status = False
        else:
            if left_knee[0] < right_knee[0]:
                counter += 1
                status = True

        return counter, status

    def sit_up(self, counter, status):
        angle = self.angle_of_the_abdomen()

        print(f"Sit-up Abdomen Angle: {angle}, Status: {status}, Counter: {counter}")

        if status:
            if angle < SITUP_DOWN_ANGLE:
                counter += 1
                status = False
        else:
            if angle > SITUP_UP_ANGLE:
                status = True

        return counter, status

    def calculate_exercise(self, exercise_type, counter, status):
        etype = exercise_type.lower().replace("-", "").replace("_", "")

        if etype == "pushup":
            return self.push_up(counter, status)
        elif etype == "pullup":
            return self.pull_up(counter, status)
        elif etype == "squat":
            return self.squat(counter, status)
        elif etype == "walk":
            return self.walk(counter, status)
        elif etype == "situp":
            return self.sit_up(counter, status)
        else:
            print(f"Unsupported exercise type: {exercise_type}")
            return counter, status

