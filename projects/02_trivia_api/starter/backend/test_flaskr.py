import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('test_user', 'test', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # Binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        # Test create_question    
        self.new_question = {
            'question': 'What is the best test? ',
            'answer': 'The test done.',
            'category': 2,
            'difficulty': 3
        }


    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    #-------------------------------------------
    # Unittest Handler GET request (questions all categories)
    #-------------------------------------------
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)       
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))
        self.assertEqual(data['current_category'], None)

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000', json={'difficulty': 2})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not found')

    #-------------------------------------------
    # Unittest Handler DELETE request  (questions)
    #-------------------------------------------

    def test_delete_question(self):
        res = self.client().delete('/questions/49')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 49).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['delete'], 49)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(question, None)

    def test_422_if_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    #-------------------------------------------
    # Unittest Handler POST request (create new questions)
    #-------------------------------------------

    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['current_category'], 2)

    # Fail case pending

    #-------------------------------------------
    # Unittest Search request (questions)
    #-------------------------------------------
    def test_question_search_with_results(self):
        res = self.client().post('/questions', json={'searchTerm': 'hanks'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True )
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 1)
        self.assertEqual(data['current_category'], None)

    def test_get_question_search_without_results(self):
        res = self.client().post('/questions', json={'searchTerm': 'ratio'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True )
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], None)

    #-------------------------------------------
    # Unittest Handler GET question by category 
    #-------------------------------------------
    def test_get_questions_by_category(self):
        res = self.client().get('/categories/3/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)    
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 3)
        self.assertEqual(data['current_category'], 3)

    def test_422_sent_category_out_range(self):
        res = self.client().get('/categories/0/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    #-------------------------------------------
    # Unittest Handler GET all categories 
    #-------------------------------------------
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)       
        self.assertEqual(len(data['categories']), 6)

    def test_404_sent_not_categories(self):
        res = self.client().get('/categories/0')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not found')

  #-------------------------------------------
  # Unittest Handler POST request ( quizzes ) 
  #-------------------------------------------

    def test_play_quiz_whit_category(self):
        res = self.client().post('/quizzes', json={"previous_questions": [],"quiz_category": {"type":"Art","id": "2"}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_404_sent_not_questions_by_category(self):
        res = self.client().post('/quizzes', json={"previous_questions": [],"quiz_category": {"type":"Sport","id": "6"}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()