import json
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random


from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
  #-------------------------------------------
  # Pagination section
  #-------------------------------------------
def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

  #-------------------------------------------
  # Create and configure the app
  #-------------------------------------------
def create_app(test_config=None):
  app = Flask(__name__)
  setup_db(app)
  cors = CORS(app, resources={r"/*": {"origins": "*"}})

  '''
  @TODO Ok: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  '''
  @TODO Ok: Use the after_request decorator to set Access-Control-Allow
  '''
  #-------------------------------------------
  # Headers
  #-------------------------------------------

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO Ok: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST Ok: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  #-------------------------------------------
  # Handler GET request (questions for all available categories)
  #-------------------------------------------

  @app.route('/questions')
  def get_questions():
    selection = Question.query.order_by(Question.id).all()
    questions = paginate_questions(request, selection)
    list_categories = Category.query.all()
    categories = {}
    #categories: type data = array
    for category in list_categories:
      categories[category.id] = category.type

    if len(questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': questions,
      'total_questions': len(Question.query.all()),
      'categories': categories,
      'current_category': None
    })

  '''
  @TODO Ok: 
  Create an endpoint to DELETE question using a question ID. 

  TEST Ok: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  #-------------------------------------------
  # Handler DELETE request (questions)
  #-------------------------------------------
  
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)
      
      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'delete': question_id,
        'questions': current_questions,
        'total_questions': len(Question.query.all()) 
      })

    except:
      abort(422)

  '''
  @TODO Ok: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST Ok: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @TODO Ok: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST Ok: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  #-------------------------------------------
  # Handler POST request (create new questions) and search by term.
  #-------------------------------------------

  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()
    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_difficulty= body.get('difficulty', None)
    new_category= body.get('category', None)
    searchTerm = body.get('searchTerm', None)

    current_category = Category.query.filter(Category.id == new_category).first()

    try:
      if searchTerm:

        selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(searchTerm))) 
        current_questions = paginate_questions(request, selection)       
        
        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(selection.all()),
          'current_category': None
        })
      else:

        question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=current_category.id)
        question.insert()
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(Question.query.all()),
          'current_category': current_category.id
        })

    except:
      abort(422)
    
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  #-------------------------------------------
  # Handler GET request ( questions by category)
  #-------------------------------------------

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_question_by_category(category_id):
    try:
      current_category = Category.query.filter(Category.id == category_id).one_or_none()
      selection = Question.query.filter(Question.category == current_category.id) 
      current_questions = paginate_questions(request, selection)   

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(selection.all()),
        'current_category': current_category.id
      })

    except:
      abort(422)
 
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  #-------------------------------------------
  # Handler GET request ( categories )
  #-------------------------------------------

  @app.route('/categories', methods=['GET'])
  def get_categories():    
    list_categories = Category.query.all()
    categories = {}
    #categories: type data = array
    for category in list_categories:
      categories[category.id] = category.type

    if len(categories) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': categories
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  #-------------------------------------------
  # Handler POST request ( quizzes ) to play the quiz
  #-------------------------------------------

  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
      body = request.get_json()
      # Get id [] (previous questions)
      previousQuestions = body.get('previous_questions')     
      # Get id and type (category)
      quizCategory = body.get('quiz_category', None)   

      category_id = quizCategory['id']
      if int(category_id) == 0 and len(previousQuestions) == 0:
        try: 
          list_question = Question.query.all()
          randoms = list_question[random.randint(0, len(list_question)-1)]
          question = Question.query.filter(Question.id == randoms.id ).one_or_none()

          return jsonify({
            'success': True,
            'question': question.format()
          })
        except:
          abort(404)
      elif int(category_id) != 0 and len(previousQuestions) == 0:
        try:
          list_question = Question.query.filter(Question.category == category_id).all()
          randoms = list_question[random.randint(0, len(list_question)-1)]
          question = Question.query.filter(Question.id == randoms.id ).one_or_none()
          
          return jsonify({
            'success': True,
            'question': question.format()
          })
        except:
          abort(404)

      elif int(category_id) == 0 and len(previousQuestions) != 0:
        try: 
          list_question = Question.query.filter(Question.id.notin_((previousQuestions))).all()
          randoms = list_question[random.randint(0, len(list_question)-1)]
          question = Question.query.filter(Question.id == randoms.id ).one_or_none()

          return jsonify({
            'success': True,
            'question': question.format()
          })
        except:
          abort(404)

      elif int(category_id) != 0 and len(previousQuestions) != 0:
        try:           
          list_question = Question.query.filter(Question.category == category_id).filter(Question.id.notin_((previousQuestions))).all()
          randoms = list_question[random.randint(0, len(list_question)-1)]
          question = Question.query.filter(Question.id == randoms.id ).one_or_none()

          return jsonify({
            'success': True,
            'question': question.format()
          })
        except:
          abort(422)

      else:
          abort(422)        

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  #-------------------------------------------
  # ERROR Handler
  #-------------------------------------------

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "Bad request"
        }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Resource Not found"
        }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "Unprocessable"
        }), 422

  @app.errorhandler(405)
  def not_found(error):
    return jsonify({
        "success": False, 
        "error": 405,
        "message": "Method not allowed"
        }), 405

  @app.errorhandler(500)
  def not_found(error):
    return jsonify({
        "success": False, 
        "error": 500,
        "message": "Internal Server Error"
        }), 500


  return app

    
