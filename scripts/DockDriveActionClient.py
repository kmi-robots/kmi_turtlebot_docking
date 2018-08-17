#!/usr/bin/env python

import rospy

import actionlib
from kobuki_msgs.msg import AutoDockingAction, AutoDockingGoal
from actionlib_msgs.msg import GoalStatus
from std_msgs.msg import Empty


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


def docking_cb(msg):
    client = actionlib.SimpleActionClient('dock_drive_action', AutoDockingAction)
    while not client.wait_for_server(rospy.Duration(5)):
        if rospy.is_shutdown():
            return
        print 'Action server is not connected yet. still waiting...'

    goal = AutoDockingGoal()
    client.send_goal(goal, done_cb, active_cb, feedback_cb)
    print 'Goal: Sent.'
    rospy.on_shutdown(client.cancel_goal)
    client.wait_for_result()

    print client.get_result()


def dock_drive_client():
    # add timeout setting

    rospy.Subscriber("docking", Empty, docking_cb)
    rospy.spin()


if __name__ == '__main__':
    try:
        rospy.init_node('dock_drive_client_py', anonymous=True)
        dock_drive_client()
    except rospy.ROSInterruptException:
        print "program interrupted before completion"
