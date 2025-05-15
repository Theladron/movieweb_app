import os
import sqlalchemy
from flask import Flask, request, render_template, redirect, abort, url_for
from datamanager.sqlite_data_manager import SQLiteDataManager