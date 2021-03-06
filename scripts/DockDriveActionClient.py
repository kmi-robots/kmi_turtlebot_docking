#!/usr/bin/env python

import rospy

import actionlib
from kobuki_msgs.msg import AutoDockingAction, AutoDockingGoal
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from actionlib_msgs.msg import GoalStatus
from std_msgs.msg import Empty
from kobuki_msgs.msg import SensorState
from geometry_msgs.msg import Twist

current_status = 0
pose_x = 0.0
pose_y = 0.0


def done_cb(status, result):
    state = 'UNKNOWN'
    if status == GoalStatus.PENDING:
        state = 'PENDING'
    elif status == GoalStatus.ACTIVE:
        state = 'ACTIVE'
    elif status == GoalStatus.PREEMPTED:
        state = 'PREEMPTED'
    elif status == GoalStatus.SUCCEEDED:
        state = 'SUCCEEDED'
    elif status == GoalStatus.ABORTED:
        state = 'ABORTED'
    elif status == GoalStatus.REJECTED:
        state = 'REJECTED'
    elif status == GoalStatus.PREEMPTING:
        state = 'PREEMPTING'
    elif status == GoalStatus.RECALLING:
        state = 'RECALLING'
    elif status == GoalStatus.RECALLED:
        state = 'RECALLED'
    elif status == GoalStatus.LOST:
        state = 'LOST'
    # Print state of action server
    print 'Result - [ActionServer: ' + state + ']: ' + result.text


def active_cb():
    return


def feedback_cb(feedback):
    # Print state of dock_drive module (or node.)
    print 'Feedback: [DockDrive: ' + feedback.state + ']: ' + feedback.text


def docking_cb(data):
    global current_status

    print 'docking: current status is ' + str(current_status)
    if current_status == 0:
        client_mb = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        while not client_mb.wait_for_server(rospy.Duration(5)):
            if rospy.is_shutdown():
                return
            print 'Action server is not connected yet. still waiting...'

        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = 'map'
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = pose_x
        goal.target_pose.pose.position.y = pose_y
        goal.target_pose.pose.orientation.w = 1.0

        print 'goal ready for move_base'

        client_mb.send_goal(goal)
        client_mb.wait_for_result()

        print 'result received'

        client_dk = actionlib.SimpleActionClient('dock_drive_action', AutoDockingAction)
        while not client_dk.wait_for_server(rospy.Duration(5)):
            if rospy.is_shutdown():
                return
            print 'Action server is not connected yet. still waiting...'

        goal = AutoDockingGoal()
        client_dk.send_goal(goal, done_cb, active_cb, feedback_cb)
        print 'Goal: Sent.'
        rospy.on_shutdown(client_dk.cancel_goal)
        client_dk.wait_for_result()
    else:
        pub = rospy.Publisher('/mobile_base/commands/velocity', Twist, queue_size=1)
        msg = Twist()
        msg.linear.x = -0.1
        r = rospy.Rate(10)
        k = 0
        while k < 50:
            pub.publish(msg)
            r.sleep()
            k += 1


def status_cb(msg):
    global current_status
    current_status = msg.charger


def dock_drive_client():
    # add timeout setting
    global pose_x, pose_y

    rospy.Subscriber('/docking', Empty, docking_cb)
    rospy.Subscriber('/mobile_base/sensors/core', SensorState, status_cb)

    pose_x = rospy.get_param('home/x', -0.736)
    pose_y = rospy.get_param('home/y', -1.2)

    rospy.spin()


if __name__ == '__main__':
    try:
        rospy.init_node('dock_drive_client_py', anonymous=True)
        dock_drive_client()
    except rospy.ROSInterruptException:
        print "program interrupted before completion"
