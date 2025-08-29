from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
import logging

from .models import Question, Answer
from .serializers import (
    QuestionSerializer, 
    QuestionDetailSerializer, 
    AnswerSerializer, 
    AnswerCreateSerializer
)

logger = logging.getLogger(__name__)

def api_response(success=True, data=None, message=None, error=None, status_code=200):
    return Response({
        "success": success,
        "data": data,
        "message": message,
        "error": error
    }, status=status_code)


# GET /api/questions/ — список всех вопросов
# POST /api/questions/ — создать новый вопрос
class QuestionListCreateView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.all().prefetch_related('answers')

    @swagger_auto_schema(
        tags=['Questions'],
        operation_summary="Получить список вопросов",
        operation_description="Возвращает пагинированный список всех вопросов с количеством ответов.",
        responses={200: QuestionSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            data=serializer.data,
            message="Список вопросов успешно получен"
        )

    @swagger_auto_schema(
        tags=['Questions'],
        operation_summary="Создать новый вопрос",
        operation_description="Создает новый вопрос. Текст должен содержать минимум 5 символов.",
        request_body=QuestionSerializer(),
        responses={
            201: QuestionSerializer(),
            400: 'Ошибка валидации'
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            question = serializer.save()
            logger.info(f"Создан вопрос id={question.id}")
            return api_response(
                success=True,
                data=serializer.data,
                message="Вопрос успешно создан",
                status_code=status.HTTP_201_CREATED
            )
        else:
            logger.warning(f"Ошибка валидации при создании вопроса: {serializer.errors}")
            return api_response(
                success=False,
                error=serializer.errors,
                message="Ошибка валидации",
                status_code=status.HTTP_400_BAD_REQUEST
            )


# GET /api/questions/{id}/ — получить вопрос и все ответы на него
# DELETE /api/questions/{id}/ — удалить вопрос (вместе с ответами)
class QuestionDetailView(APIView):
    def get_object(self, pk: int) -> Question | None:
        try:
            return Question.objects.prefetch_related('answers').get(pk=pk)
        except Question.DoesNotExist:
            logger.warning(f"Попытка доступа к несуществующему вопросу id={pk}")
            return None

    @swagger_auto_schema(
        tags=['Questions'],
        operation_summary="Получить вопрос со всеми ответами",
        operation_description="Возвращает детальную информацию о вопросе включая все ответы на него.",
        responses={
            200: QuestionDetailSerializer(),
            404: 'Вопрос не найден'
        },
    )
    def get(self, request, pk: int):
        question = self.get_object(pk)
        if not question:
            return api_response(
                success=False,
                error={"id": f"Вопрос с id={pk} не найден"},
                message="Вопрос не найден",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = QuestionDetailSerializer(question)
        logger.info(f"Запрос детальной информации о вопросе id={pk}")
        return api_response(
            success=True,
            data=serializer.data,
            message="Детальная информация о вопросе успешно получена"
        )

    @swagger_auto_schema(
        tags=['Questions'],
        operation_summary="Удалить вопрос",
        operation_description="Удаляет вопрос и все его ответы (каскадное удаление).",
        responses={
            204: 'Вопрос успешно удален',
            404: 'Вопрос не найден'
        },
    )
    def delete(self, request, pk: int):
        question = self.get_object(pk)
        if not question:
            return api_response(
                success=False,
                error={"id": f"Вопрос с id={pk} не найден"},
                message="Вопрос не найден",
                status_code=status.HTTP_404_NOT_FOUND
            )

        answers_count = question.answers.count()
        question.delete()
        logger.info(f"Удален вопрос id={pk} с {answers_count} ответами")
        return api_response(
            success=True,
            data={"id": pk, "deleted_answers": answers_count},
            message=f"Вопрос #{pk} и {answers_count} ответов успешно удалены",
            status_code=status.HTTP_204_NO_CONTENT
        )


# POST /api/questions/{id}/answers/ — добавить ответ к вопросу
class AnswerCreateView(APIView):
    @swagger_auto_schema(
        tags=['Answers'],
        operation_summary="Создать ответ на вопрос",
        operation_description="Создает новый ответ на указанный вопрос",
        request_body=AnswerCreateSerializer,
        responses={
            201: AnswerSerializer,
            400: 'Ошибка валидации',
            404: 'Вопрос не найден'
        },
        manual_parameters=[
            openapi.Parameter(
                'question_id',
                openapi.IN_PATH,
                description="ID вопроса",
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def post(self, request, question_id: int):
        try:
            question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            logger.warning(f"Попытка создать ответ на несуществующий вопрос id={question_id}")
            return api_response(
                success=False,
                error={"question_id": f"Вопрос с id={question_id} не найден"},
                message="Вопрос не найден",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = AnswerCreateSerializer(data=request.data)
        if serializer.is_valid():
            answer = serializer.save(question=question)
            logger.info(f"Создан ответ id={answer.id} на вопрос id={question_id}")

            response_serializer = AnswerSerializer(answer)
            return api_response(
                success=True,
                data=response_serializer.data,
                message="Ответ успешно создан",
                status_code=status.HTTP_201_CREATED
            )
        else:
            logger.warning(
                f"Ошибка валидации при создании ответа на вопрос id={question_id}: {serializer.errors}"
            )
            return api_response(
                success=False,
                error=serializer.errors,
                message="Ошибка валидации данных",
                status_code=status.HTTP_400_BAD_REQUEST
            )

# GET /api/answers/{id}/ — получить конкретный ответ
# DELETE /api/answers/{id}/ — удалить ответ
class AnswerDetailView(APIView):

    def get_object(self, pk: int) -> Answer | None:
        try:
            return Answer.objects.select_related('question').get(pk=pk)
        except Answer.DoesNotExist:
            logger.warning(f"Попытка доступа к несуществующему ответу id={pk}")
            return None

    @swagger_auto_schema(
        tags=['Answers'],
        operation_summary="Получить ответ",
        responses={
            200: AnswerSerializer(),
            404: "Ответ не найден"
        }
    )
    def get(self, request, pk: int):
        answer = self.get_object(pk)
        if not answer:
            return api_response(
                success=False,
                error={"answer_id": f"Ответ с id={pk} не найден"},
                message="Ответ не найден",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = AnswerSerializer(answer)
        logger.info(f"Запрос информации об ответе id={pk}")
        return api_response(
            success=True,
            data=serializer.data,
            message="Ответ получен",
            status_code=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        tags=['Answers'],
        operation_summary="Удалить ответ",
        responses={
            204: "Ответ удален",
            404: "Ответ не найден"
        }
    )
    def delete(self, request, pk: int):
        answer = self.get_object(pk)
        if not answer:
            return api_response(
                success=False,
                error={"answer_id": f"Ответ с id={pk} не найден"},
                message="Ответ не найден",
                status_code=status.HTTP_404_NOT_FOUND
            )

        question_id = answer.question_id
        answer.delete()
        logger.info(f"Удален ответ id={pk} на вопрос id={question_id}")
        return api_response(
            success=True,
            data={"answer_id": pk, "question_id": question_id},
            message=f"Ответ #{pk} успешно удален",
            status_code=status.HTTP_204_NO_CONTENT
        )
