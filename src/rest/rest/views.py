import logging
import os
from datetime import datetime

from bson import ObjectId, errors as bson_errors
from pymongo import MongoClient, DESCENDING
from pymongo.errors import PyMongoError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


logger = logging.getLogger(__name__)

_mongo_client = None


class TodoValidationError(Exception):
    pass


class TodoNotFoundError(Exception):
    pass


def get_db():
    global _mongo_client
    if _mongo_client is None:
        mongo_host = os.environ.get("MONGO_HOST", "localhost")
        mongo_port = os.environ.get("MONGO_PORT", "27017")
        _mongo_client = MongoClient(f"mongodb://{mongo_host}:{mongo_port}")
    return _mongo_client['test_db']


class TodoService:
    MAX_DESCRIPTION_LENGTH = 500
    
    @staticmethod
    def validate_description(description):
        if not description or not description.strip():
            raise TodoValidationError("Description cannot be empty")
        if len(description) > TodoService.MAX_DESCRIPTION_LENGTH:
            raise TodoValidationError(f"Description exceeds {TodoService.MAX_DESCRIPTION_LENGTH} characters")
        return description.strip()
    
    @staticmethod
    def serialize_todo(todo):
        return {
            'id': str(todo['_id']),
            'description': todo.get('description', ''),
            'completed': todo.get('completed', False),
            'created_at': todo['created_at'].isoformat() if todo.get('created_at') else None
        }
    
    @staticmethod
    def get_all_todos():
        collection = get_db().todos
        todos = collection.find().sort("created_at", DESCENDING)
        return [TodoService.serialize_todo(todo) for todo in todos]
    
    @staticmethod
    def create_todo(description):
        validated_desc = TodoService.validate_description(description)
        collection = get_db().todos
        
        todo_doc = {
            'description': validated_desc,
            'completed': False,
            'created_at': datetime.utcnow()
        }
        
        result = collection.insert_one(todo_doc)
        todo_doc['_id'] = result.inserted_id
        return TodoService.serialize_todo(todo_doc)
    
    @staticmethod
    def update_todo_status(todo_id, completed):
        collection = get_db().todos
        
        try:
            object_id = ObjectId(todo_id)
        except bson_errors.InvalidId:
            raise TodoValidationError("Invalid todo ID format")
        
        result = collection.update_one(
            {'_id': object_id},
            {'$set': {'completed': completed}}
        )
        
        if result.matched_count == 0:
            raise TodoNotFoundError(f"Todo with id {todo_id} not found")
    
    @staticmethod
    def delete_todo(todo_id):
        collection = get_db().todos
        
        try:
            object_id = ObjectId(todo_id)
        except bson_errors.InvalidId:
            raise TodoValidationError("Invalid todo ID format")
        
        result = collection.delete_one({'_id': object_id})
        
        if result.deleted_count == 0:
            raise TodoNotFoundError(f"Todo with id {todo_id} not found")


class TodoListView(APIView):
    
    def get(self, request):
        try:
            todos = TodoService.get_all_todos()
            return Response({
                'success': True,
                'data': todos,
                'count': len(todos)
            }, status=status.HTTP_200_OK)
        
        except PyMongoError as e:
            logger.error(f"Database error fetching todos: {str(e)}")
            return Response({
                'success': False,
                'error': 'Database error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            logger.error(f"Unexpected error fetching todos: {str(e)}")
            return Response({
                'success': False,
                'error': 'An unexpected error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        try:
            description = request.data.get('description', '')
            todo = TodoService.create_todo(description)
            
            return Response({
                'success': True,
                'message': 'Todo created successfully',
                'data': todo
            }, status=status.HTTP_201_CREATED)
        
        except TodoValidationError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except PyMongoError as e:
            logger.error(f"Database error creating todo: {str(e)}")
            return Response({
                'success': False,
                'error': 'Database error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            logger.error(f"Unexpected error creating todo: {str(e)}")
            return Response({
                'success': False,
                'error': 'An unexpected error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TodoDetailView(APIView):
    
    def patch(self, request, todo_id):
        try:
            completed = request.data.get('completed')
            
            if completed is None:
                return Response({
                    'success': False,
                    'error': 'completed field is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            TodoService.update_todo_status(todo_id, completed)
            
            return Response({
                'success': True,
                'message': 'Todo updated successfully'
            }, status=status.HTTP_200_OK)
        
        except (TodoValidationError, TodoNotFoundError) as e:
            status_code = status.HTTP_404_NOT_FOUND if isinstance(e, TodoNotFoundError) else status.HTTP_400_BAD_REQUEST
            return Response({
                'success': False,
                'error': str(e)
            }, status=status_code)
        
        except PyMongoError as e:
            logger.error(f"Database error updating todo: {str(e)}")
            return Response({
                'success': False,
                'error': 'Database error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            logger.error(f"Unexpected error updating todo: {str(e)}")
            return Response({
                'success': False,
                'error': 'An unexpected error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, todo_id):
        try:
            TodoService.delete_todo(todo_id)
            
            return Response({
                'success': True,
                'message': 'Todo deleted successfully'
            }, status=status.HTTP_200_OK)
        
        except (TodoValidationError, TodoNotFoundError) as e:
            status_code = status.HTTP_404_NOT_FOUND if isinstance(e, TodoNotFoundError) else status.HTTP_400_BAD_REQUEST
            return Response({
                'success': False,
                'error': str(e)
            }, status=status_code)
        
        except PyMongoError as e:
            logger.error(f"Database error deleting todo: {str(e)}")
            return Response({
                'success': False,
                'error': 'Database error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            logger.error(f"Unexpected error deleting todo: {str(e)}")
            return Response({
                'success': False,
                'error': 'An unexpected error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
