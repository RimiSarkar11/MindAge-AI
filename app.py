from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

import json
import random

from analyzer import analyze_text


app = Flask(__name__)


# =========================================================
# APP CONFIGURATION
# =========================================================

app.config["SECRET_KEY"] = "mindage-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mindage.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# =========================================================
# DATABASE
# =========================================================

db = SQLAlchemy(app)


# =========================================================
# LOGIN MANAGER
# =========================================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"


# =========================================================
# USER MODEL
# =========================================================

class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )


# =========================================================
# EXISTING EMOTIONAL ASSESSMENT MODEL
# =========================================================

class Assessment(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    positivity = db.Column(db.Integer)

    negativity = db.Column(db.Integer)

    neutrality = db.Column(db.Integer)

    empathy = db.Column(db.Integer)

    impulsiveness = db.Column(db.Integer)

    emotional_stability = db.Column(db.Integer)

    maturity_age = db.Column(db.Integer)

    communication_style = db.Column(
        db.String(200)
    )


# =========================================================
# QUESTION MODEL
# =========================================================

class Question(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    category = db.Column(
        db.String(50),
        nullable=False
    )

    question = db.Column(
        db.String(500),
        nullable=False
    )

    question_type = db.Column(
        db.String(20),
        default="MCQ"
    )

    options = db.Column(
        db.Text,
        nullable=False
    )


# =========================================================
# MODULE RESULT MODEL
# =========================================================

class ModuleResult(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    category = db.Column(
        db.String(50),
        nullable=False
    )

    result_title = db.Column(
        db.String(150),
        nullable=False
    )

    profile_description = db.Column(
        db.Text,
        nullable=False
    )

    scores = db.Column(
        db.Text,
        nullable=False
    )

    answers = db.Column(
        db.Text,
        nullable=False
    )


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

with app.app_context():

    db.create_all()


# =========================================================
# QUESTION DATA
# =========================================================

QUESTION_DATA = {

    "lifestyle": [

        {
            "question": "When buying clothes, what matters most to you?",
            "options": [
                {
                    "label": "Comfort",
                    "scores": {"practicality": 3, "trend": 1, "quality": 2}
                },
                {
                    "label": "Brand",
                    "scores": {"practicality": 1, "trend": 2, "quality": 2}
                },
                {
                    "label": "Price",
                    "scores": {"practicality": 3, "trend": 0, "quality": 1}
                },
                {
                    "label": "Latest trends",
                    "scores": {"practicality": 0, "trend": 3, "quality": 1}
                },
                {
                    "label": "Quality",
                    "scores": {"practicality": 2, "trend": 1, "quality": 3}
                }
            ]
        },

        {
            "question": "How often do you usually shop for clothes?",
            "options": [
                {
                    "label": "Rarely",
                    "scores": {"practicality": 3, "trend": 0, "quality": 2}
                },
                {
                    "label": "Once in a few months",
                    "scores": {"practicality": 2, "trend": 1, "quality": 2}
                },
                {
                    "label": "About once a month",
                    "scores": {"practicality": 1, "trend": 2, "quality": 2}
                },
                {
                    "label": "Several times a month",
                    "scores": {"practicality": 0, "trend": 3, "quality": 1}
                }
            ]
        },

        {
            "question": "When you find something you really like while shopping, what do you usually do?",
            "options": [
                {
                    "label": "Buy it immediately",
                    "scores": {"practicality": 0, "trend": 2, "quality": 1}
                },
                {
                    "label": "Compare prices first",
                    "scores": {"practicality": 3, "trend": 1, "quality": 1}
                },
                {
                    "label": "Think about whether I really need it",
                    "scores": {"practicality": 3, "trend": 0, "quality": 2}
                },
                {
                    "label": "Wait for a sale",
                    "scores": {"practicality": 3, "trend": 1, "quality": 1}
                },
                {
                    "label": "Check reviews",
                    "scores": {"practicality": 2, "trend": 1, "quality": 3}
                }
            ]
        },

        {
            "question": "Which clothing style do you prefer most?",
            "options": [
                {
                    "label": "Casual",
                    "scores": {"practicality": 3, "trend": 1, "quality": 1}
                },
                {
                    "label": "Formal",
                    "scores": {"practicality": 2, "trend": 1, "quality": 3}
                },
                {
                    "label": "Sporty",
                    "scores": {"practicality": 3, "trend": 2, "quality": 1}
                },
                {
                    "label": "Traditional",
                    "scores": {"practicality": 2, "trend": 0, "quality": 3}
                },
                {
                    "label": "Trendy / Fashion-focused",
                    "scores": {"practicality": 0, "trend": 3, "quality": 1}
                }
            ]
        },

        {
            "question": "When choosing between an expensive branded product and a cheaper alternative, what would you usually choose?",
            "options": [
                {
                    "label": "The branded product",
                    "scores": {"practicality": 1, "trend": 2, "quality": 3}
                },
                {
                    "label": "The cheaper alternative",
                    "scores": {"practicality": 3, "trend": 0, "quality": 1}
                },
                {
                    "label": "Whichever has better quality",
                    "scores": {"practicality": 2, "trend": 1, "quality": 3}
                },
                {
                    "label": "Whichever has better reviews",
                    "scores": {"practicality": 2, "trend": 1, "quality": 3}
                },
                {
                    "label": "It depends on the product",
                    "scores": {"practicality": 2, "trend": 1, "quality": 2}
                }
            ]
        },

        {
            "question": "When planning your monthly spending, what approach do you prefer?",
            "options": [
                {
                    "label": "I plan most expenses",
                    "scores": {"practicality": 3, "trend": 0, "quality": 2}
                },
                {
                    "label": "I keep a rough budget",
                    "scores": {"practicality": 2, "trend": 1, "quality": 2}
                },
                {
                    "label": "I mostly spend as needed",
                    "scores": {"practicality": 1, "trend": 1, "quality": 2}
                },
                {
                    "label": "I enjoy spontaneous purchases",
                    "scores": {"practicality": 0, "trend": 3, "quality": 1}
                }
            ]
        }
    ],


    "cars": [

        {
            "question": "What matters most when choosing a car?",
            "options": [
                {
                    "label": "Safety",
                    "scores": {"practicality": 3, "comfort": 2, "performance": 1}
                },
                {
                    "label": "Performance",
                    "scores": {"practicality": 1, "comfort": 1, "performance": 3}
                },
                {
                    "label": "Comfort",
                    "scores": {"practicality": 2, "comfort": 3, "performance": 1}
                },
                {
                    "label": "Technology",
                    "scores": {"practicality": 2, "comfort": 2, "performance": 2}
                },
                {
                    "label": "Mileage / Efficiency",
                    "scores": {"practicality": 3, "comfort": 1, "performance": 1}
                }
            ]
        },

        {
            "question": "Which type of car would you prefer?",
            "options": [
                {
                    "label": "SUV",
                    "scores": {"practicality": 3, "comfort": 3, "performance": 2}
                },
                {
                    "label": "Sedan",
                    "scores": {"practicality": 2, "comfort": 3, "performance": 2}
                },
                {
                    "label": "Hatchback",
                    "scores": {"practicality": 3, "comfort": 2, "performance": 1}
                },
                {
                    "label": "Sports car",
                    "scores": {"practicality": 0, "comfort": 1, "performance": 3}
                },
                {
                    "label": "Electric vehicle",
                    "scores": {"practicality": 2, "comfort": 2, "performance": 2}
                }
            ]
        },

        {
            "question": "What kind of driving experience do you prefer?",
            "options": [
                {
                    "label": "Relaxed and comfortable",
                    "scores": {"practicality": 2, "comfort": 3, "performance": 1}
                },
                {
                    "label": "Fast and exciting",
                    "scores": {"practicality": 1, "comfort": 1, "performance": 3}
                },
                {
                    "label": "Balanced",
                    "scores": {"practicality": 2, "comfort": 2, "performance": 2}
                },
                {
                    "label": "Efficient and economical",
                    "scores": {"practicality": 3, "comfort": 1, "performance": 1}
                }
            ]
        },

        {
            "question": "How important is technology in your car?",
            "options": [
                {
                    "label": "Very important",
                    "scores": {"practicality": 2, "comfort": 2, "performance": 2}
                },
                {
                    "label": "Somewhat important",
                    "scores": {"practicality": 2, "comfort": 2, "performance": 1}
                },
                {
                    "label": "Not very important",
                    "scores": {"practicality": 3, "comfort": 2, "performance": 1}
                }
            ]
        },

        {
            "question": "What would you prioritize for a long road trip?",
            "options": [
                {
                    "label": "Comfort",
                    "scores": {"practicality": 2, "comfort": 3, "performance": 1}
                },
                {
                    "label": "Fuel / energy efficiency",
                    "scores": {"practicality": 3, "comfort": 1, "performance": 1}
                },
                {
                    "label": "Performance",
                    "scores": {"practicality": 1, "comfort": 1, "performance": 3}
                },
                {
                    "label": "Storage and practicality",
                    "scores": {"practicality": 3, "comfort": 2, "performance": 1}
                }
            ]
        }
    ],


    "books": [

        {
            "question": "Which type of book do you enjoy most?",
            "options": [
                {
                    "label": "Fiction",
                    "scores": {"imagination": 3, "learning": 1, "consistency": 2}
                },
                {
                    "label": "Biography",
                    "scores": {"imagination": 1, "learning": 3, "consistency": 2}
                },
                {
                    "label": "Self-development",
                    "scores": {"imagination": 1, "learning": 3, "consistency": 3}
                },
                {
                    "label": "Science / Technology",
                    "scores": {"imagination": 1, "learning": 3, "consistency": 2}
                },
                {
                    "label": "Mystery / Thriller",
                    "scores": {"imagination": 3, "learning": 1, "consistency": 2}
                }
            ]
        },

        {
            "question": "How often do you read?",
            "options": [
                {
                    "label": "Every day",
                    "scores": {"imagination": 2, "learning": 2, "consistency": 3}
                },
                {
                    "label": "Several times a week",
                    "scores": {"imagination": 2, "learning": 2, "consistency": 2}
                },
                {
                    "label": "Occasionally",
                    "scores": {"imagination": 2, "learning": 1, "consistency": 1}
                },
                {
                    "label": "Rarely",
                    "scores": {"imagination": 1, "learning": 1, "consistency": 0}
                }
            ]
        },

        {
            "question": "What usually makes you choose a book?",
            "options": [
                {
                    "label": "Interesting story",
                    "scores": {"imagination": 3, "learning": 1, "consistency": 2}
                },
                {
                    "label": "Useful knowledge",
                    "scores": {"imagination": 1, "learning": 3, "consistency": 2}
                },
                {
                    "label": "Recommendation",
                    "scores": {"imagination": 2, "learning": 2, "consistency": 2}
                },
                {
                    "label": "Author",
                    "scores": {"imagination": 2, "learning": 2, "consistency": 2}
                }
            ]
        },

        {
            "question": "Which format do you prefer?",
            "options": [
                {
                    "label": "Physical books",
                    "scores": {"imagination": 2, "learning": 2, "consistency": 3}
                },
                {
                    "label": "E-books",
                    "scores": {"imagination": 2, "learning": 3, "consistency": 2}
                },
                {
                    "label": "Audiobooks",
                    "scores": {"imagination": 2, "learning": 2, "consistency": 2}
                }
            ]
        },

        {
            "question": "When reading something difficult, what do you usually do?",
            "options": [
                {
                    "label": "Keep trying until I understand",
                    "scores": {"imagination": 1, "learning": 3, "consistency": 3}
                },
                {
                    "label": "Look for another explanation",
                    "scores": {"imagination": 2, "learning": 3, "consistency": 2}
                },
                {
                    "label": "Skip it",
                    "scores": {"imagination": 2, "learning": 1, "consistency": 0}
                },
                {
                    "label": "Come back to it later",
                    "scores": {"imagination": 2, "learning": 2, "consistency": 2}
                }
            ]
        }
    ],


    "movies": [

        {
            "question": "Which movie genre do you enjoy most?",
            "options": [
                {
                    "label": "Drama",
                    "scores": {"story": 3, "emotion": 3, "adventure": 1}
                },
                {
                    "label": "Comedy",
                    "scores": {"story": 2, "emotion": 2, "adventure": 2}
                },
                {
                    "label": "Action",
                    "scores": {"story": 1, "emotion": 1, "adventure": 3}
                },
                {
                    "label": "Thriller / Mystery",
                    "scores": {"story": 3, "emotion": 1, "adventure": 3}
                },
                {
                    "label": "Romance",
                    "scores": {"story": 2, "emotion": 3, "adventure": 1}
                }
            ]
        },

        {
            "question": "What matters most in a good movie?",
            "options": [
                {
                    "label": "Strong story",
                    "scores": {"story": 3, "emotion": 2, "adventure": 1}
                },
                {
                    "label": "Interesting characters",
                    "scores": {"story": 3, "emotion": 3, "adventure": 1}
                },
                {
                    "label": "Exciting action",
                    "scores": {"story": 1, "emotion": 1, "adventure": 3}
                },
                {
                    "label": "Humour",
                    "scores": {"story": 2, "emotion": 2, "adventure": 2}
                }
            ]
        },

        {
            "question": "Where do you prefer watching movies?",
            "options": [
                {
                    "label": "Cinema",
                    "scores": {"story": 2, "emotion": 2, "adventure": 3}
                },
                {
                    "label": "At home",
                    "scores": {"story": 3, "emotion": 2, "adventure": 1}
                },
                {
                    "label": "Either is fine",
                    "scores": {"story": 2, "emotion": 2, "adventure": 2}
                }
            ]
        },

        {
            "question": "How do you feel about movies with emotional endings?",
            "options": [
                {
                    "label": "I really enjoy them",
                    "scores": {"story": 2, "emotion": 3, "adventure": 1}
                },
                {
                    "label": "Sometimes",
                    "scores": {"story": 2, "emotion": 2, "adventure": 2}
                },
                {
                    "label": "I prefer lighter endings",
                    "scores": {"story": 2, "emotion": 1, "adventure": 2}
                }
            ]
        },

        {
            "question": "Would you rewatch a movie you really liked?",
            "options": [
                {
                    "label": "Definitely",
                    "scores": {"story": 3, "emotion": 3, "adventure": 2}
                },
                {
                    "label": "Sometimes",
                    "scores": {"story": 2, "emotion": 2, "adventure": 2}
                },
                {
                    "label": "Usually not",
                    "scores": {"story": 1, "emotion": 1, "adventure": 3}
                }
            ]
        }
    ],


    "hobbies": [

        {
            "question": "How do you prefer spending your free time?",
            "options": [
                {
                    "label": "Creative activities",
                    "scores": {"creativity": 3, "learning": 2, "social": 1}
                },
                {
                    "label": "Learning something new",
                    "scores": {"creativity": 1, "learning": 3, "social": 1}
                },
                {
                    "label": "Sports / physical activities",
                    "scores": {"creativity": 1, "learning": 2, "social": 3}
                },
                {
                    "label": "Spending time with friends",
                    "scores": {"creativity": 1, "learning": 1, "social": 3}
                },
                {
                    "label": "Relaxing alone",
                    "scores": {"creativity": 2, "learning": 2, "social": 0}
                }
            ]
        },

        {
            "question": "Which hobby sounds most interesting to you?",
            "options": [
                {
                    "label": "Photography",
                    "scores": {"creativity": 3, "learning": 2, "social": 1}
                },
                {
                    "label": "Gaming",
                    "scores": {"creativity": 2, "learning": 2, "social": 2}
                },
                {
                    "label": "Reading",
                    "scores": {"creativity": 1, "learning": 3, "social": 1}
                },
                {
                    "label": "Travel",
                    "scores": {"creativity": 2, "learning": 2, "social": 3}
                },
                {
                    "label": "Cooking",
                    "scores": {"creativity": 3, "learning": 2, "social": 2}
                }
            ]
        },

        {
            "question": "When learning a new hobby, what motivates you most?",
            "options": [
                {
                    "label": "Creating something",
                    "scores": {"creativity": 3, "learning": 2, "social": 1}
                },
                {
                    "label": "Improving my skills",
                    "scores": {"creativity": 1, "learning": 3, "social": 1}
                },
                {
                    "label": "Meeting people",
                    "scores": {"creativity": 1, "learning": 1, "social": 3}
                },
                {
                    "label": "Having fun",
                    "scores": {"creativity": 2, "learning": 1, "social": 2}
                }
            ]
        },

        {
            "question": "How often do you try a new hobby or activity?",
            "options": [
                {
                    "label": "Very often",
                    "scores": {"creativity": 3, "learning": 3, "social": 2}
                },
                {
                    "label": "Sometimes",
                    "scores": {"creativity": 2, "learning": 2, "social": 2}
                },
                {
                    "label": "Rarely",
                    "scores": {"creativity": 1, "learning": 1, "social": 1}
                }
            ]
        },

        {
            "question": "Would you prefer a hobby you can do alone or with others?",
            "options": [
                {
                    "label": "Mostly alone",
                    "scores": {"creativity": 2, "learning": 3, "social": 0}
                },
                {
                    "label": "Mostly with others",
                    "scores": {"creativity": 1, "learning": 1, "social": 3}
                },
                {
                    "label": "A mixture of both",
                    "scores": {"creativity": 2, "learning": 2, "social": 2}
                }
            ]
        }
    ]
}


# =========================================================
# SEED QUESTIONS
# =========================================================

def seed_questions():

    for category, questions in QUESTION_DATA.items():

        existing_count = Question.query.filter_by(
            category=category
        ).count()

        if existing_count > 0:
            continue

        for item in questions:

            question = Question(
                category=category,
                question=item["question"],
                question_type="MCQ",
                options=json.dumps(item["options"])
            )

            db.session.add(question)

    db.session.commit()


with app.app_context():

    seed_questions()


# =========================================================
# LOGIN USER LOADER
# =========================================================

@login_manager.user_loader
def load_user(user_id):

    return db.session.get(
        User,
        int(user_id)
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "dashboard.html"
    )

# =========================================================
# EMOTIONAL MATURITY PROFILE SUMMARY
# =========================================================

def generate_emotional_profile(result):

    if result["communication_style"] == "Emotionally mature and balanced":

        return (
            "Balanced Communicator",
            "Your responses show a generally positive and balanced "
            "communication pattern, with signs of emotional awareness "
            "and consideration for others."
        )

    elif result["communication_style"] == "Moderately self-aware":

        return (
            "Developing Self-Awareness",
            "Your responses show a moderate level of emotional awareness. "
            "You appear to recognize your reactions while still having "
            "areas where reflection and emotional control can develop."
        )

    else:

        return (
            "Emotionally Reactive Communicator",
            "Your responses show stronger emotional reactions in the "
            "situations described. Taking time to reflect before reacting "
            "may help support more balanced communication."
        )

# =========================================================
# EMOTIONAL MATURITY
# =========================================================

@app.route("/emotional-maturity")
@login_required
def emotional_maturity():

    return redirect(
        url_for("home")
    )


# =========================================================
# GENERIC QUESTIONNAIRE ROUTE
# =========================================================

@app.route(
    "/section/<category>",
    methods=["GET", "POST"]
)
@login_required
def section(category):

    valid_categories = [
        "lifestyle",
        "cars",
        "books",
        "movies",
        "hobbies"
    ]

    if category not in valid_categories:

        return redirect(
            url_for("dashboard")
        )


    questions = Question.query.filter_by(
        category=category
    ).all()


    if request.method == "POST":

        scores = {}

        selected_answers = {}


        for question in questions:

            answer = request.form.get(
                f"question_{question.id}"
            )

            if not answer:
                continue


            selected_answers[
                str(question.id)
            ] = answer


            options = json.loads(
                question.options
            )


            selected_option = next(
                (
                    option
                    for option in options
                    if option["label"] == answer
                ),
                None
            )


            if selected_option:

                for dimension, value in selected_option[
                    "scores"
                ].items():

                    scores[dimension] = (
                        scores.get(dimension, 0)
                        + value
                    )


        if len(selected_answers) != len(questions):

            flash(
                "Please answer all questions before submitting.",
                "warning"
            )

            return redirect(
                url_for(
                    "section",
                    category=category
                )
            )


        # -----------------------------------------
        # Convert scores to percentages
        # -----------------------------------------

        max_score = len(questions) * 3

        percentage_scores = {}


        for dimension, score in scores.items():

            percentage_scores[dimension] = round(
                (score / max_score) * 100
            )


        # -----------------------------------------
        # Determine profile
        # -----------------------------------------

        profile_title, profile_description = (
            generate_profile(
                category,
                percentage_scores
            )
        )


        # -----------------------------------------
        # Save result
        # -----------------------------------------

        result = ModuleResult(

            user_id=current_user.id,

            category=category,

            result_title=profile_title,

            profile_description=profile_description,

            scores=json.dumps(
                percentage_scores
            ),

            answers=json.dumps(
                selected_answers
            )
        )


        db.session.add(result)

        db.session.commit()


        return redirect(
            url_for(
                "module_result",
                result_id=result.id
            )
        )


    # Prepare options for template

    for question in questions:

        question.options_list = json.loads(
            question.options
        )


    category_names = {

        "lifestyle": (
            "Lifestyle & Shopping",
            "👕"
        ),

        "cars": (
            "Cars & Mobility",
            "🚗"
        ),

        "books": (
            "Books & Reading",
            "📚"
        ),

        "movies": (
            "Movies & Entertainment",
            "🎬"
        ),

        "hobbies": (
            "Hobbies & Interests",
            "🎨"
        )
    }


    section_name, section_icon = (
        category_names[category]
    )


    return render_template(
        "questionnaire.html",
        section_name=section_name,
        section_icon=section_icon,
        questions=questions
    )


# =========================================================
# PROFILE GENERATION
# =========================================================

def generate_profile(category, scores):

    if category == "lifestyle":

        practicality = scores.get(
            "practicality",
            0
        )

        trend = scores.get(
            "trend",
            0
        )

        quality = scores.get(
            "quality",
            0
        )


        if practicality >= trend and practicality >= quality:

            return (
                "Practical & Value-Conscious",
                "Your choices show a stronger preference for "
                "practicality, usefulness and thoughtful spending."
            )

        elif trend >= practicality and trend >= quality:

            return (
                "Trend-Oriented Explorer",
                "Your choices show a stronger interest in "
                "fashion, variety and keeping up with trends."
            )

        else:

            return (
                "Quality-Focused Shopper",
                "Your choices show a stronger preference for "
                "quality, durability and getting good value from products."
            )


    if category == "cars":

        performance = scores.get(
            "performance",
            0
        )

        comfort = scores.get(
            "comfort",
            0
        )

        practicality = scores.get(
            "practicality",
            0
        )


        if performance >= comfort and performance >= practicality:

            return (
                "Performance-Oriented Driver",
                "Your choices show a stronger preference for "
                "performance, excitement and driving experience."
            )

        elif comfort >= performance and comfort >= practicality:

            return (
                "Comfort-Oriented Driver",
                "Your choices show a stronger preference for "
                "comfort, relaxation and a pleasant driving experience."
            )

        else:

            return (
                "Practical Driver",
                "Your choices show a stronger preference for "
                "utility, efficiency and everyday practicality."
            )


    if category == "books":

        learning = scores.get(
            "learning",
            0
        )

        imagination = scores.get(
            "imagination",
            0
        )

        consistency = scores.get(
            "consistency",
            0
        )


        if learning >= imagination and learning >= consistency:

            return (
                "Curious Learner",
                "Your reading choices show a strong interest "
                "in learning, knowledge and discovering new ideas."
            )

        elif imagination >= learning and imagination >= consistency:

            return (
                "Imaginative Reader",
                "Your reading choices show a strong interest "
                "in stories, imagination and creative experiences."
            )

        else:

            return (
                "Consistent Reader",
                "Your choices show a preference for regular "
                "reading and building a steady reading habit."
            )


    if category == "movies":

        story = scores.get(
            "story",
            0
        )

        emotion = scores.get(
            "emotion",
            0
        )

        adventure = scores.get(
            "adventure",
            0
        )


        if story >= emotion and story >= adventure:

            return (
                "Story-Driven Viewer",
                "You appear to place strong importance on "
                "stories, characters and engaging narratives."
            )

        elif emotion >= story and emotion >= adventure:

            return (
                "Emotion-Driven Viewer",
                "You appear to value emotional connection, "
                "characters and memorable moments."
            )

        else:

            return (
                "Adventure-Seeking Viewer",
                "You appear to enjoy excitement, action "
                "and energetic entertainment experiences."
            )


    if category == "hobbies":

        creativity = scores.get(
            "creativity",
            0
        )

        learning = scores.get(
            "learning",
            0
        )

        social = scores.get(
            "social",
            0
        )


        if creativity >= learning and creativity >= social:

            return (
                "Creative Explorer",
                "Your hobby choices show a strong interest "
                "in creativity, making and self-expression."
            )

        elif learning >= creativity and learning >= social:

            return (
                "Curious Learner",
                "Your interests show a strong preference "
                "for learning, exploration and skill development."
            )

        else:

            return (
                "Social Explorer",
                "Your interests show a strong preference "
                "for shared experiences, activities and connection."
            )


    return (
        "Unique Explorer",
        "Your answers reveal an interesting combination "
        "of preferences."
    )


# =========================================================
# RESULT PAGE
# =========================================================

@app.route("/result/<int:result_id>")
@login_required
def module_result(result_id):

    result = ModuleResult.query.filter_by(
        id=result_id,
        user_id=current_user.id
    ).first_or_404()


    scores = json.loads(
        result.scores
    )


    category_names = {

        "lifestyle": (
            "Lifestyle & Shopping",
            "👕"
        ),

        "cars": (
            "Cars & Mobility",
            "🚗"
        ),

        "books": (
            "Books & Reading",
            "📚"
        ),

        "movies": (
            "Movies & Entertainment",
            "🎬"
        ),

        "hobbies": (
            "Hobbies & Interests",
            "🎨"
        )
    }


    section_name, section_icon = (
        category_names[result.category]
    )


    return render_template(
        "result.html",
        result=result,
        scores=scores,
        section_name=section_name,
        section_icon=section_icon
    )


# =========================================================
# HISTORY
# =========================================================

@app.route("/history")
@login_required
def history():

    results = ModuleResult.query.filter_by(
        user_id=current_user.id
    ).order_by(
        ModuleResult.id.desc()
    ).all()


    return render_template(
        "history.html",
        results=results
    )


# =========================================================
# EXISTING EMOTIONAL MATURITY ANALYSIS
# =========================================================

@app.route("/", methods=["GET", "POST"])
@login_required
def home():

    if request.method == "POST":

        text = request.form["text"]

        result = analyze_text(text)

        profile_title, profile_summary = generate_emotional_profile(
            result
        )

        assessment = Assessment(

            user_id=current_user.id,

            positivity=result["positivity"],

            negativity=result["negativity"],

            neutrality=result["neutrality"],

            empathy=result["empathy"],

            impulsiveness=result["impulsiveness"],

            emotional_stability=result[
                "emotional_stability"
            ],

            maturity_age=result[
                "maturity_age"
            ],

            communication_style=result[
                "communication_style"
            ]
        )

        db.session.add(assessment)

        db.session.commit()

        return render_template(
            "index.html",
            result=result,
            user_text=text,
            profile_title=profile_title,
            profile_summary=profile_summary
        )

    return render_template(
        "index.html",
        result=None,
        user_text="",
        profile_title=None,
        profile_summary=None
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        username = request.form["username"]

        email = request.form["email"]

        password = request.form["password"]


        existing_user = User.query.filter(
            (User.username == username) |
            (User.email == email)
        ).first()


        if existing_user:

            flash(
                "Username or email already exists.",
                "danger"
            )

            return redirect(
                url_for("register")
            )


        hashed_password = generate_password_hash(
            password
        )


        user = User(

            username=username,

            email=email,

            password_hash=hashed_password
        )


        db.session.add(user)

        db.session.commit()


        flash(
            "Registration successful. Please login.",
            "success"
        )


        return redirect(
            url_for("login")
        )


    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]


        user = User.query.filter_by(
            email=email
        ).first()


        if user and check_password_hash(
            user.password_hash,
            password
        ):

            login_user(user)

            return redirect(
                url_for("dashboard")
            )


        flash(
            "Invalid email or password.",
            "danger"
        )


    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()


    flash(
        "You have been logged out.",
        "success"
    )


    return redirect(
        url_for("login")
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)