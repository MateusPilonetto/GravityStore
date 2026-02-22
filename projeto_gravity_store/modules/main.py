from flask import Flask, render_template, request, url_for, session, redirect, Blueprint, jsonify
import css_parser

main_bp = Blueprint('main', __name__)
