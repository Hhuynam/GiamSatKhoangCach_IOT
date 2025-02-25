import time
import datetime
import cv2
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, render_template, Response
import os
import requests
import numpy as np

# Khởi tạo Firebase
cred = credentials.Certificate(
    r"D:\Project\GiamSatKhoangCach_IOT\Firebase\giamsatkhoangcachiot-firebase-adminsdk-e6yo6-e7c20c31c6.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://giamsatkhoangcachiot-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

my_firebase = db.reference()
