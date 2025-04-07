from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Course
from .serializers import CourseListSerializer, CourseDetailSerializer


@api_view(["GET"])
def test_course_list(request):
    courses = Course.objects.all()[:5]  # 첫 5개만 가져오기
    serializer = CourseListSerializer(courses, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def test_course_detail(request, pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=404)

    serializer = CourseDetailSerializer(course)
    return Response(serializer.data)
