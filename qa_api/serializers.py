from rest_framework import serializers
from rest_framework.validators import ValidationError
from .models import Question, Answer
import uuid
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Сериализатор для модели Answer - GET /answers/{id}/
class AnswerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Answer
        fields = ['id', 'question', 'user_id', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_user_id(self, value) -> uuid.UUID:
        if not value:
            raise ValidationError("user_id не может быть пустым")
        
        # Если передали строку - конвертируем в UUID
        if isinstance(value, str):
            try:
                value = uuid.UUID(value)
            except ValueError:
                raise ValidationError("user_id должен быть валидным UUID")
        
        return value

    def validate_text(self, value: str) -> str:
        if not value or not value.strip():
            raise ValidationError("Текст ответа не может быть пустым")
        
        cleaned_text = value.strip()
        if len(cleaned_text) < 3:
            raise ValidationError("Ответ должен содержать минимум 3 символа")
        
        return cleaned_text

    def validate_question(self, value: Question) -> Question:
        if not value:
            raise ValidationError("Необходимо указать вопрос")
        return value

# Сериализатор для модели Answer - POST /questions/{id}/answers/
class AnswerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'user_id', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_user_id(self, value) -> uuid.UUID:
        if not value:
            raise ValidationError("user_id не может быть пустым")
        
        if isinstance(value, str):
            try:
                value = uuid.UUID(value)
            except ValueError:
                raise ValidationError("user_id должен быть валидным UUID")
        
        return value

    def validate_text(self, value: str) -> str:
        if not value or not value.strip():
            raise ValidationError("Текст ответа не может быть пустым")
        
        cleaned_text = value.strip()
        if len(cleaned_text) < 3:
            raise ValidationError("Ответ должен содержать минимум 3 символа")
        
        return cleaned_text

    def create(self, validated_data: Dict[str, Any]) -> Answer:
        logger.info(f"Создается ответ на вопрос id={validated_data.get('id')}")
        return super().create(validated_data)


# Сериализатор для модели Question - GET, POST /questions/
class QuestionSerializer(serializers.ModelSerializer):
    answers_count = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'text', 'created_at', 'answers_count']
        read_only_fields = ['id', 'created_at', 'answers_count']

    def validate_text(self, value: str) -> str:
        if not value or not value.strip():
            raise ValidationError("Текст вопроса не может быть пустым")
        
        cleaned_text = value.strip()
        if len(cleaned_text) < 5:
            raise ValidationError("Вопрос должен содержать минимум 5 символов")
        
        return cleaned_text

    def get_answers_count(self, obj: Question) -> int:
        return obj.answers.count()

    def create(self, validated_data: Dict[str, Any]) -> Question:
        logger.info("Создается новый вопрос")
        return super().create(validated_data)


# Сериализатор для модели Question с ответами - GET /questions/{id}/
class QuestionDetailSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    answers_count = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'text', 'created_at', 'answers', 'answers_count']
        read_only_fields = ['id', 'created_at', 'answers', 'answers_count']

    def get_answers_count(self, obj: Question) -> int:
        return obj.answers.count()